#!/usr/bin/env python3
"""L3 battlefield term-graph model: the spine-chain encoding.

Models only the abstract mechanism of notes/L3-battlefield-graph.md, not Magic:
  * every node is an Aura token with "Enchant permanent"; the only pointer is
    "attached to" (one host per Aura, CR 303.4d), so the board is a forest;
  * a term  h a1 .. an  is a head leaf h (attached to its position P) with a
    chain of CELL Auras: c1 attached to h, c_{i+1} attached to c_i, and the root
    leaf of argument a_i attached to c_i;
  * primitives (one game action each):
      MOVE  n -> host   re-attach an Aura   (Simic Guildmage {1}{U})
      COPY  n -> host   token copy of one Aura, attached by 303.4f choice
                         (Flash Photography / Replication Technique; one-shot)
      SAC   n           sacrifice an Aura   (Auratog), then state-based actions:
                         704.5m repeated (704.3) until no Aura is unattached.
Checks every step, in lockstep, against a reference normal-order reducer.
Stdlib only.
"""
import sys

ARITY = {'I': 1, 'K': 2, 'S': 3, 'B': 3, 'C': 3, 'W': 2}
# result templates: ('arg', j) or ('app', j, [items]); the result head is always an arg
RULE = {
    'I': (1, []),
    'K': (1, []),
    'S': (1, [('arg', 3), ('app', 2, [('arg', 3)])]),
    'B': (1, [('app', 2, [('arg', 3)])]),
    'C': (1, [('arg', 3), ('arg', 2)]),
    'W': (1, [('arg', 2), ('arg', 2)]),
}
CARD = {'CELL': 'Confiscate', 'ANCHOR': 'Island', 'S': 'Indestructibility',
        'K': 'Bound in Gold', 'I': "Intercessor's Arrest", 'B': "Faith's Fetters",
        'C': 'Lay Claim', 'W': 'Take Possession'}
VARCARDS = ['Dream Leash', 'Volition Reins', "Curator's Ward", 'Elemental Resonance']

# ---------------------------------------------------------------- reference
def parse(s):
    toks = s.replace('(', ' ( ').replace(')', ' ) ').split()
    pos = 0
    def seq():
        nonlocal pos
        t = None
        while pos < len(toks) and toks[pos] != ')':
            if toks[pos] == '(':
                pos += 1; a = seq(); pos += 1
            else:
                a = toks[pos]; pos += 1
            t = a if t is None else (t, a)
        return t
    return seq()

def show(t):
    if isinstance(t, str):
        return t
    f, a = t
    return show(f) + ' ' + (show(a) if isinstance(a, str) else '(' + show(a) + ')')

def unwind(t):
    args = []
    while isinstance(t, tuple):
        args.append(t[1]); t = t[0]
    return t, args[::-1]

def rebuild(h, args):
    for a in args:
        h = (h, a)
    return h

def inst(tpl, args):
    def item(it):
        if it[0] == 'arg':
            return args[it[1] - 1]
        return rebuild(args[it[1] - 1], [item(x) for x in it[2]])
    j0, items = tpl
    return rebuild(args[j0 - 1], [item(x) for x in items])

def ref_step(t):
    """One leftmost-outermost step, or None if t is normal."""
    h, args = unwind(t)
    if h in ARITY and len(args) >= ARITY[h]:
        k = ARITY[h]
        return rebuild(inst(RULE[h], args[:k]), args[k:])
    for i, a in enumerate(args):
        r = ref_step(a)
        if r is not None:
            return rebuild(h, args[:i] + [r] + args[i + 1:])
    return None

