import sys

def OffsetList(offsets, data):
    if isinstance(data, tuple):
        return OffsetListTuple(offsets, data)
    else:
        return OffsetListSingle(offsets, data)

class OffsetListSingle(object):
    def __init__(self, offsets, data):
        self.offsets = offsets
        self.raw = data

    def _mapify(self, i):
        return self.raw[i]

    def __getitem__(self, key):
        if isinstance(key, tuple):
            if len(key) != 2:
                raise ValueError
            if key[1] < 0 or key[1] >= self.length(key[0]):
                raise IndexError
            return self._mapify(self.offsets[key[0]] + key[1])
        else:
            return self._mapify(slice(self.offsets[key], self.offsets[key+1]))

    def __iter__(self):
        return (self[i] for i in xrange(len(self)))

    def length(self, i = None):
        if i == None:
            return len(self.offsets)-1
        else:
            return self.offsets[i+1] - self.offsets[i]

    def __len__(self):
        return self.length()


class OffsetListTuple(OffsetListSingle):
    if sys.hexversion >= 0x020600f0:
        def _mapify(self, i):
            return self.raw.__class__._make([ val[i] for val in self.raw ])

        def __getattr__(self, key):
            return OffsetListSingle(self.offsets, getattr(self.raw, key))

        fields = property(lambda self: self.raw._fields)

        def slice(self, key):
            if isinstance(key, str):
                return OffsetListSingle(self.offsets, getattr(self.raw, key))
            else:
                return OffsetListSingle(self.offsets, self.raw[key])
    else:
        def _mapify(self, i):
            return tuple([ val[i] for val in self.raw ])

        def slice(self, key):
            return OffsetListSingle(self.offsets, self.raw[key])


class IndexedOffsetList:
    def __init__(self, entities, indices, offsets, raw):
        self.entities = entities
        self.indices = indices
        self.offsets = offsets
        self.raw = raw

    def __getitem__(self, key):
        return self.raw[ self.index(key) ]

    def index(self, key):
        if isinstance(key, tuple):
            if len(key) != 2:
                raise ValueError
            if key[1] < 0 or key[1] >= self.length(key[0]):
                raise IndexError
            return self.indices[ self.offsets[key[0]] + key[1] ]
        else:
            return self.indices[ self.offsets[key]:self.offsets[key+1] ]

    def length(self, i = None):
        if i == None:
            return len(self.offsets)-1
        else:
            return self.offsets[i+1] - self.offsets[i]

    def __len__(self):
        return self.length()
