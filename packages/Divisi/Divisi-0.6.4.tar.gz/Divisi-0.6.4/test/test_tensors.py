from csc.divisi.tensor import DenseTensor
from csc.divisi.labeled_view import LabeledView
from nose.tools import eq_, assert_raises
from numpy import zeros

def test_iter_dim_keys():
    raw = DenseTensor(zeros((2, 3)))
    labels = [['a', 'b'], ['c', 'd', 'e']]
    tensor = LabeledView(raw, labels)

    i = 0
    for key in tensor.iter_dim_keys(0):
        eq_(key, labels[0][i])
        i += 1
    eq_(i, 2)

    i = 0
    for key in tensor.iter_dim_keys(1):
        eq_(key, labels[1][i])
        i += 1
    eq_(i, 3)

def test_combine_by_element():
    t1 = LabeledView(DenseTensor(zeros((2,2))), [['a', 'b'], ['c', 'd']])
    t2 = LabeledView(DenseTensor(zeros((2,2))), [['a', 'b'], ['c', 'd']])
    t1['a', 'c'] = 1
    t1['b', 'c'] = 2
    t2['a', 'c'] = 4
    t2['a', 'd'] = 5

    t3 = t1.combine_by_element(t2, lambda x, y: x + (2*y))
    eq_(t3['a', 'c'], 9)
    eq_(t3['b', 'c'], 2)
    eq_(t3['a', 'd'], 10)
    eq_(t3['b', 'd'], 0)

    t4 = DenseTensor(zeros((3, 2)))
    assert_raises(IndexError, lambda: t1.combine_by_element(t4, lambda x, y: x + y))
    t4 = DenseTensor(zeros((2, 2, 1)))
    assert_raises(IndexError, lambda: t1.combine_by_element(t4, lambda x, y: x + y))
