import unittest
from divisi.tensor import DictTensor, DenseTensor
from divisi.normalized_view import NormalizedView, TfIdfView, ZeroMeanView
from divisi.labeled_view import LabeledView
from divisi.ordered_set import OrderedSet, IdentitySet
from divisi.unfolded_set import UnfoldedSet
from divisi.labeled_tensor import SparseLabeledTensor
from math import sqrt

import numpy
import random
import sys

def nested_list_to_dict(ndarray):
    '''
    Makes a dict of {index: value} out of a nested list or ndarray.

    >>> sorted(nested_list_to_dict([[1,2],[3,4]]).items())
    [((0, 0), 1), ((0, 1), 2), ((1, 0), 3), ((1, 1), 4)]

    Since numpy ndarrays iterate over their rows, this seems to work
    for them also.
    '''
    if isinstance(ndarray[0], (int, float, None.__class__)):
        return dict(((idx,), val) for idx, val in enumerate(ndarray))

    res = {}
    for idx, lst in enumerate(ndarray):
        for k, v in nested_list_to_dict(lst).iteritems():
            res[(idx,)+k] = v
    return res

def dict_fill_in_missing_dims(d):
    items = d.items()
    ndim = len(items[0])
    dim_keys = [set() for i in xrange(ndim)]

    for cur_dim in xrange(ndim):
        for key, value in items:
            dim_keys[cur_dim].add(key[cur_dim])

    def enumerate_keys(dim_keys):
        if len(dim_keys) == 0:
            yield ()
        else:
            for key_end in enumerate_keys(dim_keys[1:]):
                for key_part in dim_keys[0]:
                    yield (key_part,) + key_end

    new_dict = {}
    for key in enumerate_keys(dim_keys):
        new_dict[key] = d.get(key, None)

    return new_dict

def nones_removed(d):
    return dict((k, v) for k, v in d.iteritems() if v is not None)


def get_shape_for_dict(expected):
    if len(expected.keys()) == 0:
        return ()
 
    ndim = len(expected.keys()[0])
    num_indices = [0 for dim in xrange(ndim)]
    for dim in xrange(ndim):
        s = set((k[dim] for k in expected.iterkeys()))
        num_indices[dim] = len(s)

    return tuple(num_indices)

class TensorTest(unittest.TestCase):
    def assertDimsConsistent(self):
        self.assertEqual(self.tensor.ndim, len(self.tensor.shape))
    
    def assertShapeEqual(self, actual, expected):
        expected_shape = get_shape_for_dict(expected)
        self.assertEqual(expected_shape, actual.shape)
        self.assertEqual(len(expected_shape), actual.dims)
        self.assertEqual(len(expected_shape), actual.ndim)

    def assertValuesEqual(self, actual, expected):
        '''
        Test which values are specified in the tensor.

        Args:
         actual: the Tensor result
         expected: a dictionary of expected results
        '''
        for index, expected_value in expected.iteritems():
            if expected_value is not None:
                self.assertTrue(index in actual)
                self.assertTrue(actual.has_key(index))
                self.assertAlmostEqual(actual[index], expected_value)
            else:
                self.assertFalse(index in actual)
                self.assertFalse(actual.has_key(index))        
                self.assertAlmostEqual(actual[index], actual.default_value)

        # Test some the shape boundary condition
        self.assertFalse(get_shape_for_dict(expected) in actual)

    def assertItemsCorrect(self, actual, expected):
        # Filter just what's specified.
        specified = nones_removed(expected)

        # Test __iter__
        specified_keys = specified.keys()
        specified_keys.sort()
        indices = list(iter(actual))

        self.assertEqual(sorted(indices), specified_keys)
        self.assertEqual(sorted(actual.keys()), specified_keys)

        # Same test for iteritems()
        items_iter = sorted(list(actual.iteritems()))
        items_noniter = sorted(actual.items())
        specified_items = sorted(specified.items())
        # Values are subject to floating-point error, so an
        # AlmostEqual test is required.
        for (actual_key, actual_val), (expected_key, expected_val) \
                in zip(items_iter, specified_items):
            self.assertEqual(actual_key, expected_key)
            self.assertAlmostEqual(actual_val, expected_val)
        for (actual_key, actual_val), (expected_key, expected_val) \
                in zip(items_noniter, specified_items):
            self.assertEqual(actual_key, expected_key)
            self.assertAlmostEqual(actual_val, expected_val)

        # Test the values() method
        specified_values = specified.values()
        for a, e in zip(sorted(actual.values()), sorted(specified_values)):
            self.assertAlmostEqual(a, e)

        # Test that the length of the tensor is equal to the number of specified items
        self.assertEqual(len(actual), len(specified_keys))

        # Test the __contains__ method
        self.assertTrue(specified_keys[0] in actual)
        # can't easily test the contrapositive, since we can't easily make up an index that's not in there.

    def assertIterDimKeysCorrect(self, actual, expected):
        specified_indices = [k for k, v in expected.iteritems()
                             if v is not None]
        for dim in xrange(len(specified_indices[0])):
            expected_keys = set(key[dim] for key in specified_indices)
            dim_keys = list(actual.iter_dim_keys(dim))
            self.assertEqual(sorted(dim_keys), sorted(expected_keys))

    def assertTensorEqual(self, actual, expected):
        '''Takes an n-dimensional array 'expected' and runs several
        tests on the tensor 'actual'. For the test description, see
        assertTensorEqualCompleteDict.
        '''
        expected_dict = nested_list_to_dict(expected)
        self._assertTensorEqualCompleteDict(actual, expected_dict)

    def assertTensorEqualDict(self, actual, expected_dict):
        expected_complete_dict = dict_fill_in_missing_dims(expected_dict)
        self._assertTensorEqualCompleteDict(actual, expected_complete_dict)

    def _assertTensorEqualCompleteDict(self, actual, expected_dict):
        '''
        Takes a tensor and a dictionary of key => value pairs, e.g.
        {(0,0) : 1, (0, 1) : 2}
        and performs the following tests:

        1. actual's dimension and shape match that of expected
        2. Every index of actual has the same value as expected.
        3. Every index of expected is contained (i.e. using python's "in")
           in actual (Note: values in expected can be None, in which case
           actual is assumed to not contain the index and 
           the value of actual at that index is the tensor's default
           value)
        4. Iteration (__iter__ and iteritems) correctly iterate over 
           only the specified indices of actual
        5. iter_dim_keys iterates over specified keys of the specified dimension
        6. keys() and values() methods return only the specified indices
           of actual
        7. len(actual) returns the number of specified indices in expected
        8. has_key returns True for specified indices and False for unspecified indices
        '''
        self.assertShapeEqual(actual, expected_dict)
        self.assertValuesEqual(actual, expected_dict)
        self.assertItemsCorrect(actual, expected_dict)
        self.assertIterDimKeysCorrect(actual, expected_dict)


