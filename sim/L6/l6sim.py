#!/usr/bin/env python3
"""L6 hybrid: L3's spine-chain Aura forest driven by L2's repeatable copy engine.

Models the abstract mechanism of notes/L6-hybrid.md, at the level of game actions:

  * The term is a forest of "Enchant permanent" Aura tokens, pointer = "attached to"
    (L3 spine-chain encoding): a term  h a1..an  is a head leaf h attached to its position
    P, a chain of CELL Auras below it (c1 on h, c(i+1) on c(i)), and the root leaf of a(i)
    attached to c(i).  The whole term hangs from one anchor (a basic land).
  * The engine (all controlled by one player, "P"):
      mana   Isochron Scepter (imprinted Dramatic Reversal) + Gilded Lotus: each loop
             iteration nets +1 mana of one chosen colour and uses two stack objects.
      COPY   Flash Photography (FP) is cast once and parked at the bottom of the stack for
             the whole session.  Each node copy = cast Reiterate with buyback targeting FP,
             Reiterate resolves (copy of FP with a NEW target: the node), the FP copy
             resolves: a token copy of the node enters, its host chosen under CR 303.4f.
      MOVE   Simic Guildmage {1}{U}: target Aura; on resolution choose the new host, which
             must not be the current host and must have the same controller as the current
             host (Gatherer ruling 2006-05-01).
      SAC    Auratog: sacrifice an enchantment (cost), then state-based actions: 704.5m
             repeated (704.3) until no Aura is unattached; tokens cease to exist (704.5d).
  * Rewrites: explicit per-rule sequences of MOVE / COPY / SAC (see RULE SEQUENCES below).
  * Redex search: leftmost-outermost over the encoding; checked in lockstep against an
    independent reference normal-order reducer, step by step.

The simulator enforces the RULES checks it models (targets on the stack / battlefield,
Guildmage host conditions, 303.4f host legality, sorcery timing for the casts, mana) and,
separately, PROTOCOL checks (acyclicity, encoding invariants) that the cards do not enforce.
It does not model the opponent (assumed to pass), turns, or anything outside one main phase.
Stdlib only.  Run:  python3 -I l6sim.py
"""
import random
import sys

sys.setrecursionlimit(20000)

ARITY = {'I': 1, 'K': 2, 'S': 3, 'B': 3, 'C': 3, 'W': 2}

# ----------------------------------------------------------------- label cards
# Oracle text is quoted in the note.  Colour and mana cost are used for checks/setup only.
LABEL = {'CELL': 'Indestructibility', 'S': 'Bound in Gold', 'K': "Intercessor's Arrest",
         'I': "Curator's Ward", 'B': 'Essence Leak', 'C': "Faith's Fetters",
         'W': 'Elemental Resonance'}
VARLABELS = ['Confiscate', 'Lay Claim', 'Volition Reins', 'Take Possession',
             'Psychic Overload', 'Dream Leash']
CARD = {  # name: (mana cost dict, colour)
    'Indestructibility': ({'W': 1, 'gen': 3}, 'W'),
    'Bound in Gold': ({'W': 1, 'gen': 2}, 'W'),
    "Intercessor's Arrest": ({'W': 1, 'gen': 2}, 'W'),
    "Curator's Ward": ({'U': 1, 'gen': 2}, 'U'),
    'Essence Leak': ({'U': 1}, 'U'),
    "Faith's Fetters": ({'W': 1, 'gen': 3}, 'W'),
    'Elemental Resonance': ({'G': 2, 'gen': 2}, 'G'),
    'Confiscate': ({'U': 2, 'gen': 4}, 'U'),
    'Lay Claim': ({'U': 2, 'gen': 5}, 'U'),
    'Volition Reins': ({'U': 3, 'gen': 3}, 'U'),
    'Take Possession': ({'U': 2, 'gen': 5}, 'U'),
    'Psychic Overload': ({'U': 1, 'gen': 3}, 'U'),
    'Dream Leash': ({'U': 2, 'gen': 3}, 'U'),
    'Island': ({}, None),
}
ETB = {"Faith's Fetters": 'you gain 4 life',
       'Psychic Overload': 'tap enchanted permanent',
       'Volition Reins': 'if enchanted permanent is tapped, untap it'}
COST_REITERATE = {'R': 2, 'gen': 4}      # {1}{R}{R} + buyback {3}
COST_GUILDMAGE = {'U': 1, 'gen': 1}      # {1}{U}
COST_FP = {'U': 2, 'gen': 2}             # {2}{U}{U}


class RulesError(Exception):
    """A move the Comprehensive Rules (as modelled) do not allow."""


class ProtocolError(Exception):
    """A legal move that the cooperative protocol forbids (the cards do not prevent it)."""


