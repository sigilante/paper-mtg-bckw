#!/usr/bin/env python3
"""L2 "stack is the term": abstract model of the prefix-block stack machine.

This models ONLY the abstract mechanism of notes/L2-stack-as-term.md, not Magic.

State: the Magic stack, a list of objects (top = end of list). Every object is an
inert, targetless instant spell identified by its card name ("label"):
  combinator atoms S K I B C W, the application marker '@', free variables
  (lowercase), and a frame marker '|'. A template row of one object per label
  (plus the Counterspell template 'CS') sits at the very bottom and is never touched.

A frame (everything above a '|' marker) is read top-first as a sequence of
prefix-coded blocks  b0 b1 ... bn , denoting the left-nested application
(b0 b1 ... bn). A block is: an atom, or '@' followed by two blocks.

The ONLY operations on the stack are the three that real cards supply
(see the note for card text and rules citations):
  copy(obj)     push a copy of any object on the stack       [Reiterate -> 1 cast]
  counter(obj)  remove any object from the stack             [Reiterate copying the
                                                              Counterspell template with a
                                                              new target -> 1 cast + 1 pass]
  resolve_top() the top object resolves (all players pass);  [CR 117.4 / 405.5]
                allowed only for the no-op labels '@' and 'I'.
Everything else (parsing blocks, choosing what to copy/counter) is done by the
controller below, i.e. by the cooperating player reading the public stack (CR 400.2).
"""

import itertools
import random
import sys

ATOMS = {"S": 3, "K": 2, "I": 1, "B": 3, "C": 3, "W": 2}  # arity of each rule


class Obj:
    _ids = itertools.count()

    def __init__(self, label):
        self.label = label
        self.id = next(Obj._ids)

    def __repr__(self):
        return self.label


class Stack:
    def __init__(self, labels_needed):
        self.s = []
        self.ops = {"copy": 0, "counter": 0, "resolve": 0}
        self.trace = None  # list of strings if tracing
        self.tmpl = {}
        for lab in sorted(labels_needed | {"@", "|", "CS"}):
            o = Obj(lab)
            self.s.append(o)  # cast from hand / built once during setup
            self.tmpl[lab] = o
        self.base = len(self.s)

    # ---- the three primitive operations -------------------------------------
    def copy(self, o, why=""):
        assert o in self.s, "Reiterate needs a target on the stack"
        n = Obj(o.label)
        self.s.append(n)
        self.ops["copy"] += 1
        self._log(f"Reiterate -> copy {o.label}#{o.id} {why}")
        return n

    def counter(self, o, why=""):
        assert o in self.s and o.label != "CS"
        self.s.remove(o)
        self.ops["counter"] += 1
        self._log(f"Reiterate -> copy CS, new target {o.label}#{o.id}; CS copy resolves {why}")

    def resolve_top(self, why=""):
        top = self.s[-1]
        assert top.label in ("@", "I"), "only no-op spells are allowed to resolve"
        self.s.pop()
        self.ops["resolve"] += 1
        self._log(f"all pass -> {top.label}#{top.id} resolves (no-op) {why}")

    def _log(self, msg):
        if self.trace is not None:
            self.trace.append(f"  {msg:62s} | top-first: {self.show()}")

    def show(self, lo=None):
        lo = self.base if lo is None else lo
        return " ".join(o.label for o in reversed(self.s[lo:]))


# ---- the controller: what the cooperating player does ------------------------
def blocks(st, mark_idx):
    """Parse the frame above stack index mark_idx (top-first) into prefix blocks.
    Returns list of blocks, each a list of objects in top-first order."""
    seq = list(reversed(st.s[mark_idx + 1:]))
    out, i = [], 0
    while i < len(seq):
        need, j = 1, i
        while need:
            assert seq[j].label != "|", "block crossed a frame marker"
            need += 1 if seq[j].label == "@" else -1
            j += 1
        out.append(seq[i:j])
        i = j
    return out


def push_block(st, blk, why=""):
    """Copy a whole block to the top, deepest object first, so it reads the same."""
    for o in reversed(blk):
        st.copy(o, why)


def kill_block(st, blk, why=""):
    for o in blk:
        st.counter(o, why)


