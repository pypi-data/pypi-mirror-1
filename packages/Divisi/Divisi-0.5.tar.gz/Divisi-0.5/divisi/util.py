import os.path
import cPickle as pickle
import gzip
from divisi.labeled_tensor import SparseLabeledTensor
from functools import wraps

def get_picklecached_thing(filename, func, name=None):
    if name is None: name = filename
    if filename.endswith('.gz'): opener = gzip.open
    else: opener = open
    try:
        f = opener(filename, 'rb')
        print 'Loading', name
        result = pickle.load(f)
        f.close()
    except IOError:
        print 'Computing', name
        result = func()
        print 'Saving', name
        f = opener(filename, 'wb')
        pickle.dump(result, f, -1)
        f.close()
    return result

path_join = os.path.join

class Picklr(object):
    def __init__(self, dir):
        self._dir = os.path.abspath(dir)
        self._cache = {}

    def __filename_for_key(self, key):
        return path_join(self._dir, key+'.pkl')
    
    def __getattr__(self, key):
        assert not key.startswith('_')
        if key not in self._cache:
            f = open(self._filename_for_key(key),'rb')
            self._cache[key] = pickle.load(f)
            f.close()

        return self._cache[key]

    def __setattr__(self, key, val):
        if key.startswith('_'):
            return super(Picklr, self).__setattr__(key, val)
        
        self._cache[key] = val
        f = open(self.__filename_for_key(key), 'wb')
        pickle.dump(val, f, -1)
        f.close()

    def __delattr__(self, key):
        del self._cache[key]
        os.remove(self.__filename_for_key(key))

    def __dir__(self):
        # This is only useful for Python 2.6+.
        return [filename[:-4] for filename in os.listdir(self._dir)
                if filename.endswith('.pkl')]

    
class pcache(object):
    '''Takes a thunk and pickle-caches it.

    >>> @pcache('test.pkl')
    ... def f():
    ...   return 1
    ...
    >>> f()
    ... 1
    >>> pickle.load(open('test.pkl','rb'))
    ... 1
    '''
    def __init__(self, filename, name=None):
        self.filename = filename
        if name is None: name = filename
        self.name = name
        self.cache = None

    def __call__(self, thunk):
        @wraps(thunk)
        def f():
            if self.cache is None:
                self.cache = get_picklecached_thing(self.filename, thunk, self.name)
            return self.cache
        return f


###
### Old blending stuff
###
    
def find_factor_from_SVD(t1, t2):
    sigma1 = t1.svals[0:10]
    a = sigma1[0]
    sigma2 = t2.svals[0:10]
    b = sigma2[0]
    return float(a/(a+b))

def normalize_and_copy_three(tensor):
    newt = SparseLabeledTensor(ndim=3)
    newt.update(tensor.normalized())
    return newt

def normalize_and_copy(tensor):
    newt = SparseLabeledTensor(ndim=2)
    newt.update(tensor.normalized())
    return newt

def autoblend2(tensor1, tensor2, svd1, svd2):
    if svd1 is None: svd1 = tensor1.svd(k=35)
    if svd2 is None: svd2 = tensor2.svd(k=35)
    factor = find_factor_from_SVD(svd1, svd2)
    print "The factor is: ", factor

    blend = tensor1*(1-factor) + tensor2*factor
    return blend

def autoblend3(tensor1, tensor2, svd1, svd2):
    if svd1 is None: svd1 = tensor1.svd(k=35)
    if svd2 is None: svd2 = tensor2.svd(k=35)
    u0 = find_factor_from_SVD(svd1.r[0], svd2.r[0])
    u1 = find_factor_from_SVD(svd1.r[1], svd2.r[1])
    u2 = find_factor_from_SVD(svd1.r[2], svd2.r[2])
    print "The factors are: ", u0, u1, u2
    factor = (u0 + u1 + u2)/3.00

    tensor1 = normalize_and_copy_three(tensor1)
    tensor2 = normalize_and_copy_three(tensor2)

    blend = tensor1*(1-factor) + tensor2*factor

    return blend

try:
    all
except NameError:
    def all(seq):
        for item in seq:
            if not item: return False
        return True