# ----------------------------------------------------------------- reference reducer
def parse(s):
    toks = s.replace('(', ' ( ').replace(')', ' ) ').split()
    pos = 0

    def seq():
        nonlocal pos
        t = None
        while pos < len(toks) and toks[pos] != ')':
            if toks[pos] == '(':
                pos += 1
                a = seq()
                pos += 1
            else:
                a = toks[pos]
                pos += 1
            t = a if t is None else (t, a)
        return t
    return seq()


def show(t):
    if isinstance(t, str):
        return t
    f, a = t
    return show(f) + ' ' + (show(a) if isinstance(a, str) else '(' + show(a) + ')')


def size(t):
    """Number of Aura nodes encoding t: one leaf per atom, one cell per application."""
    return 1 if isinstance(t, str) else size(t[0]) + size(t[1]) + 1


def unwind(t):
    args = []
    while isinstance(t, tuple):
        args.append(t[1])
        t = t[0]
    return t, args[::-1]


def rebuild(h, args):
    for a in args:
        h = (h, a)
    return h


def contract(h, a):
    if h in ('I', 'K'):
        return a[0]
    if h == 'S':
        return ((a[0], a[2]), (a[1], a[2]))
    if h == 'B':
        return (a[0], (a[1], a[2]))
    if h == 'C':
        return ((a[0], a[2]), a[1])
    if h == 'W':
        return ((a[0], a[1]), a[1])


def ref_step(t):
    """One leftmost-outermost step, or None if t is in normal form."""
    h, args = unwind(t)
    if h in ARITY and len(args) >= ARITY[h]:
        k = ARITY[h]
        return rebuild(contract(h, args[:k]), args[k:])
    for i, a in enumerate(args):
        r = ref_step(a)
        if r is not None:
            return rebuild(h, args[:i] + [r] + args[i + 1:])
    return None


def ref_nf(t, fuel):
    """Independent normal-order normaliser (head reduction, then arguments)."""
    while True:
        h, args = unwind(t)
        if h in ARITY and len(args) >= ARITY[h]:
            fuel[0] -= 1
            if fuel[0] < 0:
                raise RuntimeError('fuel')
            k = ARITY[h]
            t = rebuild(contract(h, args[:k]), args[k:])
            continue
        return rebuild(h, [ref_nf(a, fuel) for a in args])


# ----------------------------------------------------------------- the game model
class Perm:
    __slots__ = ('id', 'name', 'kind', 'token', 'host', 'tapped')

    def __init__(self, pid, name, kind, token, host):
        self.id, self.name, self.kind, self.token, self.host = pid, name, kind, token, host
        self.tapped = False


