#!/usr/bin/env python
''' define find_pkg_file '''

import os
import digipy
from pkg_resources import resource_filename, resource_exists


digit_path = os.path.join('datasets', 'digits') 
pkg_digit_path = os.path.join(digipy.__name__, 'datasets', 'digits') 

def find_pkg_file(fname):

    if os.path.isfile(fname):
        return fname
    elif os.path.isfile(os.path.join(digit_path, fname)):
        return os.path.join(digit_path, fname)
    elif resource_exists(digipy.__name__, fname):
        return resource_filename(digipy.__name__, fname)
    elif resource_exists(pkg_digit_path, fname):
        return resource_filename(pkg_digit_path, fname)
    else:
        raise ValueError("Can't find resource %s" % fname)
    


