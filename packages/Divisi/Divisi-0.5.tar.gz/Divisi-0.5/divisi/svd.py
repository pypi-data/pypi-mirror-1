'''
Processes for performing singular value decomposition on a matrix or tensor,
and working with the results.
'''

from divisi.tensor import Tensor, DenseTensor, outer_tuple_iterator, TheEmptySlice
#from divisi.labeled_tensor import DenseLabeledTensor
from itertools import imap
import numpy
from math import sqrt
from warnings import warn
import logging
from divisi._svdlib import CSCMatrix
from divisi.exceptions import DimensionMismatch
import random

class ReconstructedTensor(Tensor):
    '''
    A ReconstructedTensor is a wrapper around a
    [SVDResults](divisi.svd.SVDResults) object. The
    ReconstructedTensor behaves like the tensor constructed by
    multiplying together the U, Sigma and V matrices (reconstructing
    the original matrix from its SVD).

    ReconstructedTensors require much less storage space than the
    actual reconstructed tensor would require. However, access times
    for a ReconstructedTensor are slower, since accessing an entry
    requires computing a dot product. To mitigate this problem,
    ReconstructedTensors cache the values of recently-accessed entries.
    '''
    def __init__(self, svd_results):
        '''
        Create a ReconstructedTensor from a
        [SVDResults](divisi.svd.SVDResults) object.
        '''
        self.svd = svd_results
        self.a = svd_results.orig
        self.r = svd_results.r
        self.clear_cache()

    def __repr__(self):
        return u'<ReconstructedTensor from %r>' % (self.svd,)

    def clear_cache(self):
        '''
        Clear the cache of recently computed entries. (The cache can
        become very large, so this may free up a significant amount of
        memory.)
        '''
        self._cache = {}

    def __getitem__(self, key):
        # Ken says: I did this in a very wrong way that happens to work
        # in one case.
        if key not in self._cache:
            a = self.a
            nskipped = 0
            to_smooth = []
            for i, k in enumerate(key):
                if isinstance(k, slice):
                    nskipped += 1
                    to_smooth.append(i)
                    continue
                smoothing = self.svd.smoothing_slice(i, k)
                a = a.tensordot(smoothing, nskipped)
            for i, dim in enumerate(to_smooth):
                smoothing = self.svd.smoothing_mat(dim)
                a = a.tensordot(smoothing, i)
            self._cache[key] = a
        return self._cache[key]
        

class SVDResults(object):
    """
    Stores the results of an arbitrary higher-order SVD. If you are simply
    taking the SVD of a matrix, you are probably looking for the SVD2DResults
    class.
    
    self.r is a list of SVD2DResults, one for each unfolding of the tensor.
    """
    def __init__(self, orig, sub_results):
        self.orig = orig
        self.r = sub_results

    @property
    def reconstructed(self):
        return ReconstructedTensor(self)

    @property
    def core(self):
        raise NotImplementedError

    def smoothing_slice(self, n, idx):
        u = self.r[n].u
        ui = u[idx, :]
        return u*ui

    def smoothing_mat(self, n):
        u = self.r[n].u
        return u*u.transpose()