class Game:
    def __init__(self, log=False, verbose_engine=False):
        self.bf = {}            # battlefield: id -> Perm (everything controlled by P)
        self.stack = []         # list of dicts; top = end
        self.pool = {}          # mana pool, colour -> amount
        self.nid = 0
        self.log = log
        self.verbose_engine = verbose_engine
        self.life = 20
        self.hand = {'Reiterate'}
        self.var_label = {}
        self.n = dict(moves=0, copies=0, sacs=0, sba_passes=0, dr_loops=0, resolutions=0,
                      triggers=0, reiterates=0)
        self.lotus = self._perm('Gilded Lotus', 'ENGINE', False, None)
        self.scepter = self._perm('Isochron Scepter', 'ENGINE', False, None)  # DR imprinted
        self.guildmage = self._perm('Simic Guildmage', 'ENGINE', False, None)
        self.auratog = self._perm('Auratog', 'ENGINE', False, None)
        self.anchor = self._perm('Island', 'ANCHOR', False, None)
        self.thost = self._perm('Island', 'THOST', False, None)            # template host
        self.templates = {}
        self.fp = None
        self.loop_shown = False

    # ------------------------------------------------ bookkeeping
    def _perm(self, name, kind, token, host):
        self.nid += 1
        p = Perm(self.nid, name, kind, token, host)
        self.bf[self.nid] = p
        return p.id

    def label(self, kind):
        if kind in LABEL:
            return LABEL[kind]
        if kind not in self.var_label:
            if len(self.var_label) >= len(VARLABELS):
                raise RulesError('more free variables than distinct variable label cards')
            self.var_label[kind] = VARLABELS[len(self.var_label)]
        return self.var_label[kind]

    def nm(self, i):
        p = self.bf[i]
        k = '' if p.kind in ('ENGINE',) else p.kind + '#'
        return '%s%d[%s]' % (k, i, p.name) if k else '%s#%d' % (p.name, i)

    def say(self, s):
        if self.log:
            print('      ' + s)

    def stack_str(self):
        return 'stack(bottom->top): ' + ', '.join(o['desc'] for o in self.stack)

    def is_aura(self, i):
        return self.bf[i].kind not in ('ENGINE', 'ANCHOR', 'THOST', 'LANDTOKEN')

    def children(self, i):
        return sorted(m for m, p in self.bf.items() if p.host == i)

    def descendants(self, i):
        out, todo = set(), [i]
        while todo:
            x = todo.pop()
            for m in self.children(x):
                if m not in out:
                    out.add(m)
                    todo.append(m)
        return out

    # ------------------------------------------------ priority, SBA, stack
    def sba(self):
        """CR 117.5 / 704.3: repeat state-based actions until none apply. Returns #passes."""
        passes = 0
        while True:
            dead = [i for i, p in self.bf.items()
                    if self.is_aura(i) and (p.host is None or p.host not in self.bf)]  # 704.5m
            if not dead:
                return passes
            passes += 1
            self.n['sba_passes'] += 1
            self.say('SBA pass %d (704.5m; tokens cease to exist 704.5d): %s'
                     % (passes, ', '.join(self.nm(i) for i in sorted(dead))))
            for i in dead:
                del self.bf[i]

    def push(self, obj):
        self.stack.append(obj)
        self.sba()

    def resolve_top(self):
        """All players pass in succession (117.4, 405.5); the top object resolves."""
        obj = self.stack.pop()
        self.n['resolutions'] += 1
        obj['fn'](obj)
        self.sba()

    # ------------------------------------------------ mana engine
    def mana_loop(self, colour):
        """Tap Lotus for three of `colour`; pay {2} for Scepter; cast the Dramatic Reversal
        copy; it resolves and untaps all nonland permanents you control.  Net +1 `colour`."""
        L, Sc = self.bf[self.lotus], self.bf[self.scepter]
        if L.tapped or Sc.tapped:
            raise RulesError('mana engine tapped')
        L.tapped = True
        self.pool[colour] = self.pool.get(colour, 0) + 3          # mana ability, no stack
        self.pool[colour] -= 2
        Sc.tapped = True

        def scepter_res(o):
            def dr_res(o2):
                for p in self.bf.values():
                    if p.kind not in ('ANCHOR', 'THOST', 'LANDTOKEN'):
                        p.tapped = False          # "Untap all nonland permanents you control."
            self.push({'desc': 'Dramatic Reversal (Scepter copy, cast)', 'fn': dr_res})
        self.push({'desc': 'Isochron Scepter ability', 'fn': scepter_res})
        self.resolve_top()          # Scepter ability -> cast DR copy
        self.resolve_top()          # DR copy -> untap
        self.n['dr_loops'] += 1
        if self.verbose_engine and not self.loop_shown:
            self.loop_shown = True
            self.say('[one mana loop, in full: tap Gilded Lotus for %s%s%s (mana ability, no stack); '
                     'pay {2}, tap Isochron Scepter: ability on the stack above FP; all pass: '
                     'it resolves, you cast the copy of Dramatic Reversal; all pass: it resolves, '
                     'untapping Lotus and Scepter. Net: +1 %s, stack back to FP alone]'
                     % (colour, colour, colour, colour))

    def pay(self, cost):
        loops0 = self.n['dr_loops']
        for c, k in cost.items():
            if c == 'gen':
                continue
            while self.pool.get(c, 0) < k:
                self.mana_loop(c)
            self.pool[c] -= k
        g = cost.get('gen', 0)
        while sum(self.pool.values()) < g:
            self.mana_loop('U')
        for c in sorted(self.pool, key=lambda c: -self.pool[c]):
            take = min(g, self.pool[c])
            self.pool[c] -= take
            g -= take
        if self.verbose_engine and self.n['dr_loops'] > loops0:
            self.say('mana: %d Scepter/Dramatic Reversal/Lotus loop(s) (2 stack objects each)'
                     % (self.n['dr_loops'] - loops0))

    # ------------------------------------------------ setup (not counted in step costs)
    def cast_template(self, kind):
        """Cast one physical label card as an Aura spell targeting the template host
        (303.4a); sorcery timing: main phase, empty stack (117.1a, 307.1)."""
        if self.stack:
            raise RulesError('enchantment spell needs an empty stack')
        name = self.label(kind)
        if name == 'Dream Leash':
            self.bf[self.thost].tapped = True        # "can't choose an untapped permanent"
            self.pool['U'] = self.pool.get('U', 0) + 1
        self.pay(CARD[name][0])

        def res(o):
            tid = self._perm(name, kind, False, self.thost)    # 608.3c
            self.templates[kind] = tid
            self._etb(tid)
        self.push({'desc': name + ' (Aura spell -> template host)', 'fn': res})
        self.resolve_top()
        while self.stack:
            self.resolve_top()

    def open_session(self):
        """Cast Flash Photography (sorcery: main phase, empty stack) targeting the
        template host.  It stays on the stack, under everything, for the whole session."""
        if self.stack:
            raise RulesError('Flash Photography: sorcery timing needs an empty stack')
        self.pay(COST_FP)
        self.fp = {'desc': 'Flash Photography (original, target %s)' % self.nm(self.thost),
                   'fn': self._fp_resolve, 'target': self.thost, 'card': 'FP'}
        self.push(self.fp)
        self.say('cast Flash Photography targeting %s; %s' % (self.nm(self.thost), self.stack_str()))

    def close_session(self):
        """Everyone passes: the original FP resolves last (token copy of the template
        host's land, harmless) and the stack is empty."""
        while self.stack:
            self.resolve_top()

    def _fp_resolve(self, o):
        t = o['target']
        if t not in self.bf:                      # 608.2b: single target illegal -> fizzle
            self.say('%s: target gone, does not resolve' % o['desc'])
            return
        p = self.bf[t]
        if self.is_aura(t):
            h = o['host']                        # 303.4f: chosen as the token enters
            if h not in self.bf or h == 'new':
                raise RulesError('303.4f: host must be a permanent on the battlefield')
            nid = self._perm(p.name, p.kind, True, h)
            o['made'] = nid
            self.n['copies'] += 1
            self._etb(nid)
        else:
            self._perm(p.name, 'LANDTOKEN', True, None)
            self.say('%s resolves: token copy of %s (harmless)' % (o['desc'], self.nm(t)))

    def _etb(self, nid):
        eff = ETB.get(self.bf[nid].name)
        if not eff:
            return
        self.n['triggers'] += 1

        def res(o):
            h = self.bf[nid].host if nid in self.bf else None
            if eff.startswith('you gain'):
                self.life += 4
            elif eff.startswith('tap') and h in self.bf:
                self.bf[h].tapped = True
            elif eff.startswith('if') and h in self.bf:
                self.bf[h].tapped = False
        self.push({'desc': 'ETB trigger of %s: %s' % (self.nm(nid), eff), 'fn': res})
        self.resolve_top()

    # ------------------------------------------------ the three primitives
    def COPY(self, n, host, why=''):
        """Reiterate (buyback) on the parked FP; new target n; token enters on `host`."""
        if not any(o.get('card') == 'FP' for o in self.stack):
            raise RulesError('Reiterate needs an instant or sorcery spell on the stack')
        if 'Reiterate' not in self.hand:
            raise RulesError('Reiterate not in hand')
        if n not in self.bf:
            raise RulesError('Flash Photography copy: target must be a permanent')
        self.pay(COST_REITERATE)
        self.hand.discard('Reiterate')
        self.n['reiterates'] += 1
        fp = self.fp
        rec = {}

        def reit_res(o):
            if fp not in self.stack:                         # 608.2b
                raise RulesError('Reiterate target left the stack')
            cp = {'desc': 'FP copy (new target %s)' % self.nm(n), 'fn': self._fp_resolve,
                  'target': n, 'host': host, 'card': 'FPcopy'}  # 707.10, 707.10c
            rec['cp'] = cp
            self.hand.add('Reiterate')                       # buyback, 702.27a
            self.stack.append(cp)
            if self.verbose_engine:
                self.say('Reiterate resolves: copy of FP with new target %s; Reiterate -> hand; %s'
                         % (self.nm(n), self.stack_str()))
            self.sba()
        self.push({'desc': 'Reiterate (buyback, target FP)', 'fn': reit_res})
        if self.verbose_engine:
            self.say('cast Reiterate with buyback targeting FP; %s' % self.stack_str())
        self.resolve_top()
        self.resolve_top()                                   # the FP copy resolves
        m = rec['cp']['made']
        self.say('COPY  %s => new %s on %s  (Reiterate+FP copy; host by 303.4f)%s'
                 % (self.nm(n), self.nm(m), self.nm(host), (' ' + why) if why else ''))
        if self.verbose_engine:
            self.say('      %s' % self.stack_str())
        self.protocol_check_acyclic()
        return m

    def MOVE(self, n, h, why=''):
        """Simic Guildmage {1}{U}: attach target Aura attached to a permanent to another
        permanent with the same controller (chosen on resolution; ruling 2006-05-01)."""
        if n not in self.bf or not self.is_aura(n) or self.bf[n].host not in self.bf:
            raise RulesError('Guildmage: target must be an Aura attached to a permanent')
        self.pay(COST_GUILDMAGE)
        self.n['moves'] += 1
        old = self.bf[n].host

        def res(o):
            cur = self.bf[n].host
            if h == cur:
                raise RulesError('Guildmage: new host must not be the current host')
            if h not in self.bf or h == n:
                raise RulesError('303.4d / 701.3b: illegal host')
            # same controller: everything is controlled by P (checked in check_control)
            if h in self.descendants(n):
                raise ProtocolError('MOVE would create an attachment cycle (rules allow it)')
            self.bf[n].host = h
        self.push({'desc': 'Simic Guildmage ability (target %s)' % self.nm(n), 'fn': res})
        if self.verbose_engine:
            self.say('activate Guildmage targeting %s; %s' % (self.nm(n), self.stack_str()))
        self.resolve_top()
        self.say('MOVE  %s : %s -> %s  (Simic Guildmage {1}{U})%s'
                 % (self.nm(n), self.nm(old), self.nm(h), (' ' + why) if why else ''))

    def SAC(self, n, why=''):
        """Auratog: 'Sacrifice an enchantment' is the cost; SBAs run before priority."""
        if n not in self.bf or not self.is_aura(n):
            raise RulesError('Auratog: sacrifice an enchantment you control')
        self.n['sacs'] += 1
        self.say('SAC   %s  (Auratog cost)%s' % (self.nm(n), (' ' + why) if why else ''))
        del self.bf[n]                                       # 701.21a; token ceases, 704.5d

        def res(o):
            pass                                             # +2/+2 until end of turn
        before = self.n['sba_passes']
        self.push({'desc': 'Auratog ability', 'fn': res})
        self.resolve_top()
        return self.n['sba_passes'] - before

    # ------------------------------------------------ term structure
    def cell_child(self, i):
        cs = [m for m in self.children(i) if self.bf[m].kind == 'CELL']
        return cs[0] if cs else None

    def leaf_child(self, i):
        cs = [m for m in self.children(i) if self.bf[m].kind != 'CELL']
        return cs[0] if cs else None

    def chain(self, leaf):
        out, c = [], self.cell_child(leaf)
        while c is not None:
            out.append(c)
            c = self.cell_child(c)
        return out

    def last(self, leaf):
        ch = self.chain(leaf)
        return ch[-1] if ch else leaf

    def root(self):
        return self.leaf_child(self.anchor)

    def decode(self, leaf=None):
        if leaf is None:
            leaf = self.root()
        return rebuild(self.bf[leaf].kind,
                       [self.decode(self.leaf_child(c)) for c in self.chain(leaf)])

    def term_nodes(self):
        return [i for i, p in self.bf.items()
                if self.is_aura(i) and p.host != self.thost and p.token]

    # ------------------------------------------------ invariants
    def protocol_check_acyclic(self):
        for i in self.term_nodes():
            seen, x = set(), i
            while x is not None and self.bf[x].kind not in ('ANCHOR', 'THOST'):
                if x in seen:
                    raise ProtocolError('attachment cycle')
                seen.add(x)
                x = self.bf[x].host

    def check(self):
        """Between steps: encoding invariants (protocol) and label side-effect checks."""
        A = self.anchor
        if len([m for m in self.children(A)]) != 1:
            raise ProtocolError('anchor must hold exactly the root')
        self.protocol_check_acyclic()
        for i in self.term_nodes():
            p = self.bf[i]
            hostp = self.bf[p.host]
            cs = self.children(i)
            cells = [m for m in cs if self.bf[m].kind == 'CELL']
            leaves = [m for m in cs if self.bf[m].kind != 'CELL']
            if len(cells) > 1:
                raise ProtocolError('two cells on one node')
            if p.kind == 'CELL':
                if len(leaves) != 1:
                    raise ProtocolError('cell must hold exactly one argument')
            else:
                if leaves:
                    raise ProtocolError('leaf holds only its first cell')
                if hostp.kind not in ('CELL', 'ANCHOR'):
                    raise ProtocolError('a leaf must enchant a cell or the anchor')
            # label side effects (see the note): Essence Leak never on a red/green permanent
            if p.name == 'Essence Leak' and CARD.get(hostp.name, ({}, None))[1] in ('R', 'G'):
                raise ProtocolError('Essence Leak on a red or green permanent')


