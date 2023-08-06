"""Base semantics class."""

class _command(object):
    def __init__(self, func, commands, **kwargs):
        self.func = func
        if isinstance(commands, str):
            self.commands = map(ord, commands)
        else:
            self.commands = commands
        self.kwargs = kwargs

class SemanticsBase(object):
    class __metaclass__(type):
        def __new__(metacls, name, bases, dict):
            commands = {}
            for base in bases:
                if hasattr(base, 'commandmap'):
                    commands.update(base.commandmap)
            for k, v in dict.items():
                if not isinstance(v, _command): continue
                dict[k] = v.func
                v.func.__dict__.update(v.kwargs)
                for c in v.commands:
                    commands[c] = k
            dict['commandmap'] = commands
            return type.__new__(metacls, name, bases, dict)

    def __init__(self):
        self.commands = dict((k, getattr(self, v)) for k,v in self.commandmap.items())

    @staticmethod
    def register(commands, **kwargs):
        def callback(func):
            return _command(func, commands, **kwargs)
        return callback

class SemanticsOverlay(SemanticsBase):
    def __init__(self, semantics):
        SemanticsBase.__init__(self)
        self.semantics = semantics

    def __getattr__(self, name):
        return getattr(self.semantics, name)

class Semantics(SemanticsBase):
    def __init__(self, platform):
        SemanticsBase.__init__(self)
        self.platform = platform

    @classmethod
    def create_space(self):
        raise NotImplemented

    @classmethod
    def init_ip(self, ip):
        pass

    def walk(self, ip):
        ip.position = ip.space.normalize(ip.position + ip.delta, ip.delta)

    def stringmode(self, ip):
        raise NotImplemented

    def undefined(self, ip):
        raise NotImplemented

    def command(self, ip):
        if ip.stringmode:
            method = self.stringmode
        else:
            try:
                method = ip.commands[ip.space.get(ip.position)]
            except KeyError:
                method = self.undefined
        return method(ip)

    def execute(self, ip):
        if self.command(ip):
            # some commands advance IP twice but do not treat second command
            # as marker, so we should not skip such markers. but there can be
            # another markers following, e.g. "#x;...;", which should be
            # ignored here since ip.walk() does skip such markers automatically.
            ip.position += ip.delta
            cell = ip.space.get(ip.position)
            if cell == 32 or cell == 59: self.walk(ip)
        else:
            self.walk(ip)

