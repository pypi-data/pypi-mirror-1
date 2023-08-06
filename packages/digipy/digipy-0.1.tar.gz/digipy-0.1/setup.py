#!/usr/bin/env python
# -*- coding: utf-8 -*-
#  Copyright (C) 2006-2009 Francis Piéraut <fpieraut@gmail.com>
#  Copyright (C) 2009 Yannick Gingras <ygingras@ygingras.net>

#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.

#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.

#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

"A cool demo for Montreal Python 6 that does real time digits recognition"

from setuptools import setup, find_packages
from digipy import __version__

setup(name='digipy',
      version=__version__,
      author='Francis Pieraut',
      author_email='fpieraut@gmail.com',
      description = __doc__,
      license="AGPL v3 or later",
      packages = find_packages(),
      include_package_data=True,
      install_requires=["mlboost>=0.4"],
      entry_points={
      'console_scripts': ["digipy = digipy.app:main",
                          "digipy-freq-analysis = digipy.data_analysis_freq:main",
                          "digipy-features2D = digipy.features_2d:main",
                          "digipy-train = digipy.train:main",
                          "digipy-extract-features = digipy.extract_features:main",
                          "digipy-see-data = digipy.see_sample_digits:main"],
      
      }
)
