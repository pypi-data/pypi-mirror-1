#!/usr/bin/env python
import urllib
import gzip
import cPickle as pickle

def main():
    print 'Retrieving tensor...'
    fname, headers = urllib.urlretrieve('http://openmind.media.mit.edu/en/tensor.gz')
    print 'loading pickle...'
    t=pickle.load(gzip.open(fname,'rb'))

    if t.shape[0]*t.shape[1] > 10000000:
        print 'success!'
    else:
        print 'hm, kinda small.'

if __name__ == '__main__':
    main()

