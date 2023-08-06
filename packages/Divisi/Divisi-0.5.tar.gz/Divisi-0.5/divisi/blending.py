from divisi.cnet import conceptnet_2d_from_db, conceptnet_2d_from_db_tuple
from divisi.labeled_tensor import SparseLabeledTensor
from divisi.util import get_picklecached_thing
from divisi.export_svdview import export_svdview
import cPickle as pickle
import gzip, os

#os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'csamoa.settings')

def pickledump(filename, obj):
    if not isinstance(filename, basestring):
        filename, obj = obj, filename
    f = gzip.open(filename, 'wb')
    pickle.dump(obj, f)
    f.close()

def normalize_and_copy(tensor):
    newt = SparseLabeledTensor(ndim=2)
    newt.update(tensor.normalized())
    return newt

def normalize_and_copy_mode_one(tensor):
    newt = SparseLabeledTensor(ndim=2)
    newt.update(tensor.normalized(mode=1))
    return newt

def run_3blend_simple(tensor1, tensor2, tensor3, factor=None, factor2=None):
    tensor1 = normalize_and_copy(tensor1)
    tensor2 = normalize_and_copy(tensor2)
    tensor3 = normalize_and_copy(tensor3)
    
    if factor is None: 
        factor = find_rough_factor(tensor1, tensor2)
        print "Using factor: ", factor
    
    blend = tensor1*(1-factor) + tensor2*factor

    if factor2 is None: 
        factor2 = find_rough_factor(blend, tensor3)
        print "Using factor2: ", factor2

    blend2 = blend*(1-factor2) + tensor3*factor2
    svd = blend2.svd(k=50)
    #svd.summarize(k=10)
    return svd

def run_blend_simple(tensor1, tensor2, factor=None):
    tensor1 = normalize_and_copy(tensor1)
    tensor2 = normalize_and_copy(tensor2)
    
    if factor is None:
        factor = find_rough_factor(tensor1, tensor2)
        print "Using factor: ", factor
    
    blend = tensor1*(1-factor) + tensor2*factor
    svd = blend.svd(k=50)
    #svd.summarize()
    return svd

def find_rough_factor(tensor1, tensor2):
    # Only first sigmas
    t1 = tensor1.svd(k=20) 
    sigma1 = t1.svals[0:10]
    a = sigma1[0]
    t2 = tensor2.svd(k=20)
    sigma2 = t2.svals[0:10]
    b = sigma2[0]
    return float(a/(a+b))
    
def pickledumpsvd(svd, basename):
    svd_u, svd_s, svd_v, svd_a = ['pickle/'+ basename + '_%s_.4f.pickle.gz' % (typ) for typ in ['u', 's', 'v', 'a']]
    pickledump(svd_u, svd.u)
    pickledump(svd_s, svd.svals)
    pickledump(svd_v, svd.v)
    pickledump(svd_a, blend)
    

def conceptnet_with_custom_identities(identconst=20):
    cnet = conceptnet_2d_from_db('en', identities=0.0)
    for concept in cnet.label_list(0):
        cnet[concept, "DescribedAs/"+concept] = identconst
        cnet[concept, "IsA/"+concept] = identconst
    for (key, value) in cnet.iteritems():
        concept, feature = key
        if value < 0:
            if feature.startswith('CapableOf') or feature.endswith('CapableOf') or feature.startswith('Desires') or feature.endswith('Desires'): continue
            cnet[key] = 0
    return cnet

def get_yelp_blend():
    cnettensor = get_picklecached_thing('cnet.pickle',
      conceptnet_with_custom_identities, 'ConceptNet')
    # To regenerate these next two, run yelp_matrix_creation.py
    yelpwordstensor = get_picklecached_thing('yelp-tfidf.pickle', None, 'Yelp TFIDF')
    yelpcatstensor = get_picklecached_thing('yelp_cats_and_price.pickle', None, 'Yelp Cats')
    print yelpwordstensor
    print yelpcatstensor
    return run_3blend_simple(cnettensor, yelpwordstensor, yelpcatstensor, None,
    0.03)

if __name__ == '__main__':    
    svd = get_picklecached_thing('yelp-cnet-blend.pickle', get_yelp_blend)
    export_svdview(svd, "/csc/svdview/data/yelp-tweek.tsv")
