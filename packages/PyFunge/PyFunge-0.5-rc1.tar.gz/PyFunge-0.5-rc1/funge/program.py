"""Main entry point to Funge program.

This module connects all other modules: funge.semantics for Funge commands,
funge.space for Funge space, funge.ip for individual IP, funge.stack for
stack stack, funge.fingerprint for fingerprints, and funge.platform for
platform-dependent operations.

One should use this module to execute Funge code, unless internal information
is needed (e.g. writing debugger).
"""

from funge.vector import Vector
from funge.ip import IP
from funge.fingerprint import FingerprintLookup
from funge.platform import BufferedPlatform
from funge.exception import IPQuitted, IPStopped

import sys, os

class Program(object):
    def __init__(self, semantics, platform=None, args=None, environ=None,
            warnings=False):
        if args is None:
            args = sys.argv
        if environ is None:
            environ = os.environ
        if platform is None:
            cls = BufferedPlatform # XXX
            platform = cls(args=args, environ=environ, warnings=warnings)

        self.semantics = semantics(platform)
        self.space = self.semantics.create_space()
        self.platform = platform
        self.fplookup = FingerprintLookup()
        self.ips = {}
        self.ipnext = 1

    def generate_ipid(self):
        id = self.ipnext
        self.ipnext += 1
        return id

    def create_ip(self):
        id = self.generate_ipid()
        ip = IP(self, id)
        self.semantics.init_ip(ip)
        self.ips[id] = ip

    def clone_ip(self, ip):
        newip = IP(self)
        newip.th_team = ip.th_team
        newip.th_id = self.generate_ipid()
        newip.position = ip.position
        newip.delta = -ip.delta
        newip.offset = ip.offset
        newip.stack = ip.stack.copy()
        # do not copy fingerprint status. (XXX that's proven to be hard, but...)

        self.ips[newip.th_id] = newip
        return newip

    def load_code(self, code):
        self.space.putspace((0,) * self.space.dimension, code)

    def execute_step(self):
        for id in self.ips.keys():
            try:
                self.semantics.execute(self.ips[id])
            except IPStopped:
                self.ips.pop(id).final()
            except IPQuitted:
                self.ips.clear()
                raise

    def execute(self):
        ips = self.ips
        try:
            if self.execute_step.im_func is Program.execute_step.im_func:
                # shortcut for execute_step. (im_func is required for identity test)
                semantics_execute = self.semantics.execute
                while ips:
                    for id in ips.keys():
                        try:
                            semantics_execute(ips[id])
                        except IPStopped:
                            ips.pop(id).final()
                        except IPQuitted:
                            ips.clear()
                            raise
            else:
                execute_step = self.execute_step
                while ips: execute_step()
            return 0
        except IPQuitted, err:
            return err.exitcode

class DebuggingProgram(Program):
    def __init__(self, semantics, args, stoppos=None, warnings=False):
        Program.__init__(self, semantics, args=args, warnings=warnings)
        self.stopposition = stoppos

    def dump_ips(self):
        flag = False
        for id, ip in self.ips.items():
            if flag:
                print >>sys.stderr
            else:
                flag = True

            print >>sys.stderr, '%d:' % id,
            try:
                print >>sys.stderr, chr(self.space.get(ip.position)),
            except Exception:
                print >>sys.stderr, ' ',
            print >>sys.stderr, ip.position, ip.delta, len(ip.stack[-1]),
            if len(ip.stack) > 1:
                print >>sys.stderr, ip.stack[-2][-20:],
            print >>sys.stderr, ip.stack[-1][-20:],

    def execute_step(self):
        if any(ip.position == self.stopposition for ip in self.ips.values()):
            self.debugging = True

        if self.debugging:
            self.dump_ips()
            raw_input()
        Program.execute_step(self)

    def execute(self):
        self.debugging = False
        try:
            return Program.execute(self)
        except Exception:
            print >>sys.stderr, '-' * 60
            self.dump_ips()
            print >>sys.stderr
            raise