class SparseTensorTest(TensorTest):
    is_abstract = True

    slice_testcase = [[1,    None, None],
                       [None, 2,    3   ],
                       [4,    None, None],
                       [None, 5,    None]]
    
    def test_initial(self):
        self.assertEqual(len(self.tensor), 0)
        self.assertEqual(len(self.tensor.keys()), 0)
        self.assertDimsConsistent()
        self.assertEqual(self.tensor.shape, (0, 0))
        self.assert_(isinstance(self.tensor[4, 5], (float, int, long)))
        self.assertEqual(self.tensor[5, 5], 0)
        self.assertEqual(self.tensor[2, 7], 0)

    def test_storage(self):
        self.tensor[5, 5] = 1
        self.tensor[2, 7] = 2

        self.assertTensorEqual(self.tensor,
                               [[None]*8,
                                [None]*8,
                                [None]*7 + [2],
                                [None]*8,
                                [None]*8,
                                [None]*5 + [1, None, None]])

    def test_slice(self):
        self.tensor.update(nones_removed(nested_list_to_dict(self.slice_testcase)))
        
        # Test end conditions: start index
        # is included in slice, end index is not
        slice = self.tensor[1:3, 0:2]
        self.assertTensorEqual(slice,
                               [[None, 2],
                                [4, None]])

        # Test that slicing on some dims correctly 
        # reduces the dimensionality of the tensor
        slice = self.tensor[3, :]
        self.assertTensorEqual(slice, [None, 5, None])

        # Test the step parameter
        slice = self.tensor[1:4:2, :]
        self.assertTensorEqual(slice, 
                               [[None, 2, 3],
                                [None, 5, None]])

    def test_transpose(self):
        self.tensor[0, 0] = 1
        self.tensor[1, 2] = 3
        self.tensor[2, 0] = 4
        self.tensor[3, 1] = 5

        t = self.tensor.transpose()
        self.assertTensorEqual(t,
                               [[1, None, 4, None],
                                [None, None, None, 5],
                                [None, 3, None, None]])

    def test_delete(self):
        self.tensor.update(nones_removed(nested_list_to_dict(self.slice_testcase)))
        self.assertTensorEqual(self.tensor, self.slice_testcase)

        del self.tensor[0,0]
        self.assertTensorEqual(self.tensor,
                               [[None, None, None],
                                [None, 2,    3   ],
                                [4,    None, None],
                                [None, 5,    None]])

    def test_contains(self):
        self.tensor[1,2] = 1
        self.tensor[4,5] = 2
        self.assertTrue((1,2) in self.tensor)
        self.assertTrue(self.tensor.has_key((1,2)))
        self.assertFalse((4,2) in self.tensor)
        self.assertFalse((1,5) in self.tensor)


        
