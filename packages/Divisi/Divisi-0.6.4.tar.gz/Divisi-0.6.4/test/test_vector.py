from csc.divisi.tensor import DenseTensor
from csc.divisi.labeled_view import LabeledView
from nose.tools import eq_, assert_almost_equal, raises
from numpy import zeros, sqrt

def testDotProduct():
    # Set up two tensors
    tensor = DenseTensor(zeros((5,)))
    tensor2 = DenseTensor(zeros(5,))
    # Dot them
    result = tensor * tensor2
    eq_(result, 0)

def testAdding():
    # Set up two tensors.
    tensor = DenseTensor(zeros((5,)))
    tensor2 = DenseTensor(zeros(5,))
    tensor2[3] = 3
    # Add them.
    result = tensor + tensor2
    assert (result._data == [0,0,0,3,0]).all()

@raises(ValueError)
def test_add_length_mismatch():
    DenseTensor(zeros((5,))) + DenseTensor(zeros(3,))

@raises(TypeError)
def test_add_shape_mismatch():
    DenseTensor(zeros((5,))) + DenseTensor(zeros(5,5))

def testVectorNorm():
    tensor = DenseTensor(zeros((5,)))
    tensor[0] = 1
    tensor[1] = 5
    assert_almost_equal(tensor.norm(), sqrt(26.0))
    normalized = tensor.normalized_copy()
    assert_almost_equal(normalized*normalized, 1.0)
    assert_almost_equal(normalized.norm(), 1.0)

def test_cosine_angle():
    v1 = DenseTensor(zeros((5,)))
    v2 = DenseTensor(zeros((5,)))
    v1[0] = v2[0] = 5
    assert_almost_equal(v1.cosine_of_angle_to(v2), 1.0)

    v1 = DenseTensor(zeros((5,)))
    v2 = DenseTensor(zeros((5,)))
    v1[0] = v2[1] = 5
    assert_almost_equal(v1.cosine_of_angle_to(v2), 0.0)

    v1 = DenseTensor(zeros((5,)))
    v2 = DenseTensor(zeros((5,)))
    v1[0] = 5
    v2[0] = -5
    assert_almost_equal(v1.cosine_of_angle_to(v2), -1.0)


def test_extremes():
    tensor = DenseTensor(zeros(100,))
    for i in range(100):
        tensor[i] = i*10

    extremes = tensor.extremes()
    bottom, top = extremes[:10], extremes[10:]
    eq_(bottom, [((i,), i*10.) for i in range(10)])
    eq_(top, [((i,), i*10.) for i in range(90,100)])
    

def empty_labeled_dense_vector(labels):
    return LabeledView(DenseTensor(zeros((len(labels),))), [labels])
    
labels = ['a', 'b', 'c']

def test_add_labeled():
    # Make two tensors
    tensor = empty_labeled_dense_vector(labels)
    tensor['c'] = 3
    
    tensor2 = empty_labeled_dense_vector(labels)
    tensor2['a'] = 2

    # Add.
    result = tensor + tensor2
    eq_(result['a'], 2)
    eq_(result['b'], 0)
    eq_(result['c'], 3)

@raises(IndexError) # Should fail because the new dense tensor would have to be bigger
def test_labeled_add_mismatch():
    # Set up the other tensor
    tensor = empty_labeled_dense_vector(labels)
    tensor['c'] = 3

    tensor2 = empty_labeled_dense_vector(['q','r','s'])
    tensor2['q'] = 2

    tensor + tensor2
