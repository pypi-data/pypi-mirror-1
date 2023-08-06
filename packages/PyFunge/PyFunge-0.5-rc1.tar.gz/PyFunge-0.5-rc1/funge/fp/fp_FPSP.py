from funge.fingerprint import Fingerprint

import sys
import math
import struct

class FPSP(Fingerprint):
    'Single precision floating point'

    API = 'PyFunge v2'
    ID = 0x46505350

    if sys.hexversion < 0x20600f0:
        plusinf = 1e99999
        minusinf = -1e99999
        nan = plusinf + minusinf
    else:
        plusinf = float('inf')
        minusinf = float('-inf')
        nan = float('nan')

    def fpop(self, ip):
        return struct.unpack('f', struct.pack('I', ip.pop() & 0xffffffff))[0]

    def fpush(self, ip, value):
        ip.push(struct.unpack('i', struct.pack('f', value))[0])

    @Fingerprint.register('A')
    def add(self, ip):
        b = self.fpop(ip)
        a = self.fpop(ip)
        self.fpush(ip, a + b)

    @Fingerprint.register('B')
    def sine(self, ip):
        v = self.fpop(ip)
        self.fpush(ip, math.sin(v))

    @Fingerprint.register('C')
    def cosine(self, ip):
        v = self.fpop(ip)
        self.fpush(ip, math.cos(v))

    @Fingerprint.register('D')
    def divide(self, ip):
        b = self.fpop(ip)
        a = self.fpop(ip)
        if b == 0:
            self.fpush(ip, self.nan) # XXX should be inf or -inf?
        else:
            self.fpush(ip, a / b)

    @Fingerprint.register('E')
    def arcsine(self, ip):
        v = self.fpop(ip)
        if -1 <= v <= 1:
            self.fpush(ip, math.asin(v))
        else:
            self.fpush(ip, self.nan)

    @Fingerprint.register('F')
    def from_integer(self, ip):
        self.fpush(ip, ip.pop())

    @Fingerprint.register('G')
    def arctangent(self, ip):
        v = self.fpop(ip)
        self.fpush(ip, math.atan(v))

    @Fingerprint.register('H')
    def arccosine(self, ip):
        v = self.fpop(ip)
        if -1 <= v <= 1:
            self.fpush(ip, math.acos(v))
        else:
            self.fpush(ip, self.nan)

    @Fingerprint.register('I')
    def to_integer(self, ip):
        v = self.fpop(ip)
        ip.push(int(v))

    @Fingerprint.register('K')
    def logarithm(self, ip):
        v = self.fpop(ip)
        if v <= 0:
            self.fpush(ip, self.minusinf)
        else:
            self.fpush(ip, math.log(v))

    @Fingerprint.register('L')
    def logarithm_10(self, ip):
        v = self.fpop(ip)
        if v <= 0:
            self.fpush(ip, self.minusinf)
        else:
            self.fpush(ip, math.log10(v))

    @Fingerprint.register('M')
    def multiply(self, ip):
        b = self.fpop(ip); a = self.fpop(ip)
        self.fpush(ip, a * b)

    @Fingerprint.register('N')
    def negate(self, ip):
        self.fpush(ip, -self.fpop(ip))

    @Fingerprint.register('P')
    def output(self, ip):
        v = self.fpop(ip)
        self.platform.putstr('%f' % v)

    @Fingerprint.register('Q')
    def sqrt(self, ip):
        v = self.fpop(ip)
        if v < 0:
            self.fpush(ip, self.nan)
        else:
            self.fpush(ip, math.sqrt(v))

    @Fingerprint.register('R')
    def from_string(self, ip):
        try:
            self.fpush(ip, float(ip.pop_string()))
        except Exception:
            self.reflect(ip)

    @Fingerprint.register('S')
    def subtract(self, ip):
        b = self.fpop(ip)
        a = self.fpop(ip)
        self.fpush(ip, a - b)

    @Fingerprint.register('T')
    def tangent(self, ip):
        v = self.fpop(ip)
        self.fpush(ip, math.tan(v))

    @Fingerprint.register('V')
    def absolute_value(self, ip):
        self.fpush(ip, abs(self.fpop(ip)))

    @Fingerprint.register('X')
    def exponential(self, ip):
        self.fpush(ip, math.exp(self.fpop(ip)))

    @Fingerprint.register('Y')
    def power(self, ip):
        y = self.fpop(ip)
        x = self.fpop(ip)
        try:
            self.fpush(ip, x ** y)
        except ValueError:
            self.reflect(ip) # XXX

