"""Instruction pointer (IP) implementation."""

import copy, os.path

from funge.stack import StackStack
from funge.space import BoundedSpace
from funge.vector import Vector

class IP(object):
    def __init__(self, program, id=0):
        self.program = program

        self.stringmode = self.queuemode = self.invertmode = False
        self.th_team = 1 # unused
        self.th_id = id

        self.dimension = program.space.dimension
        self.position = Vector.zero(self.dimension)
        self.delta = Vector.zero(self.dimension)
        self.offset = Vector.zero(self.dimension)
        self.space = program.space
        self.stack = StackStack()

        self.commands = program.semantics.commands.copy()
        self.prevcommands = {}
        self.fploaded = []

    def add_commands(self, overlay):
        for cmd, callback in overlay.commands.items():
            self.prevcommands.setdefault(cmd, []).append(self.commands.get(cmd))
            self.commands[cmd] = callback

    def remove_commands(self, overlay):
        for cmd, callback in overlay.commands.items():
            # TODO check self.commands[cmd] and callback for diagnostics.
            prevcmds = self.prevcommands.get(cmd, [])
            if len(prevcmds) > 0:
                callback = prevcmds.pop()
                if callback is None:
                    try:
                        del self.commands[cmd]
                    except Exception:
                        pass
                else:
                    self.commands[cmd] = callback

    def load_fingerprint(self, fpid):
        try:
            fpcls = self.program.fplookup[fpid]
            fp = fpcls(self.program.semantics)
            fp.init(self)
            self.fploaded.append(fp)
            return True
        except Exception:
            return False

    def unload_fingerprint(self, fpid):
        try:
            fpcls = self.program.fplookup[fpid]
        except Exception:
            return False

        for i in reversed(xrange(len(self.fploaded))):
            if self.fploaded[i].__class__ is fpcls:
                try:
                    self.fploaded.pop(i).final(self)
                    return True
                except Exception:
                    return False
        return False

    def final(self):
        for fp in self.fploaded:
            fp.final(self)

    def push(self, item):
        self.stack.push(item, self.invertmode)

    def pushmany(self, items):
        self.stack.pushmany(items, self.invertmode)

    def push_string(self, s):
        self.stack.push_string(s, self.invertmode)

    def push_vector(self, v):
        self.stack.push_vector(v, self.invertmode)

    def pop(self):
        return self.stack.pop(self.queuemode)

    def popmany(self, n):
        return self.stack.popmany(n, self.queuemode)

    def pop_string(self):
        return self.stack.pop_string(self.queuemode)

    def pop_vector(self):
        return Vector(self.stack.pop_vector(self.dimension, self.queuemode))

    getvector = pop_vector

