#!/usr/bin/env python3
"""L7 cursor machine: normal-order SKI/BCKW reduction on the L3 spine-chain
Aura forest, decomposed into ONE-HOP operations driven by a finite set of
cursors (marks) and a finite-control program.

Model (an abstraction of "forced" card events, not of the Comprehensive Rules):
  * The board is a forest. Each node has a label (combinator, variable, CELL)
    and at most one host ("attached to"). Two fixed roots: ANCHOR and PARK.
  * A cursor is a mark that sits on at most one node (think: the unique
    permanent with some characteristic, or the host of a unique cursor Aura).
  * Every operation may reference a node only as  (cursor, rel)  with
    rel in {self, host, leaf, cell}: the marked node, its host, or its unique
    leaf / cell child (children are told apart by label class only).
    So every operation touches objects within one hop of a marked object.
  * Operations, each counted as one event:
      MARK  c := ref         (move a cursor one hop, or onto another cursor's node)
      MOVE  ref_a -> ref_b   (re-attach a node; its subtree comes along)
      COPY  ref_a -> ref_b   (new node with a's label, attached to b; attachments
                              of a are NOT copied, as with 707.2)
      SAC   ref_a            (delete; then the 704.5m-style cascade removes every
                              node whose host is gone, one level per pass)
  * The control program reads only the labels / existence of one-hop
    neighbours of marked nodes, and its own finite state.

Each reduction step is checked against a reference normal-order reducer
(same step count, equal decoded term after every step). Stdlib only.
Run:  python3 -I cursor_machine.py
"""
import random
import sys

COMB = {"I": 1, "K": 2, "B": 3, "C": 3, "W": 2, "S": 3}
CELL = "@cell"
ALL_CURSORS = set()
ROOTS = ("ANCHOR", "PARK")


# ---------------------------------------------------------------- terms
def app(f, *xs):
    for x in xs:
        f = ("@", f, x)
    return f


def parse(s):
    toks = s.replace("(", " ( ").replace(")", " ) ").split()
    pos = 0

    def seq():
        nonlocal pos
        t = None
        while pos < len(toks) and toks[pos] != ")":
            if toks[pos] == "(":
                pos += 1
                a = seq()
                pos += 1
            else:
                a = toks[pos]
                pos += 1
            t = a if t is None else ("@", t, a)
        return t

    return seq()


def show(t):
    if isinstance(t, str):
        return t
    h, args = spine(t)
    return " ".join([h] + [a if isinstance(a, str) else "(" + show(a) + ")" for a in args])


def spine(t):
    args = []
    while not isinstance(t, str):
        args.append(t[2])
        t = t[1]
    return t, args[::-1]


def size(t):
    return 1 if isinstance(t, str) else size(t[1]) + size(t[2])


def contract(h, a):
    if h == "I":
        return a[0], a[1:]
    if h == "K":
        return a[0], a[2:]
    if h == "B":
        return app(a[0], app(a[1], a[2])), a[3:]
    if h == "C":
        return app(a[0], a[2], a[1]), a[3:]
    if h == "W":
        return app(a[0], a[1], a[1]), a[2:]
    if h == "S":
        return app(a[0], a[2], app(a[1], a[2])), a[3:]
    raise ValueError(h)


def ref_step(t):
    """One leftmost-outermost step, or None if t is normal."""
    h, args = spine(t)
    if h in COMB and len(args) >= COMB[h]:
        r, rest = contract(h, args)
        return app(r, *rest)
    for i, a in enumerate(args):
        s = ref_step(a)
        if s is not None:
            return app(h, *(args[:i] + [s] + args[i + 1:]))
    return None


# ---------------------------------------------------------------- board
class Locality(Exception):
    pass


