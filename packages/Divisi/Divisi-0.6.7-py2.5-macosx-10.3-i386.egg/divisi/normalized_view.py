from divisi.tensor import View, InvalidLayeringException

EPSILON = 0.000000001   # for floating point comparisons

from numpy import zeros
from math import sqrt, log

class NormalizedView(View):
    '''A normalized view of a tensor.

    The norm is a Euclidean norm (sqrt of sum of squares) over one dimension.

    To demonstrate its use, let's create a demonstration ordinary tensor:
    >>> a = SparseLabeledTensor(ndim=2)
    >>> for fruit in ['apple', 'banana', 'pear', 'peach']:
    ...     for color in ['red', 'yellow', 'green']:
    ...        a[fruit, color] = 1

    Then we can make the normalized view.
    >>> an = NormalizedView(a, mode=0)

    Getting at item returns the normalized value. The dimension
    along which it normalizes is specified in the constructor;
    it defaults to 0 (the first dimension).

    >>> an['apple', 'red'] * sqrt(3)
    1.0

    You can also specify a base norm that is added to every vector.
    It is as if every vector had an extra element of base**2. It
    defaults to 0.
    >>> an.base
    0.0
    >>> an.base = 1
    >>> an['apple', 'red'] * sqrt(4)
    1.0
    '''
    # Specify that this view maps numeric labels to (the same) numeric labels.
    input_is_numeric = True
    output_is_numeric = True
    

    def __init__(self, tensor, mode=0):
        '''tensor: tensor to view.
        mode: which mode to normalize over (0 = rows, 1 = columns, etc.)
        '''
        if len(tensor) == 0:
            raise ValueError('Tensor ' + repr(tensor) + ' is empty.')
        
        # The underlying tensor must be numeric.
        for part in tensor.example_key():
            if not isinstance(part, (int, long)):
                raise InvalidLayeringException

        View.__init__(self, tensor)
        self.base = 0.0
        self._normalize_mode = mode

        self.refresh_norms()
        # FIXME: register change notification.

    def __repr__(self):
        return '<%s of %r, mode=%r, base=%s>' % (
            self.__class__.__name__, self.tensor, self._normalize_mode, self.base)

    @property
    def normalize_mode(self):
        return self._normalize_mode

    @property
    def norms(self):
        return self._norms
        
    def refresh_norms(self):
        tensor = self.tensor
        mode = self._normalize_mode
        if not isinstance(mode, list): modes = [mode]
        else: modes = mode
        norms = [zeros((tensor.shape[mode],)) for mode in modes]
        for key, value in self.tensor.iteritems():
            for mode in modes:
                norms[modes.index(mode)][key[mode]] += value*value
        self._norms = norms

    def update_norm(self, indices, prev, current):
        mode = self._normalize_mode
        if not isinstance(mode, list): modes = [mode]
        else: modes = mode
        # Handle growing the norms array.
        for mode in modes:
                index = indices[mode]
                i_mode = modes.index(mode)
                while index >= self._norms[i_mode].shape[0]:
                    self._norms[i_mode].resize((2*self._norms[i_mode].shape[0],))
                self._norms[i_mode][index] += (current*current - prev*prev)

    def item_changed(self, indices, oldvalue, newvalue):
        self.update_norm(indices, oldvalue, newvalue)

    def __getitem__(self, indices):
        if not isinstance(indices, (list, tuple)):
            indices = (indices,)
        mode = self._normalize_mode
        if not isinstance(mode, list): modes = [mode]
        else: modes = mode
        norm = self.base
        for i, i_mode in [(indices[mode], modes.index(mode)) for mode in modes]:
            norm += self._norms[i_mode][i]
        data = self.tensor[indices]
        #if abs(data) < EPSILON and abs(norm) < EPSILON: return 0.0
        return data / sqrt(norm)

    def __setitem__(self, unused, _):
        raise TypeError('Normalized views are read-only.')


    ### Extraction and views
    def normalized(self, mode=0):
        return NormalizedView(self.tensor, mode)

    def unnormalized(self):
        return self.tensor

    def layer_on(self, tensor):
        # FIXME: This looks shady.
        return NormalizedView(self.tensor, self.mode)

    def svd(self, *a, **kw):
        from divisi.svd import svd_sparse
        return svd_sparse(self, *a, **kw)
    
    # All other operations fall back to the tensor.


