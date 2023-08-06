import logging
import numpy as np
cimport cython
cimport numpy as np

# The type of doubles in numpy
DTYPE=np.float
ctypedef np.float_t DTYPE_t

cdef extern from "svdlib.h":
    
    #  /******************************** Structures *********************************/
   
    #/* Harwell-Boeing sparse matrix. */
    cdef struct smat:
        long rows
        long cols
        long vals      # /* Total non-zero entries. */
        long *pointr   # /* For each col (plus 1), index of first non-zero entry. */
        long *rowind   # /* For each nz entry, the row index. */
        double *value  # /* For each nz entry, the value. */
    
    #/* Row-major dense matrix.  Rows are consecutive vectors. */
    cdef struct dmat:
        long rows
        long cols
        double **value # /* Accessed by [row][col]. Free value[0] and value to free.*/
    cdef struct svdrec:
        int d       #  /* Dimensionality (rank) */
        dmat *Ut     #  /* Transpose of left singular vectors. (d by m)
                    #     The vectors are the rows of Ut. */
        double *S   #  /* Array of singular values. (length d) */
        dmat *Vt     #  /* Transpose of right singular vectors. (d by n)
                    #     The vectors are the rows of Vt. */
    #/******************************** Variables **********************************/
    
    #File formats:
    #SVD_F_STH: sparse text, SVDPACK-style
    #SVD_F_ST:  sparse text, SVDLIB-style
    #SVD_F_DT:  dense text
    #SVD_F_SB:  sparse binary
    #SVD_F_DB:  dense binary
    
    #/* True if a file format is sparse: */
    #int SVD_IS_SPARSE(format):
    #    ((format >= SVD_F_STH) && (format <= SVD_F_SB))
    
    #/******************************** Functions **********************************/
    
    #/* Creates an empty dense matrix. */
    #DMat svdNewDMat(int rows, int cols)
    
    #/* Frees a dense matrix. */
    #void svdFreeDMat(DMat D)
    
    #/* Creates an empty sparse matrix. */
    cdef extern smat *svdNewSMat(int rows, int cols, int vals)
    
    #/* Frees a sparse matrix. */
    cdef extern void svdFreeSMat(smat *S)
    
    #/* Creates an empty SVD record. */
    cdef extern svdrec *svdNewSVDRec()
    
    #/* Frees an svd rec and all its contents. */
    cdef extern void svdFreeSVDRec(svdrec *R)
    
    #/* Converts a sparse matrix to a dense one (without affecting former) */
    #DMat svdConvertStoD(SMat S)
    
    #/* Converts a dense matrix to a sparse one (without affecting former) */
    #SMat svdConvertDtoS(DMat D)
    
    #/* Transposes a dense matrix (returning a new one) */
    #DMat svdTransposeD(DMat D)
    
    #/* Transposes a sparse matrix (returning a new one) */
    #SMat svdTransposeS(SMat S)
    
    #/* Writes an array to a file. */
    #void svdWriteDenseArray(double *a, int n, char *filename, char binary)
    
    #/* Reads an array from a file, storing its size in *np. */
    #double *svdLoadDenseArray(char *filename, int *np, char binary)
    
    #/* Loads a matrix file (in various formats) into a sparse matrix. */
    #SMat svdLoadSparseMatrix(char *filename, int format)
    
    #/* Loads a matrix file (in various formats) into a dense matrix. */
    #DMat svdLoadDenseMatrix(char *filename, int format)
    
    #/* Writes a dense matrix to a file in a given format. */
    #void svdWriteDenseMatrix(DMat A, char *filename, int format)
    
    #/* Writes a sparse matrix to a file in a given format. */
    #void svdWriteSparseMatrix(SMat A, char *filename, int format)
    
    #/* Performs the las2 SVD algorithm and returns the resulting Ut, S, and Vt. */
    cdef extern svdrec *svdLAS2(smat *A, long dimensions, long iterations, double end[2], double kappa)
    
    #/* Chooses default parameter values.  Set dimensions to 0 for all dimensions: */
    cdef extern svdrec *svdLAS2A(smat *A, long dimensions)
    
    #cdef extern void freeVector(double *v)
    #cdef extern double *mulDMatSlice(DMat *D1, DMat *D2, int index, double *weight)
    #cdef extern double *dMatNorms(DMat *D)