class Board:
    def __init__(self):
        self.lab = {}
        self.host = {}
        self.nid = 0
        self.cur = {}
        self.stats = dict(MARK=0, MOVE=0, COPY=0, SAC=0, SBA=0)
        self.cursors_used = set()
        for r in ROOTS:
            i = self._new(r, None)
            self.cur[r] = i

    def _new(self, label, host):
        self.nid += 1
        self.lab[self.nid] = label
        self.host[self.nid] = host
        return self.nid

    def kids(self, n):
        return [k for k, h in self.host.items() if h == n]

    # one-hop reference: (cursor, rel)
    def ref(self, r):
        c, rel = r
        if c not in self.cur:
            raise Locality("unknown cursor %s" % c)
        n = self.cur[c]
        if n is None:
            return None
        if rel == "self":
            return n
        if rel == "host":
            return self.host[n]
        ks = self.kids(n)
        if rel == "cell":
            ks = [k for k in ks if self.lab[k] == CELL]
        elif rel == "leaf":
            ks = [k for k in ks if self.lab[k] != CELL]
        else:
            raise Locality(rel)
        if len(ks) > 1:
            raise Locality("ambiguous %s child of %s" % (rel, c))
        return ks[0] if ks else None

    def label(self, r):
        n = self.ref(r)
        return None if n is None else self.lab[n]

    def same(self, c1, c2):
        return self.cur.get(c1) is not None and self.cur.get(c1) == self.cur.get(c2)

    # operations
    def mark(self, c, r):
        self.cur[c] = self.ref(r)
        self.cursors_used.add(c)
        ALL_CURSORS.add(c)
        self.stats["MARK"] += 1

    def move(self, ra, rb):
        a, b = self.ref(ra), self.ref(rb)
        assert a is not None and b is not None, (ra, rb)
        x = b
        while x is not None:  # no cycles
            assert x != a, "cycle"
            x = self.host[x]
        self.host[a] = b
        self.stats["MOVE"] += 1

    def copy(self, ra, rb, c):
        a, b = self.ref(ra), self.ref(rb)
        self.cur[c] = self._new(self.lab[a], b)
        self.cursors_used.add(c)
        ALL_CURSORS.add(c)
        self.stats["COPY"] += 1

    def sac(self, ra):
        a = self.ref(ra)
        dead = {a}
        self._remove(dead)
        self.stats["SAC"] += 1
        while True:  # SBA passes: Auras whose host is gone
            dead = {n for n, h in self.host.items() if h is not None and h not in self.lab}
            if not dead:
                break
            self._remove(dead)
            self.stats["SBA"] += 1

    def _remove(self, dead):
        for n in dead:
            del self.lab[n]
            del self.host[n]
        for c, n in self.cur.items():
            if n in dead:
                self.cur[c] = None

    # encoding / decoding (setup and checking only; not part of the machine)
    def encode(self, t, host):
        h, args = spine(t)
        leaf = self._new(h, host)
        prev = leaf
        for a in args:
            c = self._new(CELL, prev)
            self.encode(a, c)
            prev = c
        return leaf

    def decode_at(self, p):
        leaves = [k for k in self.kids(p) if self.lab[k] != CELL]
        assert len(leaves) == 1, ("position must hold one leaf", p, leaves)
        h = leaves[0]
        t = self.lab[h]
        cells = [k for k in self.kids(h) if self.lab[k] == CELL]
        while cells:
            assert len(cells) == 1
            c = cells[0]
            t = ("@", t, self.decode_at(c))
            cells = [k for k in self.kids(c) if self.lab[k] == CELL]
        return t

    def check_invariants(self):
        assert not self.kids(self.cur["PARK"]), "PARK not empty"
        for n, l in self.lab.items():
            if l in ROOTS:
                continue
            assert self.host[n] in self.lab, "dangling"
            ks = self.kids(n)
            nl = sum(1 for k in ks if self.lab[k] != CELL)
            nc = len(ks) - nl
            if l == CELL:
                assert nl == 1 and nc <= 1, ("cell shape", n)
            else:
                assert nl == 0 and nc <= 1, ("leaf shape", n)


# ---------------------------------------------------------------- machine
def walk_to_end(B, e, start):
    """E := start; follow cell children to the end of the chain (one hop per MARK)."""
    B.mark(e, (start, "self"))
    while B.ref((e, "cell")) is not None:
        B.mark(e, (e, "cell"))


