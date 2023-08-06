"""Classes to read/write Dan Bernstein's cdb ("constant database") file format.
See http://cr.yp.to/cdb.html for the cdb specification.
"""

import os, struct

__all__ = ["cdb_hash", "iterlocations", "itervalues", "Index", "CDB", "CDBWriter"]

try:
    from _cdblib import cdb_hash, LiteIndex

    class Index(object):

        def __init__(self, f):
            self._liteindex = LiteIndex(load_hash_table(f))

        def get_hash_locations(self, h):
            return self._liteindex.get_hash_locations(h)

        def get_key_locations(self, key):
            return self.get_hash_locations(cdb_hash(key))

except ImportError:
    import warnings
    warnings.warn("Could not load module '_cdblib'. Using Python fallback implementation.")

    def cdb_hash(s):
        h = 5381
        for c in map(ord, s):
            h = (((h << 5) + h) ^ c) & 0xffffffff
        return h

    class Index(object):

        def __init__(self, f):
            self.htable = load_hash_table(f)

        def get_hash_locations(self, h):
            return self.htable[h]

        def get_key_locations(self, key):
            return self.get_hash_locations(cdb_hash(key))

class Error(Exception): pass
class CorruptedIndex(Error): pass

def icheck(cond, msg=""):
    if not cond:
        raise CorruptedIndex(msg or "index corrupted")
    
pack_header = struct.Struct("< 512I").pack

slot_packer = struct.Struct("< 2I")
SLOT_SIZE = slot_packer.size
unpack_slot = slot_packer.unpack
pack_slot = slot_packer.pack

HEADER_SIZE = 2048
HASH_TABLE_COUNT = 256
MAX_RECORD_LOCATION = 0xFFFFFFFFL - 8

def load_hash_table(f):
    htable = {}
    arg_is_filename = isinstance(f, str)
    if arg_is_filename:
        f = open(f, "rb")
    fread = f.read
    f.seek(0)
    start = struct.unpack("<I", fread(4))[0]
    icheck(start >= HEADER_SIZE, "invalid hash table offset")
    f.seek(start)
    while True:
        buf = fread(8192)
        icheck(len(buf) % SLOT_SIZE == 0, "invalid hash tables length")
        if not buf:
            break
        for i in range(0, len(buf), SLOT_SIZE):
            rec_hash, rec_pos = unpack_slot(buf[i:i+SLOT_SIZE])
            if rec_pos == 0:
                continue
            icheck(HEADER_SIZE <= rec_pos <= MAX_RECORD_LOCATION, "invalid record location")
            htable.setdefault(rec_hash, []).append(rec_pos)
    if arg_is_filename:
        f.close()
    return htable
    
def iterlocations(f, key):
    h = cdb_hash(key)
    div, mod = divmod(h, HASH_TABLE_COUNT)
    f.seek(mod * SLOT_SIZE)
    tstart, tlen = unpack_slot(f.read(SLOT_SIZE))
    if not tlen:
        raise StopIteration
    tend = tstart + tlen * SLOT_SIZE
    n = 0
    locations = []
    slot_pos = tstart + ((div % tlen) * SLOT_SIZE)
    while n < tlen:
        f.seek(slot_pos)
        rec_hash, rec_pos = unpack_slot(f.read(SLOT_SIZE))
        if rec_pos == 0:
            break
        if rec_hash == h:
            yield rec_pos
        slot_pos += SLOT_SIZE
        if slot_pos == tend:
            # Loop around to beginning of hash table.
            slot_pos = tstart
        n += 1

def itervalues(f, key, locations=None):
    fread = f.read; fseek = f.seek
    locations = locations or iterlocations(f, key)
    h = cdb_hash(key)
    for location in locations:
        fseek(location)
        klen, dlen = unpack_slot(fread(SLOT_SIZE))
        if klen == len(key):
            dkey = fread(klen)
            #assert cdb_hash(dkey) == h
            if dkey == key:
                if dlen > 0:
                    yield fread(dlen)
                else:
                    yield ""

class _BaseCDB(object):

    def __getitem__(self, key):
        if self.f.closed:
            raise ValueError("I/O operation on closed CDB file")
        try:
            # If key is not in the index, KeyError will be raised.
            locations = self.index.get_key_locations(key) if self.index else None
            return itervalues(self.f, key, locations).next()
        except (KeyError, StopIteration):
            raise KeyError(key)

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def __contains__(self, key):
        try:
            self[key]
            return True
        except KeyError:
            return False

    def getall(self, key):
        if self.f.closed:
            raise ValueError("I/O operation on closed CDB file")
        try:
            # If key is not in the index, KeyError will be raised.
            locations = self.index.get_key_locations(key) if self.index else None
        except KeyError:
            raise KeyError(key)
        return list(itervalues(self.f, key, locations))

class CDB(_BaseCDB):

    def __init__(self, fname, load_index=False):
        self.f = open(fname, "rb")
        if load_index:
            self.index = Index(self.f)
        else:
            self.index = None

    def close(self):
        self.f.close()

class CDBWriter(_BaseCDB):

    class Index(object):

        def __init__(self, f=None):
            if f:
                self.htable = load_hash_table(f)
            else:
                self.htable = {}

        def get_hash_locations(self, h):
            return self.htable[h]

        def get_key_locations(self, key):
            return self.get_hash_locations(cdb_hash(key))

        def add_location(self, key, location):
            self.htable.setdefault(cdb_hash(key), []).append(location)

        def save(self, f, eod):
            f.seek(eod)
            htables = {}
            for h, tpos in self.htable.iteritems():
                table = htables.setdefault(h % HASH_TABLE_COUNT, [])
                for pos in tpos:
                    table.append((h, pos))
            ptables = []
            for i in range(HASH_TABLE_COUNT):
                htable = htables.get(i, [])
                if not htable:
                    ptables.extend((f.tell(), 0))
                    continue
                hsize = len(htable) * 2
                ptables.extend((f.tell(), hsize))
                slot_table = [(0, 0)] * hsize
                for rec_hash, rec_pos in htable:
                    where = (rec_hash // HASH_TABLE_COUNT) % hsize
                    while slot_table[where][1]:
                        where += 1
                        if where == hsize:
                            where = 0
                    slot_table[where] = (rec_hash, rec_pos)
                f.write("".join([pack_slot(*slot) for slot in slot_table]))
            f.seek(0)
            f.write(pack_header(*ptables))
            f.flush()

    def __init__(self, fname):
        if os.path.exists(fname):
            self.f = open(fname, "r+b")
            self.index = CDBWriter.Index(self.f)
            self.f.seek(0)
            self.eod = struct.unpack("<I", self.f.read(4))[0]
            self.f.seek(0, 2) # Seek to end of file
            self.size = self.f.tell()
        else:
            self.f = open(fname, "w+b")
            self.f.write('\0' * 2048)
            self.size = self.eod = 2048
            self.index = CDBWriter.Index()
        self.dirty = False

    def __setitem__(self, key, value):
        if self.f.closed:
            raise ValueError("I/O operation on closed CDB file")
        f = self.f
        dpos = self.eod
        f.seek(self.eod)
        klen = len(key); dlen = len(value)
        f.write(pack_slot(klen, dlen))
        f.write(key); f.write(value); f.flush()
        self.eod += klen + dlen + SLOT_SIZE
        self.size += klen + dlen + 24
        self.index.add_location(key, dpos)
        self.dirty = True

    def close(self):
        if self.dirty:
            self.index.save(self.f, self.eod)
        self.f.close()
