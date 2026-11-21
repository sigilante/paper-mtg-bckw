#!/usr/bin/env python3
"""L4: the library/graveyard/exile ("LGX") machine for BCKW+SI terms, stdlib only.

Abstract model of the paper-Magic construction in notes/L4-library-paper-native.md.

Zones (lists of card names):
  L  library,   L[0]  is the top card (kept revealed, e.g. by Courser of Kruphix)
  G  graveyard, G[-1] is the top card; read bottom-to-top G is the scanned prefix of the term
  X  exile, a face-up pool (multiset); the fuel reserve and the garbage heap

Term encoding: Polish (prefix) notation, one card per symbol. '@' is an application
card; 'S','K','I','B','C','W' are combinator cards; any other name is a variable card.
  ((K x) y)  ->  @ @ K x y

The ONLY moves on cards are four single-card transfers, each the effect of a real card
(Oracle text quoted in the note):
  MILL         L top      -> G top    (mill one card)
  RECLAIM(d)   G[depth d] -> L top    ("put target card from your graveyard on top of your library")
  OOZE(d)      G[depth d] -> X        ("exile target card from a graveyard")
  PULL(name)   X card     -> G top    ("put target face-up card in exile into its owner's graveyard")
Control (which move next, and the bracket count that finds a subterm's extent) belongs to
the referee procedure `run`, not to the game. That is the honest model: cooperative /
refereed, not forced.
"""
import sys
from collections import Counter

ARITY = {'I': 1, 'K': 2, 'W': 2, 'B': 3, 'C': 3, 'S': 3}
# Right-hand sides in prefix form over argument indices 1..k.
RHS = {
    'I': [1],
    'K': [1],
    'W': ['@', '@', 1, 2, 2],
    'B': ['@', 1, '@', 2, 3],
    'C': ['@', '@', 1, 3, 2],
    'S': ['@', '@', 1, 3, '@', 2, 3],
}


class OutOfFuel(Exception):
    pass


class Machine:
    def __init__(self, term_cards, pool=None, trace=False):
        self.L = list(term_cards)
        self.G = []
        self.X = Counter(pool or {})
        self.n_cards = len(self.L) + sum(self.X.values())
        self.moves = Counter()
        self.rewrites = []
        self.trace = trace

    # ---- the four card moves -------------------------------------------------
    def MILL(self):
        c = self.L.pop(0); self.G.append(c); self.moves['MILL'] += 1
        self.log(f'MILL {c}')

    def RECLAIM(self, d=0):
        c = self.G.pop(-1 - d); self.L.insert(0, c); self.moves['RECLAIM'] += 1
        self.log(f'RECLAIM {c} (depth {d})')

    def OOZE(self, d=0):
        c = self.G.pop(-1 - d); self.X[c] += 1; self.moves['OOZE'] += 1
        self.log(f'OOZE {c} (depth {d})')

    def PULL(self, name):
        if self.X[name] <= 0:
            raise OutOfFuel(name)
        self.X[name] -= 1; self.G.append(name); self.moves['PULL'] += 1
        self.log(f'PULL {name}')

    def log(self, what):
        if self.trace == 'moves':
            self.show('  ' + what)

    # ---- referee procedure -----------------------------------------------------
    def show(self, label):
        if self.trace:
            pool = ' '.join(f'{k}x{v}' for k, v in sorted(self.X.items()) if v)
            print(f'  {label:<34} L=[{" ".join(self.L)}]  G=[{" ".join(self.G)}]  X={{{pool}}}')

    def spine(self):
        m = 0
        while m < len(self.G) and self.G[-1 - m] == '@':
            m += 1
        return m

    def push_segment(self):
        """Mill one whole subterm from L to G; return its length (bracket count)."""
        need, n = 1, 0
        while need:
            need += 1 if self.L[0] == '@' else -1
            self.MILL(); n += 1
        return n

    def rewrite(self, h):
        k, rhs = ARITY[h], RHS[h]
        s_out = 0
        while s_out < len(rhs) and rhs[s_out] == '@':
            s_out += 1
        body = rhs[s_out:]
        self.MILL(); self.OOZE()                     # head card: L -> G -> X
        for _ in range(k - s_out):                   # spare spine @ cards -> X
            self.OOZE()
        self.show(f'{h}: head + {k - s_out} spine @ exiled')
        lens = [self.push_segment() for _ in range(k)]   # a1..ak now on top of G
        self.show(f'{h}: args milled, lens={lens}')
        # segment i (1-based) occupies G depths [off_i, off_i+len_i); top segment is k.
        alive = {i: True for i in range(1, k + 1)}

        def top_depth(i):          # depth of the LAST card of segment i (its top in G)
            return sum(lens[j - 1] for j in range(i + 1, k + 1) if alive[j])

        # 1. garbage: unused arguments go to the exile pool (refuels copies)
        for i in range(k, 0, -1):
            if i not in body:
                for _ in range(lens[i - 1]):
                    self.OOZE(top_depth(i))
                alive[i] = False
        # 2. build body on top of L, last item first
        leftmost = {}
        for pos, it in enumerate(body):
            if it != '@' and it not in leftmost:
                leftmost[it] = pos
        for pos in range(len(body) - 1, -1, -1):
            it = body[pos]
            if it == '@':
                self.PULL('@'); self.RECLAIM(0)
            elif leftmost[it] != pos:               # a duplicate: copy by name from X
                d0 = top_depth(it)
                names = [self.G[-1 - (d0 + j)] for j in range(lens[it - 1])]  # last card first
                for nm in names:
                    self.PULL(nm); self.RECLAIM(0)
            else:                                    # the original cards
                for _ in range(lens[it - 1]):
                    self.RECLAIM(top_depth(it))
                alive[it] = False
        self.rewrites.append(h)
        self.show(f'{h}: contractum on top of L')

    def run(self, max_rewrites=10_000):
        self.show('start')
        while self.L:
            t = self.L[0]
            if t in ARITY and self.spine() >= ARITY[t]:
                if len(self.rewrites) >= max_rewrites:
                    return 'step-bound'
                self.rewrite(t)
            else:
                self.MILL()
        self.show('halt (G bottom-to-top = normal form)')
        assert len(self.G) + sum(self.X.values()) == self.n_cards  # cards conserved
        return 'nf'


