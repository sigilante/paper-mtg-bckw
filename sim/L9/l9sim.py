#!/usr/bin/env python3
"""L9: L6's spine-chain Aura forest with Replicator as the COPY primitive.

Derived from lines/L6/l6sim.py (reference reducer, encoding, rule sequences, tests and
programs are unchanged).  What changed (see notes/L9-replicator.md):

  * COPY   Replicator "{2}, {T}: Create a tapped token that's a copy of target token you
           control."  Rules checks: the target is a TOKEN on the battlefield; Replicator is
           untapped when activated (a Scepter/Dramatic Reversal loop untaps it); {2} paid;
           the new token enters TAPPED; an Aura token's host is chosen as it enters (303.4f).
           No spell is parked on the stack: between primitives the stack is empty.
  * SEEDS  The first token of each label: cast the label card (sorcery timing) targeting the
           Food token Replicator made when it entered; with the spell on the stack, Lithoform
           Engine "{4}, {T}: Copy target permanent spell you control. (The copy becomes a
           token.)"; the copy resolves first and becomes an Aura token on the Food.  Take
           Possession is refused (split second).  Dream Leash needs a tapped target: a
           Replicator copy of the Food (it enters tapped).
  * ANCHOR Lithoform Engine itself (idle after setup).  No lands at all.
  * MOVE   mode 'G': Simic Guildmage as in L6.  mode 'R': no Guildmage; each rewrite builds
           the reduct beside the old head by Replicator copies, then sacrifices the head and
           the SBA cascade removes the old subterm ("rebuild" machine: COPY + SAC only).
  * PAUSES Optional: between any two primitives the player may let the step end (mana pool
           empties, 106.4) or the whole turn pass (untap step, upkeep, draw, first main phase
           with Elemental Resonance triggers).  Lockstep must survive this.
  * INVARIANT checked after EVERY primitive (not only between steps): a leaf enchants a cell
           or the anchor; a cell enchants a leaf or a cell; no cycle; Essence Leak never on a
           red or green permanent.

The simulator models rules checks and protocol checks separately, as in L6.  It does not
model the opponent (always passes), combat, or the engine reaching the battlefield.
Stdlib only.  Run:  python3 -I l9sim.py
"""
import importlib.util
import os
import random
import sys

sys.setrecursionlimit(20000)
sys.dont_write_bytecode = True      # importing L6 for comparison must not write into lines/L6

ARITY = {'I': 1, 'K': 2, 'S': 3, 'B': 3, 'C': 3, 'W': 2}

# ----------------------------------------------------------------- label cards
LABEL = {'CELL': 'Indestructibility', 'S': 'Bound in Gold', 'K': "Intercessor's Arrest",
         'I': "Curator's Ward", 'B': 'Essence Leak', 'C': "Faith's Fetters",
         'W': 'Elemental Resonance'}
# Take Possession (L6's 4th variable) is dropped: split second forbids activating Lithoform
# Engine while it is on the stack, so it cannot be seeded.
VARLABELS = ['Confiscate', 'Lay Claim', 'Volition Reins', 'Psychic Overload', 'Dream Leash']
SPLIT_SECOND = {'Take Possession'}
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
    'Lithoform Engine': ({'gen': 4}, None),
    'Food': ({}, None),
}
ETB = {"Faith's Fetters": 'you gain 4 life',
       'Psychic Overload': 'tap enchanted permanent',
       'Volition Reins': 'if enchanted permanent is tapped, untap it'}
COST_REPLICATOR = {'gen': 2}             # {2}, {T}
COST_LITHO_PERMANENT = {'gen': 4}        # {4}, {T}
COST_GUILDMAGE = {'U': 1, 'gen': 1}      # {1}{U}


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
    return 1 if not isinstance(t, tuple) else size(t[0]) + size(t[1]) + 1


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
    """Normal-order normaliser (head reduction, then arguments); shares contract/unwind."""
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

    def __init__(self, pid, name, kind, token, host, tapped=False):
        self.id, self.name, self.kind, self.token, self.host = pid, name, kind, token, host
        self.tapped = tapped


