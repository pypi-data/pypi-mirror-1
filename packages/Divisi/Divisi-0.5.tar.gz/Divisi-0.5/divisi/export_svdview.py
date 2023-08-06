#from divisi import *
#from divisi.cnet import *
from csamoa.conceptnet import Concept

def unstem(lstem):
    '''
    Takes the stem of a concept and returns its unstemmed version.
    '''
    if isinstance(lstem, tuple):
        stem, lang = lstem
    else:
        stem = lstem
        lang = 'en'
    try: 
        concept = Concept.get_raw(stem, lang)
        result = concept.canonical_name.lower()
    except Concept.DoesNotExist:
        result = stem
    if lang != 'en': return '%s [%s]' % (result, lang)
    else: return result

def export_svdview(svd, outfn, unstem=unstem):
    '''
    Export a tab-separated value file that can be visualized
    with svdview. The data is saved to the file named _outfn_.
    '''
    out = open(outfn, 'wb')
    for lstem in svd.u.label_list(0):
        concept = unstem(lstem)
        data = svd.u[lstem,:].tensor._data[0:40]
        #data += svd.u[lstem,:].tensor._data[1:40:2]
        #for i in range(0, 40, 2): data[i//2] *= svd.svals[i]
        datastr = '\t'.join(str(x) for x in data)
        print >> out, "%s\t%s" % (concept.encode('utf-8'), datastr)
    out.close()

def write_packed(matrix, out_basename, unstem=unstem, cutoff=40):
    '''
    Export in the new binary coordinate file format.

    Format description:
    Everything is stored in big-endian (network) byte order.
    Header:
    4 bytes: number of dimensions (integer)
    4 bytes: number of items (integer)
    Body:
    a sequence of items (no separator)
    each item has a coordinate for each dimension (specified in the header)
    each coordinate is an IEEE float (32-bit) in big-endian order.
    '''
    
    import struct
    names = open(out_basename+'.names','wb')
    coords = open(out_basename+'.coords', 'wb')

    num_vecs, num_dims = matrix.shape
    if num_dims > cutoff: num_dims = cutoff
    coords.write(struct.pack('>ii', num_dims, num_vecs))

    # Write the whole file.
    format_str = '>' + 'f'*num_dims
    for concept in sorted(matrix.iter_dim_keys(0)):
        data = map(float, matrix[concept,:].tensor._data[:num_dims])
	coords.write(struct.pack(format_str, *data))
        names.write(unstem(concept).encode('utf-8')+'\n')

    names.close()
    coords.close()
    
        