cdef extern from "Python.h":

    ctypedef struct PyObject:
        pass


cdef extern from "svdwrapper.h":

    cdef extern void init_numpy()

    cdef extern object wrapDMat(dmat *d)

    cdef extern object wrap_double_array(double* d, int len)

    cdef extern object wrapSVDrec(svdrec *rec, int transposed)

cdef extern from "math.h":

    cdef extern double sqrt(double n)

###### Python functions ######

cdef class CSCMatrix:
    __slots__ = ['cmatrix']
    cdef object tensor #holds our Python tensor
    cdef object row_factors  #holds row division factors, if applicable
    cdef smat *cmatrix  #our C matrix to send to svdlib
    cdef svdrec *svdrec #the wrapper for the SVD results to return
    cdef int transposed #variable to pass to wrapper letting it know if we transposed for speed
    cdef int rows, cols 
    cdef int nonZero    #number of non zero entries in matrix
    def __init__(self, pyTensor, row_factors=None):
        #init function takes 1 or 2 arguments, the Python tensor, and an array representing
        #the row _factors to divide by 
        self.tensor = pyTensor
        self.transposed = 0

        if self.tensor.ndim != 2:
            raise ValueError("You can only pack a 2 dimensional tensor")
        self.rows, self.cols = self.tensor.shape
        self.nonZero = len(self.tensor)
        assert self.nonZero != 0

        self.row_factors = row_factors

    cdef pack(self):
        self.cmatrix = svdNewSMat(self.rows, self.cols, self.nonZero)
        self.transposed = 0
        columnDict = {}
        cols = self.cols
        for (row, column), value in self.tensor.iteritems():
            if self.row_factors is not None:
                value /= sqrt(self.row_factors[row])
            columnDict.setdefault(column, {})[row] = value
        assert len(columnDict) <= cols
        index = 0
        for colnum in xrange(cols):
            col_len = len(columnDict.get(colnum, []))
            self.setColumnSize(colnum, col_len)
            if col_len == 0: continue
            for rowk in sorted(columnDict[colnum].keys()):
                self.setValue(index, rowk,
                       float(columnDict[colnum][rowk]))
                index += 1

    cpdef dictPack(self):
        self.cmatrix = svdNewSMat(self.cols, self.rows, self.nonZero)
        self.transposed = 1
        cdef object rowDict = self.tensor._data
        cdef int rows = self.tensor.shape[0]
        cdef int colk
        cdef int index = 0
        cdef int rownum
        cdef int row_len
        cdef float val
        assert len(rowDict) <= rows 
        for rownum from 0 <= rownum < rows:
            row_len = len(rowDict.get(rownum, []))
            self.setColumnSize(rownum, row_len)
            if row_len == 0: continue
            for colk in sorted(rowDict[rownum].keys()):
                val = float(rowDict[rownum][colk])
                if self.row_factors is not None:
                    val /= sqrt(self.row_factors[rownum])
                self.setValue(index, colk, val)
                index += 1


    def __repr__(self):
        return u'<CSCMatrix>'

    def __dealloc__(self):
        svdFreeSMat(self.cmatrix)

    cdef void setColumnSize(self, int col, int size):
        self.cmatrix[0].pointr[0] = 0
        self.cmatrix.pointr[col+1] = self.cmatrix.pointr[col] + size

    cdef void setValue(self, int index, int rowind, float value):
        self.cmatrix.rowind[index] = rowind
        self.cmatrix.value[index] = value
    
    #cdef svd(self, iterations, end1, end2, kappa, k=50):
    #    svdrec = svdLAS2(self.cmatrix, k, iterations=iterations, end1=end1, end2=end2, kappa=kappa)
    #    ut, s, vt = wrapSVDrec(svdrec)
    #    return SVD2DResults(DenseTensor(ut.T), DenseTensor(vt.T), DenseTensor(s))


    cpdef object svdA(self, int k):
        cdef svdrec *svdrec
        svdrec = svdLAS2A(self.cmatrix, k)
        return wrapSVDrec(svdrec, self.transposed)
                
    @cython.boundscheck(False) 
    def isvd(self, int k=50, int niter=100, double lrate=.001):
        from csc.divisi.tensor import DenseTensor
        cdef smat* A = self.cmatrix
        print "COMPUTING INCREMENTAL SVD"
        print "ROWS: %d, COLUMNS: %d, VALS: %d" % (A.rows, A.cols, A.vals)
        print "K: %d, LEARNING_RATE: %r, ITERATIONS: %d" % (k, lrate, niter)

        cdef np.ndarray[DTYPE_t, ndim=2] u = np.add(np.zeros((A.rows, k), dtype=DTYPE), .001)
        cdef np.ndarray[DTYPE_t, ndim=2] v = np.add(np.zeros((A.cols, k), dtype=DTYPE), .001)

        # Maintain a cache of dot-products up to the current axis
        cdef smat* predicted = svdNewSMat(A.rows, A.cols, A.vals)

        # Type all loop vars
        cdef unsigned int axis, i, cur_row,cur_col, col_index, next_col_index, value_index
        cdef double err, u_value

        # Initialize dot-product cache
        # (This should be done with memcpy, but i'm not certain
        # how to do that here)
        for i in range(A.cols + 1):
            predicted.pointr[i] = A.pointr[i]
        
        for i in range(A.vals):
            predicted.rowind[i] = A.rowind[i]
            predicted.value[i] = 0

        for axis in range(k):
            for i in range(niter):
                # Iterate over all values of the sparse matrix
                for cur_col in range(A.cols):
                    col_index = A.pointr[cur_col]
                    next_col_index = A.pointr[cur_col + 1]
                    for value_index in range(col_index, next_col_index):
                        cur_row = A.rowind[value_index]
                        err = A.value[value_index] - (predicted.value[value_index] + 
                                                      u[cur_row, axis] * v[cur_col, axis])

                        u_value = u[cur_row, axis]
                        u[cur_row, axis] += lrate * err * v[cur_col, axis]
                        v[cur_col, axis] += lrate * err * u_value
    
            # Update cached dot-products
            for cur_col in range(predicted.cols):
                col_index = predicted.pointr[cur_col]
                next_col_index = predicted.pointr[cur_col + 1]
                for value_index in range(col_index, next_col_index):
                    cur_row = predicted.rowind[value_index]
                    predicted.value[value_index] += u[cur_row, axis] * v[cur_col, axis]

        # Factor out the svals from u and v
        u_sigma = np.sqrt(np.add.reduce(np.multiply(u, u)))
        v_sigma = np.sqrt(np.add.reduce(np.multiply(v, v)))
    
        u_tensor = DenseTensor(np.divide(u, u_sigma))
        v_tensor = DenseTensor(np.divide(v, v_sigma))
        sigma = DenseTensor(np.multiply(u_sigma, v_sigma))

        svdFreeSMat(predicted)

        if self.transposed:
            return v_tensor, u_tensor, sigma
        else:
            return u_tensor, v_tensor, sigma

def svd(tensor, k=50, row_factors=None):
    CSC = CSCMatrix(tensor, row_factors)
    CSC.pack()
    return CSC.svdA(k)

def dictSvd(tensor, k=50, row_factors=None):
    CSC = CSCMatrix(tensor, row_factors)
    CSC.dictPack()
    return CSC.svdA(k)

def isvd(tensor, k=50, niter=100, lrate=.001, row_factors=None):
    CSC = CSCMatrix(tensor, row_factors)
    CSC.pack()
    return CSC.isvd(k, niter, lrate)

def dictIsvd(tensor, k=50, niter=100, lrate=.001, row_factors=None):
    CSC = CSCMatrix(tensor, row_factors)
    CSC.dictPack()
    return CSC.isvd(k, niter, lrate)