class Game:
    """mode 'G': MOVE by Simic Guildmage, COPY by Replicator.
       mode 'R': no Guildmage; rewrite = rebuild the reduct by Replicator copies, SAC head."""

    def __init__(self, mode='G', log=False, verbose_engine=False):
        assert mode in ('G', 'R')
        self.mode = mode
        self.bf = {}            # battlefield: id -> Perm (everything controlled by P)
        self.kids = {}          # host id -> set of ids attached to it (index only)
        self.stack = []
        self.pool = {}
        self.nid = 0
        self.log = log
        self.verbose_engine = verbose_engine
        self.life = 20
        self.library = 10 ** 9  # turns are bounded by the real library (704.5b); counted only
        self.var_label = {}
        self.n = dict(moves=0, copies=0, sacs=0, sba_passes=0, dr_loops=0, resolutions=0,
                      triggers=0, rep_acts=0, extra_untap_loops=0, pauses=0, turns=0,
                      mana_lost=0, er_mana=0, local_checks=0)
        self.lotus = self._perm('Gilded Lotus', 'ENGINE', False, None)
        self.scepter = self._perm('Isochron Scepter', 'ENGINE', False, None)  # DR imprinted
        self.auratog = self._perm('Auratog', 'ENGINE', False, None)
        self.guildmage = (self._perm('Simic Guildmage', 'ENGINE', False, None)
                          if mode == 'G' else None)
        self.anchor = self._perm('Lithoform Engine', 'ANCHOR', False, None)
        self.replicator = self._perm('Replicator', 'ENGINE', False, None)
        self.food = None
        self.seeds = {}
        self.loop_shown = False
        self.pause_rng = None
        self.pause_prob = 0.0
        self._replicator_etb()

    # ------------------------------------------------ bookkeeping
    def _perm(self, name, kind, token, host, tapped=False):
        self.nid += 1
        p = Perm(self.nid, name, kind, token, host, tapped)
        self.bf[self.nid] = p
        if host is not None:
            self.kids.setdefault(host, set()).add(self.nid)
        return p.id

    def _set_host(self, i, h):
        old = self.bf[i].host
        if old is not None:
            self.kids.get(old, set()).discard(i)
        self.bf[i].host = h
        self.kids.setdefault(h, set()).add(i)

    def _delete(self, i):
        p = self.bf.pop(i)
        if p.host is not None:
            self.kids.get(p.host, set()).discard(i)

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
        if p.kind == 'ENGINE':
            return '%s#%d' % (p.name, i)
        return '%s#%d[%s]%s' % (p.kind, i, p.name, '(T)' if p.tapped else '')

    def say(self, s):
        if self.log:
            print('      ' + s)

    def stack_str(self):
        return 'stack(bottom->top): ' + (', '.join(o['desc'] for o in self.stack) or 'empty')

    def is_aura(self, i):
        return self.bf[i].kind not in ('ENGINE', 'ANCHOR', 'THOST')

    def children(self, i):
        return sorted(m for m in self.kids.get(i, ()) if m in self.bf and self.bf[m].host == i)

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
                self._delete(i)

    def push(self, obj):
        self.stack.append(obj)
        self.sba()

    def resolve_top(self):
        """All players pass in succession (117.4, 405.5); the top object resolves."""
        obj = self.stack.pop()
        self.n['resolutions'] += 1
        obj['fn'](obj)
        self.sba()

    # ------------------------------------------------ mana / untap engine
    def mana_loop(self, colour):
        """Tap Gilded Lotus for three of `colour`; pay {2}, tap Isochron Scepter; cast the
        Dramatic Reversal copy; it untaps all nonland permanents you control (Lotus,
        Scepter, Replicator, Lithoform Engine, tokens).  Net +1 `colour`."""
        L, Sc = self.bf[self.lotus], self.bf[self.scepter]
        if L.tapped or Sc.tapped:
            raise RulesError('mana engine tapped')
        L.tapped = True
        self.pool[colour] = self.pool.get(colour, 0) + 3          # mana ability, no stack
        self.pool[colour] -= 2
        Sc.tapped = True

        def scepter_res(o):
            def dr_res(o2):
                for p in self.bf.values():      # no lands are on the battlefield at all
                    p.tapped = False            # "Untap all nonland permanents you control."
            self.push({'desc': 'Dramatic Reversal (Scepter copy, cast)', 'fn': dr_res})
        self.push({'desc': 'Isochron Scepter ability', 'fn': scepter_res})
        self.resolve_top()
        self.resolve_top()
        self.n['dr_loops'] += 1
        if self.verbose_engine and not self.loop_shown:
            self.loop_shown = True
            self.say('[one loop, in full: tap Gilded Lotus for %s%s%s (mana ability); pay {2}, '
                     'tap Isochron Scepter: ability on the stack; all pass: cast the Dramatic '
                     'Reversal copy; all pass: it resolves, untapping Lotus, Scepter, Replicator '
                     'and every other nonland permanent. Net +1 %s; stack back to what it was]'
                     % (colour, colour, colour, colour))

    def avail(self):
        return sum(self.pool.values())

    def pay(self, cost):
        loops0 = self.n['dr_loops']
        for c, k in cost.items():
            if c == 'gen':
                continue
            while self.pool.get(c, 0) < k:
                self.mana_loop(c)
            self.pool[c] -= k
        g = cost.get('gen', 0)
        while self.avail() < g:
            self.mana_loop('U')
        for c in sorted(self.pool, key=lambda c: -self.pool[c]):
            take = min(g, self.pool[c])
            self.pool[c] -= take
            g -= take
        if self.verbose_engine and self.n['dr_loops'] > loops0:
            self.say('mana: %d Scepter/Dramatic Reversal/Lotus loop(s)'
                     % (self.n['dr_loops'] - loops0))

    def untapped_for(self, pid, cost):
        """Activate a {T} ability: if it is tapped and the pool already pays the cost, run one
        extra loop for its untap; otherwise paying the cost runs loops, which untap it."""
        if self.bf[pid].tapped and self.avail() >= sum(cost.values()):
            self.mana_loop('U')
            self.n['extra_untap_loops'] += 1
        self.pay(cost)
        if self.bf[pid].tapped:
            raise RulesError('%s is tapped: {T} cost cannot be paid' % self.bf[pid].name)
        self.bf[pid].tapped = True                                 # 602.2: costs paid together

    # ------------------------------------------------ setup
    def _replicator_etb(self):
        """Replicator entered earlier (assumed): its ETB made a Food token."""
        def res(o):
            self.food = self._perm('Food', 'THOST', True, None)
        self.push({'desc': 'Replicator ETB trigger: create a Food token', 'fn': res})
        self.resolve_top()

    def seed(self, kind):
        """Make the first token of a label: cast the label card (sorcery timing) targeting
        the Food; with it on the stack, Lithoform Engine {4},{T} copies the permanent spell;
        the copy resolves first and becomes an Aura token attached to the same target
        (707.10, 707.10f; Lithoform rulings: no new targets for a permanent spell)."""
        if self.stack:
            raise RulesError('enchantment spell needs an empty stack (117.1a)')
        name = self.label(kind)
        target = self.food
        if name == 'Dream Leash':                       # needs a tapped target as cast
            target = self.COPY(self.food, None, '(tapped Food copy, a target for Dream Leash)')
        self.pay(CARD[name][0])
        spell = {'desc': name + ' (Aura spell, target %s)' % self.nm(target), 'card': name,
                 'target': target}
        rec = {}

        def spell_res(o):
            if o['target'] not in self.bf:
                return
            cid = self._perm(name, kind, False, o['target'])
            rec['card'] = cid
            self._etb(cid)
        spell['fn'] = spell_res
        self.push(spell)
        self.say('cast %s; %s' % (name, self.stack_str()))
        if name in SPLIT_SECOND:
            raise RulesError('split second: Lithoform Engine cannot be activated while %s is on '
                             'the stack' % name)
        self.untapped_for(self.anchor, COST_LITHO_PERMANENT)

        def litho_res(o):
            if spell not in self.stack:
                raise RulesError('Lithoform target left the stack (608.2b)')

            def copy_res(o2):
                tid = self._perm(name, kind, True, o2['target'])       # becomes a token
                rec['seed'] = tid
                self._etb(tid)
            self.stack.append({'desc': 'copy of %s (same target)' % name, 'fn': copy_res,
                               'target': spell['target']})
            self.sba()
        self.push({'desc': 'Lithoform Engine ability (target %s spell)' % name, 'fn': litho_res})
        self.say('activate Lithoform Engine {4},{T}; %s' % self.stack_str())
        self.resolve_top()          # Lithoform ability -> copy of the spell on the stack
        self.resolve_top()          # the copy resolves: Aura token on the target
        self.resolve_top()          # the original resolves: the card on the target
        self.seeds[kind] = rec['seed']
        self.say('seed %s made; label card %s also on %s'
                 % (self.nm(rec['seed']), self.nm(rec['card']), self.nm(target)))
        if self.stack:
            raise RulesError('stack not empty after seeding')

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

    # ------------------------------------------------ the primitives
    def COPY(self, n, host, why=''):
        """Replicator {2},{T}: tapped token copy of target token you control; an Aura token's
        host is chosen as it enters (303.4f)."""
        if n not in self.bf:
            raise RulesError('Replicator: target must be on the battlefield')
        if not self.bf[n].token:
            raise RulesError('Replicator: target must be a token (%s is a card)' % self.nm(n))
        self.untapped_for(self.replicator, COST_REPLICATOR)
        self.n['rep_acts'] += 1
        rec = {}

        def res(o):
            if n not in self.bf:                                  # 608.2b
                raise RulesError('Replicator target gone on resolution')
            p = self.bf[n]
            if self.is_aura(n):
                if host is None or host not in self.bf or host == 'new':
                    raise RulesError('303.4f: host must be a permanent on the battlefield')
                m = self._perm(p.name, p.kind, True, host, tapped=True)
                self.n['copies'] += 1
            else:
                m = self._perm(p.name, p.kind, True, None, tapped=True)
            rec['m'] = m
            self._etb(m)
        self.push({'desc': 'Replicator ability (target %s)' % self.nm(n), 'fn': res})
        if self.verbose_engine:
            self.say('activate Replicator {2},{T} targeting %s; %s' % (self.nm(n), self.stack_str()))
        self.resolve_top()
        m = rec['m']
        self.say('COPY  %s => new %s on %s  (Replicator; host by 303.4f)%s'
                 % (self.nm(n), self.nm(m), self.nm(host) if host else '-',
                    (' ' + why) if why else ''))
        self.after_primitive()
        return m

    def MOVE(self, n, h, why=''):
        """Simic Guildmage {1}{U} (mode G only)."""
        if self.guildmage is None:
            raise RulesError('no Simic Guildmage in this engine')
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
            if h in self.descendants(n):
                raise ProtocolError('MOVE would create an attachment cycle (rules allow it)')
            self._set_host(n, h)
        self.push({'desc': 'Simic Guildmage ability (target %s)' % self.nm(n), 'fn': res})
        if self.verbose_engine:
            self.say('activate Guildmage targeting %s; %s' % (self.nm(n), self.stack_str()))
        self.resolve_top()
        self.say('MOVE  %s : %s -> %s  (Simic Guildmage {1}{U})%s'
                 % (self.nm(n), self.nm(old), self.nm(h), (' ' + why) if why else ''))
        self.after_primitive()

    def SAC(self, n, why=''):
        """Auratog: 'Sacrifice an enchantment' is the cost; SBAs run before priority."""
        if n not in self.bf or not self.is_aura(n):
            raise RulesError('Auratog: sacrifice an enchantment you control')
        self.n['sacs'] += 1
        self.say('SAC   %s  (Auratog cost)%s' % (self.nm(n), (' ' + why) if why else ''))
        self._delete(n)                                       # 701.21a; token ceases, 704.5d

        def res(o):
            pass                                              # +2/+2 until end of turn
        before = self.n['sba_passes']
        self.push({'desc': 'Auratog ability', 'fn': res})
        self.resolve_top()
        d = self.n['sba_passes'] - before
        self.after_primitive()
        return d

    # ------------------------------------------------ pausing across steps and turns
    def after_primitive(self):
        self.check_local()
        if self.pause_rng is not None and self.pause_rng.random() < self.pause_prob:
            self.pause(self.pause_rng.choice(['step', 'turn']))

    def pause(self, kind):
        """Stop between primitives.  The stack is empty here, so nothing is lost but mana."""
        if self.stack:
            raise RulesError('pause with a non-empty stack would not end the step (500.2)')
        self.n['pauses'] += 1
        lost = self.avail()
        self.n['mana_lost'] += lost
        self.pool = {}                                       # 106.4
        if kind == 'step':
            self.say('PAUSE: the step ends (pool of %d empties, 106.4); resume in the next step'
                     % lost)
            self.check_local()
            return
        self.n['turns'] += 1
        # opponent's turn: the opponent passes.  P's untap step: untap P's permanents, except
        # a permanent enchanted by Psychic Overload ("doesn't untap during its controller's
        # untap step").
        for i, p in self.bf.items():
            if not any(self.bf[m].name == 'Psychic Overload' for m in self.children(i)):
                p.tapped = False
        # upkeep: the only label with an upkeep clause is Essence Leak, conditional on a red
        # or green host; check_local asserts that never happens.
        self.check_local()
        # draw step
        self.library -= 1
        if self.library < 0:
            raise RulesError('704.5b: draw from an empty library')
        # precombat main phase: Elemental Resonance triggers, one per copy on the battlefield
        added = 0
        for i in sorted(self.bf):
            p = self.bf[i]
            if p.name != 'Elemental Resonance' or p.host not in self.bf:
                continue
            cost = CARD.get(self.bf[p.host].name, ({}, None))[0]
            self.n['triggers'] += 1

            def res(o, cost=cost):
                for c, k in cost.items():
                    cc = 'C' if c == 'gen' else c
                    self.pool[cc] = self.pool.get(cc, 0) + k
            self.push({'desc': 'Elemental Resonance trigger', 'fn': res})
            self.resolve_top()
            added += sum(cost.values())
        self.n['er_mana'] += added
        self.say('PAUSE: turn passes (pool of %d empties; untap step; upkeep; draw; first main '
                 'phase: Elemental Resonance adds %d); resume' % (lost, added))

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
        """Aura tokens not hanging (directly) on a seed host (Food or a Food copy)."""
        return [i for i, p in self.bf.items()
                if self.is_aura(i) and p.token and p.host in self.bf
                and self.bf[p.host].kind != 'THOST']

    # ------------------------------------------------ invariants
    def protocol_check_acyclic(self):
        for i in self.term_nodes():
            seen, x = set(), i
            while x is not None and x in self.bf and self.bf[x].kind not in ('ANCHOR', 'THOST'):
                if x in seen:
                    raise ProtocolError('attachment cycle')
                seen.add(x)
                x = self.bf[x].host

    def check_local(self):
        """After EVERY primitive: both halves of the leaf/cell host invariant behind the
        label analysis, acyclicity, and Essence Leak never on a red or green permanent."""
        self.n['local_checks'] += 1
        nodes = set(self.term_nodes())
        for i in nodes:
            p = self.bf[i]
            hp = self.bf[p.host]
            if p.kind == 'CELL':
                if p.host not in nodes:
                    raise ProtocolError('a cell must enchant a leaf or a cell (on %s)'
                                        % self.nm(p.host))
            else:
                if not (hp.kind == 'CELL' and p.host in nodes) and p.host != self.anchor:
                    raise ProtocolError('a leaf must enchant a cell or the anchor (on %s)'
                                        % self.nm(p.host))
        for i, p in self.bf.items():
            if p.name == 'Essence Leak' and p.host in self.bf:
                if CARD.get(self.bf[p.host].name, ({}, None))[1] in ('R', 'G'):
                    raise ProtocolError('Essence Leak on a red or green permanent')
        self.protocol_check_acyclic()

    def check(self):
        """Between steps: encoding invariants (as L6) plus the local invariant."""
        if len(self.children(self.anchor)) != 1:
            raise ProtocolError('anchor must hold exactly the root')
        self.check_local()
        for i in self.term_nodes():
            cs = self.children(i)
            cells = [m for m in cs if self.bf[m].kind == 'CELL']
            leaves = [m for m in cs if self.bf[m].kind != 'CELL']
            if len(cells) > 1:
                raise ProtocolError('two cells on one node')
            if self.bf[i].kind == 'CELL':
                if len(leaves) != 1:
                    raise ProtocolError('cell must hold exactly one argument')
            elif leaves:
                raise ProtocolError('leaf holds only its first cell')