# ---------------------------------------------------------------- board
class Board:
    def __init__(self, term, log=False):
        self.host, self.kind = {}, {}
        self.nid = 0
        self.log = log
        self.stats = dict(steps=0, moves=0, copies=0, sacs=0, sba_passes=0,
                          max_sba_depth=0, max_nodes=0)
        self.varcard = {}
        self.anchor = self._new('ANCHOR', None)
        self._build(term, self.anchor)          # initial setup, not counted

    def _new(self, kind, host):
        self.nid += 1
        self.kind[self.nid], self.host[self.nid] = kind, host
        return self.nid

    def _build(self, t, P):
        h, args = unwind(t)
        n = self._new(h, P)
        last = n
        for a in args:
            c = self._new('CELL', last)
            self._build(a, c)
            last = c
        return n

    def name(self, n):
        k = self.kind[n]
        if k in CARD:
            card = CARD[k]
        else:
            if k not in self.varcard:
                self.varcard[k] = VARCARDS[len(self.varcard) % len(VARCARDS)]
            card = self.varcard[k]
        return '%s#%d[%s]' % (k, n, card)

    def say(self, s):
        if self.log:
            print('    ' + s)

    def children(self, n):
        return sorted(m for m, h in self.host.items() if h == n)

    def leaf_child(self, n):
        cs = [m for m in self.children(n) if self.kind[m] != 'CELL']
        return cs[0] if cs else None

    def cell_child(self, n):
        cs = [m for m in self.children(n) if self.kind[m] == 'CELL']
        return cs[0] if cs else None

    def chain(self, leaf):
        cs, c = [], self.cell_child(leaf)
        while c is not None:
            cs.append(c); c = self.cell_child(c)
        return cs

    def decode(self, leaf=None):
        if leaf is None:
            leaf = self.leaf_child(self.anchor)
        return rebuild(self.kind[leaf], [self.decode(self.leaf_child(c)) for c in self.chain(leaf)])

    def check(self):
        assert len(self.children(self.anchor)) == 1, 'anchor must hold exactly the root'
        for n, k in self.kind.items():
            if k == 'ANCHOR':
                continue
            assert self.host[n] in self.kind, 'unattached Aura survived SBA'
            cs = self.children(n)
            cells = [m for m in cs if self.kind[m] == 'CELL']
            leaves = [m for m in cs if self.kind[m] != 'CELL']
            assert len(cells) <= 1
            if k == 'CELL':
                assert len(leaves) == 1, 'cell must hold one argument'
            else:
                assert len(leaves) == 0, 'leaf holds only its first cell'

    # -------- primitives (each = one game action)
    def move(self, n, h):
        self.stats['moves'] += 1
        self.say('MOVE  %s -> %s   (Simic Guildmage: attach target Aura to another permanent)'
                 % (self.name(n), self.name(h)))
        self.host[n] = h

    def copy_node(self, n, h):
        self.stats['copies'] += 1
        m = self._new(self.kind[n], h)
        self.say('COPY  %s => new %s on %s   (token copy; host chosen per 303.4f)'
                 % (self.name(n), self.name(m), self.name(h)))
        return m

    def copy_subtree(self, leaf, h):
        """Lazy node-by-node copy, top-down so every copy attaches to an existing node."""
        new = self.copy_node(leaf, h)
        last = new
        for c in self.chain(leaf):
            nc = self.copy_node(c, last)
            self.copy_subtree(self.leaf_child(c), nc)
            last = nc
        return new

    def sac(self, n):
        self.stats['sacs'] += 1
        self.say('SAC   %s   (Auratog: sacrifice an enchantment)' % self.name(n))
        del self.host[n]; del self.kind[n]
        depth = 0
        while True:                          # 704.3: repeat SBA check; 704.5m each pass
            dead = [m for m, h in self.host.items()
                    if self.kind[m] != 'ANCHOR' and h not in self.kind]
            if not dead:
                break
            depth += 1
            self.stats['sba_passes'] += 1
            self.say('SBA pass %d (704.5m, tokens cease 704.5d): %s'
                     % (depth, ', '.join(self.name(m) for m in sorted(dead))))
            for m in dead:
                del self.host[m]; del self.kind[m]
        self.stats['max_sba_depth'] = max(self.stats['max_sba_depth'], depth)

    # -------- redex search: leftmost-outermost, as the reference
    def find(self, leaf):
        k = self.kind[leaf]
        cs = self.chain(leaf)
        if k in ARITY and len(cs) >= ARITY[k]:
            return leaf
        for c in cs:
            r = self.find(self.leaf_child(c))
            if r is not None:
                return r
        return None

    def rewrite(self, h):
        k = ARITY[self.kind[h]]
        P = self.host[h]
        cells = self.chain(h)
        red, rest = cells[:k], (cells[k] if len(cells) > k else None)
        r = [self.leaf_child(c) for c in red]          # r[j-1] = root of arg j
        j0, items = RULE[self.kind[h]]

        def uses(it, acc):
            if it[0] == 'arg':
                acc.append(it[1])
            else:
                acc.append(it[1]); [uses(x, acc) for x in it[2]]
        used = [j0]
        for it in items:
            uses(it, used)
        placed = set()
        # cells of dropped args stay put and die with h; others are reusable
        pool = [red[j - 1] for j in range(k, 0, -1) if j in used]   # deepest first
        parked = set()

        def place(j, at):
            if j not in placed:
                placed.add(j)
                if self.host[r[j - 1]] != at:
                    self.move(r[j - 1], at)
                return r[j - 1]
            return self.copy_subtree(r[j - 1], at)

        def take_cell(L, j):
            # prefer the cell already holding arg j (it carries the arg along)
            c = red[j - 1] if (red[j - 1] in pool and j not in placed) else pool[0]
            pool.remove(c)
            keep = r[j - 1] if c == red[j - 1] else None
            for m in self.children(c):
                if m == keep:
                    continue
                if self.kind[m] == 'CELL':
                    if m in pool or m == rest:
                        self.move(m, self.anchor); parked.add(m)
                else:
                    jj = r.index(m) + 1
                    if jj in used and jj not in placed:
                        self.move(m, self.anchor); parked.add(m)
            if self.host[c] != L:
                self.move(c, L)
            return c

        def last_of(leaf):
            ch = self.chain(leaf)
            return ch[-1] if ch else leaf

        def append(leaf, its):
            for it in its:
                L = last_of(leaf)
                c = take_cell(L, it[1])
                sub = place(it[1], c)
                if it[0] == 'app':
                    append(sub, it[2])

        head = place(j0, P)
        append(head, items)
        if rest is not None:
            self.move(rest, last_of(head))
        self.sac(h)