# ----------------------------------------------------------------- RULE SEQUENCES
# P = host of the head leaf h; c1..ck its redex cells; r_j = root leaf of argument j;
# rest = c(k+1) (with everything below it) or None; last(r) = last cell of r's spine (or r).
def rewrite(g, h):
    kind = g.bf[h].kind
    k = ARITY[kind]
    P = g.bf[h].host
    cells = g.chain(h)
    c = cells[:k]
    rest = cells[k] if len(cells) > k else None
    r = [g.leaf_child(x) for x in c]
    M, Cp = g.MOVE, g.COPY

    if kind in ('I', 'K'):                       # I x -> x ;  K x y -> x
        M(r[0], P, '(x becomes the head)')
        if rest:
            M(rest, g.last(r[0]), '(rest of the spine)')
    elif kind == 'B':                            # B x y z -> x (y z)
        M(r[0], P, '(x becomes the head)')
        M(c[1], g.last(r[0]), '(cell holding y, with z and rest below it)')
        M(c[2], g.last(r[1]), '(cell holding z goes under y: (y z))')
        if rest:
            M(rest, c[1], '(rest of the spine)')
    elif kind == 'C':                            # C x y z -> x z y
        M(r[0], P, '(x becomes the head)')
        M(c[2], g.last(r[0]), '(cell holding z)')
        M(c[1], c[2], '(cell holding y after z)')
        if rest:
            M(rest, c[1], '(rest of the spine)')
    elif kind == 'W':                            # W x y -> x y y
        M(r[0], P, '(x becomes the head)')
        M(c[1], g.last(r[0]), '(cell holding y)')
        M(c[0], c[1], '(freed cell: second y)')
        if rest:
            M(rest, c[0], '(rest of the spine)')
        copy_subtree(g, r[1], c[0])
    elif kind == 'S':                            # S x y z -> x z (y z)
        M(r[0], P, '(x becomes the head)')
        M(c[2], g.last(r[0]), '(cell holding z)')
        M(c[1], c[2], '(cell holding y)')
        if rest:
            M(rest, c[1], '(rest of the spine)')
        M(c[0], g.last(r[1]), '(freed cell: argument of y)')
        copy_subtree(g, r[2], c[0])
    return g.SAC(h, '(old head; SBA cascade collects whatever still hangs from it)')


