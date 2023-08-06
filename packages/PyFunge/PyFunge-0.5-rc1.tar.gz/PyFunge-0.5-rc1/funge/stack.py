"""Implementation of stack and stack stack."""

class Stack(list):
    def push(self, item, bottom=False):
        if bottom:
            self.insert(0, item)
        else:
            self.append(item)

    def pushmany(self, items, bottom=False):
        if bottom:
            self[0:0] = items
        else:
            self.extend(reversed(items))

    def push_string(self, s, bottom=False):
        items = map(ord, s) + [0]
        if bottom:
            self[0:0] = items
        else:
            self.extend(reversed(items))

    def push_vector(self, v, bottom=False):
        if bottom:
            self[0:0] = reversed(v)
        else:
            self.extend(v)

    def pop(self, bottom=False):
        try:
            if bottom:
                return list.pop(self, 0)
            else:
                return list.pop(self)
        except Exception:
            return 0

    def popmany(self, n, bottom=False):
        """stack.popmany(n) -> [stack.pop() for i in xrange(n)]"""
        assert n > 0
        if bottom:
            result = self[:n]
            del self[:n]
        else:
            result = self[-1:-n-1:-1]
            del self[-n:]
        if len(result) < n:
            result.extend([0] * (n - len(result)))
        return result

    def pop_string(self, bottom=False):
        if bottom:
            try:
                firstzero = self.index(0)
            except Exception:
                firstzero = len(self)
            items = self[:firstzero]
            del self[:firstzero+1]
        else:
            for firstzero in xrange(len(self)-1, -1, -1):
                if self[firstzero] == 0: break
            else:
                firstzero = None
            if firstzero is None:
                items = self[::-1]
                del self[:]
            else:
                items = self[-1:firstzero:-1]
                del self[firstzero:]
        return ''.join(map(chr, items))

    def pop_vector(self, n, bottom=False):
        assert n > 0
        if bottom:
            result = self[n-1::-1]
            del self[:n]
        else:
            result = self[-n:]
            del self[-n:]
        if len(result) < n:
            result = [0] * (n - len(result)) + result
        return result

    def clear(self):
        del self[:]

class StackStack(object):
    def __init__(self):
        self.sstack = [Stack()]

    def __len__(self):
        return len(self.sstack)

    def __getitem__(self, key):
        return self.sstack[key]

    def __getattr__(self, name):
        return getattr(self.sstack, name)

    @property
    def top(self):
        return self.sstack[-1]

    @property
    def second(self):
        return self.sstack[-2]

    def push_stack(self):
        self.sstack.append(Stack())

    def pop_stack(self):
        self.sstack.pop()

    def push(self, item, bottom=False):
        self.sstack[-1].push(item, bottom)

    def pushmany(self, items, bottom=False):
        return self.sstack[-1].pushmany(items, bottom)

    def push_string(self, s, bottom=False):
        self.sstack[-1].push_string(s, bottom)

    def push_vector(self, v, bottom=False):
        self.sstack[-1].push_vector(v, bottom)

    def pop(self, bottom=False):
        return self.sstack[-1].pop(bottom)

    def popmany(self, n, bottom=False):
        return self.sstack[-1].popmany(n, bottom)

    def pop_string(self, bottom=False):
        return self.sstack[-1].pop_string(bottom)

    def pop_vector(self, n, bottom=False):
        return self.sstack[-1].pop_vector(n, bottom)

    def copy(self):
        obj = StackStack()
        obj.sstack = [Stack(st[:]) for st in self.sstack]
        return obj