def copy_subtree(B, src, dst):
    """Copy the subtree rooted at cursor src under cursor dst, node by node.
    Two cursors (A on the original, Bc on the copy) and a 3-state control."""
    B.mark("A", (src, "self"))
    B.copy(("A", "self"), (dst, "self"), "Bc")
    state = "down"
    while True:
        if state == "down":
            if B.ref(("A", "leaf")) is not None:
                B.mark("A", ("A", "leaf"))
                B.copy(("A", "self"), ("Bc", "self"), "Bc")
                continue
            state = "after_leaf"
        if state == "after_leaf":
            if B.ref(("A", "cell")) is not None:
                B.mark("A", ("A", "cell"))
                B.copy(("A", "self"), ("Bc", "self"), "Bc")
                state = "down"
                continue
            state = "up"
        if state == "up":
            if B.same("A", src):
                return
            was_leaf = B.label(("A", "self")) != CELL
            B.mark("A", ("A", "host"))
            B.mark("Bc", ("Bc", "host"))
            state = "after_leaf" if was_leaf else "up"


def rewrite(B, h):
    """Contract the redex whose head leaf is H = leaf(P)."""
    n = COMB[h]
    # place cursors one hop at a time
    B.mark("C1", ("H", "cell"))
    B.mark("R1", ("C1", "leaf"))
    if n >= 2:
        B.mark("C2", ("C1", "cell"))
        B.mark("R2", ("C2", "leaf"))
    if n >= 3:
        B.mark("C3", ("C2", "cell"))
        B.mark("R3", ("C3", "leaf"))
    B.mark("T", ("C%d" % n, "cell"))
    if B.ref(("T", "self")) is not None:
        B.move(("T", "self"), ("PARK", "self"))
    B.move(("H", "self"), ("PARK", "self"))  # old head (with its chain) aside
    B.move(("R1", "self"), ("P", "self"))  # x becomes the head at P
    walk_to_end(B, "E", "R1")  # end of x's own chain
    if h in ("I", "K"):
        last = "E"
    elif h == "B":  # x (y z)
        B.move(("C3", "self"), ("PARK", "self"))  # detach z's cell from y's
        B.move(("C2", "self"), ("E", "self"))
        walk_to_end(B, "E2", "R2")
        B.move(("C3", "self"), ("E2", "self"))
        last = "C2"
    elif h == "C":  # x z y
        B.move(("C3", "self"), ("E", "self"))
        B.move(("C2", "self"), ("C3", "self"))
        last = "C2"
    elif h == "W":  # x y y
        B.move(("C2", "self"), ("E", "self"))
        B.move(("C1", "self"), ("C2", "self"))
        copy_subtree(B, "R2", "C1")
        last = "C1"
    elif h == "S":  # x z (y z)
        B.move(("C3", "self"), ("E", "self"))
        B.move(("C2", "self"), ("C3", "self"))
        walk_to_end(B, "E2", "R2")
        B.move(("C1", "self"), ("E2", "self"))
        copy_subtree(B, "R3", "C1")
        last = "C2"
    if B.ref(("T", "self")) is not None:
        B.move(("T", "self"), (last, "self"))
    B.sac(("H", "self"))  # 704.5m cascade removes unused cells and discarded args