class SVD2DResults(object):
    '''
    This class wraps the _U_, Sigma (_S_) and _V_ matrices that result from
    computing an SVD. An SVD decomposes the matrix _A_ s.t. _A =
    U*S*(V^T)_. Both _U_ and _V_ are orthonormal matrices, and _S_ is a
    diagonal matrix.

    This class also provides utility methods to make common
    SVD-related math easy.
    '''

    def __init__(self, u, v, svals):
        '''
        Construct an SVD2DResults object from the matrices created by
        an SVD. Note that svals is a 1-D vector of sigma values from
        the SVD.
        '''
        self.u = u
        self.v = v
        self.svals = svals
        self.reconstructed = Reconstructed2DTensor(self)
        self.clear_cache()

    def clear_cache(self):
        '''
        Delete all cached tensors from this object.
        '''
        self._core, self._weighted_u, self._weighted_v = None, None, None

    @property
    def core(self):
        '''
        Get the core tensor. The core tensor is the diagonal _S_
        matrix from an SVD.
        '''
        if self._core is None:
            self._core = DenseTensor(numpy.diag(self.svals))
        return self._core
    
    @property
    def ut(self):
        warn(DeprecationWarning("ut and vt are incorrect names, use u and v."))
        return self.u

    @property
    def vt(self):
        warn(DeprecationWarning("ut and vt are incorrect names, use u and v."))
        return self.v

    @property
    def weighted_u(self):
        '''
        Return _U * S_, the result of weighting each column of the _U_
        matrix by its corresponding sigma value.
        '''
        if self._weighted_u is None:
            self._weighted_u = self.u*self.core
        return self._weighted_u
    
    @property
    def weighted_ut(self):
        warn(DeprecationWarning("ut and vt are incorrect names, use u and v."))
        return self.weighted_u()

    @property
    def weighted_v(self):
        '''
        Return _V * S_, the result of weighting each column of the _V_
        matrix by its corresponding sigma value.
        '''
        if self._weighted_v is None:
            self._weighted_v = self.v*self.core
        return self._weighted_v

    @property
    def weighted_vt(self):
        warn(DeprecationWarning("ut and vt are incorrect names, use u and v."))
        return self.weighted_v()

    def u_distances_to(self, vec):
        '''
        Return the dot product of _vec_ with every weighted _u_
        vector.

        TODO: This name is somewhat misleading. My first instinct
        about what this method does is that it returns _||vec - ((vec *
        u) * u^hat)||_, that is it returns the magnitude of the
        component of _vec_ orthogonal to _u_. -- jayant 2/26/2009
        '''
        return self.weighted_u * vec

    def u_angles_to(self, vec):
        '''
        Return the cosine of the angle between _vec_ and every weighted
        _u_ vector. This value can be used as a similarity measure that
        ranges from -1 to 1.
        '''
        u = self.weighted_u
        angles = self.u_distances_to(vec)
        vec_magnitude = sqrt(vec*vec)
        # Normalize distances to get the cos(angles)
        for key, value in angles.iteritems():
            u_vector_magnitude = sqrt(u[key[0], :]*u[key[0], :])
            angles[key] = float(value)/(u_vector_magnitude*vec_magnitude)
        
        return angles

    def weighted_u_vec(self, idx):
        '''
        Get the weighted _u_ vector with key _idx_.
        '''
        return self.weighted_u[idx, :]

    def v_distances_to(self, vec):
        '''
        Compute the dot product of _vec_ with every weighted _v_
        vector.

        TODO: This name is somewhat misleading. My first instinct
        about what this method does is that it returns _||vec - ((vec *
        v) * v^hat)||_, that is it returns the magnitude of the
        component of _vec_ orthogonal to _v_. -- jayant 2/26/2009
        '''
        return self.weighted_v * vec

    def v_angles_to(self, vec):
        '''
        Return the cosine of the angle between _vec_ and every weighted
        _v_ vector. This value can be used as a similarity measure that
        ranges from -1 to 1.
        '''
        v = self.weighted_v
        angles = self.v_distances_to(vec)
        vec_magnitude = sqrt(vec*vec)
        # Normalize distances to get the cos(angles)
        for key, value in angles.iteritems():
            v_vector_magnitude = sqrt(v[key[0], :]*v[key[0], :])
            angles[key] = float(value)/(v_vector_magnitude*vec_magnitude)
        
        return angles

    def weighted_v_vec(self, idx):
        '''
        Get the weighted _v_ vector with key _idx_.
        '''
        return self.weighted_v[idx, :]

    def get_ahat(self, indices):
        '''
        Get the value of one entry of the reconstructed matrix (_A^hat
        = U * S * V^T).
        '''
        i0, i1 = indices
        try:
            return self.u[i0, :]*self.core*self.v[i1, :]
        except KeyError:
            return 0

    def u_similarity(self, idx1, idx2):
        '''
        Get the similarity of two rows of the weighted _U_
        matrix. Similarity is measured by the dot product of the two
        _u_ vectors.
        '''
        return self.u[idx1, :]*self.core*self.u[idx2, :]

    def v_similarity(self, idx1, idx2):
        '''
        Get the similarity of two rows of the weighted _V_
        matrix. Similarity is measured by the dot product of the two
        _v_ vectors.
        '''
        return self.v[idx1, :]*self.core*self.v[idx2, :]

    def summarize(self, k=None, u_only=False):
        '''
        For each axis (up to the _k_th axis), print the items of the
        _u_ and _v_ matrices with the largest components on the axis.
        '''
        if k is None: k = len(self.svals)
        else: k = min(k, len(self.svals))
        for axis in range(k):
            print "\nAxis %d (U)" % axis
            self.u[:,axis].show_extremes(10)
            if not u_only:
                print "\nAxis %d (V)" % axis
                self.v[:,axis].show_extremes(10)
            print "sigma = %5.5f" % self.svals[axis]
            print

    def safe_svals(self):
        '''
        Get the sigma values as an array of floats, no matter what they were before.
        '''
        return numpy.array([float(self.svals[i]) for i in range(len(self.svals))])
    
    def export_svdview(self, outfn, unstem=None):
        '''
        Output a tab-separated values file suitable for use with 
        svdview. The data is saved to the file named _outfn_. 

        The optional _unstem_ procedure takes as a parameter a row label 
        of the _U_ matrix and should return a suitable string representation 
        of the row label. If left unspecified, it defaults to 
        [unstem](divisi.export_svdview.html), which reconstructs a
        concept's full name from its stemmed name.
        '''
        import export_svdview
        if unstem is None:
            unstem = export_svdview.unstem
        return export_svdview.export_svdview(self, outfn, unstem)

