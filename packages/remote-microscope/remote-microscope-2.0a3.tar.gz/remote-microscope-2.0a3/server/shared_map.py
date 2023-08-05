"""mems.instrument.server.shared_map

Contains helper functions for opening a shared, mmap()'ed file.  The
set_map() function stores an arbitrary Python object (anything that
can be pickled) into the shared area and read_map() reads the stored
object, or returns None if nothing seems to be stored in the file.
"""

__revision__ = "$Id: shared_map.py,v 1.2 2003/01/02 16:19:38 akuchlin Exp $"


import cPickle, mmap

mapped_file = None
map = None
def map_open ():
    global mapped_file, map
    mapped_file = open('/www/var/microscope/fake-microscope-status', 'wb+')

    # Ensure that the file is at least a page long
    mapped_file.seek(0, 2)
    if mapped_file.tell() != mmap.PAGESIZE:
        mapped_file.seek(0)
        mapped_file.write('\0' * mmap.PAGESIZE)

    map = mmap.mmap(mapped_file.fileno(),
                    mmap.PAGESIZE,
                    mmap.MAP_SHARED)
    return map

# Magic character used to indicate that there's a pickled object
# in the mmapped region.
MAGIC = '\x7f'

def set_map (object):
    S = MAGIC + cPickle.dumps(object)
    assert len(S) < mmap.PAGESIZE, "Pickled object is too large"
    map[0:len(S)] = S
    map.flush()

def read_map ():
    S = map[0:mmap.PAGESIZE]
    if S[0] != MAGIC:
        return None
    object = cPickle.loads(S[1:])
    return object

