"""
A Tensor, in short, is an n-dimensional array that we can do math to.

Often, n=2, in which case the tensor would be better known as a _matrix_.
Or sometimes n=1, in which case it's a _vector_. But Divisi can also deal with
n=3 and beyond.

Divisi uses many different kinds of tensors to store data. Fundamentally, there
are DenseTensors, which are built around NumPy arrays, and DictTensors, which
store data sparsely in dictionaries; then, there are various kinds of views
that wrap around them to let you work with your data.
"""

import numpy, sys
from divisi.dict_mixin import MyDictMixin
import copy

from divisi.exceptions import DimensionMismatch

TheEmptySlice = slice(None)

def is_scalar(obj):
    return len(getattr(obj, 'shape', ())) == 0

# Subclasses of Tensor need at a bare minimum:
#  - shape
#  - __iter__()
#  - __getitem__()
# and you can probably make a faster implementation of:
#  - __len__(): number of keys
#  - iter_dim_keys()

class Tensor(object, MyDictMixin):
    """
    Tensors are the main type of object handled by Divisi. This is the base
    class for all Tensors.
    
    See [the tensor module](divisi.tensor.html) for more context.
    
    Tensors act like dictionaries whenever possible, so you can use
    dictionary methods such as `keys`, `iteritems`, and `update` as you would
    for a dictionary. They also act like Numpy arrays in some ways, but
    acting like a dictionary takes priority.
    
    Many tensor operations refer to _modes_; these are the dimensions by which
    a tensor is indexed. For example, a matrix has two modes, numbered 0 and 1.
    Mode 0 refers to rows, and mode 1 refers to columns.
    
    _Obscure terminology_: For higher-dimensional tensors, mode 2 has sometimes
    been called "tubes". Modes 3 and higher don't have names.
    """
    def __repr__(self): raise NotImplementedError
    def example_key(self):
        try:
            return self.__iter__().next()
        except StopIteration:
            return None
    
    @property
    def dims(self):
        """The number of dimensions of data in this tensor. For compatibility
        with Numpy, this is the same as `self.ndim`."""
        return self.ndim

    def __len__(self):
        """
        The number of _entries_ stored in this tensor.
        
        This does not count the implied zeros in a
        [DictTensor](divisi.tensor.DictTensor).
        
        Note that this differs from the len() of a Numpy array, which would
        instead count its number of _rows_.
        """
        # This should be implemented more efficiently by subclasses.
        return len(self.keys())

    def iter_dim_keys(self, mode):
        '''Get an iterator over the keys of a specified mode of the tensor.'''
        # Some subclasses may override this with a more efficient method
        assert(mode >= 0 and mode < self.dims)
        seen_keys = {}
        for key in self.iterkeys():
            if key[mode] not in seen_keys:
                seen_keys[key[mode]] = True
                yield key[mode]

    def dim_keys(self, mode):
        return list(self.iter_dim_keys(mode))

    def combine_by_element(self, other, op):
        '''  
        Takes two tensors and combines them element by element using `op`.
        
        For example, given input tensors _a_ and _b_, `result[i] = op(a[i],
        b[i])`, for all indices _i_ in _a_ and _b_. This operation requires _a_
        and _b_ to have the same indices; otherwise, it doesn't make any sense.
        
        (Note that for the sake of efficiency, this doesn't run op on keys that
        neither _a_ nor _b_ have.)
        '''
        if other.shape != self.shape:
            raise IndexError('Element-by-element combination requires that both matrices have the same shape (%r.element_multiply(%r)' % (self, other))

        # This assumes that having the same dimensions => having the same keys.
        res = copy.deepcopy(self)
        seen_keys = {}
        for key, value in self.iteritems():
            res[key] = op(value, other[key])
            seen_keys[key] = True

        # Run the operation for all items in the other tensor that we haven't already
        # evaluated. 
        for key, value in other.iteritems():
            if key not in seen_keys:
                res[key] = op(self[key], other[key])

        return res

    # Extraction and views
    def slice(self, mode, index):
        """
        Gets a tensor of only the entries indexed by `index` on mode `mode`.
        
        The resulting tensor will have one mode fewer than the original tensor.
        For example, a slice of a 2-D matrix is a 1-D vector.
        
        Examples:
        
        * To get a particular row of a matrix, use `matrix.slice(0, row)`.
        * To get a particular column, use `matrix.slice(1, col)`.
        """
        indices = [TheEmptySlice]*self.ndim
        indices[mode] = index
        return self[indices]

    def label(self, mode, index):
        """
        Returns the index as the 'label' for that entry, so the label for an
        unlabeled index is simply the index itself.  Added to allow certain 
        operations which work on labeled views to work on all tensors.
        """
        return index 

    def add_layer(self, cls, *a, **kw):
        """
        Layer a view onto this tensor.
        
        Tensors can be wrapped by various kinds of
        [views](divisi.tensor.View.html). This method adds a view in the
        appropriate place. In this case, this is a plain Tensor, so it simply
        passes it to the view's constructor, but other Views will override
        this to layer on the new View in the appropriate way.
        """
        return cls(self, *a, **kw)

    def unfolded(self, mode):
        """
        Get an [UnfoldedView](divisi.unfolded_view.UnfoldedView.html)
        of this tensor.
        """
        from divisi.unfolded_view import UnfoldedView
        return self.add_layer(UnfoldedView, mode)

    def labeled(self, labels):
        """
        Get a [LabeledView](divisi.labeled_view.LabeledView.html) of this
        tensor.
        
        `labels` should be a list of
        [OrderedSets](divisi.ordered_set.OrderedSet.html), one for each mode,
        which assign labels to its indices, or `None` if that mode should
        remain unlabeled.
        """
        from divisi.labeled_view import LabeledView
        return self.add_layer(LabeledView, labels)

    def normalized(self, mode=0):
        """
        Get a [NormalizedView](divisi.normalized_view.NormalizedView.html)
        of this tensor.
        """
        from divisi.normalized_view import NormalizedView
        return self.add_layer(NormalizedView, mode)

    def zero_mean_normalized(self, mode=0):
        from divisi.normalized_view import ZeroMeanView
        return self.add_layer(ZeroMeanView, mode)

    # Math
    def __add__(self, other):
        res = copy.deepcopy(self)
        res += other
        return res
        
    def __iadd__(self, other):
        if is_scalar(other):
            return self.scalar_iadd(other)
        else:
            return self.tensor_iadd(other)

    def __mul__(self, other):
        """
        This performs matrix multiplication, not elementwise multiplication.
        See the documentation for dot().
        
        If `other` is a scalar, this will perform scalar multiplication instead.
        """
        if hasattr(other, 'shape'):
            return self.dot(other)
        else:
            return self.cmul(other)
        
    def dot(self, other):
        """
        Get the product of two tensors, using matrix multiplication.
        
        When two tensors _a_ and _b_ are multiplied, the entries in the result
        come from the dot products of the last mode of _a_ with the first mode
        of _b_. So the product of a _k_-dimensional tensor with an
        _m_-dimensional tensor will have _(k + m - 2)_ dimensions.
        
        The `*` operation on two tensors uses this method.
        """
        raise NotImplementedError
    
    def cmul(self, other):
        """
        Returns the scalar product of this tensor and a scalar.
        
        The `*` operation does this when given a scalar as its second argument.
        """
        raise NotImplementedError, "Don't know how to cmul a %s" % type(self)

    def __div__(self, other):
        """
        Performs scalar division.
        
        It actually just multiplies by 1/`other`, so if you're clever enough
        you might be able to make it divide by some other kind of object.
        """
        return self * (1.0/other)

    def magnitude(self):
        '''
        Sum of squares of each element.
        '''
        mag = 0.0
        for v in self.itervalues():
            mag += v**2
        return mag
    
    def norm(self):
        """
        Calculate the Frobenius (or Euclidean) norm of this tensor.
        
        The Frobenius norm of a tensor is simply the square root of the sum of
        the squares of its elements. For a vector, this is the same as the
        Euclidean norm.
        """

    def extremes(self, n=10, top_only=False):
        """
        Extract the interesting parts of this tensor.
        
        In many applications, we're not interested in all the values in a
        particular tensor we calculated, just the ones with the highest
        magnitude. `extremes` returns the `n` highest and `n` lowest values
        in a tensor, along with their indices, in the form used by `dict.items()`.
        
        If this is a vector (as it often is), note that the indices are going
        to be tuples with one thing in them, for consistency.
        """
        pairs = sorted(self.items(), key=lambda x: x[1])
        if top_only:
            return pairs[:n]
        else:
            return pairs[:n] + pairs[-n:]

    def show_extremes(self, n=10, output=sys.stdout):
        """
        Display the `extremes` of this tensor in a nice tabular format.
        """
        extremes = self.extremes(n)
        for key, value in [x for x in extremes if x[1] < 0]:
            if len(key) == 1: key = key[0]
            if isinstance(key, unicode): key = key.encode('utf-8')
            print >> output, "%+5.5f\t%s" % (value, key)
        print >> output
        for key, value in [x for x in extremes if x[1] > 0]:
            if len(key) == 1: key = key[0]
            if isinstance(key, unicode): key = key.encode('utf-8')
            print >> output, "%+5.5f\t%s" % (value, key)