class Reconstructed2DTensor(Tensor):
    '''
    This class wraps the results of a 2-D SVD (represented by 
    a [SVD2DResults](divisi.svd.SVD2DResults.html) object) and 
    behaves like the [Tensor](divisi.tensor.Tensor.html) created 
    by multiplying together the _U_, _S_ and _V_ matrices of the 
    SVD result.

    Reconstructed2DTensors require much less storage space than the
    actual reconstructed tensor. However, access times
    for a Reconstructed2DTensor are slower, since accessing an entry
    requires computing a dot product.
    '''
    ndim = 2
    def __init__(self, svd):
        '''
        Create a Reconstructed2DTensor from a 
        [SVD2DResults](divisi.svd.SVD2DResults.html) object.
        '''
        self.svd = svd
        self.shape = svd.u.shape[0], svd.v.shape[0]

    def __repr__(self):
        return u'<%r shape=%r svd=%r>' % (self.__class__, self.shape, self.svd)
    
    def __len__(self):
        return self.shape[0] * self.shape[1]

    def __iter__(self):
        return imap(lambda x: (self.svd.u.label(0, x[0]), self.svd.v.label(0, x[1])), outer_tuple_iterator(self.shape))

    def __getitem__(self, idx):
        if len(idx) != 2:
            raise DimensionMismatch
        i0, i1 = idx

        if i0 == TheEmptySlice and i1 == TheEmptySlice: 
            return self
        elif i0 == TheEmptySlice:
            return self.svd.weighted_u*self.svd.v[i1, :]            
        elif i1 == TheEmptySlice:
            return self.svd.v*self.svd.weighted_u[i0, :]
        elif isinstance(i0, slice) or isinstance(i1, slice):
            raise ValueError('Only the `:` slice supported.')
        else:
            return self.svd.get_ahat(idx)

    def has_key(self, idx):
        if len(idx) != 2: return False
        return idx[0] in self.svd.u.dim_keys(0) and idx[1] in self.svd.v.dim_keys(0)

    def iter_dim_keys(self, dim):
        if dim == 0:
            return self.svd.u.iter_dim_keys(0)
        elif dim == 1:
            return self.svd.v.iter_dim_keys(0)
        else:
            raise DimensionMismatch
    
    def sample(self, source, power=2):
        def sample_dist(vec):
            """
            Samples from a labeled vector.
            """
            data = vec._data
            if random.randint(0, 1): data = -data
            no_neg = numpy.maximum(vec._data, 0)
            cumulprob = numpy.cumsum(no_neg) / numpy.sum(no_neg)
            index = numpy.searchsorted(cumulprob, random.random())
            return vec.label(0, index), no_neg[index]
        
        while True:
            which_sval, prob1 = sample_dist(self.svd.svals)
            which_u, prob2 = sample_dist(self.svd.u[:, which_sval])
            which_v, prob3 = sample_dist(self.svd.v[:, which_sval])
            
            # don't sample things we already knew
            if source[which_u, which_v] > 0: continue
            if (isinstance(which_v, basestring) and 
                (which_v.startswith('InheritsFrom') or
                 which_v.endswith('InheritsFrom'))):
                continue
            if (isinstance(which_v, tuple) and
                (which_v[1] == 'InheritsFrom')): continue
            
            u_modified = numpy.maximum(self.svd.u[which_u, :]._data, 0)
            v_modified = numpy.maximum(self.svd.v[which_v, :]._data, 0)
            u_modified2 = numpy.minimum(self.svd.u[which_u, :]._data, 0)
            v_modified2 = numpy.minimum(self.svd.v[which_v, :]._data, 0)
            sample_prob1 = numpy.dot(u_modified, v_modified)\
                         * self.svd.svals[which_sval]
            sample_prob2 = numpy.dot(u_modified2, v_modified2)\
                         * self.svd.svals[which_sval]
            sample_prob = sample_prob1 + sample_prob2
            u_row = self.svd.u[which_u, :]._data
            v_row = self.svd.v[which_v, :]._data
            actual_prob = max(0, numpy.dot(u_row, v_row)
                                 * self.svd.svals[which_sval])

            acceptance_prob = actual_prob / sample_prob
            assert acceptance_prob <= 1.000001
            if random.random() < acceptance_prob:
                if power == 1 or random.random() < actual_prob:
                    return (which_u, which_v, actual_prob)