# ----------------------------------------------------------------- RULE SEQUENCES
def rewrite(g, h):
    return rewrite_G(g, h) if g.mode == 'G' else rewrite_R(g, h)


def rewrite_G(g, h):
    """L6's per-rule sequences, unchanged (MOVE by Guildmage, COPY now by Replicator)."""
    kind = g.bf[h].kind
    k = ARITY[kind]
    P = g.bf[h].host
    cells = g.chain(h)
    c = cells[:k]
    rest = cells[k] if len(cells) > k else None
    r = [g.leaf_child(x) for x in c]
    M = g.MOVE

    if kind in ('I', 'K'):
        M(r[0], P, '(x becomes the head)')
        if rest:
            M(rest, g.last(r[0]), '(rest of the spine)')
    elif kind == 'B':
        M(r[0], P, '(x becomes the head)')
        M(c[1], g.last(r[0]), '(cell holding y, with z and rest below it)')
        M(c[2], g.last(r[1]), '(cell holding z goes under y: (y z))')
        if rest:
            M(rest, c[1], '(rest of the spine)')
    elif kind == 'C':
        M(r[0], P, '(x becomes the head)')
        M(c[2], g.last(r[0]), '(cell holding z)')
        M(c[1], c[2], '(cell holding y after z)')
        if rest:
            M(rest, c[1], '(rest of the spine)')
    elif kind == 'W':
        M(r[0], P, '(x becomes the head)')
        M(c[1], g.last(r[0]), '(cell holding y)')
        M(c[0], c[1], '(freed cell: second y)')
        if rest:
            M(rest, c[0], '(rest of the spine)')
        copy_subtree(g, r[1], c[0])
    elif kind == 'S':
        M(r[0], P, '(x becomes the head)')
        M(c[2], g.last(r[0]), '(cell holding z)')
        M(c[1], c[2], '(cell holding y)')
        if rest:
            M(rest, c[1], '(rest of the spine)')
        M(c[0], g.last(r[1]), '(freed cell: argument of y)')
        copy_subtree(g, r[2], c[0])
    return g.SAC(h, '(old head; SBA cascade collects whatever still hangs from it)')


