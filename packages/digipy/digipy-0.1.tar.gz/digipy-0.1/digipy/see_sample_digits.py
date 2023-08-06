#!/usr/bin/python
''' show dataset train and test samples '''

from optparse import OptionParser
import sys
import flayers as fl
from random import choice

from mlboost.core import ppdataset
from mlboost.core import pphisto
from mlboost.image.util import *
from digipy.pkg_util import find_pkg_file

N_CHARACTER = 10
N_TEST_PER_CHARACTER = 4

def parse_opts():
    parser = OptionParser(description=__doc__)

    dataset_fname = 'digits-train.csv'
    trained_fname = 'digits-train.save'
    base_dir =  find_pkg_file(os.path.join('datasets','digits'))

    parser.add_option("-d", "--dataset", dest="dataset_fname", 
                      default=dataset_fname, help="dataset fname")
    parser.add_option("-b", "--base", dest="base_trained_dir", default=base_dir,
                      help="default training neural network base directory")
    parser.add_option("-t", "--trained-nn", dest="trained_fname", 
                      default=trained_fname, 
                      help="neural net parameters filename")

    options, args = parser.parse_args()
    return options

def sorted_best_guess(trainer, n):
    probs={}
    for i in range(10):
        probs[i]=trainer.prob(i)
        sprobs=pphisto.SortHistogram(probs,False,True)
        
    print "top %s choices" %n
    for el in sprobs[0:3]:
        print "digit %s -> %.0f%%" %(el[0],el[1])    
    return probs

def main():
    options = parse_opts()
    print "Loading training set"
    dataset_train = ppdataset.Dataset(find_pkg_file(options.dataset_fname),
                                      exception_continuous_fields=[])

    figure()
    gray()
    figtitle="Example of training digits"
    t = gcf().text(0.5, 0.95, figtitle, horizontalalignment='center')
    for i in range(N_CHARACTER):
        subplot(4,3,i+1)
        title("digit %s" % i)
        idigits = dataset_train.GetConstrainedData(('digit',i))
        input = choice(idigits)[:-1]
        imshow(toimage(input))

    pyshow()
    raw_input()

    print "Loading test set + experimentation"
    fname = 'digits-test.csv'
    dataset = ppdataset.Dataset(find_pkg_file(fname), 
                                exception_continuous_fields=[])
    print "Loading pre trained neural network"

    trainer = fl.loadTrainer(find_pkg_file(options.trained_fname), 
                           options.base_trained_dir)

    print "select randomly 3 digits"
    choices = []
    for i in range(3):
        choices.append(choice([x for x in range(1,N_CHARACTER+1) if x not 
    in choices]))

    print "Digit %s choices: %s" %(3,choices)
    for i in choices:
        for j in range(N_TEST_PER_CHARACTER):
            n = sqrt(N_TEST_PER_CHARACTER)
            subplot(n, n, j+1)
            idigits = dataset.GetConstrainedData(('digit',i))
            input = choice(idigits)[:-1]
            digit = int(fl.fprop(input,trainer))
            prob = trainer.prob(digit)
            sorted_best_guess(trainer, 3)
            title('Digit %s : prediction %s prob=%.0f%%' % (i, digit,
                                                            round(prob)))
            imshow(toimage(input))
        print "Press any key"
        pyshow()
        raw_input()
        
        
if __name__ == '__main__':
    main()
