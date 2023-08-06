from divisi.ordered_set import OrderedSet, IdentitySet
from divisi.tensor import View, TheEmptySlice
import copy
import heapq
from operator import itemgetter

try:
    all
except NameError:
    from divisi.util import all

def indexable_set(x, dim):
    if x is None:
        return IdentitySet(dim)
    if getattr(x, 'index_is_efficient', False):
        return x
    return OrderedSet(x)

class LabelingMixin(object):
    def vector_keys(self):
        """
        Like keys(), but returns plain labels instead of singletons of labels
        for a 1st-order tensor.
        """
        if self.tensor.ndim == 1: return self.label_lists()[0]
        else: return self.keys()


    def label(self, mode, index):
        """
        Get the label for a particular place in the matrix -- that is,
        a given index along a given mode.
        
        The inverse of this function is index().
        """
        return self._labels[mode][index]
    
    def row_label(self, index): return self.label(0, index)
    def column_label(self, index): return self.label(1, index)
    def labels(self, indices):
        return tuple([self.label(mode, index) for mode, index in enumerate(indices)])
    def label_lists(self):
        """
        A list of all label lists for this tensor, in order by mode.
        """
        return self._labels


    def label_list(self, mode):
        """
        Get the label list for a particular mode.
        """
        return self._labels[mode]

    label_sets = label_lists

    def index(self, mode, label, create=False):
        """
        Find the index, along a given mode, that is labeled with a given label.
        
        The inverse of this function is label().
        """
        if create:
            return self._labels[mode].add(label)
        else:
            return self._labels[mode].index(label)

    def row_index(self, index): return self.label(0, index)
    def column_index(self, index): return self.label(1, index)

    def indices(self, labels):
        '''
        Look up the underlying tensor keys for a tuple of labels.
        '''
        return tuple([self.index(mode, labels[mode])
                     for mode in xrange(len(labels))])

    def slice_index(self, mode, theslice, create=False):
        if theslice == TheEmptySlice: return TheEmptySlice
        return self.index(mode, theslice, create)

    def slice_indices(self, slicelabels, create=False):
        return tuple(self.slice_index(mode, slicelabels[mode], create)
                     for mode in xrange(len(slicelabels)))
    

class LabeledView(LabelingMixin, View):
    '''
    A LabeledView creates a layer of labels (probably strings) that
    map to the numerical keys of the underlying tensor.
    '''

    # Flag to the layering procedure that this view takes numeric inputs and maps
    # them to non-numeric outputs.
    input_is_numeric = True
    output_is_numeric = False

    def __init__(self, tensor, label_lists=None):
        View.__init__(self, tensor)
        shape = tensor.shape
        if label_lists is None:
            label_lists = [None]*self.tensor.ndim

        if tensor.ndim != len(label_lists):
            raise IndexError('Number of label lists (%d) does not match number of dimensions (%s)', (len(label_lists), tensor.ndim))

        self._labels = [indexable_set(l, shape[mode])
                        for mode, l in enumerate(label_lists)]

        #for i in xrange(self.ndim):
        #    pass
        # FIXME: actually check labels. We run into trouble when the underlying
        # thing is a LabeledView. Perhaps we subclass LabeledView for that?
#            if len(self._labels[i]) != shape[i]:
#                raise IndexError("Bad labels for dimension %d" % i)


    def __repr__(self):
        return '<LabeledView of %r, keys like: %r>' % (
            self.tensor, self.example_key())


    @property
    def shape(self):
