from divisi.tensor import DictTensor
from divisi.ordered_set import OrderedSet
from divisi.labeled_view import LabeledView

import logging

# Subclasses of Tensor need at a bare minimum:
#  - shape
#  - __iter__()
#  - __getitem__()
# and you can probably make a faster implementation of:
#  - __len__(): number of keys
#  - iter_dim_keys()

def partial_list_repr(lst, max_len):
    if len(lst) <= max_len:
        return repr(lst)
    else:
        return u'[%s, ... (%d total)]' % (
            ', '.join(repr(item) for item in lst[:max_len]),
            len(lst))

class Blend(LabeledView):
    def __init__(self, tensors, svds=None, factors=None):
        '''
        Create a new Blend from a list of tensors.

        Limitations:
        * Only supports 2D blends right now.
        * Often assumes that no keys appear in more than one tensor. Results
          may be subtly wrong in some cases if this is not true.
        '''
        self._set_tensors(tensors)

        # Can't call __init__ for either LabeledView or View 's init,
        # because they expect the tensor to be passed.
        #View.__init__(self)

        if svds is None: svds = [None]*len(tensors)
        else: svds = svds[:] # shallow copy
        self.svds = svds

        self.factors = factors
        
    def __repr__(self):
        return u'<Blend of %s>' % partial_list_repr(self.tensors, 2)
        
    def _set_tensors(self, tensors):
        self._tensors = tuple(tensors)

        logging.info('Blend: Making ordered sets')
        rows, cols = OrderedSet(), OrderedSet()
        row_overlap = col_overlap = 0
        for tensor in self._tensors:
            rows.extend(tensor.label_list(0))
            cols.extend(tensor.label_list(1))
#             for r, c in tensor.keys():
#                 if r in rows: row_overlap += 1
#                 else: rows.add(r)

#                 if c in cols: col_overlap += 1
#                 else: cols.add(r)

        self.row_overlap, self.col_overlap = row_overlap, col_overlap
        self._labels = [rows, cols]
        #self.shape = (len(rows), len(cols))

        # Invalidate other data
        self._factors = self.svds = self._tensor = None

    tensors = property(lambda self: self._tensors, _set_tensors)

    def _set_factors(self, factors):
        tensors, svds = self._tensors, self.svds
        if factors is None: factors = [None]*len(tensors)
        
        # Compute autoblend factors for any factors that are unspecified.
        for i, factor in enumerate(factors):
            if factor is not None: continue

            if svds[i] is None:
                logging.info('Blend: computing SVD for %r for autoblend' % (tensors[i],))
                svds[i] = tensors[i].svd(k=1)

            # Take singular value 0 as the blending factor.
            factors[i] = 1/svds[i].svals[0]

        logging.info('Blend: Normalizing factors')
        self._factors = factors
        self.normalize_factors()

    factors = property(lambda self: self._factors, _set_factors)
        
    def normalize_factors(self):
        '''
        Make the factors sum to 1
        '''
        scale = float(sum(self._factors))
        self._factors = tuple(factor / scale for factor in self._factors)

    @property
    def tensor(self):
        if self._tensor is None:
            # Compute the tensor. (FIXME: hardcoded 2d)
            logging.info('Blend: building combined tensor.')
            row, col = self._labels
            tensor = self._tensor = DictTensor(2)

            for cur_tensor in self._tensors:
                logging.info('Blend: merging %r' % cur_tensor)
                for (r, c), val in cur_tensor.iteritems():
                    tensor[row.index(r), col.index(c)] += val
        
        return self._tensor

    def __iter__(self):
        return (self.labels(idx) for idx in self.tensor.__iter__())    


if __name__=='__main__':
    # ConceptNet blend test
    logging.basicConfig(level=logging.DEBUG)
    from csamoa.conceptnet.analogyspace import conceptnet_by_relations
    by_rel = conceptnet_by_relations('en')
    
    