def run(term, max_steps=400, trace=None):
    B = Board()
    B.encode(term, B.cur["ANCHOR"])
    B.mark("P", ("ANCHOR", "self"))
    ref = term
    steps = 0
    per_step = []
    while True:
        B.mark("H", ("P", "leaf"))
        h = B.label(("H", "self"))
        # arity test: walk up to COMB[h] cells, one hop at a time
        ok = False
        if h in COMB:
            B.mark("Q", ("H", "self"))
            k = 0
            while k < COMB[h] and B.ref(("Q", "cell")) is not None:
                B.mark("Q", ("Q", "cell"))
                k += 1
            ok = k == COMB[h]
        if ok:
            before = dict(B.stats)
            rewrite(B, h)
            steps += 1
            ref = ref_step(ref)
            got = B.decode_at(B.cur["ANCHOR"])
            assert got == ref, ("mismatch", show(got), show(ref))
            B.check_invariants()
            per_step.append({k: B.stats[k] - before[k] for k in B.stats})
            if trace is not None:
                trace.append("step %d: %s-rule at %s  -> %s   %s" % (
                    steps, h, "ANCHOR" if B.same("P", "ANCHOR") else "cell",
                    show(got), per_step[-1]))
            if steps >= max_steps:
                return B, steps, per_step, "fuel"
            continue
        # head normal form at P: descend into first argument, or advance
        if B.ref(("H", "cell")) is not None:
            B.mark("P", ("H", "cell"))
            continue
        # subterm at P is normal: advance to the next position
        while True:
            if B.same("P", "ANCHOR"):
                assert ref_step(ref) is None
                return B, steps, per_step, "normal"
            if B.ref(("P", "cell")) is not None:
                B.mark("P", ("P", "cell"))
                break
            # climb the cell chain to its head leaf, then to that leaf's position
            B.mark("P", ("P", "host"))
            while B.label(("P", "self")) == CELL:
                B.mark("P", ("P", "host"))
            B.mark("P", ("P", "host"))


TESTS = [
    "S K K x", "W K x", "B f g x", "C f x y", "S x y (K a b)", "S I I (K a)",
    "S (S (K S) K) I f x", "K a (S I I (S I I))", "S (K (S I)) K a b",
    "W (S K) (K a b)", "B (C K) W x y", "S x y z w", "B B C f g x y",
    "W (B (S I) K) x y", "C (W K) y z", "S (K a) (S I I) b",
]


def rand_term(rng, d):
    if d == 0 or rng.random() < 0.3:
        return rng.choice(list(COMB) + ["x", "y", "z"])
    return ("@", rand_term(rng, d - 1), rand_term(rng, d - 1))


def main():
    out = []
    p = out.append
    p("== worked trace: S K K x ==")
    tr = []
    run(parse("S K K x"), trace=tr)
    out.extend(tr)
    p("")
    p("== lockstep check vs reference normal-order reducer ==")
    p("%-24s %-14s %5s %5s %5s %5s %5s %5s" % ("term", "normal form", "steps", "MARK", "MOVE", "COPY", "SAC", "SBA"))
    for s in TESTS:
        B, n, ps, how = run(parse(s))
        nf = show(B.decode_at(B.cur["ANCHOR"]))
        st = B.stats
        p("%-24s %-14s %5d %5d %5d %5d %5d %5d" % (s, nf if how == "normal" else "(fuel)", n,
                                                   st["MARK"], st["MOVE"], st["COPY"], st["SAC"], st["SBA"]))
    # per-rule event counts on atomic arguments, empty tail
    p("")
    p("== events for one rewrite with atomic arguments, empty tail (excluding redex search) ==")
    for h in ["I", "K", "B", "C", "W", "S"]:
        args = ["x", "y", "z"][:COMB[h]]
        B, n, ps, how = run(parse(" ".join([h] + args)), max_steps=1)
        p("%s: %s" % (h, ps[0]))
    p("")
    p("== copy cost scales with |copied argument| (S x y z, z = K applied to k atoms) ==")
    for k in range(0, 5):
        z = "(" + " ".join(["K"] + ["a"] * k) + ")" if k else "a"
        B, n, ps, how = run(parse("S x y " + z), max_steps=1)
        p("|z| nodes=%2d  first step: %s" % (1 + 2 * k, ps[0]))
    rng = random.Random(7)
    ok = fuel = 0
    for _ in range(3000):
        t = rand_term(rng, 5)
        B, n, ps, how = run(t, max_steps=60)
        if how == "normal":
            ok += 1
        else:
            fuel += 1
    p("")
    p("random terms (depth<=5, seed 7): %d reached normal form, %d hit 60-step fuel; all steps agreed" % (ok, fuel))
    p("cursors used by the control program: %s (%d, plus fixed ANCHOR, PARK)" % (
        sorted(ALL_CURSORS), len(ALL_CURSORS)))
    p("ALL OK")
    print("\n".join(out))


if __name__ == "__main__":
    sys.setrecursionlimit(10000)
    main()