def whnf(st, mark_idx, fuel):
    """Head-reduce the frame above mark_idx until stuck. Returns remaining fuel."""
    while True:
        if fuel[0] <= 0:
            raise RuntimeError("out of fuel")
        fuel[0] -= 1
        bl = blocks(st, mark_idx)
        head = bl[0]
        h = head[0]
        if h.label == "@":                      # unwind: strip the application marker
            st.resolve_top("[unwind @]")
            continue
        args = bl[1:]
        ar = ATOMS.get(h.label)
        if ar is None or len(args) < ar:
            return                              # variable head, or too few args: stuck
        L = h.label
        if L == "I":                            # I x -> x
            st.resolve_top("[I]")
        elif L == "K":                          # K x y -> x : drop K and block y
            kill_block(st, args[1], "[K: drop y]")
            st.counter(h, "[K]")
        elif L == "W":                          # W x y -> x y y
            x, y = args[0], args[1]
            push_block(st, y, "[W: dup y]")
            push_block(st, x, "[W: re-top x]")
            kill_block(st, x, "[W: old x]")
            st.counter(h, "[W]")
        elif L == "C":                          # C x y z -> x z y
            x, y, z = args[:3]
            push_block(st, y, "[C: y]")
            push_block(st, z, "[C: z]")
            push_block(st, x, "[C: x]")
            for b in (x, y, z):
                kill_block(st, b, "[C: old]")
            st.counter(h, "[C]")
        elif L == "B":                          # B x y z -> x (y z) = x @ y z
            x = args[0]
            st.copy(st.tmpl["@"], "[B: @]")
            push_block(st, x, "[B: re-top x]")
            kill_block(st, x, "[B: old x]")
            st.counter(h, "[B]")
        elif L == "S":                          # S x y z -> x z (y z) = x z @ y z
            x, z = args[0], args[2]
            st.copy(st.tmpl["@"], "[S: @]")
            push_block(st, z, "[S: dup z]")
            push_block(st, x, "[S: re-top x]")
            kill_block(st, x, "[S: old x]")
            st.counter(h, "[S]")


def normalize(st, mark_idx, fuel, wrap=False):
    """Normal-order normalisation of the frame above mark_idx, in place.
    With wrap=True (an argument frame) the result h a1..an is re-coded as ONE
    block by pushing n '@' markers on top, so it can rejoin its parent frame."""
    whnf(st, mark_idx, fuel)
    bl = blocks(st, mark_idx)
    head, args = bl[0], bl[1:]
    assert len(head) == 1
    if not args:
        return
    for a in reversed(args):                    # deepest argument first
        m = st.copy(st.tmpl["|"], "[open frame]")
        push_block(st, a, "[arg to frame]")
        normalize(st, st.s.index(m), fuel, wrap=True)
        st.counter(m, "[close frame]")
    st.copy(head[0], "[re-top head]")
    st.counter(head[0], "[old head]")
    for a in args:
        kill_block(st, a, "[old arg]")
    if wrap:
        for _ in args:
            st.copy(st.tmpl["@"], "[re-wrap as one block]")


# ---- terms, encoding, readback, reference reducer -----------------------------
def parse(src):
    toks = src.replace("(", " ( ").replace(")", " ) ").split()
    pos = [0]

    def seq():
        t = None
        while pos[0] < len(toks) and toks[pos[0]] != ")":
            tok = toks[pos[0]]
            pos[0] += 1
            if tok == "(":
                a = seq()
                pos[0] += 1
            else:
                a = tok
            t = a if t is None else (t, a)
        return t

    return seq()


def show(t):
    if isinstance(t, str):
        return t
    f, a = t
    return f"{show(f)} {show(a) if isinstance(a, str) else '(' + show(a) + ')'}"


def prefix(t):
    return [t] if isinstance(t, str) else ["@"] + prefix(t[0]) + prefix(t[1])


def labels(t):
    return {t} if isinstance(t, str) else labels(t[0]) | labels(t[1])


def readback(st, mark_idx):
    def blk(seq, i):
        if seq[i].label == "@":
            f, i = blk(seq, i + 1)
            a, i = blk(seq, i)
            return (f, a), i
        return seq[i].label, i + 1

    t = None
    for b in blocks(st, mark_idx):
        u, _ = blk(b, 0)
        t = u if t is None else (t, u)
    return t


