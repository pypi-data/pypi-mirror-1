from csc.divisi.tensor import Tensor
import sqlite3

class SQLTensor(Tensor):
    is_sparse = True

    def __init__(self, ndim, file=':memory:', sqlite3_opts=None):
        self.ndim = ndim
        self.file = file
        self._shape = [0]*ndim

        if sqlite3_opts is None: sqlite3_opts = {}
        sqlite3_opts.setdefault('detect_types', sqlite3.PARSE_DECLTYPES)

        self.conn = sqlite3.connect(file, **sqlite3_opts)
        self.cursor = self.conn.cursor()

        # Create the data table.
        self._gogosql('CREATE TABLE data (%s, val FLOAT, PRIMARY KEY (%s));' % (
                ','.join('k%d INTEGER'%i for i in xrange(ndim)),
                ','.join('k%d'%i for i in xrange(ndim))))

        self.insert_sql = 'INSERT OR REPLACE INTO data VALUES (%s)' % ','.join('?'*(ndim+1))
        self.getone_sql = 'SELECT val FROM data WHERE ' + (
            ' AND '.join('k%d=?'%i for i in xrange(ndim)))

    def _gogosql(self, sql, *a, **kw):
        #print sql
        return self.cursor.execute(sql, *a, **kw)

    def __repr__(self):
        return '<SQLTensor shape: %r; %d items>' % (self.shape, len(self))

    def __getitem__(self, keys):
        res = self._gogosql(self.getone_sql, keys).fetchall()
        if len(res) == 0:
            raise KeyError, keys
        if len(res) != 1:
            raise RuntimeError, 'Somehow we got non-unique entries.'
        return res[0][0]

    def __setitem__(self, key, val):
        self._gogosql(self.insert_sql, key+(val,))