class AvgNormalizedView(NormalizedView):
    '''A NormalizedView that makes the average to be zero, instead of using a Euclidean norm.'''    
    def refresh_norms(self):
        tensor = self.tensor
        mode = self._normalize_mode
        if not isinstance(mode, list): modes = [mode]
        else: modes = mode
        norms = [zeros((tensor.shape[mode],2)) for mode in modes]
        for key, value in self.tensor.iteritems():
            for mode in modes:
                # sum, count
                norms[modes.index(mode)][key[mode]][0] += value
                norms[modes.index(mode)][key[mode]][1] += 1
        self._norms = norms

    def update_norm(self, indices, prev, current):
        raise NotImplementedError

    def __getitem__(self, indices):
        mode = self._normalize_mode
        if not isinstance(mode, list): modes = [mode]
        else: modes = mode
        norm = self.base
        for i, i_mode in [(indices[mode], modes.index(mode)) for mode in modes]:
            norm += self._norms[i_mode][i][0] / self._norms[i_mode][i][1]
        data = self.tensor[indices]
        if abs(data) < EPSILON and abs(norm) < EPSILON: return 0.0
        return data - norm


class TfIdfView(NormalizedView):
    '''
    Normalizes by the total frequency (TF-IDF).
    '''
    def __init__(self, tensor):
        super(TfIdfView, self).__init__(tensor, 0) # We only support mode 0.

    def refresh_norms(self):
        tensor = self.tensor
        terms, documents = self.tensor.shape
        counts_for_document = zeros((documents,))
        num_docs_that_contain_term = zeros((terms,1))
        for key, value in self.tensor.iteritems():
            term, document = key
            counts_for_document[document] += value
            num_docs_that_contain_term[term] += 1
            
        self.counts_for_document = counts_for_document
        self.num_docs_that_contain_term = num_docs_that_contain_term 
        self.num_documents = self.tensor.shape[1]
       
    def update_norm(self, indices, prev, current):
        raise NotImplementedError

    def tf(self, term, document):
        return self.tensor[term, document] / self.counts_for_document[document]

    def idf(self, term):
        return log(self.num_documents / self.num_docs_that_contain_term[term])
    
    def __getitem__(self, indices):
        term, document = indices
        return self.tf(term, document) * self.idf(term)

class ZeroMeanView(View):   
    ''' 
    This normalized view makes the mean of all values along the
    specified mode equal to 0. The view accomplishes this by
    "mirroring" the keys along the specified mode such that each key
    along the mode has a "mirror" key. The "mirror" key has value -1 *
    (value of original key).

    For example, the tensor
    0  1  2  4
    0  0  3  0

    mirrored along mode 0 is:
    0  1  2  4 
    0  0  3  0
    0 -1 -2 -4
    0  0 -3  0
    '''
    def __init__(self, tensor, mode):
        self.duplicate_mode = mode
        self.tensor = tensor
        self.tensor_mode_len = tensor.shape[mode]

    def _normalize_key(self, indices):
        # 1d tensors don't take tuple indices...
        if not (isinstance(indices, list) or isinstance(indices, tuple)):
            indices = [indices]

        # Indices larger than the dimension size get wrapped around         
        if indices[self.duplicate_mode] >= self.tensor_mode_len:
            indices = list(indices)
            indices[self.duplicate_mode] = indices[self.duplicate_mode] - self.tensor_mode_len

        return tuple(indices)

    def _duplicate_key(self, indices):
        # 1d tensors don't take tuple indices...
        if not (isinstance(indices, list) or isinstance(indices, tuple)):
            indices = [indices]
        indices = list(indices)
        indices[self.duplicate_mode] = indices[self.duplicate_mode] + self.tensor_mode_len
        return tuple(indices)

    def _is_duplicate_key(self, indices):
        # 1d tensors don't take tuple indices...
        if not (isinstance(indices, list) or isinstance(indices, tuple)):
            indices = [indices]

        return indices[self.duplicate_mode] >= self.tensor_mode_len

    def __getitem__(self, indices):
        if self._is_duplicate_key(indices):
            return -1 * self.tensor[self._normalize_key(indices)]
        else:
            return self.tensor[indices]

    def __len__(self):
        # The tensor duplicates all keys, so there are twice as many
        # in this tensor as there are in the base tensor
        return 2*len(self.tensor)

    @property
    def shape(self):
        s = list(self.tensor.shape)
        s[self.duplicate_mode] *= 2
        return tuple(s)

    def has_key(self, key):
        return self._normalize_key(key) in self.tensor

    def __iter__(self):
        for k in self.tensor:
            yield k
            yield self._duplicate_key(k)

    def __repr__(self):
        return '<ZeroMeanView of %r, duplicating mode: %r>' % (
            self.tensor, self.duplicate_mode)

    def svd(self, *a, **kw):
        from divisi.svd import svd_sparse
        return svd_sparse(self, *a, **kw)

    def incremental_svd(self, *a, **kw):
        """
        Take the singular value decomposition of this tensor using an
        incremental SVD algorithm.
        """
        from divisi.svd import incremental_svd
        return incremental_svd(self, *a, **kw)