# ---- reference: trees and leftmost-outermost reduction -------------------------
def parse(s):
    """Parse 'S K K x' / '(K x) y' style, left-assoc application."""
    toks = s.replace('(', ' ( ').replace(')', ' ) ').split()
    pos = 0

    def atom():
        nonlocal pos
        t = toks[pos]; pos += 1
        if t == '(':
            e = expr(); pos += 1; return e
        return t

    def expr():
        nonlocal pos
        e = atom()
        while pos < len(toks) and toks[pos] != ')':
            e = (e, atom())
        return e
    return expr()


def to_prefix(t):
    return ['@'] + to_prefix(t[0]) + to_prefix(t[1]) if isinstance(t, tuple) else [t]


def from_prefix(cs):
    it = iter(cs)

    def go():
        c = next(it)
        return (go(), go()) if c == '@' else c
    t = go()
    assert next(it, None) is None
    return t


def show(t):
    if not isinstance(t, tuple):
        return t
    f, a = t
    return f'{show(f)} {("(" + show(a) + ")") if isinstance(a, tuple) else a}'


def spine_of(t):
    args = []
    while isinstance(t, tuple):
        args.append(t[1]); t = t[0]
    return t, args[::-1]


def step(t):
    """One leftmost-outermost step; returns (new_term, combinator) or None."""
    h, args = spine_of(t)
    if h in ARITY and len(args) >= ARITY[h]:
        k = ARITY[h]; a = args[:k]
        r = {'I': lambda: a[0], 'K': lambda: a[0],
             'W': lambda: ((a[0], a[1]), a[1]),
             'B': lambda: (a[0], (a[1], a[2])),
             'C': lambda: ((a[0], a[2]), a[1]),
             'S': lambda: ((a[0], a[2]), (a[1], a[2]))}[h]()
        for x in args[k:]:
            r = (r, x)
        return r, h
    for i, x in enumerate(args):
        s = step(x)
        if s:
            new = h
            for j, y in enumerate(args):
                new = (new, s[0] if j == i else y)
            return new, s[1]
    return None


def normalize(t, bound=10_000):
    seq = []
    while len(seq) < bound:
        s = step(t)
        if not s:
            return t, seq
        t, c = s; seq.append(c)
    return None, seq


TESTS = [
    # (term, extra pool) -- affine (BCKI) terms need no pool
    ('C K x y', {}),
    ('B K I x y', {}),
    ('B (C K) I x y', {}),
    ('C (B K I) x y z', {}),
    ('x (I K) (K y z) (C I w f)', {}),
    ('K (I x) (B y z w)', {}),
    ('B B C f g x y', {}),
    # duplicating (W, S) terms: fuel = pool of spare cards
    ('W K x', {}),                         # copy of a 1-card var; uses the pool
    ('S K K x', {}),
    ('S (K x) I y', {}),
    ('W (B K I) (x y)', {}),
    ('S I I (K z)', {}),
    ('S (S K K) (S K K) (K q)', {}),
    ('C (W (C K)) (S I x) y', {}),
]


def run_test(src, pool, base_pool=3, trace=False):
    t = parse(src)
    ref, seq = normalize(t)
    names = set(to_prefix(t)) | {'@'}
    P = Counter({n: base_pool for n in names}); P.update(pool)
    m = Machine(to_prefix(t), P, trace=trace)
    try:
        status = m.run()
    except OutOfFuel as e:
        return src, False, f'OUT OF FUEL ({e})', m
    got = from_prefix(m.G)
    ok = (got == ref) and (m.rewrites == seq)
    return src, ok, f'{show(got)}   rewrites={"".join(m.rewrites)} ref={"".join(seq)}', m