class InvalidLayeringException(StandardError):
    pass


class View(Tensor):
    """    
    A _view_ is a wrapper around a tensor that performs some operations
    differently.
    
    For almost all purposes, it acts like a Tensor itself, and
    all methods that are not specially handled by the View are passed through
    to the Tensor.
    
    This is the base class for Views, which doesn't itself do anything. One
    useful example of a View is the [LabeledView](divisi.labeled_view.LabeledView.html).
    """

    def __init__(self, tensor):
        """
        Create a new View wrapping a Tensor.
        """
        self.tensor = tensor

    def __repr__(self):
        return '<View of %s>' % repr(self.tensor)

    def __getattr__(self, name):
        '''Fall back to the tensor operation.'''
        if name.startswith('__'): raise AttributeError(name)
        return getattr(self.tensor, name)

    def __iter__(self):
        return self.tensor.__iter__()

    def add_layer(self, cls, *a, **kw):
        """
        Given a class of View, determine where it should go in the stack
        and add it as a layer there.
        """
        try:
            return cls(self, *a, **kw)
        except InvalidLayeringException:
            # Layer it below here.
            return self.layer_on(self.tensor.add_layer(cls, *a, **kw))

    def layer_on(self, tensor):
        # Just make a copy of the same class viewing the new tensor.
        # Subclasses should override this.
        return self.__class__(tensor)


