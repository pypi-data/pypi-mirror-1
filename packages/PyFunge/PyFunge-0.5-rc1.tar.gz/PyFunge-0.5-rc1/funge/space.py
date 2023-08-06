"""Implementation of Funge space.

Funge-98 space is conceptually N-dimensional grid with walkaround semantics,
called Lahey-space. Befunge-93 space is a subset of Funge-98 space, which have
explicit boundary from (0,0) to (79,23).
"""

from itertools import izip, count

from funge.exception import *
from funge.vector import Vector

class Space(object):
    """Lahey-space implementation."""

    def __init__(self, dimension, default=32):
        assert dimension >= 1

        self.dimension = dimension
        self.space = {}
        self.rectmin = None
        self.rectmax = None
        self.rectcount = [{} for i in xrange(dimension)]
        self.rectchanged = False
        self.default = default

    def get(self, pos):
        try:
            return self.space[pos]
        except KeyError:
            return self.default

    def put(self, pos, char):
        prevpresent = pos in self.space

        if char == self.default:
            try:
                del self.space[pos]
            except Exception:
                pass

            if prevpresent:
                for i in xrange(self.dimension):
                    self.rectcount[i][pos[i]] -= 1
                self.rectchanged = True
        else:
            self.space[pos] = char

            if not prevpresent:
                for i in xrange(self.dimension):
                    try:
                        self.rectcount[i][pos[i]] += 1
                    except KeyError:
                        self.rectcount[i][pos[i]] = 1

                rectmax = self.rectmax
                if rectmax is None:
                    self.rectmax = Vector(pos)
                else:
                    self.rectmax = rectmax.pairwise_max(pos)

                rectmin = self.rectmin
                if rectmin is None:
                    self.rectmin = Vector(pos)
                else:
                    self.rectmin = rectmin.pairwise_min(pos)

                if rectmax != self.rectmax or rectmin != self.rectmin:
                    self.rectchanged = True

    def getspace(self, pos, size, rtrim=True):
        dimension = self.dimension
        get = self.space.get
        if dimension == 1:
            rangex = xrange(pos[0], pos[0]+size[0])
            if rtrim:
                return ''.join(chr(get((x,), 32)) for x in rangex).rstrip(' ')
            else:
                return ''.join(chr(get((x,), 32)) for x in rangex)
        elif dimension == 2:
            rangex = xrange(pos[0], pos[0]+size[0])
            rangey = xrange(pos[1], pos[1]+size[1])
            if rtrim:
                return '\n'.join(
                    ''.join(chr(get((x,y), 32)) for x in rangex).rstrip(' ')
                    for y in rangey).rstrip('\n')
            else:
                return '\n'.join(
                    ''.join(chr(get((x,y), 32)) for x in rangex)
                    for y in rangey)
        elif dimension == 3:
            rangex = xrange(pos[0], pos[0]+size[0])
            rangey = xrange(pos[1], pos[1]+size[1])
            rangez = xrange(pos[2], pos[2]+size[2])
            if rtrim:
                return '\f'.join(
                    '\n'.join(
                        ''.join(chr(get((x,y,z), 32)) for x in rangex).rstrip(' ')
                        for y in rangey).rstrip('\n')
                    for z in rangez).rstrip('\f')
            else:
                return '\f'.join(
                    '\n'.join(
                        ''.join(chr(get((x,y,z), 32)) for x in rangex)
                        for y in rangey)
                    for z in rangez)
        else:
            raise NotImplemented

    def putspace(self, pos, str):
        self.rectchanged = True

        if len(pos) < 3:
            pos = tuple(list(pos)) + (0,) * (3 - len(pos))

        dimension = self.dimension
        x = mx = pos[0]
        y = my = pos[1]
        z = mz = pos[2]
        put = self.put

        if dimension < 3:
            str = str.replace('\f', '')
        if dimension < 2:
            str = str.replace('\r\n', '').replace('\r', '').replace('\n', '')

        for plane in str.split('\f'):
            for line in plane.splitlines():
                for ch in line:
                    if ch != ' ':
                        put(((x, y, z) + pos[3:])[:self.dimension], ord(ch))
                    x += 1
                if mx < x: mx = x
                y += 1
                x = pos[0]
            if my < y: my = y
            z += 1
            y = pos[1]
        if mz < z: mz = z

        maxrect = [mx - pos[0], my - pos[1], mz - pos[2]] + [1] * self.dimension
        maxrect = maxrect[:self.dimension]

        return maxrect

    def updaterect(self):
        if self.rectchanged:
            rectmin = []
            rectmax = []
            for count in self.rectcount:
                nonemptylines = [k for k,v in count.items() if v > 0]
                rectmin.append(min(nonemptylines))
                rectmax.append(max(nonemptylines))
            self.rectmin = Vector(rectmin)
            self.rectmax = Vector(rectmax)
            self.rectchanged = False

        return self.rectmin, self.rectmax

    def normalize(self, position, delta):
        rectmin = self.rectmin
        rectmax = self.rectmax

        for i in xrange(self.dimension):
            if not rectmin[i] <= position[i] <= rectmax[i]: break
        else:
            return position # nothing to do

        # find out maximum backstep which locates IP to other edges.
        # i.e. find maximum k such that rectmin <= IP - k * delta <= rectmax
        backsteps = []
        for i in xrange(self.dimension):
            if delta[i] > 0:
                backsteps.append((position[i] - rectmin[i]) // delta[i])
            elif delta[i] < 0:
                backsteps.append((position[i] - rectmax[i]) // delta[i])

        assert backsteps
        return position - min(backsteps) * delta

    def scanuntil(self, position, delta, value):
        space = self.space
        default = self.default
        rectmin = self.rectmin
        rectmax = self.rectmax
        dimrange = range(self.dimension)
        normalize = self.normalize

        try:
            cell = space[position]
        except KeyError:
            cell = default

        while cell != value:
            position += delta
            for i in dimrange:
                if not rectmin[i] <= position[i] <= rectmax[i]:
                    position = normalize(position, delta)
                    break

            try:
                cell = space[position]
            except KeyError:
                cell = default

        return position

    def scanwhile(self, position, delta, value):
        space = self.space
        default = self.default
        rectmin = self.rectmin
        rectmax = self.rectmax
        dimrange = range(self.dimension)
        normalize = self.normalize

        try:
            cell = space[position]
        except KeyError:
            cell = default

        while cell == value:
            position += delta
            for i in dimrange:
                if not rectmin[i] <= position[i] <= rectmax[i]:
                    position = normalize(position, delta)
                    break

            try:
                cell = space[position]
            except KeyError:
                cell = default

        return position

class BoundedSpace(Space):
    def __init__(self, dimension, rectmin, rectmax, default=32):
        Space.__init__(self, dimension, default)
        self.rectmin = Vector(rectmin)
        self.rectmax = Vector(rectmax)

    def check_position(self, pos):
        for x in xrange(0, self.dimension):
            if not self.rectmin[x] <= pos[x] <= self.rectmax[x]: return False
        return True

    def get(self, pos):
        if self.check_position(pos):
            return Space.get(self, pos)
        else:
            return self.default

    def put(self, pos, char):
        if self.check_position(pos):
            Space.put(self, pos, char)

    def putspace(self, pos, str):
        rectmin = self.rectmin
        rectmax = self.rectmax
        result = Space.putspace(self, pos, str)
        self.rectmin = rectmin
        self.rectmax = rectmax
        return result

    def updaterect(self):
        pass

    def normalize(self, position, delta):
        return Vector([rmin + (pos - rmin) % (rmax - rmin + 1) for pos, rmin, rmax
                in zip(position, self.rectmin, self.rectmax)])

class Befunge93Space(BoundedSpace):
    def __init__(self):
        BoundedSpace.__init__(self, 2, (0, 0), (79, 24))