class DictTensorTest(SparseTensorTest):
    def setUp(self):
        self.tensor = DictTensor(2)
                
    def test_1D(self):
        tensor_1D = DictTensor(1)
        tensor_1D[2] = 1 

        self.assertTensorEqual(tensor_1D,
                               [None, None, 1])

    def test_combine_by_element(self):
        t1 = DictTensor(2)
        t2 = DictTensor(2)
        t1[1, 1] = 1
        t1[1, 0] = 2
        t2[1, 1] = 4
        t2[0, 1] = 5

        t3 = t1.combine_by_element(t2, lambda x, y: x + (2*y))
        self.assertTensorEqual(t3,
                               [[None, 10],
                                [2, 9]])

        # Make sure errors are raised when the tensors don't have the
        # same shape or number of dimensions
        t4 = DictTensor(2)
        t4[0, 2] = 3
        t4[1, 0] = 5
        self.assertRaises(IndexError, lambda: t1.combine_by_element(t4, lambda x, y: x + y))
        t4 = DictTensor(3)
        self.assertRaises(IndexError, lambda: t1.combine_by_element(t4, lambda x, y: x + y))

    def testAdd(self):
        t1 = DictTensor(2)
        t2 = DictTensor(2)
        t1[0, 0] = 1
        t1[1, 1] = 1
        t1[1, 0] = 2
        t2[2, 1] = 4
        t2[1, 0] = 5

        t3 = t1 + t2
        self.assertTensorEqual(t3,
                               [[1, None],
                                [7, 1],
                                [None, 4]])

    def testReprOfEmpty(self):
        repr(self.tensor)
        self.tensor.example_key()

    def testMagnitude(self):
        mag_test = [[0,0,0],
                    [0,1,0],
                    [0,5.0,0]]
        self.tensor.update(nested_list_to_dict(mag_test))
        self.assertEqual(self.tensor.magnitude(), 26.0)
            
from numpy import zeros
class DenseTensorTest(TensorTest):
    def setUp(self):
        self.tensor = DenseTensor(zeros((3,4)))

    def test_initial(self):
        self.assertEqual(len(self.tensor), 3*4)
        self.assertEqual(len(self.tensor.keys()), 3*4)
        self.assertDimsConsistent()
        self.assert_(isinstance(self.tensor[2, 3], (float, int, long)))
        self.assertEqual(self.tensor.shape, (3, 4))
        self.assertEqual(self.tensor[1, 2], 0)
        self.assertEqual(self.tensor[0, 3], 0)

    def test_container(self):
        self.tensor[0, 0] = 1
        self.tensor[2, 3] = 2
        self.tensor[0, -1] = 3

        self.assertTensorEqual(self.tensor,
                               [[1, 0, 0, 3],
                                [0, 0, 0, 0],
                                [0, 0, 0, 2]])

class DenseVectorTest(TensorTest):
    def setUp(self):
        self.tensor = DenseTensor(zeros((5,)))

    def testDotProduct(self):
        # Set up the other tensor
        tensor2 = DenseTensor(zeros(5,))
        # Dot them
        result = self.tensor*tensor2
        self.assertEqual(result, 0)

    def testAdding(self):
        # Set up the other tensor
        tensor2 = DenseTensor(zeros(5,))
        tensor2[3] = 3
        # Add them.
        result = self.tensor + tensor2
        self.assert_((result._data == [0,0,0,3,0]).all())

    def testAddDims(self):
        self.assertRaises(ValueError, lambda: self.tensor + DenseTensor(zeros(3,)))
        self.assertRaises(TypeError, lambda: self.tensor + DenseTensor(zeros(5,5)))    