class DictTensor(Tensor):
    '''
    A sparse tensor that stores data in nested dictionaries.
    
    The first level of dictionaries specifies the rows, the second level
    specifies columns, and so on for higher modes. Therefore, slicing by
    rows is the easiest to do. Despite this, you can slice on any mode,
    possibly returning a [SlicedView](divisi.sliced_view.SlicedView.html)
    for the sake of efficiency.
    
    DictTensors can save a lot of memory, can efficiently provide input
    to a Lanczos [SVD](divisi.svd.html), and work well with
    [LabeledViews](divisi.labeled_view.LabeledView.html). However, for some
    operations you may need to convert the DictTensor to a
    [DenseTensor](divisi.tensor.DenseTensor.html).
    '''
    
    # Indicates that not all possible keys will necessarily be iterated over.
    # NOTE: not used anywhere yet.
    is_sparse = True
    
    def __init__(self, ndim, default_value=0.0):
        """
        Create a new, empty DictTensor with `ndim` dimensions.
        
        Frequently, `ndim` is 2, creating a sparse matrix.
        
        default_value is the value of all unspecified entries. An SVD will
        only work when `default_value=0.0`.
        """
        self._data = {}
        self.ndim = ndim
        self._shape = [0]*ndim
        self.default_value = default_value

    def __repr__(self):
        return '<DictTensor shape: %s; %d items>' % (repr(self.shape),
                                                     len(self))

    def sparsity(self):
        '''Find out how sparse the tensor is.

        Returns (num specified elements)/(num possible elements).
        '''
        possible_elements = 1
        for dim in self.shape: possible_elements *= dim
        return float(len(self))/possible_elements
    
    def __getstate__(self):
        return dict(self.__dict__, version=1)
    
    def __setstate__(self, state):
        version = state.pop('version', None)
        if version is None:
            # Version-less loading
            self.ndim = state['ndim']
            self.default_value = state['default_value']
            self._shape = state['_shape']

            # Try to handle the non-nested format.
            data = state['_data']
            if len(data) > 0 and not isinstance(data.iterkeys().next(), int):
                print 'Attempting to load non-nested DictTensor.'
                self.update(data)
            else:
                # Should be the current format.
                self._data = data
        elif version == 1:
            self.__dict__.update(state)
        else:
            raise TypeError('unsupported version of DictTensor: '+str(version))
    
    def __len__(self):
        # This is probably going to be slow, but speed 
        # isn't too important here.
        # (if it is important, store the counter and 
        # increment the count every time an item is added)
        count = 0
        for x in self.__iter__():
            count += 1
        return count

    def __iter__(self):
        def iter_helper(dict, num_nested, key_base):
            if num_nested == 1:
                for x in dict.__iter__():
                    # TODO: is using append here too slow?
                    yield key_base + (x,)
            else:
                for key, child_dict in dict.iteritems():
                    for x in iter_helper(child_dict, num_nested - 1, key_base + (key,)):
                        yield x
        return iter_helper(self._data, self.ndim, ())

    @property
    def shape(self):
        """
        A tuple representing the shape of this tensor.
        """
        return tuple(self._shape)        

    # Support negative reference semantics
    # TODO: it would be nice if this method could be eliminated by
    # somehow making _dict_walk directly return a reference to the 
    # *value* in the final dictionary instead of the final dictionary.
    def _adjust_index(self, index, dim):
        if index < 0:
            new_index = self.shape[dim] + index
            # Don't allow the tensor to have actual negative indices
            if new_index < 0:
                raise IndexError('List index out of range')
            return new_index
        return index

    def _dict_walk(self, indices, create=False):
        # Walk nested dictionaries to get to the dictionary that
        # contains the value
        cur = self._data
        for i in xrange(0, self.ndim - 1):
            index = self._adjust_index(indices[i], i)

            if index not in cur:
                if create:
                    cur[index] = {}
                else:
                    raise KeyError
            cur = cur[index]
        return cur
        
    # Note: __contains__ is defined in terms of has_key by DictMixin

    def has_key(self, indices):
        """
        Given a tuple of _indices_, is there a specified value at those indices?
        """
        try:
            _ = self._dict_walk(indices)[self._adjust_index(indices[-1], self.ndim - 1)]
        except KeyError:
            return False
        return True

    def __getitem__(self, indices):
        """Get an item from the dictionary. Return 0.0 if no such entry exists.
        This doesn't bother to check if the element is out of bounds."""
        if not isinstance(indices, (list, tuple)):
            indices = (indices,)

        if self.dims != len(indices):
            raise DimensionMismatch

        try:
            return self._dict_walk(indices)[self._adjust_index(indices[-1], self.ndim - 1)]
            
        except TypeError: # Dictionary raises this when you try and index into it with a slice
            # Two kinds of slices: 
            # The optimal kind of slice is retrieving an entire
            # first dimension, e.g. tensor[1, :]. This resolves
            # to a dictionary lookup. 
            # The other slice is a SlicedView 
            slice = False
            opt_slice = False

            if hasattr(indices[0], 'indices'):
                slice = True
            else:
                opt_slice = True

            for index in indices[1:]:
                if hasattr(index, 'indices'):
                    slice = True
                else:
                    opt_slice = False

            if opt_slice:
                # This is sort of a hack...
                t = DictTensor(self.dims - 1)
                t._data = self._data[indices[0]]
                t._shape = self.shape[1:]
                t.default_value = self.default_value
                return t
            else:
                from divisi.sliced_view import SlicedView
                return SlicedView(self, indices)

        except KeyError:
            return self.default_value

    def __setitem__(self, indices, value):
        if not isinstance(indices, (list, tuple)):
            indices = (indices,)

        d = self.ndim
        if len(indices) != d: raise KeyError("You need %d indices" % d)

        s = self._shape
        for mode, idx in enumerate(indices):
            assert isinstance(idx, (int, long))
            if idx >= s[mode]:
                s[mode] = idx + 1

        # Walk nested dictionaries to where the item should
        # go, creating the dictionaries if necessary
        innermost_dict = self._dict_walk(indices, create=True)
        final_index = self._adjust_index(indices[-1], self.ndim - 1)
        if False:#value == self.default_value:
            if final_index in innermost_dict:
                del innermost_dict[final_index]
        else:
            innermost_dict[final_index] = value

    def __delitem__(self, indices):
        # TODO: update shape correctly.
        ndim = self.ndim
        if len(indices) != ndim: raise DimensionMismatch
        indices = [self._adjust_index(index, i) for i, index in enumerate(indices)]
        cur = self._data
        for i, index in enumerate(indices):
            if i == ndim-1:
                del cur[index]
            else:
                cur = cur[index]

    def purge(self):
        '''
        Removes any values that are specified as the default value.
        '''
        self._recursive_purge(self._data, self.ndim - 1)

    def _recursive_purge(self, data, nesting_level):
        default_value = self.default_value
        if nesting_level == 0:
            # Purge values
            to_purge = [k for k, v in data.iteritems() if v == default_value]
        else:
            to_purge = []
            for k, v in data.iteritems():
                self._recursive_purge(v, nesting_level - 1)
                if len(v) == 0:
                    to_purge.append(k)
        for k in to_purge:
            del data[k]
            

    def svd(self, *a, **kw):
        """
        Take the singular value decomposition of this tensor, using the
        Lanczos algorithm for sparse SVD.
        
        This returns an [SVDResults](divisi.svd.SVDResults.html) or
        [SVD2DResults](divisi.svd.SVD2DResults.html) object, containing the
        SVD factors of this matrix.
        """
        from divisi.svd import svd_sparse
        return svd_sparse(self, *a, **kw)

    def incremental_svd(self, *a, **kw):
        """
        Take the singular value decomposition of this tensor using an
        incremental SVD algorithm.
        """
        from divisi.svd import incremental_svd
        return incremental_svd(self, *a, **kw)

    def to_dense(self):
        """
        Convert this to a [DenseTensor](divisi.tensor.DenseTensor.html).
        """
        dense = numpy.zeros(self.shape)
        for idx, value in self.iteritems():
            dense[idx] = value
        return DenseTensor(dense)

    def cmul(self, other):
        '''Multiply by a constant'''
        res = self.__class__(ndim=self.ndim)
        for i, value in self.iteritems():
            res[i] = value * other
        return res

    # Products:
    # * dot product: vector by vector
    # * matrix product: matrix by {vector, matrix}
    # * tensor products:
    #   - tensordot: tensor by vector (param: mode)
    #   - tensor by matrix: also takes mode param
    
    def dot(self, other, mode=0, into=None):
        raise NotImplementedError
