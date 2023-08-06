#!/usr/bin/python
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

''' Define UI class used for the hand digits recognition demo '''

from StringIO import StringIO
import os
from random import choice, random

from numpy import array

from PyQt4 import QtGui, QtCore

opencv_installed = False
try:
    import opencv
    from opencv import highgui
    opencv_installed = True
except Exception, ex:
    print ex
    print "forcing testing option"
    pass

import Image
from PIL.ImageDraw import Draw
from ImageFilter import *
import ImageEnhance


from ui.ui_campui_gui import Ui_CampuiGui

from digipy.pkg_util import find_pkg_file

from mlboost.nn import nn
from mlboost.core import ppdataset
from mlboost.core import pphisto
from mlboost.image.util import toimage
from mlboost.core import extract_features

# On some machines this seems to be 0, on others its 1.
CV_CAM_INDEX = 0
CAM_IMG_WIDTH = 200
NN_IMG_WITH = CAM_IMG_WIDTH


def blackwhite(im, higher=256, lower=0, k=1.0/3):
    ''' force a black and with transformation; 
        k is a value between 0 and 1 '''
    min, max = im.getextrema()
    t = min + max * k
    def x(v):
        if v>t:
            return higher 
        return lower
    return im.point(x)

filters={}
filters['BLUR']=BLUR
filters['CONTOUR']=CONTOUR
filters['DETAIL']=DETAIL
filters['EDGE_ENHANCE']=EDGE_ENHANCE
filters['EDGE_ENHANCE_MORE']=EDGE_ENHANCE_MORE
filters['EMBOSS']=EMBOSS
filters['FIND_EDGES']=FIND_EDGES
filters['SMOOTH']=SMOOTH
filters['SMOOTH_MORE']=SMOOTH_MORE
filters['SHARPEN']=SHARPEN
 
def new_dim(w, h, max_side):
    scale = 1.0*max(w, h)/max_side
    return (int(w/scale), int(h/scale))

def scale(img, max_side, aa=True):
    w, h = img.size
    ndim = new_dim(w, h, max_side)
    if aa:
        return img.resize(ndim, Image.ANTIALIAS)
    else:
        return img.resize(ndim)

def pil_img_to_qpixmap(img):
    io = StringIO()
    img.save(io, "BMP")
    pix = QtGui.QPixmap()
    pix.loadFromData(io.getvalue())
    return pix