def ref_normalize(t, fuel=200):
    trace = [t]
    while len(trace) <= fuel:
        s = ref_step(trace[-1])
        if s is None:
            break
        trace.append(s)
    return trace


def lockstep(src, log=False, fuel=200):
    t = parse(src)
    trace = ref_normalize(t, fuel)
    b = Board(t, log=log)
    assert b.decode() == t
    i = 0
    while True:
        b.check()
        b.stats['max_nodes'] = max(b.stats['max_nodes'], len(b.kind) - 1)
        assert b.decode() == trace[i], 'diverged at step %d: %s vs %s' % (i, show(b.decode()), show(trace[i]))
        h = b.find(b.leaf_child(b.anchor))
        if h is None:
            break
        if i >= fuel:
            break
        i += 1
        b.stats['steps'] += 1
        if log:
            print('  step %d: redex head %s on %s' % (i, b.name(h), b.name(b.host[h])))
        b.rewrite(h)
        if log:
            print('    => ' + show(b.decode()))
    assert i == len(trace) - 1, 'step count mismatch'
    return trace[-1], b.stats


TESTS = [
    ('S K K x', 'x'),
    ('W K x', 'x'),
    ('B f g x', 'f (g x)'),
    ('C f x y', 'f y x'),
    ('S x y (K a b)', 'x a (y a)'),                # duplicates a compound argument
    ('S I I (K a)', 'a'),                          # duplicates (K a), then discards
    ('S (S (K S) K) I f x', 'f (f x)'),            # Church 2
    ('K a (S I I (S I I))', 'a'),                  # normal order discards a divergent arg
    ('S (K (S I)) K a b', 'b a'),
    ('W (S K) (K a b)', 'a'),
    ('B (C K) W x y', 'y'),                        # mixed BCKW; C K x x y -> K x x y? see ref
]

if __name__ == '__main__':
    print('== worked trace: S K K x (card names in brackets) ==')
    nf, st = lockstep('S K K x', log=True)
    print('  normal form:', show(nf), st)
    print()
    print('== lockstep check vs reference normal-order reducer ==')
    ok = True
    for src, expect in TESTS:
        try:
            nf, st = lockstep(src)
            good = show(nf) == expect
            ok &= good
            print('%-24s -> %-12s %s  steps=%d moves=%d copies=%d sacs=%d sba_passes=%d max_depth=%d max_nodes=%d'
                  % (src, show(nf), 'OK ' if good else 'BAD(expected %s)' % expect,
                     st['steps'], st['moves'], st['copies'], st['sacs'], st['sba_passes'],
                     st['max_sba_depth'], st['max_nodes']))
        except AssertionError as e:
            ok = False
            print('%-24s FAIL %s' % (src, e))
    print()
    print('== runs that fire no S or W need no COPY (moves + sacrifices only): ==')
    for src in ['B f g x', 'C f x y', 'K a (S I I (S I I))', 'B (C K) I x y', 'C (B K I) x y']:
        nf, st = lockstep(src)
        print('%-24s -> %-8s copies=%d moves=%d sacs=%d' % (src, show(nf), st['copies'], st['moves'], st['sacs']))
    print('ALL OK' if ok else 'SOME FAILED')
    sys.exit(0 if ok else 1)