#         if into is None:
#             into = DictTensor(2) # FIXME
#         for key, val in self.iteritems():
#             pass#FIXME

    def tensordot(self, other, mode):
        shape = self.shape
        if other.ndim != 1 or shape[mode] != other.shape[0]:
            raise IndexError('Incompatible dimensions for sparse tensordot (%r.tensordot(%r, %d)' % (self, other, mode))
        result_shape = tuple(shape[:mode] + shape[mode+1:])
        result = numpy.zeros(result_shape)
        for key, val in self.iteritems():
            result[key[:mode]+key[mode+1:]] += val * other[key[mode]]
        # Check if the result is a 0-d array, in which case return a scalar
        if(result.shape == ()):
            return result[()]
        return DenseTensor(result)

    def tensor_by_matrix(self, other, mode):
        pass

    def transpose(self):
        '''
        Returns a new DictTensor that is the transpose of this tensor.

        Only works for matrices (i.e., tensor.ndim=2)
        '''
        if self.ndim != 2:
            raise DimensionMismatch('Can only transpose a 2D tensor')
        tensor = DictTensor(2)
        for key, value in self.iteritems():
            tensor[key[1], key[0]] = value

        return tensor

    @property
    def T(self):
        '''
        Returns a new DictTensor that is the transpose of this tensor.

        Only works for matrices (i.e., tensor.ndim=2)
        '''
        return self.transpose()

    def scalar_iadd(self, other):
        '''
        Add _other_ to every value in this tensor. Mutates the value of this tensor.
        '''
        self.default_value += other
        for k in self.iterkeys():
            self[k] += other
        return self
        
    def tensor_iadd(self, other):
        '''
        Element-by-element tensor addition. For all keys k in this
        tensor t and the other tensor o, set t[k] = t[k] + o[k].
        '''
        if self.ndim != other.ndim:
            raise DimensionMismatch()
        assert getattr(other, 'default_value', 0) == 0 # Lazy...
        for k, v in other.iteritems():
            if v:
                self[k] += v
        return self
        
    def __sub__(self, other):
        '''
        Element-by-element tensor subtraction. For all keys k in this
        tensor t and the other tensor o, return a new tensor r
        s.t. r[k] = t[k] - o[k].
        '''
        res = copy.deepcopy(self)
        res -= other
        return res
        
    def __isub__(self, other):
        '''
        Element-by-element tensor subtraction. For all keys k in this
        tensor t and the other tensor o, set t[k] = t[k] - o[k].
        '''
        if self.ndim != other.ndim:
            raise DimensionMismatch()
        assert getattr(other, 'default_value', 0) == 0 # Lazy...
        for k, v in other.iteritems():
            if v:
                self[k] -= v
        return self
        
    def __neg__(self):
        '''
        Return a new tensor whose values are the negation of this
        tensor's values. That is, return a tensor r s.t. for all keys
        k, r[k] = -t[k], where t is this tensor.
        '''
        res = DictTensor(self.ndim, -1*self.default_value)
        for key, value in self.iteritems():
            res[key] = -value
        return res


