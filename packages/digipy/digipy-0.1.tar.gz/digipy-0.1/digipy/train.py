#!/usr/bin/env python
''' demo training of a Neural Network using flayers '''
import sys
import time
import pylab
import flayers as fl
from optparse import OptionParser
from digipy.pkg_util import find_pkg_file

def parse_opts():
    parser = OptionParser()

    parser.add_option("-f", "--file", dest="filename", default='digits.data',
                      help="dataset input filename")
    parser.add_option("-e", dest="n", default=10, type=int, help="# epoch")
    parser.add_option("-t", "--train", dest="train", default=0.5, 
                      type=float, help="# epoch")
    parser.add_option("-v", "--valid", dest="valid", default=0.3, 
                      type=float, help="# epoch")
    parser.add_option("-T", "--test", dest="test", default=0.2, 
                      type=float, help="# epoch")
    parser.add_option("-s", "--save", dest="save_fname", default="test",
                      help="save filename")

    (options, args) = parser.parse_args()
    return options

def main():
    options = parse_opts()
    print "dataset file:", find_pkg_file(options.filename)
    data_options = "-d %s -t %s -v %s -T %s" % (find_pkg_file(options.filename),
                                                options.train,
                                                options.valid,
                                                options.test)

    trainer = fl.fexp("%s / -e 0 -h 100 --oh --lsm -l 0.01 -o %s" 
                      % (data_options, options.save_fname))

    error_train=[]
    error_valid=[]
    x=[]
    start = time.time()


    print "#,time,train error,valid error"
    for i in range(int(options.n)):
        errt = trainer.train(1)
        error_train.append(errt)
        stop = time.time()
        errv = trainer.test('v')
        error_valid.append(errv)
        ti = stop - start
        x.append(ti)
        print "%2s %2s %2s %2s" %(i,ti, errt, errv)

    if options.test>0:
        err_test = trainer.test('T')
        print "test error = %s" %err_test

    pylab.plot(x,error_train,'o-b')
    pylab.plot(x,error_valid,'o-g')
    pylab.xlabel("time (sec)")
    pylab.ylabel("Error classification %")
    pylab.legend(("training error","validation error"))
    pylab.title("%s error classification" % options.filename)
    pylab.show()

if __name__ == '__main__':
    main()
