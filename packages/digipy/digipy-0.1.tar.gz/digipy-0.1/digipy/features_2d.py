#!/usr/bin/env python
''' demo of feature 2D visualization to see possible clusters '''

import os, sys
from mlboost.core import ppdataset
from matplotlib import pylab
import colorsys
from digipy.pkg_util import find_pkg_file
from optparse import OptionParser


def parse_opts():
    parser = OptionParser(description=__doc__)

    input_fname = os.path.join('datasets', 'digits', 'fe-digits-all.csv')
    parser.add_option("-f", "--file", dest="filename", default=input_fname,
                      help="neural net parameters filename")
    parser.add_option("-x", dest="x", default="convol_0", help="x field name")
    parser.add_option("-y", dest="y", default="convol_8", 
                      help="y field name")
    parser.add_option("-C", dest="classes", default=None, 
                      help="list of classes to see; default all")
    parser.add_option("-c", "--choices", dest="choices", action= "store_true", 
                      default = False, help="show field choices")

    options, args = parser.parse_args()
    return options

def main():
    options = parse_opts()

    classes = None
    if options.classes:
        classes = options.classes.split(',')
        classes = ["digit %s" %el for el in classes] 

    ds = ppdataset.Dataset(find_pkg_file(options.filename), 
                           exception_continuous_fields=['digit', 
                                                        'start_line_4'])

    if options.choices:
        print "fields choices:"
        for field in ds.fields:
            print field
        sys.exit(0)

    xys = ds.GetXY(options.x, options.y, 'digit')
    if classes:
        xys = dict([(k, xys[k]) for k in xys if k in classes])

    n = len(xys)

    # add each class 2D points
    for i,class_value in enumerate(xys):
        if not options.classes or class_value in classes:
            x = xys[class_value].x
            y = xys[class_value].y
            color = colorsys.hsv_to_rgb(1.0 * i / (n+1), 0.8, 1)
            pylab.plot(x, y, 'o', color=color)

    pylab.title("Digits 2D cluster visualization") 
    pylab.xlabel(options.x)
    pylab.ylabel(options.y)
    pylab.legend(classes or xys.keys())
    pylab.show()

if __name__ == '__main__':
    main()