def random_check(n, seed=1):
    import random
    rng = random.Random(seed)
    leaves = list(ARITY) + ['x', 'y', 'z']

    def gen(size):
        if size <= 1:
            return rng.choice(leaves)
        k = rng.randint(1, size - 1)
        return (gen(k), gen(size - k))
    tested = ok_n = diverge = 0
    for _ in range(n):
        t = gen(rng.randint(1, 12))
        ref, seq = normalize(t, bound=300)
        if ref is None:
            diverge += 1
            continue
        P = Counter({nm: 400 for nm in leaves + ['@']})
        m = Machine(to_prefix(t), P)
        try:
            st = m.run()
        except OutOfFuel:
            st = 'fuel'
        tested += 1
        if st == 'nf' and from_prefix(m.G) == ref and m.rewrites == seq:
            ok_n += 1
        else:
            print('MISMATCH', show(t), st)
    print(f'random: {ok_n}/{tested} normalizing terms agree (term + rewrite sequence); '
          f'{diverge} skipped as non-normalizing within 300 steps')
    return ok_n == tested


def budget_check(n, seed=2):
    """Claim: with N_c physical cards of each name c, the machine normalizes t iff
    normal-order reduction of t terminates and every term on the path has at most N_c
    occurrences of c (prefix form, '@' included).  Test the exact threshold."""
    import random
    rng = random.Random(seed)
    leaves = list(ARITY) + ['x', 'y', 'z']

    def gen(size):
        if size <= 1:
            return rng.choice(leaves)
        k = rng.randint(1, size - 1)
        return (gen(k), gen(size - k))

    def need(t):
        path, cur = [t], t
        while True:
            s_ = step(cur)
            if not s_:
                break
            cur = s_[0]; path.append(cur)
            if len(path) > 300:
                return None
        tot = Counter()
        for u in path:
            for nm, c in Counter(to_prefix(u)).items():
                tot[nm] = max(tot[nm], c)
        return tot
    good = checked = 0
    for _ in range(n):
        t = gen(rng.randint(2, 12))
        tot = need(t)
        if tot is None:
            continue
        init = Counter(to_prefix(t))
        exact = Counter({nm: tot[nm] - init[nm] for nm in tot})
        def ok_with(pool):
            try:
                return Machine(to_prefix(t), pool).run() == 'nf'
            except OutOfFuel:
                return False
        res = ok_with(exact)
        tight = all(not ok_with(exact - Counter({nm: 1})) for nm in exact if exact[nm] > 0)
        checked += 1
        good += res and tight
        if not (res and tight):
            print('BUDGET MISMATCH', show(t), dict(exact), res, tight)
    print(f'budget: {good}/{checked} terms normalize with exactly the per-name budget and fail with one card less')
    return good == checked


def main():
    if '--budget' in sys.argv:
        sys.exit(0 if budget_check(int(sys.argv[sys.argv.index('--budget') + 1])) else 1)
    if '--random' in sys.argv:
        sys.exit(0 if random_check(int(sys.argv[sys.argv.index('--random') + 1])) else 1)
    if '--trace' in sys.argv:
        mode = 'moves' if '--moves' in sys.argv else True
        for src, pool in [('C K x y', {}), ('S K K x', {'x': 1})]:
            print(f'TRACE {src}   prefix: {" ".join(to_prefix(parse(src)))}   initial pool: {pool}')
            _, ok, msg, m = run_test(src, pool, base_pool=0, trace=mode)
            print(f'  result: {"PASS" if ok else "FAIL"} {msg}  moves={dict(m.moves)}')
            print()
        return
    allok = True
    for src, pool in TESTS:
        s, ok, msg, m = run_test(src, pool)
        allok &= ok
        print(f'{"PASS" if ok else "FAIL"}  {s:<28} -> {msg}  moves={dict(m.moves)}')
    # fuel exhaustion: S K K x -> K x (K x) copies the one-card argument x; with an
    # empty pool there is no spare x card, so the machine must stop OUT OF FUEL.
    s, ok, msg, m = run_test('S K K x', {}, base_pool=0)
    print(f'{"PASS" if "OUT OF FUEL" in msg else "FAIL"}  zero-pool S K K x       -> {msg}')
    allok &= 'OUT OF FUEL' in msg
    # affine terms run with an EMPTY pool
    for src in ['C K x y', 'B K I x y', 'C (B K I) x y z', 'B B C f g x y']:
        s, ok, msg, m = run_test(src, {}, base_pool=0)
        print(f'{"PASS" if ok else "FAIL"}  zero-pool {s:<18} -> {msg}')
        allok &= ok
    # divergence is reported by the step bound, not by the machine "knowing"
    m = Machine(to_prefix(parse('W W W')), Counter({'@': 5, 'W': 5}))
    st = m.run(max_rewrites=50)
    print(f'{"PASS" if st == "step-bound" else "FAIL"}  W W W (diverges)            -> {st} after {len(m.rewrites)} rewrites; '
          f'cards in play constant = {len(m.L) + len(m.G)}')
    allok &= st == 'step-bound'
    print('ALL PASS' if allok else 'SOME FAILED')


if __name__ == '__main__':
    main()