class LabeledDenseTensorTest(TensorTest):
    labels = [['a', 'b', 'c']]

    def setUp(self):
        self.raw = DenseTensor(zeros((3,)))
        self.tensor = LabeledView(self.raw, self.labels)
        self.tensor['c'] = 3

    def testAdding(self):
        # Set up the other tensor
        raw2 = DenseTensor(zeros((3,)))
        tensor2 = LabeledView(raw2, self.labels)
        tensor2['a'] = 2
        
        # Add.
        result = self.tensor + tensor2
        self.assertEqual(result['a'], 2)
        self.assertEqual(result['b'], 0)
        self.assertEqual(result['c'], 3)

    def testAddMismatch(self):
        # Set up the other tensor
        raw2 = DenseTensor(zeros((3,)))
        tensor2 = LabeledView(raw2, [['q','r','s']])
        tensor2['q'] = 2

        # Should fail because the new dense tensor would have to be bigger
        self.assertRaises(IndexError, lambda: self.tensor + tensor2)

    def test_iter_dim_keys(self):
        raw = DenseTensor(zeros((2, 3)))
        labels = [['a', 'b'], ['c', 'd', 'e']]
        tensor = LabeledView(raw, labels)

        i = 0
        for key in tensor.iter_dim_keys(0):
            self.assertEqual(key, labels[0][i])
            i += 1
        self.assertEqual(i, 2)
        
        i = 0
        for key in tensor.iter_dim_keys(1):
            self.assertEqual(key, labels[1][i])
            i += 1
        self.assertEqual(i, 3)

    def test_combine_by_element(self):
        t1 = LabeledView(DenseTensor(zeros((2,2))), [['a', 'b'], ['c', 'd']])
        t2 = LabeledView(DenseTensor(zeros((2,2))), [['a', 'b'], ['c', 'd']])
        t1['a', 'c'] = 1
        t1['b', 'c'] = 2
        t2['a', 'c'] = 4
        t2['a', 'd'] = 5

        t3 = t1.combine_by_element(t2, lambda x, y: x + (2*y))
        self.assertEqual(t3['a', 'c'], 9)
        self.assertEqual(t3['b', 'c'], 2)
        self.assertEqual(t3['a', 'd'], 10)
        self.assertEqual(t3['b', 'd'], 0)

        t4 = DenseTensor(zeros((3, 2)))
        self.assertRaises(IndexError, lambda: t1.combine_by_element(t4, lambda x, y: x + y))
        t4 = DenseTensor(zeros((2, 2, 1)))
        self.assertRaises(IndexError, lambda: t1.combine_by_element(t4, lambda x, y: x + y))

def make_labeled_dict_tensor(ndim):
    raw = DictTensor(ndim)
    labels = [OrderedSet() for _ in range(ndim)]
    return LabeledView(raw, labels)

class LabeledDictTensorTest(TensorTest):
    def setUp(self):
        self.tensor = make_labeled_dict_tensor(2)

    def test_storage(self):
#        self.assertEqual(len(self.tensor), 0)
        self.assertEqual(len(self.tensor.keys()), 0)
        self.assertEqual(self.tensor.ndim, 2)
        self.assertEqual(self.tensor.shape, (0, 0))

        # Unknown keys are 0 (or default_value).
        self.assertEqual(self.tensor['banana', 'yellow'], 0)
        self.assertEqual(self.tensor['apple', 'red'], 0)

        self.tensor['banana', 'yellow'] = 1
        self.tensor['apple', 'red'] = 2
        self.tensor['apple', 'blue'] = 3
        self.tensor['orange', 'yellow'] = 4

        expected = {('banana', 'yellow') : 1,
                    ('apple', 'red') : 2,
                    ('apple', 'blue') : 3,
                    ('orange', 'yellow') : 4}
        self.assertTensorEqualDict(self.tensor, expected)


    def test_slicing(self):
        for row in ['x', 'y', 'z']:
            for col in ['a', 'b']:
                self.tensor[row, col] = ord(row)*100+ord(col)
        
        slice = self.tensor['x', :]
        self.assertEqual(slice.shape, (2,))
        self.assertEqual(slice['a'], ord('x')*100+ord('a'))

        slice = self.tensor.slice(0, 'x')
        self.assertEqual(slice.shape, (2,))
        self.assertEqual(slice['a'], ord('x')*100+ord('a'))

        slice = self.tensor[:, 'a']
        self.assertEqual(slice.shape, (3,))
        self.assertEqual(slice['x'], ord('x')*100+ord('a'))

        slice = self.tensor.slice(1, 'a')
        self.assertEqual(slice.shape, (3,))
        self.assertEqual(slice['x'], ord('x')*100+ord('a'))


    def test_wrapped(self):
        self.tensor['a', '1'] = 2
        self.assertEqual(self.tensor['a','1'], 2)

        indices = self.tensor.indices(('a','1'))
        self.assertEqual(self.tensor.tensor[indices], 2)
        
        self.assert_(self.tensor._label_dims_correct())

    def test_contains(self):
        self.tensor['1','2'] = 1
        self.tensor['4','5'] = 2
        self.assertTrue(('1','2') in self.tensor)
        self.assertTrue(self.tensor.has_key(('1','2')))
        self.assertFalse(('4','2') in self.tensor)
        self.assertFalse(('1','5') in self.tensor)
        self.assertFalse(self.tensor.has_key(('1','5')))


    def test_add(self):
        t1 = make_labeled_dict_tensor(2)
        t2 = make_labeled_dict_tensor(2)

        t1['cat', 'mammal'] = 1
        t1['cat', 'pet'] = 1
        t1['panda', 'mammal'] = 1
        t2['cat', 'pet'] = 1
        t2['bear', 'pet'] = -1

        t3 = t1 + t2
        # FIXME: FINISH THIS!
        
normalize_testcase = [[1, None],
                      [3, 4]]

normalize_expected_result = [[1, None],
                             [3/5., 4/5.]]