def copy_subtree(g, leaf, host):
    """Top-down, node by node: each new token is attached to its already-created parent."""
    new = g.COPY(leaf, host)
    lastnew = new
    for c in g.chain(leaf):
        nc = g.COPY(c, lastnew)
        copy_subtree(g, g.leaf_child(c), nc)
        lastnew = nc
    return new


def find(g, leaf):
    k = g.bf[leaf].kind
    cs = g.chain(leaf)
    if k in ARITY and len(cs) >= ARITY[k]:
        return leaf
    for c in cs:
        x = find(g, g.leaf_child(c))
        if x is not None:
            return x
    return None


def build(g, t, host):
    """Setup: build term t top-down by COPYing the physical template Auras."""
    h, args = unwind(t)
    leaf = g.COPY(g.templates[h], host)
    last = leaf
    for a in args:
        cell = g.COPY(g.templates['CELL'], last)
        build(g, a, cell)
        last = cell
    return leaf


def kinds(t):
    return {t} if isinstance(t, str) else kinds(t[0]) | kinds(t[1])


def setup(t, log=False, verbose_engine=False):
    g = Game(log=log, verbose_engine=verbose_engine)
    for kd in sorted(kinds(t) | {'CELL'}):
        g.cast_template(kd)
    g.open_session()
    build(g, t, g.anchor)
    g.check()
    assert g.decode() == t
    base = dict(g.n)
    g.n = {k: 0 for k in g.n}
    return g, base


