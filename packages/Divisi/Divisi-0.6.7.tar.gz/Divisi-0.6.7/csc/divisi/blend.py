from csc.divisi.tensor import DictTensor
from csc.divisi.ordered_set import OrderedSet
from csc.divisi.labeled_view import LabeledView
from itertools import chain, izip
import logging
from math import sqrt

def partial_list_repr(lst, max_len):
    if len(lst) <= max_len:
        return repr(lst)
    else:
        return u'[%s, ... (%d total)]' % (
            ', '.join(repr(item) for item in lst[:max_len]),
            len(lst))

class Blend(LabeledView):
    def __init__(self, tensors, weights=None, factor=None, k_values=1, svals=None, auto_build_tensor=True):
        '''
        Create a new Blend from a list of tensors.

        tensors : [Tensor]
          a list of tensors to blend
        weights : [float]
          how much to weight each tensor
        factor : float
          the blending factor, only valid if len(tensors)==2. weights=[1-factor, factor].
        k_values : int or [int]
          number of singular values to consider for each matrix's variance
        svals : [[float]]
          If you know the svals of any of the tensors, pass them in here. Use ``None``
          or ``[]`` if you don't know a value.

        Various optimizations are possible if keys never overlap. This
        case is automatically detected -- though it may be overly
        cautious.
        '''
        self.logger = logging.getLogger('csc.divisi.Blend')
        self.k_values = k_values
        self.tensors = tensors
        self._svals = svals

        # Can't call __init__ for either LabeledView or View 's init,
        # because they expect the tensor to be passed.
        #View.__init__(self)

        if factor is not None:
            if weights is not None:
                raise TypeError('Cannot simultaneously specify factor and weights.')
            self.factor = factor
        else:
            self.weights = weights

        self.auto_build_tensor = auto_build_tensor

    def __repr__(self):
        return u'<Blend of %s, weights=%s>' % (partial_list_repr(self.tensors, 2), partial_list_repr(self.weights, 2))

    def __getstate__(self):
        return dict(
            version=1,
            tensors=self.tensors,
            weights=self.weights,
            k_values=self.k_values,
            svals=self._svals,
            auto_build_tensor=self.auto_build_tensor)

    def __setstate__(self, state):
        version = state.pop('version', 1)
        if version > 1:
            raise TypeError('Blend pickle was created by a newer version.')

        self.logger = logging.getLogger('csc.divisi.Blend')
        self.tensors = state['tensors']
        self.k_values = state.get('k_values', 1)
        self._svals = state.get('svals', None)
        self.weights = state['weights']
        self.auto_build_tensor = state.get('auto_build_tensor', True)
        
    def bake(self):
        '''
        Return a normal LabeledView with the current contents of the blend.
        '''
        if self._tensor is None: self.build_tensor()
        return LabeledView(self.tensor, self._labels)
    
    def _set_tensors(self, tensors):
        self._tensors = tuple(tensors)
        self.logger.info('tensors=%r', self._tensors)
        self.ndim = ndim = tensors[0].ndim
        if not all(tensor.ndim == ndim for tensor in tensors):
            raise TypeError('Blended tensors must have the same dimensionality.')

        self.logger.info('Making ordered sets')
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
        self.logger.info('Done making ordered sets. label_overlap: %r', label_overlap)
        if not any(label_overlap):
            self.logger.warn('No labels overlap.')
        
        # Invalidate other data
        self._weights = self._tensor = self._svals = None

    tensors = property(lambda self: self._tensors, _set_tensors)

    @property # necessary because it's a property on the parent class
    def shape(self): return self._shape

    def tensor_svals(self, tensor_idx, num_svals):
        '''
        Get the top num_svals singular values for one of the input tensors.
        '''
        if self._svals is None: self._svals = [[]]*len(self._tensors)
        if num_svals > len(self._svals[tensor_idx] or []):
            self.logger.info('computing by-tensor SVD for tensor %d, k=%d', tensor_idx, num_svals)
            self._svals[tensor_idx] = self._tensors[tensor_idx].svd(k=num_svals).svals.values()
        return self._svals[tensor_idx][:num_svals]
    
    def rough_weight(self, tensor_idx):
        '''
        Compute the rough weight for one of the input tensors.
        '''
        k = self.k_values
        if isinstance(k, (list, tuple)): k = k[tensor_idx]
        return 1.0/sqrt(sum([x*x for x in self.tensor_svals(tensor_idx, k)[:k]]))
    
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
        self.weights = [1.0-factor, float(factor)]
    factor = property(_get_factor, _set_factor)
    
    def normalize_weights(self):
        '''
        Make the weights sum to 1.
        '''
        self.logger.info('Normalizing weights')
        scale = 1.0 / float(sum(self._weights))
        self._weights = tuple(factor * scale for factor in self._weights)

    @property
    def tensor(self):
        if self._tensor is None:
            if not self.auto_build_tensor:
                raise TypeError("Tensor not yet built. Run 'build_tensor'.")
            self.build_tensor()
        return self._tensor

    def build_tensor(self, tensor=None):
        '''
        Build the combined tensor. Done explicitly because it's slow.

        If `tensor` is not None, it is used as the underlying numeric
        storage tensor. It should have the same number of dimensions
        as the blend. It defaults to a new DictTensor.
        '''
        self.logger.info('building combined tensor.')
        labels = self._labels
        if tensor is None: tensor = DictTensor(ndim=self.ndim)
        assert tensor.ndim == self.ndim

        if self._keys_never_overlap:
            self.logger.info('fast-merging.')
            tensor.update((tuple(label_list.index(label) for label_list, label in izip(labels, key)), val)
                          for key, val in self._fast_iteritems())
        else:
            for factor, cur_tensor in zip(self._weights, self._tensors):
                self.logger.info('slow-merging %r' % cur_tensor)
                for key, val in cur_tensor.iteritems():
                    tensor.inc(tuple(label_list.index(label) for label_list, label in izip(labels, key)), factor*val)
        self._tensor = tensor
        self.logger.info('done building tensor.')


    def svd(self, *a, **kw):
        '''
        Computes the SVD of the blend. Builds the tensor if necessary
        and it is not yet built.

        When the keys never overlap, this uses an optimized routine.
        '''
        if not self._keys_never_overlap or self._tensor is not None:
            # Slow case
            self.logger.info('Non-optimized svd')
            if self._tensor is None: self.build_tensor()
            return super(Blend, self).svd(*a, **kw)

        # No overlap, so iteritems is straightforward. Exploit that
        # for some speed.
        from csc.divisi.svd import svd_sparse
        from csc.divisi.labeled_view import LabeledSVD2DResults
        self.logger.info('Optimized svd')
        _svd = svd_sparse(self.fake_tensor(), *a, **kw)
        return LabeledSVD2DResults.layer_on(_svd, self)


    # Optimizations
    def fake_tensor(self):
        '''
        Return a tensor that only knows how to do iteritems. But fast.
        Used for :meth:`svd`.
        '''
        if not self._keys_never_overlap:
            raise TypeError('Can only get a fake tensor if keys never overlap.')
        length = len(self)
        class FakeTensor(object):
            ndim = self.ndim
            shape = self.shape
            def __len__(ft):
                return length
            def iteritems(ft):
                labels = self._labels
                for factor, cur_tensor in zip(self._weights, self._tensors):
                    for key, val in cur_tensor.iteritems():
                        yield (tuple(label_list.index(label) for label_list, label in izip(labels, key)),
                               factor*val)

            def _svd(ft, *a, **kw):
                from csc.divisi._svdlib import svd
                return svd(ft, *a, **kw)

        return FakeTensor()

    def __iter__(self):
        if self._keys_never_overlap:
            return chain(*self.tensors)
        else:
            return (self.labels(idx) for idx in self.tensor)

    def _fast_iteritems(self):
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

    # Visualization
    def coverage_plot(self, bin_size=50):
        '''
        Return a NumPy integer array specifying where each item in the tensor comes from.

        Blank cells are 0; cells that come from tensor n have value
        n+1. (If multiple tensors write in the same bin, the last one
        wins.)
        '''
        if not isinstance(bin_size, (list, tuple)):
            bin_size = [bin_size]*self.ndim
            
        import numpy
        src = numpy.zeros(tuple(numpy.ceil(float(items) / float(bins))
                                for items, bins in izip(self.shape, bin_size)),
                          dtype=numpy.int8)
        fill = numpy.zeros(src.shape)
        inc = 1.0 / numpy.product(src.shape)
        
        # This loop should look a lot like the one in FakeTensor.
        labels = self._labels
        for tensor_idx, tensor in enumerate(self._tensors):
            for key, val in tensor.iteritems():
                idx = tuple(label_list.index(label) / bins for label_list, label, bins in izip(labels, key, bin_size))
                src[idx] = tensor_idx + 1
                fill[idx] += inc
        return fill, src

    def coverage_pdf(self, canvas, bin_size=50, origin=None, inches_per_bin=None):
        from reportlab.lib.units import inch
        from reportlab.lib.pagesizes import letter
        from colorsys import hsv_to_rgb

        scratch = False
        if isinstance(canvas, basestring):
            from reportlab.pdfgen import canvas as pdfgen_canvas
            canvas = pdfgen_canvas.Canvas(canvas, pagesize=letter)
            scratch = True
            
        if origin is None: origin = [0.5*inch]*2
        if inches_per_bin is None:
            inches_per_bin = 0.1 # TODO: set dynamically

        import numpy
        hues = numpy.linspace(0, 1, len(self.tensors)+1)
        
        fill, src = self.coverage_plot(bin_size)
        rows, cols = src.shape
        bin_phys_size = inches_per_bin*inch
        for row in xrange(rows):
            for col in xrange(cols):
                source = src[row,col]
                if not source: continue
                canvas.setStrokeColorRGB(*hsv_to_rgb(hues[source], 1, 1-fill[row, col]))
                canvas.rect(origin[0] + bin_phys_size*col, origin[1] + bin_phys_size*row,
                            bin_phys_size, bin_phys_size, fill=True)

        if scratch:
            canvas.showPage()
            canvas.save()


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
            self.logger.info('computing actual singular values')
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
        return Blend(self.tensors, factor=factor,
                     k_values=self.k_values, svals=self._svals)
        
    def compressed_svd_u(self, k=100):
        """
        Not done yet. --Rob
        """
        labelset = set()
        for t in self.weights:
            labelset += set(t.label_list(0))
        ulabels = OrderedSet(list(labelset))
        svds = [t.svd(k) for t in self.weights]