class NormalizedViewTest(TensorTest):
    def setUp(self):
        self.raw = DictTensor(2)
        self.raw.update(nones_removed(nested_list_to_dict(normalize_testcase)))
        self.tensor = NormalizedView(self.raw, 0)

    def test_result(self):
        self.assertTensorEqual(self.tensor, normalize_expected_result)

    def test_contains(self):
        self.assertTrue((0,0) in self.tensor)
        self.assertTrue(self.tensor.has_key((0,0)))
        self.assertFalse((0,1) in self.tensor)
        self.assertFalse(self.tensor.has_key((0,1)))

class ZeroMeanViewTest(TensorTest):
    def setUp(self):
        self.tensor = DictTensor(ndim=2)
        self.tensor[0, 3] = 2
        self.tensor[3, 4] = 3
        self.tensor = self.tensor.zero_mean_normalized(mode=0)

        self.labeled_tensor = SparseLabeledTensor(ndim=2)
        self.labeled_tensor['a', 'b'] = 2
        self.labeled_tensor['b', 'c'] = 3
        self.labeled_tensor = self.labeled_tensor.zero_mean_normalized(mode=0, prefix='+')

    def test_keys(self):
        self.assertEqual(len(self.tensor), 4)
        self.assertEqual(self.tensor.shape, (8, 5))
        self.assertEqual(self.tensor.keys(),
                         [(0, 3), (4, 3),
                          (3, 4), (7, 4)])

    def test_getitem(self):
        self.assertEqual(self.tensor[0, 3], 2)
        self.assertEqual(self.tensor[4, 3], -2)
        self.assertEqual(self.tensor[3, 4], 3)
        self.assertEqual(self.tensor[7, 4], -3)

    def test_labeled_keys(self):
        self.assertEqual(len(self.labeled_tensor), 4)
        self.assertEqual(self.labeled_tensor.shape, (4, 2))
        self.assertEqual(self.labeled_tensor.keys(),
                         [('a', 'b'), ('+a', 'b'),
                          ('b', 'c'), ('+b', 'c')])

    def test_labeled_getitem(self):
        self.assertEqual(self.labeled_tensor['a', 'b'], 2)
        self.assertEqual(self.labeled_tensor['+a', 'b'], -2)
        self.assertEqual(self.labeled_tensor['b', 'c'], 3)
        self.assertEqual(self.labeled_tensor['+b', 'c'], -3)



class TfIdfTest(TensorTest):
    def test(self):
        '''Run the testcase from the Wikipedia article (in comments)'''
        tensor = DictTensor(2)
        # Consider a document containing 100 words wherein the word cow appears 3 times.
        # [specifically, let there be a document where 'cow' appears 3 times
        #  and 'moo' appears 97 times]
        doc = 0
        cow = 1
        moo = 2
        tensor[cow, doc] = 3
        tensor[moo, doc] = 97
        # Following the previously defined formulas, the term frequency (TF) for cow is then 0.03 (3 / 100).
        tfidf = TfIdfView(tensor) # (can't create it earlier b/c it's read-only)
        self.assertEqual(tfidf.counts_for_document[doc], 100)
        self.assertAlmostEqual(tfidf.tf(cow, doc), 0.03)

        # Now, assume we have 10 million documents and cow appears in one thousand of these.
        #  [specifically, let 'cow' appear in documents 0 and 10,000,000-1000+1 till 10,000,000
        for doc in xrange(10000000-1000+1,10000000):
            tensor[cow, doc] = 1

        # Then, the inverse document frequency is calculated as ln(10 000 000 / 1 000) = 9.21.
        tfidf = TfIdfView(tensor) # (have to update after adding the other docs)
        self.assertEqual(tfidf.num_documents, 10000000)
        self.assertEqual(tfidf.num_docs_that_contain_term[cow], 1000)
        self.assertAlmostEqual(tfidf.idf(cow), 9.21, 2)
        
        # The TF-IDF score is the product of these quantities: 0.03 * 9.21 = 0.28.
        score = tfidf[cow, 0]
        self.assertEqual(len(getattr(score, 'shape', ())), 0)
        self.assertAlmostEqual(score, 0.28, 2)


