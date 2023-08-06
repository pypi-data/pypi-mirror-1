from csc.divisi.tensor import DictTensor
from csc.divisi.ordered_set import OrderedSet
from csc.divisi.labeled_view import LabeledView
from itertools import chain, izip
import logging

def partial_list_repr(lst, max_len):
    if len(lst) <= max_len:
        return repr(lst)
    else:
        return u'[%s, ... (%d total)]' % (
            ', '.join(repr(item) for item in lst[:max_len]),
            len(lst))

class Blend(LabeledView):
    def __init__(self, tensors, weights=None, factor=None,
                 tensor_maker=DictTensor):
        '''
        Create a new Blend from a list of tensors.

        tensors : [Tensor]
          a list of tensors to blend
        weights : [float]
          how much to weight each tensor
        factor : float
          the blending factor, only valid if len(tensors)==2. weights=[1-factor, factor].
        tensor_maker : f(ndim)
          function that makes the internal numeric tensor that stores blend results. Defaults to DictTensor.

        Various optimizations are possible if keys never overlap. This
        case is automatically detected -- though it may be overly
        cautious.
        '''
        self.tensors = tensors

        # Can't call __init__ for either LabeledView or View 's init,
        # because they expect the tensor to be passed.
        #View.__init__(self)
        self._max_desired_svals = 10

        if factor is not None:
            if weights is not None:
                raise TypeError('Cannot simultaneously specify factor and weights.')
            self.factor = factor
        else:
            self.weights = weights

        self.tensor_maker = tensor_maker

    def __repr__(self):
        return u'<Blend of %s, weights=%r>' % (partial_list_repr(self.tensors, 2), self.weights)

    def __getstate__(self):
        return dict(
            version=1,
            tensors=self.tensors,
            weights=self.weights)

    def __setstate__(self, state):
        version = state.pop('version', 1)
        if version > 1:
            raise TypeError('Blend pickle was created by a newer version.')

        self.tensors = state['tensors']
        self.weights = state['weights']
            
        
    def _set_tensors(self, tensors):
        self._tensors = tuple(tensors)
        self.ndim = ndim = tensors[0].ndim
        if not all(tensor.ndim == ndim for tensor in tensors):
            raise TypeError('Blended tensors must have the same dimensionality.')

        logging.info('Blend: Making ordered sets')
        self._labels = labels = [OrderedSet() for _ in xrange(ndim)]
        self.label_overlap = label_overlap = [0]*ndim

        for tensor in self._tensors:
            for dim, label_list in enumerate(labels):
                for key in tensor.label_list(dim):
                    # XXX(kcarnold) This checks containment twice.
                    if key in label_list: label_overlap[dim] += 1
                    else: label_list.add(key)

        self._shape = tuple(map(len, labels))
        self._keys_never_overlap = not all(label_overlap)

        # Invalidate other data
        self._weights = self._tensor = self._svals = None

    tensors = property(lambda self: self._tensors, _set_tensors)

    @property # necessary because it's a property on the parent class
    def shape(self): return self._shape

    def tensor_svals(self, tensor_idx, num_svals):
        '''
        Get the top num_svals singular values for one of the input tensors.
        '''
        if self._svals is None or num_svals > self._max_desired_svals:
            logging.info('Blend: computing by-tensor SVDs')
            self._max_desired_svals = max(self._max_desired_svals, num_svals)
            self._svals = [tensor.svd(k=self._max_desired_svals).svals.values()
                           for tensor in self._tensors]
        return self._svals[tensor_idx][:num_svals]
    
    def rough_weight(self, tensor_idx):
        '''
        Compute the rough weight (reciprocal of sval 0) for one of the input tensors.
        '''
        return 1.0/self.tensor_svals(tensor_idx, 1)[0]
    
    def _set_weights(self, weights):
        if weights is None:
            # Rough blend
            self._weights = [self.rough_weight(tensor) for tensor in xrange(len(self.tensors))]
            self.normalize_weights()
        else:
            # Explicit
            if weights == self._weights: return # If same, no-op.
            if len(weights) != len(self._tensors):
                raise TypeError('Weight length mismatch')
            self._weights = tuple(weights)
        self._tensor = None # invalidate the tensor

    weights = property(lambda self: self._weights, _set_weights)

    def _get_factor(self):
        if len(self._tensors) != 2:
            raise TypeError('Only blends of 2 tensors have a single factor.')
        return self._weights[1]
    def _set_factor(self, factor):
        if len(self._tensors) != 2:
            raise TypeError('Only blends of 2 tensors have a single factor.')
        if not 0 <= factor <= 1:
            raise ValueError('factor must be between 0 and 1.')
        self.weights = [1.0-factor, factor]
    factor = property(_get_factor, _set_factor)
    
    def normalize_weights(self):
        '''
        Make the weights sum to 1.
        '''
        logging.info('Blend: Normalizing weights')
        scale = 1.0 / float(sum(self._weights))
        self._weights = tuple(factor * scale for factor in self._weights)

    @property
    def tensor(self):
        if self._tensor is None:
            logging.info('Blend: building combined tensor.')
            labels = self._labels
            tensor = self._tensor = self.tensor_maker(ndim=self.ndim)

            if self._keys_never_overlap:
                logging.info('Blend: fast-merging.')
                tensor.update((tuple(label_list.index(label) for label_list, label in izip(labels, key)), val)
                              for key, val in self._fast_iteritems())
            else:
                for factor, cur_tensor in zip(self._weights, self._tensors):
                    logging.info('Blend: slow-merging %r' % cur_tensor)
                    for key, val in cur_tensor.iteritems():
                        tensor.inc(tuple(label_list.index(label) for label_list, label in izip(labels, key)), factor*val)
        
        return self._tensor

    # Optimizations
    def __iter__(self):
        if self._keys_never_overlap:
            return chain(*self.tensors)
        else:
            return (self.labels(idx) for idx in self.tensor)

    def _fast_iteritems(self):
        labels = self._labels
        return ((key, factor*val)
                for factor, cur_tensor in zip(self._weights, self._tensors)
                for key, val in cur_tensor.iteritems())
    
    def iteritems(self):
        if self._keys_never_overlap:
            return self._fast_iteritems()
        else:
            return super(Blend, self).iteritems()

        
    def __len__(self):
        if self._keys_never_overlap:
            return sum(map(len, self.tensors))
        else:
            return len(self.tensor)

    # Blend analysis utilities
    def predicted_svals(self, num=50, for_each_tensor=None, track_origin=False):
        '''
        Predict the resulting singular values by multiplying the
        original singular values by the corresponding blend factor and
        sorting.

        Parameters
        ----------
        num : int
            Total number of svals to return
        for_each_tensor : int, optional
            number of singular values to consider for each tensor. If this is
            too small, some extraneous svals may make it into the top `num`.
            If not given, values `num` are considered.
        track_origin : boolean, default False
            If true, returns a list of (sval, tensor_idx).
        '''
        if for_each_tensor is None: for_each_tensor = num
        if track_origin:
            elt = lambda sval, factor, idx: (sval*factor, idx)
        else:
            elt = lambda sval, factor, idx: sval*factor
        svals = [elt(sval, factor, idx)
                 for idx, factor in enumerate(self.weights)
                 for sval in self.tensor_svals(idx, for_each_tensor)]
        svals.sort(reverse=True)
        return svals[:num]
        
    def total_veering(self, num=50, for_each_tensor=None, actual_svals=None):
        '''
        Calculate total veering.

        If you already have the singular values, pass them in as a list / array
        for a faster result.
        '''
        
        predicted_svals = self.predicted_svals(num, for_each_tensor)
        if actual_svals is None:
            logging.info('Blend: computing actual singular values')
            actual_svals = self.tensor.svd(num).svals.values()
        num = min(num, len(actual_svals))
        return sum((actual_svals[idx] - predicted_svals[idx][0])**2
                   for idx in xrange(num))

    def total_veering_at_factor(self, factor, **kw):
        "Calculates the total veering at a particular factor."
        return self.at_factor(factor).total_veering(**kw)

    def predicted_svals_at_factor(self, factor, **kw):
        return self.at_factor(factor).predicted_svals(**kw)

    def svals_at_factor(self, factor, *a, **kw):
        return self.at_factor(factor).svd(*a, **kw).svals.values()

    def at_factor(self, factor):
        # FIXME: take advantage of the fact that the labels don't change.
        return Blend(self.tensors, factor=factor)
        
    def compressed_svd_u(self, k=100):
        """
        Not done yet. --Rob
        """
        labelset = set()
        for t in self.weights:
            labelset += set(t.label_list(0))
        ulabels = OrderedSet(list(labelset))
        svds = [t.svd(k) for t in self.weights]