def board_str(g):
    lines = []

    def walk(i, d):
        lines.append('        ' + '  ' * d + g.nm(i))
        for m in g.children(i):
            walk(m, d + 1)
    walk(g.anchor, 0)
    return '\n'.join(lines)


def lockstep(src, log=False, verbose_engine=False, fuel=200, node_cap=3000, term=None):
    t = parse(src) if term is None else term
    g, setup_cost = setup(t, log=False)
    g.log, g.verbose_engine = log, verbose_engine
    if log:
        print('    initial board (child indented under the permanent it enchants):')
        print(board_str(g))
        print('    ' + g.stack_str())
    cur = t
    steps = 0
    per_step = []
    max_nodes = len(g.term_nodes())
    max_sba = 0
    status = 'nf'
    while True:
        g.check()
        d = g.decode()
        if d != cur:
            raise AssertionError('diverged at step %d: board %s vs reference %s'
                                 % (steps, show(d), show(cur)))
        nxt = ref_step(cur)
        h = find(g, g.root())
        if (h is None) != (nxt is None):
            raise AssertionError('redex search disagrees with reference at step %d' % steps)
        if h is None:
            break
        if steps >= fuel:
            status = 'fuel'
            break
        if size(nxt) > node_cap:
            status = 'cap'
            break
        steps += 1
        before = dict(g.n)
        if log:
            print('    step %d: redex head %s on %s' % (steps, g.nm(h), g.nm(g.bf[h].host)))
        rule = g.bf[h].kind
        depth = rewrite(g, h)
        max_sba = max(max_sba, depth)
        per_step.append((rule, {k: g.n[k] - before[k] for k in g.n}))
        if log:
            print('      => ' + show(g.decode()))
        cur = nxt
        max_nodes = max(max_nodes, len(g.term_nodes()))
    g.close_session()
    st = dict(g.n)
    st.update(steps=steps, max_nodes=max_nodes, max_sba_depth=max_sba, status=status)
    return cur, st, setup_cost, per_step


# ----------------------------------------------------------------- lambda -> combinators
def fv(t):
    if isinstance(t, str):
        return {t} if t.islower() else set()
    return fv(t[0]) | fv(t[1])


def abstract(x, M, basis):
    if M == x:
        return 'I' if basis != 'BCKW-noI' else (('C', 'K'), 'K')
    if x not in fv(M):
        return ('K', M)
    A, Bt = M
    if Bt == x and x not in fv(A):
        return A                                             # eta
    xa, xb = x in fv(A), x in fv(Bt)
    if basis == 'SKI':
        return (('S', abstract(x, A, basis)), abstract(x, Bt, basis))
    if xa and not xb:
        return (('C', abstract(x, A, basis)), Bt)
    if xb and not xa:
        return (('B', A), abstract(x, Bt, basis))
    if basis == 'SKIBC':
        return (('S', abstract(x, A, basis)), abstract(x, Bt, basis))
    # BCKW: \x. M' x (N' x) = W (B (C M') N')
    return ('W', (('B', ('C', abstract(x, A, basis))), abstract(x, Bt, basis)))