def rewrite_R(g, h):
    """Rebuild machine: build the reduct (with any trailing arguments) on P, next to the old
    head, by Replicator copies of the old nodes; then sacrifice the head.  The cascade
    removes the whole old subterm.  No MOVE at all."""
    kind = g.bf[h].kind
    k = ARITY[kind]
    P = g.bf[h].host
    cells = g.chain(h)
    args = [g.leaf_child(x) for x in cells]              # old argument roots (node ids)
    cellsrc = cells[0]
    new = rebuild(contract(kind, args[:k]), args[k:])    # same contraction, over node ids

    def emit(e, host):
        if not isinstance(e, tuple):
            leaf = copy_subtree(g, e, host)
            return leaf, g.last(leaf)
        fl, flast = emit(e[0], host)
        cell = g.COPY(cellsrc, flast)
        emit(e[1], cell)
        return fl, cell
    emit(new, P)
    return g.SAC(h, '(old head; the cascade removes the old subterm)')


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
    """Setup: build term t top-down by Replicator copies of the seed tokens."""
    h, args = unwind(t)
    leaf = g.COPY(g.seeds[h], host)
    last = leaf
    for a in args:
        cell = g.COPY(g.seeds['CELL'], last)
        build(g, a, cell)
        last = cell
    return leaf