def outer_tuple_iterator(shape):
    idx = [0]*len(shape)
    while True:
        yield tuple(idx)
        idx[0] += 1
        # Wraparound
        cur_dim = 0
        while idx[cur_dim] >= shape[cur_dim]:
            idx[cur_dim] = 0
            cur_dim += 1
            try:
                idx[cur_dim] += 1
            except IndexError:
                raise StopIteration

def data(tensor):
    if isinstance(tensor, DenseTensor): return tensor._data
    else: return tensor

def wrap_unless_scalar(result):
    if result.shape != (): # NumPy results always have .size, and .shape.
        return DenseTensor(result)
    else:
        return result

class DenseTensor(Tensor):
    '''
    A dense tensor representation based on numpy arrays.

    DenseTensors can be created from numpy arrays and converted to
    numpy arrays. This makes DenseTensors good for performing math
    operations, since it allows you to use numpy's optimized math
    libraries.
    '''
    
    def __init__(self, data):
        """Create a DenseTensor from a numpy array."""
        self._data = data
        self.ndim = len(data.shape)


    def __repr__(self):
        return '<DenseTensor shape: %s>' % (repr(self.shape),)


    @property
    def shape(self):
        return self._data.shape


    def __getitem__(self, indices):
        return wrap_unless_scalar(self._data[indices])

    def __setitem__(self, indices, value):
        self._data[indices] = value

    def has_key(self, indices):
        # This is broken in numpy.
        # return indices in self._data
        if not isinstance(indices, (list, tuple)):
            indices = (indices,)
        if len(indices) != self.ndim:
            raise ValueError, 'Wrong number of dimensions'
        for dim, idx in enumerate(indices):
            if not (0 <= idx < self._data.shape[dim]): return False
        return True

    def __iter__(self):
        return outer_tuple_iterator(self.shape)

    def iter_dim_keys(self, dim):
        assert(dim >= 0 and dim < self.ndim)
        return xrange(0, self.shape[dim])

    # Math operations
    def dot(self, other):
        # FIXME: this will need additional cases for other types of tensors.
        return wrap_unless_scalar(numpy.dot(self._data, data(other)))

    def cmul(self, other):
        return DenseTensor(self._data * other)

    def tensordot(self, other, mode):
        '''This is almost like numpy's tensordot function, but at the moment
        only supports summing over a single mode (axis), specified by the integer
        parameter 'mode'.'''
        return wrap_unless_scalar(numpy.tensordot(self._data, data(other), [mode, 0]))

    def __add__(self, other):
        return DenseTensor(self._data + data(other))

    def scalar_iadd(self, other):
        self._data += data(other)
        return self

    def tensor_iadd(self, other):
        self._data += data(other)
        return self

    def __neg__(self):
        return DenseTensor(-self._data)

    def transpose(self):
        if self.ndim != 2:
            raise DimensionMismatch('Can only transpose a 2D tensor')
        return DenseTensor(self._data.T)
    
    @property
    def T(self):
        return self.transpose()

    def to_dense(self):
        return self

    def to_sparse(self):
        result = DictTensor(self.ndim)
        for key, val in self.iteritems():
            if val == 0: continue
            result[key] = val
        return result

    def to_array(self):
        return self._data

    def array_op(self, op, *args, **kwargs):
        """Apply a Numpy operation to this tensor, returning a new DenseTensor."""
        
        def extract_data(t):
            if isinstance(t, DenseTensor): return t.to_array()
            else: return t

        newargs = [self.to_array()] + [extract_data(a) for a in args]
        result = op(*newargs, **kwargs)
        return DenseTensor(result)


    
    # FIXME: be consistent about whether these functions return copies.
