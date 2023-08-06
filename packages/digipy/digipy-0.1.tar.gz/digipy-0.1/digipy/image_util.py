#!/usr/bin/env python
''' extract feature util functions '''

from numpy import array
from numpy import where
import pickle  

from digipy.pkg_util import find_pkg_file

# load data required to compute digit convolution
try:
    f = open(find_pkg_file('mean_digits.txt'))
    digits_mean = pickle.load(f)
    if False:
        for el in digits_mean:
            print digits_mean[el]
    f.close()
except:
    raise("can't load precomputed train digits means")

def inverse(input):
    m = max(input)
    return array([m-x for x in input])

def surface(input):
    return [inverse(input).sum()]

def convolution_digits_mean(input, max_val=16):
    return [(input / max_val * digits_mean[i]).sum() / digits_mean[i].sum() 
            for i in range(10)]
    
def extract_start_stop(inputs, threshold=0, line_size=8):
    outputs = []
    for i in range(8):
        line = inputs[i * 8:(i+1) * 8]
        idxs= where (line > threshold)[0]
        if len(idxs) == 0:
            outputs.extend([-1,-1])
        else:
            if len(idxs)==1:
                min_x = idxs[0]
                max_x = idxs[0]      
            else:
                min_x = idxs[0]
                max_x = idxs[-1]
            if min_x>max_x:
                msg = "min > max; %s %s; idx %s" % (min_x, max_x, idxs)
                raise ValueError(msg)
            outputs.extend([min_x, max_x])

    return outputs

def extract_estimation_surface(inputs):
    outputs = extract_start_stop(inputs)
    volume = 0
    for i in range(8):
        volume += outputs[i*2+1] - outputs[i*2]
    return [volume]
        
def get_start_stop_header(nlines):
    header=[]
    for i in range(1,nlines+1):
        header.append("start_line_%i" %i)
        header.append("stop_line_%i" %i)
    return header

def extract_features(inputs, fcts):
    outputs = []
    if not isinstance(fcts, list):
        fcts = [fcts]
    for fct in fcts:
        outputs.extend(fct(inputs))
    return outputs