class UnfoldedSparseTensorTest(unittest.TestCase):
    def setUp(self):
        self.raw = DictTensor(3)
        for x1 in range(2):
            for x2 in range(3):
                for x3 in range(4):
                    self.raw[x1, x2, x3] = x1*100+x2*10+x3

    def test_unfold0(self):
        uf = self.raw.unfolded(0)
        self.assertEqual(uf.shape, (2, 3*4))
        self.assertEqual(len(uf), 2*3*4)
        for x1 in range(2):
            for x2 in range(3):
                for x3 in range(4):
                    self.assertEqual(uf[x1, (x2, x3)], x1*100+x2*10+x3)

    def test_unfold1(self):
        uf = self.raw.unfolded(1)
        self.assertEqual(uf.shape, (3, 2*4))
        for x1 in range(2):
            for x2 in range(3):
                for x3 in range(4):
                    self.assertEqual(uf[x2, (x1, x3)], x1*100+x2*10+x3)

    def test_unfold2(self):
        uf = self.raw.unfolded(2)
        self.assertEqual(uf.shape, (4, 2*3))
        for x1 in range(2):
            for x2 in range(3):
                for x3 in range(4):
                    self.assertEqual(uf[x3, (x1, x2)], x1*100+x2*10+x3)

    def test_compact0(self):
        uf = self.raw.unfolded(0)
        compact = DictTensor(2)
        uf.compact_to(compact)
        self.assertEqual(len(compact), 2*3*4)
        for x1 in range(2):
            for x2 in range(3):
                for x3 in range(4):
                    self.assertEqual(compact[x1, x2*4+x3], x1*100+x2*10+x3)


class UnfoldErrors(unittest.TestCase):
# 1D is just stupid, not an error.
#    def test_1D(self):
#        self.assertRaises(IndexError, lambda: DictTensor(1).unfolded(0))

    def test_oob(self):
        self.assertRaises(IndexError, lambda: DictTensor(3).unfolded(3))


class IdentitySetTest(unittest.TestCase):
    def test_identity(self):
        iset = IdentitySet(10)
        self.assertEqual(iset[5], 5)
        self.assertEqual(iset.index(2), 2)
        self.assertEqual(len(iset), 10)
        self.assert_(iset == OrderedSet(range(10)))

class UnfoldedSetTests(unittest.TestCase):
    def setUp(self):
        self.sets = [
            OrderedSet([2,4,6,8,10]),      # 5 items
            IdentitySet(10),               # 10 items
            OrderedSet(['a','b','c','d']), # 4 items
            ]
    
    def test_index(self):
        uset = UnfoldedSet(self.sets)
        self.assertEqual(uset.index((2, 0, 'a')), 0)
        self.assertEqual(uset.index((2, 0, 'b')), 1)
        self.assertEqual(uset.index((2, 1, 'a')), 4)
        self.assertEqual(uset.index((4, 0, 'a')), 40)

    def test_label(self):
        uset = UnfoldedSet(self.sets)
        self.assertEqual(uset[0], (2, 0, 'a'))
        self.assertEqual(uset[1], (2, 0, 'b'))
        self.assertEqual(uset[4], (2, 1, 'a'))
        self.assertEqual(uset[40], (4, 0, 'a'))

    def test_len(self):
        uset = UnfoldedSet(self.sets)
        self.assertEqual(len(uset), 5*10*4)
    
    def test_from_unfolding(self):
        u0 = UnfoldedSet.from_unfolding(0, self.sets)
        self.assertEqual(u0[0], (0, 'a'))
        self.assertEqual(u0[1], (0, 'b'))
        self.assertEqual(u0[4], (1, 'a'))

        u1 = UnfoldedSet.from_unfolding(1, self.sets)
        self.assertEqual(u1[0], (2, 'a'))
        self.assertEqual(u1[1], (2, 'b'))
        self.assertEqual(u1[4], (4, 'a'))

        u2 = UnfoldedSet.from_unfolding(2, self.sets)
        self.assertEqual(u2[0], (2, 0))
        self.assertEqual(u2[1], (2, 1))
        self.assertEqual(u2[10], (4, 0))


class TestMult(unittest.TestCase):
    '''Tests that DenseTensors and DictTensors behave identically for multiplication.'''
    def rand_pair(self):
        leftdim = random.randrange(1,30)
        innerdim = random.randrange(1,30)
        rightdim = random.randrange(1,30)
        dense1 = DenseTensor(numpy.random.random((leftdim, innerdim)))
        dense2 = DenseTensor(numpy.random.random((innerdim, rightdim)))
        return dense1, dense2

    def test_denseprod(self):
        for i in range(5):
            # Create pairs of arrays
            dense1, dense2 = self.rand_pair()
            result = dense1 * dense2
            self.assertEqual(result.shape, (dense1.shape[0], dense2.shape[1]))

    def test_tensordot(self):
        # Test degenerate case of two 1-d vectors
        t1 = DictTensor(ndim=1)
        t2 = DictTensor(ndim=1)
        t1[0] = 1
        t1[2] = 2
        t2[0] = 3
        t2[1] = 4
        t2[2] = 5
        self.assertEqual(13, t1.tensordot(t2, 0))
        self.assertEqual(13, t1.tensordot(t2.to_dense(), 0))
        self.assertEqual(13, t1.to_dense().tensordot(t2, 0))
        self.assertEqual(13, t1.to_dense().tensordot(t2.to_dense(), 0))

        for i in range(5):
            # Make a random, randomly-shaped 3D tensor
            shape = random.sample(xrange(1,30), 3)
            tensor = DenseTensor(numpy.random.random(shape))
            
            # Pick a random one of those dimensions
            dim = random.randrange(3)
        
            # Make a random vector of that length
            vec = DenseTensor(numpy.random.random((shape[dim],)))

            # Try the dense result
            result = tensor.tensordot(vec, dim)

            self.assertEqual(result.shape, tuple(shape[:dim]+shape[dim+1:]))

            # Try it with the tensor being sparse.
            sparset = tensor.to_sparse()
            result_s = sparset.tensordot(vec, dim)
            self.assertEqual(result_s.shape, result.shape)
            for key, val in result.iteritems():
                self.assertAlmostEqual(val, result_s[key])

