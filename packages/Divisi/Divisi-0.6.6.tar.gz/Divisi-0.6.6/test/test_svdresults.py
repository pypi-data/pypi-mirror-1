from nose.tools import *
from csc.divisi.svd import SVD2DResults
from csc.divisi.labeled_view import LabeledSVD2DResults
import numpy as np

k = 50
n_concepts = 1000
n_features = 5000
res = None
labeled = None
def setup():
    global res, labeled
    u = np.rand((n_concepts, k))
    v = np.rand((n_features, k))
    svals = np.linspace(42, 1, k)
    res = SVD2DResults(u, v, svals)
    labeled = LabeledSVD2DResults.layer_on(res, [range(n_concepts), range(n_features)])

#def test_filter_rows():
#    labeled.
