from csc.divisi.tensor import Tensor
import tables

# Things to be careful about:
# - what to do when there's more than one of an index in the table for some reason
#   (this may be a useful case for adding -- pull in data fast, then do one summing pass)
# - "Note that, from PyTables 1.1 on, you can nest several iterators over the same table."
#   (from the user guide) -- looks worrisome. May want to avoid returning generators.

def _colunm_name_for_index(idx):
    return 'i%d' % (idx,)

class PyTTensor(Tensor):
    is_sparse = True

    def __init__(self, ndim, filename, name='tensor', where=None):
        self.ndim = ndim
        self.filename = filename
        self._shape = [0]*ndim

        # Open the file, if necessary.
        self.fileh = fileh = \
            tables.openFile(filename, 'a') if isinstance(filename, basestring) else filename
        if where is None: where = fileh.root

        # Create the table... (should be only if necessary)
        desc = dict((_colunm_name_for_index(idx), tables.UInt32Col()) for i in range(ndim))
        desc['v'] = tables.Float64Col()
        desc = type('PyT', (tables.IsDescription,), desc)
        self.table = fileh.createTable(where, name, desc)

        # Precompute the query for getting a single item.
        self._getitem_key = ' & '.join(_colunm_name_for_index(idx)+'=%d' for idx in range(ndim))
        
    def __repr__(self):
        return '<PyTTensor shape: %r; %d items>' % (self.shape, len(self))

    # Low-level API
    def _unconditional_append(self, entries):
        for key, val in entries:
            row = self.table.row
            for idx, ent in enumerate(key):
                row['i'+str(idx)] = ent
            row['v'] = val
            row.append()

    def __getitem__(self, key):
        return self.table.readWhere(self._getitem_key % key)

    def __setitem__(self, key, val):
        if key in self:
            self.update_existing_key(key, val)
        else:
            self._unconditional_append([(key, val)])
    