class NormalizeTest(TensorTest):
    data = [[-5, 0, 0, 0],
            [0, 1, -2, 3],
            [100, 2, 0, 0]]
    
    def setUp(self):
        self.tensor = DenseTensor(zeros((3, 4)))
        self.tensor.update(nested_list_to_dict(self.data))

        self.normalized = NormalizedView(self.tensor, mode=0)

        self.randomtensor = DenseTensor(numpy.random.normal(size=(5, 8)))
        self.randomnormal = NormalizedView(self.randomtensor, mode=0)

    def test_norms(self):
        self.assertAlmostEqual(self.normalized[0,0], -1.0)
        self.assertAlmostEqual(self.normalized[2,0], 0.99980006)
        for i in range(5):
            row = [self.randomnormal[i,j] for j in range(8)]
            self.assertAlmostEqual(numpy.dot(row, row), 1.0)

# Use a matrix with a known SVD in order to test the values
# of the u / v / sigma matrices
svd_2d_test_matrix = numpy.zeros((4, 5))
svd_2d_test_matrix[0, 0] = 1
svd_2d_test_matrix[0, 4] = 2
svd_2d_test_matrix[1, 2] = 3
svd_2d_test_matrix[3, 1] = 4

class SVD2DTest(TensorTest):
    def setUp(self):
        self.tensor = DictTensor(2)
        # Note: this command actually puts 20 values in tensor!
        self.tensor.update(nested_list_to_dict(svd_2d_test_matrix))
        self.svd = self.tensor.svd(k=3)
        self.incremental = self.tensor.incremental_svd(k=3, niter=200)
        self.u, self.svals, self.v = self.svd.u, self.svd.svals, self.svd.v

    def test_incremental(self):
        self.assertEqual(self.incremental.u.shape[0], self.tensor.shape[0])
        self.assertEqual(len(self.incremental.svals), self.incremental.u.shape[1])
        self.assertEqual(len(self.incremental.svals), self.incremental.v.shape[1])
        self.assertEqual(self.incremental.v.shape[0], self.tensor.shape[1])

        self.assertTensorEqual(self.incremental.u, 
                               [[0, 0, 1],
                                [0, 1, 0],
                                [0, 0, 0],
                                [1, 0, 0]])

        self.assertTensorEqual(self.incremental.v, 
                               [[0, 0, sqrt(.2)],
                                [1, 0, 0],
                                [0, 1, 0],
                                [0, 0, 0],
                                [0, 0, sqrt(.8)]])

        self.assertTensorEqual(self.incremental.svals,
                               [4, 3, sqrt(5)])

    def test_decomposition(self):
        self.assertEqual(self.u.shape[0], self.tensor.shape[0])
        self.assertEqual(len(self.svals), self.u.shape[1])
        self.assertEqual(len(self.svals), self.v.shape[1])
        self.assertEqual(self.v.shape[0], self.tensor.shape[1])

        self.assertTensorEqual(self.u, 
                               [[0, 0, 1],
                                [0, -1, 0],
                                [0, 0, 0],
                                [1, 0, 0]])

        self.assertTensorEqual(self.v, 
                               [[0, 0, sqrt(.2)],
                                [1, 0, 0],
                                [0, -1, 0],
                                [0, 0, 0],
                                [0, 0, sqrt(.8)]])

        self.assertTensorEqual(self.svals,
                               [4, 3, sqrt(5)])

    def test_reconstructed(self):
        self.assertTensorEqual(self.svd.reconstructed,
                               [[1, 0, 0, 0, 2],
                                [0, 0, 3, 0, 0],
                                [0, 0, 0, 0, 0],
                                [0, 4, 0, 0, 0]])
        self.assertTensorEqual(self.svd.reconstructed[1,:],
                                [0, 0, 3, 0, 0])
        self.assertTensorEqual(self.svd.reconstructed[:,2],
                               [0, 3, 0, 0])

    def test_orthonormality(self):
        identity = [[1, 0, 0],
                     [0, 1, 0],
                     [0, 0, 1]]
        self.assertTensorEqual(self.u.T * self.u,
                               identity)

        self.assertTensorEqual(self.v.T * self.v,
                               identity)
    
    def test_variance(self):        
        # Assert that the SVD explained some of the variance.
        diff_k3 = self.tensor - self.svd.reconstructed
        tensor_mag = self.tensor.magnitude()
        diff_k3_mag = diff_k3.magnitude()
        self.assert_(tensor_mag > diff_k3_mag)

        # Check that a smaller SVD explains less of the variance, but still some.
        svd_k1 = self.tensor.svd(k=1)
        diff_k1 = self.tensor - svd_k1.reconstructed
        diff_k1_mag = diff_k1.magnitude()
        self.assert_(tensor_mag > diff_k1_mag > diff_k3_mag)

