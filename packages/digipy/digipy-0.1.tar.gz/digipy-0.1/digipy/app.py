#!/usr/bin/env python
#  Copyright (C) 2009 Yannick Gingras <ygingras@ygingras.net>
#  Copyright (C) 2009 Francis Pieraut <fpieraut@gmail.com>

#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.

#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.

#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

''' real time hand digit recognition demo application '''

import sys, os

from PyQt4 import QtGui

from optparse import OptionParser

from digipy.image_util import *
from digipy.pkg_util import find_pkg_file
from campui_gui import CampuiGui


def parse_opts():
    base_dir =  find_pkg_file(os.path.join('datasets','digits'))

    parser = OptionParser(description = __doc__)

    parser.add_option("-f", "--file", dest="filename", 
                      default='digits-train.save',
                      help="neural net parameters filename")
    parser.add_option("-t", "--test",dest="test", action="store_true", 
                      default=False, help="test mode")
    parser.add_option("-v", "--verbose",
                      action="store_true", dest="verbose", default=False,
                      help="set verbose to true")
    parser.add_option("-e", dest="FE_fcts", default = None, 
                      help="Feature extraction function")
    parser.add_option("-r", dest="refresh_timer", default=100, type=int, 
                      help="refresh timer")
    parser.add_option("-b", "--base", dest="base_trained_dir", default=base_dir,
                      help="default training nn base directory")

    (options, args) = parser.parse_args()

    if options.FE_fcts == "all":
        options.FE_fcts = [extract_start_stop, extract_estimation_surface, 
                           surface, convolution_digits_mean]
        options.filename = "fe-digits-all.save"
    elif options.FE_fcts == 'simple':
        options.FE_fcts = [extract_start_stop, extract_estimation_surface]
        options.filename = "fe-digits-simple.save"
    elif options.FE_fcts == 'opt':
         options.FE_fcts = [surface, convolution_digits_mean]
         options.filename = "fe-digits-opt.save"
    return options 


def main():
    options = parse_opts()
    app = QtGui.QApplication(sys.argv)
    win = CampuiGui(options)
    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