def kinds(t):
    return {t} if isinstance(t, str) else kinds(t[0]) | kinds(t[1])


def setup(t, mode='G', log=False):
    g = Game(mode=mode, log=log, verbose_engine=log)
    for kd in sorted(kinds(t) | {'CELL'}):
        g.seed(kd)
    # building the initial term: the root leaf goes on the anchor, so check_local applies
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


def lockstep(src, mode='G', log=False, verbose_engine=False, fuel=200, node_cap=3000,
             term=None, pause_rng=None, pause_prob=0.0):
    t = parse(src) if term is None else term
    g, setup_cost = setup(t, mode=mode)
    g.log, g.verbose_engine = log, verbose_engine
    g.pause_rng, g.pause_prob = pause_rng, pause_prob
    if log:
        print('    initial board (child indented under the permanent it enchants; (T) = tapped):')
        print(board_str(g))
        print('    ' + g.stack_str())
    cur = t
    steps = 0
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
        if log:
            print('    step %d: redex head %s on %s' % (steps, g.nm(h), g.nm(g.bf[h].host)))
        depth = rewrite(g, h)
        max_sba = max(max_sba, depth)
        if log:
            print('      => ' + show(g.decode()) + '    ' + g.stack_str())
        cur = nxt
        max_nodes = max(max_nodes, len(g.term_nodes()))
    if g.stack:
        raise AssertionError('stack not empty at the end')
    st = dict(g.n)
    st.update(steps=steps, max_nodes=max_nodes, max_sba_depth=max_sba, status=status)
    return cur, st, setup_cost


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
        return A
    xa, xb = x in fv(A), x in fv(Bt)
    if basis == 'SKI':
        return (('S', abstract(x, A, basis)), abstract(x, Bt, basis))
    if xa and not xb:
        return (('C', abstract(x, A, basis)), Bt)
    if xb and not xa:
        return (('B', A), abstract(x, Bt, basis))
    if basis == 'SKIBC':
        return (('S', abstract(x, A, basis)), abstract(x, Bt, basis))
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

