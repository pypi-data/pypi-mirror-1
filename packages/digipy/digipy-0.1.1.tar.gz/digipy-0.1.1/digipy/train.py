#!/usr/bin/env python
''' demo training of a Neural Network using mlboost '''
import sys
import time
from mlboost.nn import nn
from optparse import OptionParser
from digipy.pkg_util import find_pkg_file

def parse_opts():
    parser = OptionParser(description=__doc__)

    parser.add_option("-f", "--file", dest="filename", default='digits.csv',
                      help="dataset input filename")
    parser.add_option("-e", dest="n", default=10, type=int, help="# epoch")
    parser.add_option("-t", "--train", dest="train", default=0.7, 
                      type=float, help="# epoch")
    parser.add_option("-v", "--valid", dest="valid", default=0.3, 
                      type=float, help="# epoch")
    parser.add_option("-T", "--test", dest="test", default=0, 
                      type=float, help="# epoch")
    parser.add_option("-s", "--save", dest="save_fname", default="test",
                      help="save filename")
    parser.add_option("--h", dest="n_hiddens", type=int, 
                      default=100, help="set nb of hidden neurons")
    parser.add_option("-l", "--lr", dest="lr", type=float, default=0.001,
                      help="set mode_learning rate")
                      
    options, args = parser.parse_args()
    return options

def main():
    options = parse_opts()
    print "dataset file:", find_pkg_file(options.filename)

    tds, std, mu, n_inputs, n_outputs, vds, Tds = nn.load_dataset((find_pkg_file(options.filename)), verbose=False)
    trainer = nn.NeuralNet(n_inputs, options.n_hiddens, n_outputs) 
    error_train=[]
    error_valid=[]
    x=[]
    start = time.time()


    print "#,time,train error,valid error"
    for i in range(int(options.n)):
        trainer.train(tds, epochs=1, verbose=False, lr=options.lr)
        errt = trainer.test(tds)
        error_train.append(errt)
        stop = time.time()
        errv = trainer.test(vds)
        error_valid.append(errv)
        ti = stop - start
        x.append(ti)
        print "%2s %2s %2s %2s" %(i, ti, errt, errv)

    if options.test>0:
        err_test = trainer.test(Tds)
        print "test error = %s" %err_test

    try:
        import pylab
        pylab.plot(x,error_train,'o-b')
        pylab.plot(x,error_valid,'o-g')
        pylab.xlabel("time (sec)")
        pylab.ylabel("Error classification %")
        pylab.legend(("training error","validation error"))
        pylab.title("%s error classification" % options.filename)
        pylab.show()
    except:
        pass

if __name__ == '__main__':
    main()