class NormalizedSVD2DTest(TensorTest):
    def setUp(self):
        self.tensor = DictTensor(2)
        self.tensor.update(nested_list_to_dict(
                numpy.random.random_sample((10, 12))))
        self.normalized_tensor = self.tensor.normalized()
        self.svd = self.normalized_tensor.svd(k=3)
        self.u, self.svals, self.v = self.svd.u, self.svd.svals, self.svd.v

    def test_decomposition(self):
        self.assertEqual(self.u.shape[0], self.tensor.shape[0])
        self.assertEqual(len(self.svals), self.u.shape[1])
        self.assertEqual(len(self.svals), self.v.shape[1])
        self.assertEqual(self.v.shape[0], self.tensor.shape[1])

        # Assert that the singular values are decreasing 
        for i in range(1,len(self.svals)): 
            self.assert_(self.svals[i] < self.svals[i-1]) 

    def test_reconstructed(self):
        pass # TODO

    def test_orthonormality(self):
        self.assertTensorEqual(self.u.T * self.u, numpy.eye(self.u.shape[1]))
        self.assertTensorEqual(self.v.T * self.v, numpy.eye(self.u.shape[1]))
    
    def test_variance(self):        
        return # TODO
        # Assert that the SVD explained some of the variance.
        diff_k3 = self.tensor - self.svd.reconstructed
        tensor_mag = self.tensor.magnitude()
        diff_k3_mag = diff_k3.magnitude()
        self.assert_(tensor_mag > diff_k3_mag)

        # Check that a smaller SVD explains less of the variance, but still some.
        svd_k1 = self.tensor.svd(k=1)
        diff_k1 = self.tensor - svd_k1.reconstructed
        diff_k1_mag = diff_k1.magnitude()
        self.assert_(tensor_mag > diff_k1_mag > diff_k3_mag)


normalize_testcase2 = [[1, 0],
                       [3, 4]]

normalize_testcase3 = [[70, 0],
                       [3, 4]]



class NormalizedSVD2DTest2(TensorTest):
    def assertItemsEqual(self, t1, t2):
        for key in t1.iterkeys():
            self.assertAlmostEqual(t1[key], t2[key])
        

    def test_svd(self):
        t1 = DictTensor(2)
        t1.update(nested_list_to_dict(normalize_testcase2))
        svd1 = t1.normalized().svd(k=1)

        t2 = DictTensor(2)
        t2.update(nested_list_to_dict(normalize_testcase3))
        svd2 = t2.normalized().svd(k=1)
        self.assertItemsEqual(svd1.u, svd2.u)
        self.assertItemsEqual(svd1.svals, svd2.svals)
        self.assertItemsEqual(svd1.v, svd2.v)


class OrderedSetTest(unittest.TestCase):
    def test_reprOfEmpty(self):
        repr(OrderedSet())

# Runner stuff
import types
class AbstractSkippingTestLoader(unittest.TestLoader):
    def loadTestsFromModule(self, module):
        tests = [self.loadTestsFromTestCase(v) for v in globals().values()
                 if isinstance(v, (type, types.ClassType))
                 and issubclass(v, unittest.TestCase)
                 and not v.__dict__.get('is_abstract', False)]
        
        return self.suiteClass(tests)

#from ipdb import post_mortem
class DebugTestProgram(unittest.TestProgram):
    def parseArgs(self, argv):
        self.debug = '--debug' in argv
        if self.debug:
            argv.remove('--debug')
        return super(DebugTestProgram, self).parseArgs(argv)
    
    def runTests(self):
        if self.debug:
            try:
                return self.test.debug()
            except Exception:
                print "Entering post-mortem debugger."
                import pdb; pdb.post_mortem()
        else:
            return super(DebugTestProgram, self).runTests()

if __name__ == '__main__':
    DebugTestProgram(testLoader=AbstractSkippingTestLoader())
    #unittest.main(testLoader=AbstractSkippingTestLoader())
# how to run this under ipython:
#import tests
#tests.AbstractSkippingTestLoader().loadTestsFromModule(tests).debug()