class DenormalizedReconstructed2DTensor(Reconstructed2DTensor):
    def __init__(self, svd, norms, normdim=0):
        Reconstructed2DTensor.__init__(self, svd)
        self.norms = norms
        if normdim != 0:
            raise NotImplementedError('normdim != 0 not yet implemented.')

    def __getitem__(self, idx):
        if len(idx) != 2:
            raise DimensionMismatch
        i0, i1 = idx

        if i0 == TheEmptySlice and i1 == TheEmptySlice:
            return self
        elif i0 == TheEmptySlice:
            return self.svd.weighted_u*self.svd.v[i1, :] * self.norms
        elif i1 == TheEmptySlice:
            return self.svd.v * self.svd.weighted_u[i0, :] * self.norms[i0]
        elif isinstance(i0, slice) or isinstance(i1, slice):
            raise ValueError('Only the `:` slice supported.')
        else:
            return self.svd.u[i0, :]*self.svd.core*self.svd.v[i1, :] * self.norms[i0]
        
def svd_sparse(tensor, k=50):
    '''
    Compute the SVD of sparse tensor _tensor_ using Lanczos' algorithm.
    The optional parameter _k_ is the number of sigma values to retain 
    (default value is 50).
    '''
    if tensor.ndim < 2:
        raise NotImplementedError
    elif tensor.ndim == 2:
        return svd_sparse_order2(tensor, k)
    else:
        return svd_sparse_orderN(tensor, k)

def svd_sparse_order2(tensor, k=50):
    '''
    Compute the SVD of sparse 2-D tensor _tensor_. The optional 
    parameter _k_ is the number of sigma values to retain (default 
    value is 50).
    '''
    if not isinstance(tensor, CSCMatrix):
        tensor = CSCMatrix(tensor)

    ut, s, vt = tensor.svd(k)
    #cnorms = dMatNorms(vt)

    del tensor

    logging.info('ut(%s), s(%s), vt(%s)\n' % (ut.shape, s.shape, vt.shape))

    # Truncate ut and vt to the number of singular values we actually got.
    n_svals = s.shape[0]
    ut = ut[:n_svals, :]
    vt = vt[:n_svals, :]
    return SVD2DResults(DenseTensor(ut.T), DenseTensor(vt.T), DenseTensor(s))

def svd_sparse_orderN(tensor, k=50):
    '''
    Compute the higher-order SVD of _tensor_. The optional
    parameter _k_ is the number of sigma values to retain (default 
    value is 50).
    '''

    '''Negative k values mean not to normalize that unfolding.'''
    ndim = tensor.ndim

    # Assume that the given k applies for all unfoldings
    if not isinstance(k, (list, tuple)):
        k=[k]*ndim

    def sub_svd(dim):
        print 'Unfolding along dimension %s' % dim
        u = tensor.unfolded(dim)
        cur_k = k[dim]
        normalized = (cur_k > 0)
        cur_k = abs(cur_k)
        return u.svd(k=cur_k, normalized=normalized)

    return SVDResults(tensor, [sub_svd(dim) for dim in xrange(ndim)])

def incremental_svd(tensor, k=50, niter=100, lrate=.1, logging_interval=None):
    '''
    Compute SVD of 2-D tensor _tensor_ using an incremental SVD algorithm. 
    This algorithm ignores unknown entries in the sparse tensor instead 
    of treating them as 0s (like Lanczos' algorithm does). This means that
    the incremental SVD of a sparse matrix will not necessarily equal the
    Lanczos' SVD of the same matrix.

    The incremental SVD algorithm performs gradient descent to find the 
    _U_, _V_ and _S_ matrices that minimize the Frobenius norm 
    (Root Mean Squared Error) of the reconstructed matrix.

    The optional parameter _k_ is the number of sigma values to retain 
    (default 50). The _lrate_ parameter controls the "learning rate," a 
    factor that changes the rate of gradient descent (default .1). A larger value 
    means the gradient descent will take larger steps toward its goal. 
    Setting _lrate_ to a "large" value may cause the algorithm to diverge,
    and will cause a mysterious overflow error.
    The _niter_ parameter controls the number of steps performed by the
    gradient descent process (default 100).
    '''
    assert(tensor.ndim == 2)
    if not isinstance(tensor, CSCMatrix):
        tensor = CSCMatrix(tensor)
        
    u, v, sigma = tensor.isvd(k=k, niter=niter, lrate=lrate)
    return SVD2DResults(u, v, sigma)
    
