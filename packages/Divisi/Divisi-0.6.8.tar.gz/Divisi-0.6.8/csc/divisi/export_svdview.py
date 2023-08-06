"""
The ``export_svdview`` module allows SVD results to be visualized using the
separate program ``svdview`` (http://launchpad.net/svdview).

Denormalization
===============

Concepts are often stored in Divisi tensors in a normalized form,
which is often not human-friendly. The ``denormalize`` callback
provides a way "undo" the normalization as concepts are returned. A
denormalizer for ConceptNet concepts is provided, which returns the
"canonical name" of concepts.

File formats
============

Binary format
-------------

The binary format is newer and faster. It consists of a header and a
body (everything is stored in big-endian (network) byte order):

Header:
 * 4 bytes: number of dimensions (integer)
 * 4 bytes: number of items (integer)

The body is a sequence of items with no separator. Each item has a
coordinate for each dimension. Each coordinate is an IEEE float
(32-bit) in big-endian order.

TSV format
----------

The old TSV format is easier to edit by hand or with simple
scripts. Each line is a sequence of fields separated by tabs. The
first field on each line is the concept name. It is followed by a
floating point number for each dimension.

"""
from itertools import izip, imap, count

def denormalize(concept_text):
    '''
    Returns the canonical denormalized (user-visible) form of a
    concept, given its normalized text of a concept.
    '''
    from csc.conceptnet4.models import Concept

    if isinstance(concept_text, tuple):
        text, lang = concept_text
    else:
        text, lang = concept_text, 'en'
    try:
        concept = Concept.get_raw(text, lang)
        result = concept.canonical_name.lower()
    except Concept.DoesNotExist:
        result = text
    if lang != 'en': return '%s [%s]' % (result, lang)
    else: return result

def null_denormalize(x): return x

def _sorted_rowvectors(m, denormalize, num_dims):
    def fix_concept(c):
        if not c: return '_'
        return unicode(c).encode('utf-8')
    tensor = m.tensor
    concepts = sorted(izip(imap(denormalize, m.iter_dim_keys(0)), count()))
    for concept, idx in concepts:
        yield fix_concept(concept), tensor[idx,:]._data[:num_dims]


def write_tsv(matrix, outfn, denormalize=None, cutoff=40):
    '''
    Export a tab-separated value file that can be visualized
    with svdview. The data is saved to the file named _outfn_.
    '''
    if denormalize is None: denormalize = null_denormalize
    num_vecs, num_dims = matrix.shape
    if num_dims > cutoff: num_dims = cutoff

    out = open(outfn, 'wb')
    for concept, vec in _sorted_rowvectors(matrix, denormalize, num_dims):
        datastr = '\t'.join(imap(str, vec))
        out.write("%s\t%s\n" % (concept, datastr))
    out.close()

def write_packed(matrix, out_basename, denormalize=None, cutoff=40):
    '''
    Export in the new binary coordinate file format.
    '''

    import struct
    names = open(out_basename+'.names','wb')
    coords = open(out_basename+'.coords', 'wb')

    if denormalize is None: denormalize = null_denormalize

    num_vecs, num_dims = matrix.shape
    if num_dims > cutoff: num_dims = cutoff
    coords.write(struct.pack('>ii', num_dims, num_vecs))

    # Write the whole file.
    format_str = '>' + 'f'*num_dims
    for concept, vec in _sorted_rowvectors(matrix, denormalize, num_dims):
        coords.write(struct.pack(format_str, *vec))
        names.write(concept+'\n')

    names.close()
    coords.close()

def write_annotated(matrix, out_basename, denormalize=None, cutoff=40,
filter=None, annotations=None):
    '''
    Export in the new binary coordinate file format.
    '''

    import struct
    names = open(out_basename+'.names','wb')
    coords = open(out_basename+'.coords', 'wb')
    annotate = open(out_basename+'.annotate', 'wb')

    if denormalize is None: denormalize = null_denormalize
    if annotations is None: annotations = {}
    if filter is None: filter = lambda: True

    _, num_dims = matrix.shape
    if num_dims > cutoff: num_dims = cutoff
    num_vecs = 0
    for concept, vec in _sorted_rowvectors(matrix, denormalize, num_dims):
        if filter(concept): num_vecs += 1
    coords.write(struct.pack('>ii', num_dims, num_vecs))

    # Write the whole file.
    format_str = '>' + 'f'*num_dims
    for concept, vec in _sorted_rowvectors(matrix, denormalize, num_dims):
        if filter(concept):
            concept = concept.encode('utf-8')
            coords.write(struct.pack(format_str, *vec))
            names.write(concept+'\n')
            if concept in annotations:
                line = annotations[concept].replace('\n', ' ').replace('\r','')
                line = line.encode('utf-8')
                annotate.write(concept+': '+line+'\n')
            else:
                annotate.write('\n')

    names.close()
    coords.close()
    annotate.close()
