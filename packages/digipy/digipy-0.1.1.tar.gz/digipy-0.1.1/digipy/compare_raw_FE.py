''' compare raw & extraction features test classification results '''
from mlboost.nn import nn
from numpy import arange, array
from numpy.random import random
from digipy.image_util import *
from mlboost.core import extract_features
from digipy.pkg_util import find_pkg_file

FE_fcts = [surface, convolution_digits_mean]


raw_nn = nn.load(find_pkg_file('digits_raw.save'))
opt_nn = nn.load(find_pkg_file('digits_opt.save'))

ds_fname = find_pkg_file('datasets/digits/digits.csv')
tds, std, mu, n_inputs, n_outputs, vds, Tds = nn.load_dataset(ds_fname,
                                                              norm=False, test=0,                                                             validation= 0.2)
noise = 0.0


def add_noise(x):
    if random()>0.5:
        return min(x+noise*16*random(), 16)
    else:
        return max(x-noise*16*random(), 0)

def add_noise2(x):
    if random()>0.5:
        return x  + (16-x) * noise * random()
    else:
        return x - noise * x * random()

def get_noised_dataset(ds, noise):
    new_ds=[]
    for inputs, target in ds:
        new_inputs = array(map(add_noise, inputs), float)
        new_ds.append((new_inputs, target))
    return new_ds

def get_fe_dataset(ds, FE_fcts):
    new_ds=[]
    for inputs, target in ds:
        new_inputs = extract_features(inputs, FE_fcts)
        new_ds.append((new_inputs, target))
    return new_ds   

def main():
    raw_errors = []
    fe_errors = []
    noise_values = arange(0, 1, 0.1)
    print "noise raw_test_error fe_test_error"
    for noise in noise_values:
        globals()['noise'] = noise
        ds = get_noised_dataset(vds, noise)
        fe_ds = get_fe_dataset(ds, FE_fcts) 
        raw_error = raw_nn.test(ds, True, True)
        fe_error = opt_nn.test(fe_ds, True, True)
        print "%s%% %s%% %s%%" % (noise*100, raw_error, fe_error)    
        raw_errors.append(raw_error)
        fe_errors.append(fe_error)
        
    try:
        import pylab
        pylab.plot(noise_values*100, raw_errors,'o-b')
        pylab.plot(noise_values*100, fe_errors,'o-g')
        pylab.xlabel("noise %")
        pylab.ylabel("test error classification %")
        pylab.legend(("Raw inputs (64 pixels)", "Extracted Features (11)"))
        pylab.title("raw vs FE error classification comparison")
        pylab.show()
    except Exception,ex:
        print ex

if __name__ == '__main__':
    main()