#        assert self._label_dims_correct()
        return self.tensor.shape

    def _label_dims_correct(self):
        shape = self.tensor.shape
        for mode, label in enumerate(self._labels):
            if isinstance(label, IdentitySet):
                continue
            if len(label) != shape[mode]:
                return False
        return True

    
    def transpose(self):
        if self.tensor.ndim != 2:
            raise TypeError('Only 2D tensors can be transposed.')
        return LabeledView(self.tensor.transpose(), [self._labels[1], self._labels[0]])
    
    @property
    def T(self):
        return self.transpose()

    def __iter__(self):
        return (self.labels(idx) for idx in self.tensor.__iter__())

    def iter_dim_keys(self, dim):
        for label in self.label_list(dim):
            yield label

    def dim_keys(self, mode):
        return self.label_list(mode)

    def unfolded_labels(self, mode):
        '''Return the set of labels for the remaining dimensions if this view were to be
        unfolded at the given mode.'''
        if mode >= self.tensor.ndim:
            raise IndexError('Dimension out of range.')
        if self.tensor.ndim == 2:
            if mode == 0: return self._labels[1]
            else: return self.labels[0]
        # FIXME: finish this

    # __contains__ is defined in terms of has_key by MyDictMixin (see View / Tensor)
    def has_key(self, labels):
        # Handle single dimensions
        if not isinstance(labels, (list, tuple)):
            labels = (labels,)

        # Compute indices
        try:
            indices = self.slice_indices(labels)
        except KeyError:
            return False

        return indices in self.tensor
        
    def __getitem__(self, labels):
        # Handle single dimensions
        if not isinstance(labels, (list, tuple)):
            labels = (labels,)

        # Compute indices
        try:
            indices = self.slice_indices(labels)
        except KeyError:
            if hasattr(self.tensor, 'default_value'):
                return self.tensor.default_value
            else: raise

        # Extract data
        data = self.tensor[indices]

        # Return a plain number if all dimensions are specified.
        if len(getattr(data, 'shape', ())) == 0:
            return data

        # Compute new labels.
        labellists = [self._labels[mode] for mode, idx in enumerate(indices)
                      if idx == TheEmptySlice]
        return LabeledView(data, labellists)

    def __setitem__(self, labels, value):
        if not isinstance(labels, (list, tuple)):
            labels = (labels,)

        d = self.tensor.ndim
        if len(labels) != d: raise KeyError("You need %d indices" % d)

        # Make sure we have ordered numbers for each label
        for mode in xrange(d):
            self._labels[mode].add(labels[mode])
        
        self.tensor[self.indices(labels)] = value
        # FIXME: This doesn't work for slices. But we had never tested it for slices.


    ### Math operations
    def scalar_iadd(self, other):
        self.tensor += other
        return self

    def tensor_iadd(self, other):
        if not hasattr(other, 'label_list'):
            raise TypeError('Only labeled views can be added to labeled views.')
        if self.tensor.ndim != other.ndim:
            raise ValueError('Number of dimensions do not match.')

        # Adding the wrapped tensors directly is only valid if the labels
        # match up.
        if all(self.label_list(mode) == other.label_list(mode)
               for mode in xrange(self.ndim)):
            self.tensor += other.tensor
            return self

        # Otherwise, do something simple.
        for k, v in other.iteritems():
            if v:
                self[k] = self.get(k, 0) + v
        return self
        
    def __neg__(self):
        return self.layer_on(-self.tensor)

    def dot(self, other):
        """
        For first-order tensors, this is a dot product. For second-order,
        it performs matrix multiplication. Like Numpy matrices (not arrays),
        this is the operation performed by the * operator.
        """
        assert self.shape[-1] == other.shape[0]
        label_lists = [self.label_list(i) for i in xrange(self.ndim-1)]
        if hasattr(other, 'label_list'):
            data = self.tensor.dot(other.tensor)
            label_lists += [other.label_list(i) for i in xrange(1, other.ndim)]
        else:
            data = self.tensor.dot(other)
            assert isinstance(self.label_list(self.tensor.ndim-1), IdentitySet)
            label_lists += [None]*(len(other.shape)-1)

        if len(label_lists) == 0: return float(data)
        return LabeledView(data, label_lists)


    def tensordot(self, other, mode):
        shape = self.shape
        if other.ndim != 1 or shape[mode] != other.shape[0]:
            raise IndexError('Incompatible dimensions for sparse tensordot (%r.tensordot(%r, %d)' % (self, other, mode))

        # The operation will collapse the specified mode. Get the remaining labels.
        label_sets = self._labels[:mode] + self._labels[mode+1:]

        if hasattr(other, 'label_list'):
            if self._labels[mode] != other.label_list(0):
                raise IndexError("Labels for mode %d of %r don't match labels for the vector %r." % (mode, self, other))
            data = self.tensor.tensordot(other.tensor, mode)
        else:
            if not isinstance(self._labels[mode], IdentitySet):
                import warnings
                warnings.warn("Mode %d of %r is labeled, but the vector %r is not." % (mode, self, other), RuntimeWarning)
            data = self.tensor.tensordot(other, mode)

        if len(label_sets) == 0: return float(data)
        return LabeledView(data, label_sets)


    def cmul(self, other):
        return self.layer_on(self.tensor.cmul(other))


    def svd(self, *a, **kw):
        if self.ndim == 2:
            _svd = self.tensor.svd(*a, **kw)
            return LabeledSVD2DResults.layer_on(_svd, self)
        else:
            # The unfoldings will take care of labeling.
            from divisi.svd import svd_sparse
            return svd_sparse(self, *a, **kw)

    def incremental_svd(self, *a, **kw):
        if self.ndim == 2:
            _svd = self.tensor.incremental_svd(*a, **kw)
            return LabeledSVD2DResults.layer_on(_svd, self)
        else:
            raise NotImplementedError("Incremental SVDs can only be run on 2d tensors!")        

    ### Views
    def layer_on(self, tensor):
        return LabeledView(tensor, self._labels)

    def zero_mean_normalized(self, mode=0, prefix='-'):
        # This is a special case, since we must duplicate labels
        new_tensor = self.tensor.zero_mean_normalized(mode=mode)

        new_labels = copy.deepcopy(self._labels)
        # Duplicate labels, preserving the property that 
        # index(label)[mode] = index(prefix  label)[mode] - self.tensor.shape[mode]
        for i in xrange(self.tensor.shape[mode]):
            l = self.label(mode, i)
            new_labels[mode].add(prefix + l)

        return LabeledView(new_tensor, new_labels)
        
    
    def array_op(self, op, labels=None, *args, **kwargs):
        """
        Apply an operation to the tensor inside (which must be a
        DenseTensor), and return the result wrapped in the same view.
        
        This assumes the resulting tensor has the same shape, unless
        you provide a labels= parameter.
        """
        inner = self.tensor.array_op(op, *args, **kwargs)
        if labels is None: labels = self._labels
        return inner.labeled(labels)

    
    ### Utility extractions
    def vector_to_dict(self):
        '''Like #items for 1D tensors, but uses indices directly instead of
        one-item tuples.'''
        if self.ndim != 1:
            raise ValueError("vector_to_dict only works for 1D tensors. Take a slice first.")
        labels = self.label_list(0)
        return dict((labels[i], float(self.tensor[i])) for i in xrange(self.shape[0]))

    def top_items(self, n=10, largest=True, key=None, abs_val=None):
        '''
        For each of the top n items with greatest values, return a pair of
        the item and its value.

        Parameters:
         n: number of items to return
         largest: True (default) to get the largest items, else get the smallest
         abs_val: sort by absolute value instead
        '''
        if abs_val is not None:
            import warnings
            warnings.warn(DeprecationWarning('abs_val is deprecated. use key=abs.'))
            assert key is None
            key = abs
            
        #If the tensor is 1D, gives indices instead of one-item tuples.
        #Always expresses the output in floats directly.'''
        if key is not None:
            extreme_key = lambda ent: key(ent[1])
        else:
            extreme_key = itemgetter(1)

        find_extreme = heapq.nlargest if largest else heapq.nsmallest
        items = find_extreme(n, self.iteritems(), key=itemgetter(1))
        if self.ndim == 1:
            return [(k[0], float(v)) for k, v in items]
        else:
            return [(k, float(v)) for k, v in items]


    def to_dense(self):
        '''Change the underlying representation to a dense tensor.'''
        return LabeledView(self.tensor.to_dense(), self._labels)
        



from divisi.svd import SVD2DResults
class LabeledSVD2DResults(SVD2DResults):
    @classmethod
    def layer_on(cls, results, src):
        return cls(
            LabeledView(results.u, [src._labels[0], None]),
            LabeledView(results.v, [src._labels[1], None]),
            results.svals)