TESTS = [
    ('S K K x', 'x'),
    ('W K x', 'x'),
    ('S I I (K a)', 'a'),
    ('S I I I', 'I'),
    ('B f g x', 'f (g x)'),
    ('C f x y', 'f y x'),
    ('C (B f) x y', 'f (y x)'),
    ('B (C K) W x y', 'y'),
    ('S x y (K a b)', 'x a (y a)'),
    ('S (S (K S) K) I f x', 'f (f x)'),
    ('S (S (K S) K) (S (S (K S) K) I) f x', 'f (f (f x))'),
    ('S (S (K S) K) I (S (S (K S) K) I) f x', 'f (f (f (f x)))'),
    ('K a (S I I (S I I))', 'a'),
    ('K a (W W W)', 'a'),
    ('W (B f) (K a)', 'f a'),
    ('S (K (S I)) K a b', 'b a'),
    ('K (I a)', 'K a'),
]


def load_l6():
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, '..', 'L6', 'l6sim.py')
    spec = importlib.util.spec_from_file_location('l6sim_ref', path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def fmt(st):
    return ('steps=%d mv=%d cp=%d sac=%d sba=%d mana=%d res=%d trig=%d max_nodes=%d'
            % (st['steps'], st['moves'], st['copies'], st['sacs'], st['sba_passes'],
               st['dr_loops'], st['resolutions'], st['triggers'], st['max_nodes']))


def main():
    ok = True
    L6 = load_l6()
    print('L9 simulator: L6 Aura forest, COPY by Replicator (tapped token copy of a token)')
    print('engines: G = Guildmage MOVE + Replicator COPY;  R = Replicator COPY only (rebuild)')
    print('mana = Scepter/Dramatic Reversal/Lotus loops (one loop = +1 mana);')
    print('res = stack objects resolved (each needs all players to pass)')
    print()

    print('== setup trace: seeding the labels of S K K x (Lithoform Engine on cast label cards) ==')
    g, base = setup(parse('S K K x'), mode='G', log=True)
    print('  setup cost: seeds=%d (Lithoform activations), term build copies=%d, '
          'mana=%d loops, res=%d' % (len(g.seeds), base['copies'], base['dr_loops'],
                                     base['resolutions']))
    print()

    print('== worked trace 1 (engine G): S K K x ==')
    nf, st, sc = lockstep('S K K x', mode='G', log=True, verbose_engine=True)
    print('  normal form: %s ; %s' % (show(nf), fmt(st)))
    print()
    print('== worked trace 2 (engine R, no Guildmage): S K K x ==')
    nf, st, sc = lockstep('S K K x', mode='R', log=True)
    print('  normal form: %s ; %s' % (show(nf), fmt(st)))
    print()
    print('== worked trace 3 (engine G) with forced pauses after every primitive ==')
    rng = random.Random(7)
    nf, st, sc = lockstep('S K K x', mode='G', log=True, pause_rng=rng, pause_prob=1.0)
    print('  normal form: %s ; %s pauses=%d turns=%d mana_lost=%d er_mana=%d'
          % (show(nf), fmt(st), st['pauses'], st['turns'], st['mana_lost'], st['er_mana']))
    print()

    print('== lockstep vs reference reducer, fixed terms; mana and res for L6 / L9-G / L9-R ==')
    print('   %-40s %-17s %-22s %-22s %-22s' % ('term', 'nf', 'L6 mana/res', 'L9-G mana/res',
                                              'L9-R mana/res'))
    for src, expect in TESTS:
        row = []
        try:
            nf6, st6, _, _ = L6.lockstep(src)
            row.append('%d/%d' % (st6['dr_loops'], st6['resolutions']))
            good = True
            for mode in ('G', 'R'):
                nf, st, sc = lockstep(src, mode=mode)
                good &= show(nf) == expect and st['status'] == 'nf'
                good &= ref_nf(parse(src), [10000]) == nf
                if mode == 'G':
                    good &= (st['moves'], st['copies'], st['sacs']) == \
                        (st6['moves'], st6['copies'], st6['sacs'])
                row.append('%d/%d (cp %d)' % (st['dr_loops'], st['resolutions'], st['copies']))
        except (AssertionError, RulesError, ProtocolError) as e:
            print('   %-40s FAIL %r' % (src, e))
            ok = False
            continue
        ok &= good
        print('   %-40s %-17s %-22s %-22s %-22s %s' % (src, expect, row[0], row[1], row[2],
                                                      'OK' if good else 'BAD'))
    print('   (L9-G moves/copies/sacs asserted equal to L6 on every term: same rule sequences)')
    print()

    print('== non-normalising terms under a 40-step bound (lockstep on every step) ==')
    for src in ['S I I (S I I)', 'W W W', 'S (K (S I I)) (S (S (K S) K) (K (S I I))) f']:
        for mode in ('G', 'R'):
            nf, st, sc = lockstep(src, mode=mode, fuel=40, node_cap=400)
            print('   %-46s %s status=%-4s %s' % (src, mode, st['status'], fmt(st)))
    print()

    print('== per-rule cost of one head step (n = atoms in the copied/kept argument) ==')
    for rule, tpl in [('I', 'I x'), ('K', 'K x Y'), ('B', 'B x y z'), ('C', 'C x y z'),
                      ('W', 'W x Y'), ('S', 'S x y Y')]:
        for withrest in (False, True):
            for mode in ('G', 'R'):
                row = []
                for n in (1, 2, 4, 8):
                    Y = 'a'
                    for i in range(n - 1):
                        # L6 used a, b, c here; L9 has 5 variable labels, not 6, so the
                        # copied argument uses a and b only (same shape and size)
                        Y = '(%s b)' % Y if i % 2 else '(a %s)' % Y
                    src = tpl.replace('Y', Y) + (' r' if withrest else '')
                    t = parse(src)
                    g, _ = setup(t, mode=mode)
                    before = dict(g.n)
                    rewrite(g, g.root())
                    g.check()
                    assert g.decode() == ref_step(t)
                    d = {k: g.n[k] - before[k] for k in g.n}
                    row.append('n=%d: mv=%d cp=%d mana=%d res=%d'
                               % (n, d['moves'], d['copies'], d['dr_loops'], d['resolutions']))
                name = tpl + (' r' if withrest else '')
                print('   %-10s %s  %s' % (name, mode, ' | '.join(row)))
    print()

    print('== basis comparison: mana (moves/copies) for L6, L9-G, L9-R ==')
    for name, prog in PROGRAMS:
        for basis in ('SKI', 'BCKW', 'SKIBC'):
            t = compile_lam(prog, basis)
            cells = []
            try:
                _, s6, _, _ = L6.lockstep('', term=t, fuel=2000, node_cap=20000)
                cells.append('%d (%d/%d)' % (s6['dr_loops'], s6['moves'], s6['copies']))
                good = True
                for mode in ('G', 'R'):
                    nf, st, sc = lockstep('', mode=mode, term=t, fuel=2000, node_cap=20000)
                    good &= nf == ref_nf(t, [100000]) and st['status'] == 'nf'
                    cells.append('%d (%d/%d)' % (st['dr_loops'], st['moves'], st['copies']))
            except (AssertionError, RulesError, ProtocolError) as e:
                print('   %-14s %-6s FAIL %r' % (name, basis, e))
                ok = False
                continue
            ok &= good
            print('   %-14s %-6s size=%-3d L6 %-15s L9-G %-15s L9-R %-17s %s'
                  % (name, basis, size(t), cells[0], cells[1], cells[2], 'OK' if good else 'BAD'))
    print()

    print('== random terms (the same 500 as L6: seed 20261121), lockstep with a step bound ==')
    rng = random.Random(20261121)
    syms = list(ARITY) + ['a', 'b', 'c']

    def rand(n):
        if n <= 1:
            return rng.choice(syms)
        k = rng.randint(1, n - 1)
        return (rand(k), rand(n - k))
    terms = [rand(rng.randint(1, 24)) for _ in range(500)]
    prng = random.Random(99)
    for label, mode, pp in [('L6', None, 0.0), ('L9-G', 'G', 0.0), ('L9-R', 'R', 0.0),
                            ('L9-G+pauses', 'G', 0.15), ('L9-R+pauses', 'R', 0.15)]:
        counts = {'nf': 0, 'fuel': 0, 'cap': 0}
        tot = dict(steps=0, moves=0, copies=0, sacs=0, dr_loops=0, resolutions=0, pauses=0,
                   turns=0, local_checks=0, extra_untap_loops=0, mana_lost=0, er_mana=0)
        fails = 0
        for t in terms:
            try:
                if mode is None:
                    nf, st, _, _ = L6.lockstep('', term=t, fuel=80, node_cap=1500)
                else:
                    nf, st, _ = lockstep('', mode=mode, term=t, fuel=80, node_cap=1500,
                                         pause_rng=prng if pp else None, pause_prob=pp)
                if st['status'] == 'nf':
                    try:
                        if ref_nf(t, [100000]) != nf:
                            raise AssertionError('normal form differs from ref_nf')
                    except RuntimeError:
                        pass
            except (AssertionError, RulesError, ProtocolError) as e:
                ok = False
                fails += 1
                print('   FAIL %s %s : %r' % (label, show(t), e))
                continue
            counts[st['status']] += 1
            for k in tot:
                tot[k] += st.get(k, 0)
        print('   %-12s nf=%d fuel=%d cap=%d fail=%d | steps=%d mv=%d cp=%d sac=%d mana=%d '
              'res=%d' % (label, counts['nf'], counts['fuel'], counts['cap'], fails,
                          tot['steps'], tot['moves'], tot['copies'], tot['sacs'],
                          tot['dr_loops'], tot['resolutions']))
        if mode is not None:
            print('   %-12s local invariant checks=%d pauses=%d (turns passed %d) '
                  'extra untap loops=%d mana lost at step ends=%d Elemental Resonance mana=%d'
                  % ('', tot['local_checks'], tot['pauses'], tot['turns'],
                     tot['extra_untap_loops'], tot['mana_lost'], tot['er_mana']))
    print()

    print('== rules and protocol demonstrations ==')
    g, _ = setup(parse('S K K x'), mode='G')
    card = next(i for i, p in g.bf.items() if p.kind == 'S' and not p.token)
    try:
        g.COPY(card, g.anchor)
        print('   Replicator copied a card (unexpected)')
        ok = False
    except RulesError as e:
        print('   Replicator targeting the Bound in Gold CARD: refused: %s' % e)
    g2 = Game(mode='G')
    try:
        g2.var_label['q'] = 'Take Possession'
        g2.seed('q')
        print('   Take Possession seeded (unexpected)')
        ok = False
    except RulesError as e:
        print('   seeding Take Possession: refused: %s' % e)
    g3, _ = setup(parse('S K K x'), mode='G')
    s = g3.root()
    c1 = g3.cell_child(s)
    c2 = g3.cell_child(c1)
    try:
        g3.MOVE(c1, g3.leaf_child(c2))
        print('   cycle move accepted (unexpected)')
        ok = False
    except ProtocolError as e:
        print('   MOVE of cell c1 onto a leaf below it: rules pass, protocol rejects: %s' % e)
    g4, _ = setup(parse('S K K x'), mode='G')
    try:
        g4.MOVE(g4.leaf_child(g4.cell_child(g4.root())), g4.auratog)
        print('   leaf moved onto Auratog without complaint (unexpected)')
        ok = False
    except ProtocolError as e:
        print('   MOVE of a leaf onto Auratog: rules pass, per-move invariant rejects: %s' % e)
    g5, _ = setup(parse('x a b c d'), mode='G')
    print('   five variables: labels %s' % sorted(g5.var_label.values()))
    print()
    print('ALL OK' if ok else 'SOME FAILED')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