def compile_lam(t, basis):
    if isinstance(t, str):
        return t
    if t[0] == 'lam':
        return abstract(t[1], compile_lam(t[2], basis), basis)
    return (compile_lam(t[1], basis), compile_lam(t[2], basis))


def lam(v, b):
    return ('lam', v, b)


def ap(*xs):
    t = xs[0]
    for x in xs[1:]:
        t = ('app', t, x)
    return t


def church(n):
    body = 'x'
    for _ in range(n):
        body = ap('f', body)
    return lam('f', lam('x', body))


SUCC = lam('n', lam('f', lam('x', ap('f', ap('n', 'f', 'x')))))
PLUS = lam('m', lam('n', lam('f', lam('x', ap('m', 'f', ap('n', 'f', 'x'))))))
MULT = lam('m', lam('n', lam('f', ap('m', ap('n', 'f')))))


PROGRAMS = [
    ('succ 2 p q', ap(SUCC, church(2), 'p', 'q')),
    ('plus 2 2 p q', ap(PLUS, church(2), church(2), 'p', 'q')),
    ('mult 2 2 p q', ap(MULT, church(2), church(2), 'p', 'q')),
    ('2 2 p q (exp)', ap(church(2), church(2), 'p', 'q')),
    ('mult 3 2 p q', ap(MULT, church(3), church(2), 'p', 'q')),
]


# ----------------------------------------------------------------- tests
TESTS = [
    ('S K K x', 'x'),
    ('W K x', 'x'),
    ('S I I (K a)', 'a'),                          # S I I applied to a finite term
    ('S I I I', 'I'),
    ('B f g x', 'f (g x)'),
    ('C f x y', 'f y x'),
    ('C (B f) x y', 'f (y x)'),
    ('B (C K) W x y', 'y'),
    ('S x y (K a b)', 'x a (y a)'),                # copies a compound argument
    ('S (S (K S) K) I f x', 'f (f x)'),            # Church 2 f x
    ('S (S (K S) K) (S (S (K S) K) I) f x', 'f (f (f x))'),   # succ 2 f x (SKI succ)
    ('S (S (K S) K) I (S (S (K S) K) I) f x', 'f (f (f (f x)))'),  # 2 2 f x = 4 f x
    ('K a (S I I (S I I))', 'a'),                  # K discards a divergent argument
    ('K a (W W W)', 'a'),                          # same, BCKW
    ('W (B f) (K a)', 'f a'),
    ('S (K (S I)) K a b', 'b a'),
    ('K (I a)', 'K a'),                            # reduction under an argument
]


def fmt(st):
    return ('steps=%d moves=%d copies=%d sacs=%d sba=%d mana=%d stack_res=%d trig=%d '
            'max_nodes=%d' % (st['steps'], st['moves'], st['copies'], st['sacs'],
                              st['sba_passes'], st['dr_loops'], st['resolutions'],
                              st['triggers'], st['max_nodes']))


