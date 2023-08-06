#!/usr/bin/env python
''' demo features extraction '''

from numpy import zeros
import pickle
import pylab
from optparse import OptionParser

from digipy.pkg_util import find_pkg_file
from mlboost.core import ppdataset

N_CHARACTER = 10

def parse_opts():
    parser = OptionParser(description=__doc__)

    parser.add_option("-i", "--info", dest="show_info", action="store_false", 
                      default = True, help="don't show features info")

    options, args = parser.parse_args()
    return options

def gen_digits_mean(options):
    # Load dataset
    input_fname = find_pkg_file('digits-train.csv')
    ds = ppdataset.Dataset(input_fname, exception_continuous_fields=[])

    # Compute mean of each digits
    print "Extracting digit train mean"
    output = open('mean_digits.txt', 'w')
    digits_mean = {}

    max_pixel = ds.data.max()
    for i in range(N_CHARACTER):
        idigits = ds.GetConstrainedData(('digit', i))/max_pixel
        mean = zeros(8*8)
        for j in range(8*8):
            mean[j] = idigits[:, j].sum()/len(idigits)
        digits_mean[i]=mean

    pickle.dump(digits_mean, output)
    output.close()


def gen_data_sets(options):
    gen_digits_mean(options)

    # IMPORTANT: this import should happen after the creation of
    # mean_digits.txt
    from digipy.image_util import *
    # Headers related stuff
    header_start_stop = get_start_stop_header(8)

    header_opt=[]
    header_opt.append('surface')
    header_opt.extend(['convol_%i' % i for i in range(10)])

    header_simple = list(header_start_stop)
    header_simple.append('estimation_surface')

    header_all=list(header_simple)
    header_all.extend(header_opt)
    ds = ppdataset.Dataset(input_fname, exception_continuous_fields=['digit'])

    # Extract features + generate flayers format file
    print "Extracting features"
    ds_simple = ds.ExtractFeatures([extract_start_stop, 
                                    extract_estimation_surface],
                                   'digit', 
                                   'fe-digits-simple.csv', 
                                   feature_names=header_simple)
    ds_opt = ds.ExtractFeatures([surface, convolution_digits_mean], 
                                'digit',
                                'fe-digits-opt.csv', 
                                feature_names=header_opt)
    ds_all = ds.ExtractFeatures([extract_start_stop, 
                                 extract_estimation_surface, 
                                 surface, 
                                 convolution_digits_mean],
                                'digit',
                                'fe-digits-all.csv', 
                                feature_names=header_all)
def main():
    options = parse_opts()
    ds_simple, ds_opt, ds_all = gen_data_sets(options)

    print "Generating flayers file format"
    for ds, fname in [(ds_simple, "fe-digits-simple"), 
                      (ds_opt, "fe-digits-opt"), 
                      (ds_all, "fe-digits-all")]:
        ds.GenFlayerFormat('digit', fname)

        if options.show_info:

            info, prob = ds.GetInfos('digit', False, True)

            def show_feature_value(info, title_str):
                xlabels = []
                yval = []
                for x, y in info:
                    xlabels.append(x)
                    yval.append(y)
                    xval = range(len(xlabels))
                pylab.title(title_str)
                pylab.bar(xval, yval)
                pylab.xticks(xval, xlabels, rotation='vertical')

            pylab.subplot(221)
            show_feature_value(info, "Features Entropy")
            pylab.subplot(222)
            show_feature_value(prob, "Features Info (probability)")
            pylab.show()


if __name__ == '__main__':
    main()
