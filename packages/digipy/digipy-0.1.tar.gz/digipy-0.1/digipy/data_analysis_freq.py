#!/usr/bin/env python
''' demo feature analysis (frequency distributions) '''
import os, sys
from optparse import OptionParser

from digipy.pkg_util import find_pkg_file
from mlboost.core.pylabhisto import *
from mlboost.core import ppdataset


def filter(dists, corr, options):
    if options.fields:
        selected_dist={}
        selected_corr={}
        for field in options.fields.split(","):
            selected_dist[field] = dists[field]
            selected_corr[field] = corr[field]
        return selected_dist, selected_corr
    else:
        return dists, corr

def parse_opts():
    parser = OptionParser(description=__doc__)
    input_fname = os.path.join('datasets','digits','fe-digits-all.csv')
    parser.add_option("-f", "--file", dest="filename", default=input_fname,
                      help="neural net parameters filename")
    parser.add_option("-c", "--choices", dest="choices", action= "store_true", 
                      default = False, help="show field choices")
    parser.add_option("-n", "--nbins", dest="nbins", default = 20, 
                      help="nbins use to split frequency distributions")
    parser.add_option("-C", "--min-correlation", dest="min_corr", default=0.1,
                      help="min correlation [0-1]")
    parser.add_option("-F", "--fields", dest="fields", default = False, 
                      help="fields choices; default all fields")
    parser.add_option("-d", "--digit", dest="digit", default=None, 
                      help="digit to analyse; default all")

    (options, args) = parser.parse_args()
    return options

def main():
    options = parse_opts()
    ds = ppdataset.Dataset(find_pkg_file(options.filename), 
                           exception_continuous_fields=['digit'])

    if options.choices:
        print "fields choices:"
        for field in ds.fields:
            print field
        sys.exit(0)

    # set digits list 
    digits = range(10)
    if options.digit:
        digits=[int(options.digit)]

    # for all digits, show field distribution
    for i in digits:
        dists, corr, ngood, nbad = ds.GetBinDists('digit', str(i), 
                                                  nbins=int(options.nbins), 
                                                  verbose=True)
        dists, corr = filter(dists, corr, options)
        ShowBucketBinCorr(dists, 4 ,corr, options.min_corr)
 
if __name__ == '__main__':
    main()