def main():
    ok = True
    print('L6 simulator: spine-chain Aura forest + Reiterate/Flash Photography copy engine')
    print('mana = net mana drawn from the Scepter/Dramatic Reversal/Lotus loop (one loop = +1)')
    print('stack_res = stack objects resolved (each needs all players to pass)')
    print()

    print('== worked trace 1: S K K x, with the copy-engine choreography spelled out ==')
    nf, st, sc, _ = lockstep('S K K x', log=True, verbose_engine=True)
    print('  normal form: %s ; %s' % (show(nf), fmt(st)))
    print('  setup cost (templates cast + term built by COPY): copies=%d mana=%d'
          % (sc['copies'], sc['dr_loops']))
    print()

    print('== worked trace 2: S x y (K a b), step 1 copies the compound argument K a b ==')
    nf, st, sc, _ = lockstep('S x y (K a b)', log=True)
    print('  normal form: %s ; %s' % (show(nf), fmt(st)))
    print()

    print('== lockstep check vs reference normal-order reducer (fixed terms) ==')
    for src, expect in TESTS:
        try:
            nf, st, sc, _ = lockstep(src)
            good = show(nf) == expect and st['status'] == 'nf'
            nf2 = ref_nf(parse(src), [10000])
            good = good and nf2 == nf
        except (AssertionError, RulesError, ProtocolError) as e:
            good = False
            print('%-44s FAIL %r' % (src, e))
            ok = False
            continue
        ok &= good
        print('%-44s -> %-18s %s %s' % (src, show(nf), 'OK ' if good else 'BAD', fmt(st)))
    print()

    print('== non-normalising terms run under a step bound (lockstep holds on every step) ==')
    for src in ['S I I (S I I)', 'W W W', 'S (K (S I I)) (S (S (K S) K) (K (S I I))) f']:
        nf, st, sc, _ = lockstep(src, fuel=40, node_cap=400)
        print('%-46s status=%-4s %s' % (src, st['status'], fmt(st)))
    print('  (the last is Y f: head-normalises to f (Y\' f), then normal order descends into')
    print('   the argument forever; every step is a legal optional sequence, no draw: 104.4b)')
    print()

    print('== per-rule cost of one head step, as a function of the copied argument ==')
    print('   (n = number of atoms in the copied argument; its encoding has 2n-1 Auras)')
    for rule, tpl in [('I', 'I x'), ('K', 'K x Y'), ('B', 'B x y z'), ('C', 'C x y z'),
                      ('W', 'W x Y'), ('S', 'S x y Y')]:
        for withrest in (False, True):
            row = []
            for n in (1, 2, 4, 8):
                Y = 'a'
                for i in range(n - 1):
                    Y = '(%s b)' % Y if i % 2 else '(c %s)' % Y
                src = tpl.replace('Y', Y) + (' r' if withrest else '')
                t = parse(src)
                g, _ = setup(t)
                h = g.root()
                before = dict(g.n)
                rewrite(g, h)
                g.check()
                assert g.decode() == ref_step(t)
                d = {k: g.n[k] - before[k] for k in g.n}
                row.append('n=%d: mv=%d cp=%d sac=%d sba=%d mana=%d'
                           % (n, d['moves'], d['copies'], d['sacs'], d['sba_passes'],
                              d['dr_loops']))
            print('  %s%s  %s' % (tpl.replace('Y', 'Y') + (' r' if withrest else ''),
                                 ' ' * (12 - len(tpl) - (2 if withrest else 0)),
                                 ' | '.join(row)))
    print()

    print('== basis comparison: the same lambda programs compiled three ways ==')
    print('   SKI (S,K,I + eta), BCKW (B,C,K,W,I; S-case = W (B (C M) N)), SKIBC (Turner)')
    for name, prog in PROGRAMS:
        for basis in ('SKI', 'BCKW', 'BCKW-noI', 'SKIBC'):
            t = compile_lam(prog, basis)
            try:
                nf, st, sc, _ = lockstep('', term=t, fuel=2000, node_cap=20000)
                expect = ref_nf(t, [100000])
                good = nf == expect and st['status'] == 'nf'
            except (AssertionError, RulesError, ProtocolError) as e:
                good = False
                print('  %-16s %-8s FAIL %r' % (name, basis, e))
                ok = False
                continue
            ok &= good
            print('  %-16s %-8s size=%-4d nf=%-22s %s %s'
                  % (name, basis, size(t), show(nf), 'OK ' if good else 'BAD', fmt(st)))
    print()

    print('== random terms: lockstep with a step bound ==')
    rng = random.Random(20261121)
    syms = list(ARITY) + ['a', 'b', 'c']

    def rand(n):
        if n <= 1:
            return rng.choice(syms)
        k = rng.randint(1, n - 1)
        return (rand(k), rand(n - k))
    counts = {'nf': 0, 'fuel': 0, 'cap': 0}
    tot = dict(steps=0, moves=0, copies=0, sacs=0)
    n_run = 0
    for _ in range(500):
        t = rand(rng.randint(1, 24))
        n_run += 1
        try:
            nf, st, sc, _ = lockstep('', term=t, fuel=80, node_cap=1500)
            if st['status'] == 'nf':
                try:
                    if ref_nf(t, [100000]) != nf:
                        raise AssertionError('normal form differs from ref_nf')
                except RuntimeError:
                    pass
        except (AssertionError, RulesError, ProtocolError) as e:
            ok = False
            print('  FAIL %s : %r' % (show(t), e))
            continue
        counts[st['status']] += 1
        for k in tot:
            tot[k] += st[k]
    print('  %d random terms (sizes 1..24 atoms over S K I B C W a b c), all in lockstep: '
          '%d reached normal form, %d hit the 80-step bound, %d hit the 1500-node cap'
          % (n_run, counts['nf'], counts['fuel'], counts['cap']))
    print('  totals: steps=%d moves=%d copies=%d sacs=%d' % (tot['steps'], tot['moves'],
                                                            tot['copies'], tot['sacs']))
    print()

    print('== what the cards do not prevent (protocol, not rules) ==')
    t = parse('S K K x')
    g, _ = setup(t)
    s = g.root()
    c1 = g.cell_child(s)
    c2 = g.cell_child(c1)
    try:
        g.MOVE(c1, g.leaf_child(c2))
        print('  cycle move accepted (unexpected)')
        ok = False
    except ProtocolError as e:
        print('  MOVE of cell c1 onto a leaf below it: rules checks pass, protocol rejects: %s' % e)
    g2, _ = setup(t)
    s = g2.root()
    c1 = g2.cell_child(s)
    passes = g2.SAC(c1)
    print('  SAC of a cell mid-term is legal; the SBA cascade then deletes the arguments below it '
          '(%d passes); the board now reads %s' % (passes, show(g2.decode())))
    print()
    print('ALL OK' if ok else 'SOME FAILED')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
