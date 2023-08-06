from funge.fingerprint import Fingerprint

import struct

class FPRT(Fingerprint):
    'Formatted print'

    API = 'PyFunge v2'
    ID = 0x46505254

    @Fingerprint.register('D')
    def format_double_fp(self, ip):
        x, y = ip.popmany(2)
        num, = struct.unpack('d', struct.pack('II', y & 0xffffffff, x & 0xffffffff))
        format = ip.pop_string()
        try:
            ip.push_string(format % (num,))
        except (TypeError, KeyError):
            self.reflect(ip)

    @Fingerprint.register('F')
    def format_fp(self, ip):
        num, = struct.unpack('f', struct.pack('I', ip.pop() & 0xffffffff))
        format = ip.pop_string()
        try:
            ip.push_string(format % (num,))
        except (TypeError, KeyError):
            self.reflect(ip)

    @Fingerprint.register('I')
    def format_int(self, ip):
        num = ip.pop()
        format = ip.pop_string()
        try:
            ip.push_string(format % (num,))
        except (TypeError, KeyError):
            self.reflect(ip)

    @Fingerprint.register('L')
    def format_long_int(self, ip):
        x, y = ip.popmany(2)
        format = ip.pop_string()
        self.platform.warn('Attempt to print a long integer at %r.' % (ip.position,))
        ip.push_string(format)

    @Fingerprint.register('S')
    def format_str(self, ip):
        str = ip.pop_string()
        format = ip.pop_string()
        try:
            ip.push_string(format % (str,))
        except (TypeError, KeyError):
            self.reflect(ip)

