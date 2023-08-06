from cnet import conceptnet_queryset, get_relationtype_names, peopl_person, scorecurve, DEFAULT_IDENTITY_WEIGHT, DEFAULT_CUTOFF
from divisi.labeled_tensor import SparseLabeledTensor

def cnet_queryset_to_3tensor(queryset):
    relationtype_name = get_relationtype_names()
    tensor = SparseLabeledTensor(ndim=3)
    for (reltype, concept1, concept2, score, polarity) in queryset.values_list(
        'relation_id', 'concept1__text',  'concept2__text',  'score', 'polarity'
        ).iterator():
        
        tensor[peopl_person(concept1),
               relationtype_name[reltype],
               peopl_person(concept2)] = polarity*scorecurve(score)
    return tensor

def add_identities(tensor, relation='Identity', weight=DEFAULT_IDENTITY_WEIGHT):
    for text in list(tensor.label_list(0)):
        tensor[text, relation, text] = weight


def conceptnet_3d_from_db(lang,
                          identities=DEFAULT_IDENTITY_WEIGHT,
                          cutoff=DEFAULT_CUTOFF):
    '''Create a basic ConceptNet tensor from the database.
    Keys will be: [left concept, relation, right concept].
    '''
    tensor = cnet_queryset_to_3tensor(conceptnet_queryset(lang, cutoff))
    if identities:
        add_identities(tensor, identities)
    return tensor