def ref_whnf(t, fuel):
    while True:
        fuel[0] -= 1
        if fuel[0] < 0:
            raise RuntimeError("ref out of fuel")
        sp, h = [], t
        while not isinstance(h, str):
            sp.append(h[1])
            h = h[0]
        sp.reverse()                            # sp = args in order
        ar = ATOMS.get(h)
        if ar is None or len(sp) < ar:
            return h, sp
        a, rest = sp[:ar], sp[ar:]
        if h == "I": r = a[0]
        elif h == "K": r = a[0]
        elif h == "W": r = ((a[0], a[1]), a[1])
        elif h == "C": r = ((a[0], a[2]), a[1])
        elif h == "B": r = (a[0], (a[1], a[2]))
        elif h == "S": r = ((a[0], a[2]), (a[1], a[2]))
        for x in rest:
            r = (r, x)
        t = r


def ref_nf(t, fuel):
    h, sp = ref_whnf(t, fuel)
    r = h
    for x in sp:
        r = (r, ref_nf(x, fuel))
    return r


def run(src, trace=False, fuel=5000, head_only=False):
    t = parse(src)
    st = Stack(labels(t) - {"@"})
    if trace:
        st.trace = []
    mark = st.copy(st.tmpl["|"], "[setup: frame]")
    for lab in reversed(prefix(t)):             # setup: build term by copying templates
        st.copy(st.tmpl[lab], "[setup]")
    setup = dict(st.ops)
    st.ops = {k: 0 for k in st.ops}
    if head_only:
        whnf(st, st.s.index(mark), [fuel])
    else:
        normalize(st, st.s.index(mark), [fuel])
    return t, readback(st, st.s.index(mark)), st, setup


TESTS = [
    "S K K x",                # SKI identity
    "W K x",                  # BCKW: W K x -> K x x -> x
    "B f g x",                # f (g x)
    "C f x y",                # f y x
    "S I I (K a)",            # duplicates the compound argument (K a)
    "W (B f) (K a)",          # duplicates (K a); needs reduction under f
    "K (I a)",                # normal form needs reduction inside an argument
    "S (K (S I)) K a b",      # swap: -> b a
    "K a (W W W)",            # drops a divergent argument (normal order matters)
    "S (S K K) (S K K) (B a b)",  # duplicates compound (B a b)
]


def main():
    if "--trace" in sys.argv:
        src = sys.argv[sys.argv.index("--trace") + 1]
        t, got, st, _ = run(src, trace=True)
        print(f"trace of {src}")
        print("\n".join(st.trace))
        print(f"result: {show(got)}   ops: {st.ops}")
        return
    ok = True
    print(f"{'term':28s} {'stack machine':16s} {'reference':16s} copy counter resolve")
    for src in TESTS:
        t, got, st, _ = run(src)
        ref = ref_nf(t, [5000])
        good = got == ref
        ok &= good
        o = st.ops
        print(f"{src:28s} {show(got):16s} {show(ref):16s} {o['copy']:4d} {o['counter']:7d} "
              f"{o['resolve']:7d}  {'OK' if good else 'MISMATCH'}")
    # random differential test
    rng = random.Random(2026)
    syms = list(ATOMS) + ["a", "b", "c"]

    def rand(n):
        if n <= 1:
            return rng.choice(syms)
        k = rng.randint(1, n - 1)
        return (rand(k), rand(n - k))

    n_run = n_ok = n_skip = 0
    for _ in range(3000):
        t = rand(rng.randint(1, 14))
        try:
            ref = ref_nf(t, [400])
        except (RuntimeError, RecursionError):
            n_skip += 1
            continue
        n_run += 1
        _, got, _, _ = run(show(t), fuel=4000)
        if got == ref:
            n_ok += 1
        else:
            ok = False
            print("MISMATCH", show(t), show(got), show(ref))
    print(f"random: {n_ok}/{n_run} agree with reference normal-order reducer "
          f"({n_skip} skipped: reference did not normalise within fuel)")
    # cost of duplicating a big argument with no sharing
    print("cost of the single head step W x y -> x y y, |y| objects (no sharing):")
    for k in (1, 3, 7, 15):
        y = "a"
        for i in range(k // 2):
            y = f"(b {y})" if i % 2 else f"({y} c)"
        src = f"W x {y}"
        t, got, st, _ = run(src, head_only=True)
        print(f"  |y|={len(prefix(parse(y))):3d}  copies={st.ops['copy']:4d} "
              f"counters={st.ops['counter']:4d}")
    print("ALL OK" if ok else "FAILURES")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