class CampuiGui(QtGui.QDialog, Ui_CampuiGui):
    def __init__(self, options=None, *args):
        self.options = options
        if not opencv_installed:
            self.options.test = True

        QtGui.QDialog.__init__(self, *args)
        self.setupUi(self)
        self.refresh_timer = QtCore.QTimer()
        
        self.noise.setValue(options.noise)
        self.contrast.setValue(options.contrast)
        self.target = '?'
        self.nframe = 0 
        self.nframe_bad = 0.0
        if options.test:
            input_fname = find_pkg_file('digits-train.csv')
            self.ds = ppdataset.Dataset(input_fname,
                                        exception_continuous_fields=[])
            
        else:
            self.cam = highgui.cvCreateCameraCapture(CV_CAM_INDEX)
            if not self.cam:
                raise RuntimeError("Cannot access the webcam")
            
        self.connect(self.refresh_timer, 
                     QtCore.SIGNAL("timeout()"), 
                     self.refresh_cam)
        
        self.refresh_timer.start(options.refresh_timer)
        
        fname = find_pkg_file(options.filename)
        print "loading:", fname
        self.nn = nn.load(fname)
        self.position_lcd_1.display(1)
        self.position_lcd_2.display(2)
        self.position_lcd_3.display(3)
        self.guess_lcd_i=[self.guess_lcd_1, self.guess_lcd_2, 
                          self.guess_lcd_3]
        self.prob_lcd_i=[self.prob_lcd_1, self.prob_lcd_2,
                         self.prob_lcd_3]
        self.pal_guess_lcd_1 = self.guess_lcd_1.palette()
        
    def refresh_cam(self):
            
        if self.options.test:
            idigits= self.ds.GetConstrainedData(('digit', 
                                                 choice(range(10))))
            input = choice(idigits)
            self.target_lcd.display(int(input[-1]))
            self.target = int(input[-1])
            input = input[:-1]
            # keep reference to check feature extraction
            self.dataset_test_input = input
            img = Image.new("L", (8, 8))
            d = Draw(img)
            
            def normalized(x, y):
                return round(input[y * 8 + x] * 256.0/16)
            
            # set pixel values
            for x in range(8):
                for y in range(8):
                    d.point((x, y), normalized(x, y))
        else:
            img = self.capture_image()

        # refresh raw input display
        scale_img=scale(img, NN_IMG_WITH*1.5)
        self.cam_lbl.setPixmap(pil_img_to_qpixmap(scale_img))
        big_nnet_input = scale(img.resize((8,8)), NN_IMG_WITH)
        self.nnet_input_lbl_raw.setPixmap(pil_img_to_qpixmap(big_nnet_input))
            
        sprobs, nnet_input = self.analyse_image(img)

        guess = sprobs[0][0]        
        prob = sprobs[0][1]
        
        if not self.options.test:
            self.target_lcd.display(int(guess))
        
        self.pal_guess_lcd_1.setColor(self.pal_guess_lcd_1.Foreground, 
                                     QtGui.QColor(0,0,0))
        
        self.nframe += 1
        if self.target !='?' and self.target != guess:
            self.pal_guess_lcd_1.setColor(self.pal_guess_lcd_1.Foreground, 
                                    QtGui.QColor(255,0,0))
            self.nframe_bad += 1
        
        self.error_lcd.display(self.nframe_bad/self.nframe*100) 
        for i in range(3):
            self.guess_lcd_i[i].display(sprobs[i][0])
            self.prob_lcd_i[i].display(int(sprobs[i][1]))
            

        # The prob LCD receives a color that reflects how confident we
        # are in the guess.
        col = QtGui.QColor()

        # green is roughly h=120
        for i in range(3):
            col.setHsv( sprobs[i][1]*1.2, 200, 255)
            palette_prob = self.prob_lcd_i[i].palette()
            palette_digit = self.prob_lcd_i[i].palette()
            palette_prob.setColor(palette_prob.Foreground, col)
            palette_digit.setColor(palette_digit.Foreground, col)

    def capture_image(self):
        ''' return img and pix '''
        frame = highgui.cvQueryFrame(self.cam)
        mat = opencv.cvGetMat(frame)
        img = scale(opencv.adaptors.Ipl2PIL(mat), CAM_IMG_WIDTH)
        return img

    def analyse_image(self, img):
        ''' return sorted digits (digits,probs) and neural net image input''' 
        # black and white conversion
        filter_choice = str(self.filter.currentText())
        if self.options.verbose:
            print "applying filter :", filter_choice
        
        im_fil = img.copy()
        if filter_choice in filters:
            im_fil = img.filter(filters[filter_choice])
        
        contrast = 1.0 + float(self.contrast.value()) / 100
        if self.options.verbose:
            print "contrast", contrast,self.contrast.value()
        if self.contrast.value() > 0:
            enh = ImageEnhance.Contrast(im_fil)
            im_fil = enh.enhance(contrast)
    
        bw_im = im_fil.convert("L")
        if filter_choice == "BLACKWHITE":
            bw_im = blackwhite(bw_im)
        
        if self.inverse.isChecked():
            bw_im = bw_im.point(lambda x:256-x)
        
        if self.box_digit.isChecked():
            box = bw_im.getbbox()
            bw_im = bw_im.crop(box)
        
        resize_im = bw_im.resize((8,8))

        if self.noise.value() > 0:

            def add_noise(x):
                if random()>0.5:
                    return min(x + float(self.noise.value())/100 
                               * 256 * random(), 256)
                else:
                    return max(x - float(self.noise.value()/100)
                               * 256 * random(), 0)

            resize_im = resize_im.point(add_noise)
        
        # refresh preprocessing image
        big_nnet_input = scale(resize_im, NN_IMG_WITH)
        self.nnet_input_lbl.setPixmap(pil_img_to_qpixmap(big_nnet_input))
        
        inputs = array(array(resize_im).flatten(), float) / 256 * 16
   
        if self.options.bypass_pp:
            inputs = self.dataset_test_input

        if self.options.FE_fcts:
            inputs = extract_features(inputs, self.options.FE_fcts)
            if self.options.test_extraction_features:
                ref_inputs = extract_features(self.dataset_test_input, 
                                              self.options.FE_fcts)
                if inputs != ref_inputs:
                    print "extracted features:",inputs
                    print "expected features :",ref_inputs
                    raise(ValueError("Something is wrong with extraction_features_option"))
                    
            inputs = array(array(inputs).flatten(), float)
        self.nn.fprop(inputs, normalize=True)

        probs={}
        nnprobs = self.nn.probs()
        for i in range(10):
            probs[i]=nnprobs[i]

        sprobs=pphisto.SortHistogram(probs,False,True)
                
        return sprobs, resize_im
