# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'digipy/ui/campui_gui.ui'
#
# Created: Mon Apr 13 23:57:53 2009
#      by: PyQt4 UI code generator 4.3.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_CampuiGui(object):
    def setupUi(self, CampuiGui):
        CampuiGui.setObjectName("CampuiGui")
        CampuiGui.resize(QtCore.QSize(QtCore.QRect(0,0,831,488).size()).expandedTo(CampuiGui.minimumSizeHint()))

        self.vboxlayout = QtGui.QVBoxLayout(CampuiGui)
        self.vboxlayout.setObjectName("vboxlayout")

        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setObjectName("hboxlayout")

        self.groupBox = QtGui.QGroupBox(CampuiGui)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred,QtGui.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.groupBox.setObjectName("groupBox")

        self.vboxlayout1 = QtGui.QVBoxLayout(self.groupBox)
        self.vboxlayout1.setObjectName("vboxlayout1")

        self.cam_lbl = QtGui.QLabel(self.groupBox)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred,QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cam_lbl.sizePolicy().hasHeightForWidth())
        self.cam_lbl.setSizePolicy(sizePolicy)
        self.cam_lbl.setMaximumSize(QtCore.QSize(500,16777215))
        self.cam_lbl.setScaledContents(True)
        self.cam_lbl.setObjectName("cam_lbl")
        self.vboxlayout1.addWidget(self.cam_lbl)
        self.hboxlayout.addWidget(self.groupBox)

        self.groupBox_2 = QtGui.QGroupBox(CampuiGui)
        self.groupBox_2.setObjectName("groupBox_2")

        self.vboxlayout2 = QtGui.QVBoxLayout(self.groupBox_2)
        self.vboxlayout2.setObjectName("vboxlayout2")

        self.hboxlayout1 = QtGui.QHBoxLayout()
        self.hboxlayout1.setObjectName("hboxlayout1")

        self.guess_lcd_1 = QtGui.QLCDNumber(self.groupBox_2)

        font = QtGui.QFont()
        font.setPointSize(12)
        self.guess_lcd_1.setFont(font)
        self.guess_lcd_1.setNumDigits(1)
        self.guess_lcd_1.setSegmentStyle(QtGui.QLCDNumber.Filled)
        self.guess_lcd_1.setObjectName("guess_lcd_1")
        self.hboxlayout1.addWidget(self.guess_lcd_1)

        self.prob_lcd_1 = QtGui.QLCDNumber(self.groupBox_2)
        self.prob_lcd_1.setSmallDecimalPoint(False)
        self.prob_lcd_1.setNumDigits(2)
        self.prob_lcd_1.setSegmentStyle(QtGui.QLCDNumber.Filled)
        self.prob_lcd_1.setObjectName("prob_lcd_1")
        self.hboxlayout1.addWidget(self.prob_lcd_1)

        self.label_2 = QtGui.QLabel(self.groupBox_2)

        font = QtGui.QFont()
        font.setPointSize(16)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.hboxlayout1.addWidget(self.label_2)
        self.vboxlayout2.addLayout(self.hboxlayout1)

        self.hboxlayout2 = QtGui.QHBoxLayout()
        self.hboxlayout2.setObjectName("hboxlayout2")

        self.guess_lcd_2 = QtGui.QLCDNumber(self.groupBox_2)
        self.guess_lcd_2.setNumDigits(1)
        self.guess_lcd_2.setSegmentStyle(QtGui.QLCDNumber.Filled)
        self.guess_lcd_2.setObjectName("guess_lcd_2")
        self.hboxlayout2.addWidget(self.guess_lcd_2)

        self.prob_lcd_2 = QtGui.QLCDNumber(self.groupBox_2)
        self.prob_lcd_2.setSmallDecimalPoint(False)
        self.prob_lcd_2.setNumDigits(2)
        self.prob_lcd_2.setSegmentStyle(QtGui.QLCDNumber.Filled)
        self.prob_lcd_2.setObjectName("prob_lcd_2")
        self.hboxlayout2.addWidget(self.prob_lcd_2)

        self.label_3 = QtGui.QLabel(self.groupBox_2)

        font = QtGui.QFont()
        font.setPointSize(16)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.hboxlayout2.addWidget(self.label_3)
        self.vboxlayout2.addLayout(self.hboxlayout2)

        self.hboxlayout3 = QtGui.QHBoxLayout()
        self.hboxlayout3.setObjectName("hboxlayout3")

        self.guess_lcd_3 = QtGui.QLCDNumber(self.groupBox_2)
        self.guess_lcd_3.setNumDigits(1)
        self.guess_lcd_3.setSegmentStyle(QtGui.QLCDNumber.Filled)
        self.guess_lcd_3.setObjectName("guess_lcd_3")
        self.hboxlayout3.addWidget(self.guess_lcd_3)

        self.prob_lcd_3 = QtGui.QLCDNumber(self.groupBox_2)
        self.prob_lcd_3.setSmallDecimalPoint(False)
        self.prob_lcd_3.setNumDigits(2)
        self.prob_lcd_3.setSegmentStyle(QtGui.QLCDNumber.Filled)
        self.prob_lcd_3.setObjectName("prob_lcd_3")
        self.hboxlayout3.addWidget(self.prob_lcd_3)

        self.label_4 = QtGui.QLabel(self.groupBox_2)

        font = QtGui.QFont()
        font.setPointSize(16)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.hboxlayout3.addWidget(self.label_4)
        self.vboxlayout2.addLayout(self.hboxlayout3)
        self.hboxlayout.addWidget(self.groupBox_2)

        self.vboxlayout3 = QtGui.QVBoxLayout()
        self.vboxlayout3.setObjectName("vboxlayout3")

        self.groupBox_4 = QtGui.QGroupBox(CampuiGui)
        self.groupBox_4.setObjectName("groupBox_4")

        self.nnet_input_lbl_raw = QtGui.QLabel(self.groupBox_4)
        self.nnet_input_lbl_raw.setGeometry(QtCore.QRect(10,40,241,161))
        self.nnet_input_lbl_raw.setScaledContents(True)
        self.nnet_input_lbl_raw.setObjectName("nnet_input_lbl_raw")

        self.nnet_input_lbl = QtGui.QLabel(self.groupBox_4)
        self.nnet_input_lbl.setGeometry(QtCore.QRect(10,240,231,171))
        self.nnet_input_lbl.setScaledContents(True)
        self.nnet_input_lbl.setObjectName("nnet_input_lbl")

        self.label = QtGui.QLabel(self.groupBox_4)
        self.label.setGeometry(QtCore.QRect(10,210,71,18))
        self.label.setObjectName("label")

        self.label_5 = QtGui.QLabel(self.groupBox_4)
        self.label_5.setGeometry(QtCore.QRect(10,20,71,18))
        self.label_5.setObjectName("label_5")
        self.vboxlayout3.addWidget(self.groupBox_4)
        self.hboxlayout.addLayout(self.vboxlayout3)
        self.vboxlayout.addLayout(self.hboxlayout)

        self.hboxlayout4 = QtGui.QHBoxLayout()
        self.hboxlayout4.setObjectName("hboxlayout4")

        self.inverse = QtGui.QCheckBox(CampuiGui)
        self.inverse.setObjectName("inverse")
        self.hboxlayout4.addWidget(self.inverse)

        self.box_digit = QtGui.QCheckBox(CampuiGui)
        self.box_digit.setObjectName("box_digit")
        self.hboxlayout4.addWidget(self.box_digit)

        spacerItem = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout4.addItem(spacerItem)

        self.contrast = QtGui.QSlider(CampuiGui)
        self.contrast.setMouseTracking(True)
        self.contrast.setProperty("value",QtCore.QVariant(10))
        self.contrast.setOrientation(QtCore.Qt.Horizontal)
        self.contrast.setInvertedAppearance(False)
        self.contrast.setTickPosition(QtGui.QSlider.TicksBelow)
        self.contrast.setObjectName("contrast")
        self.hboxlayout4.addWidget(self.contrast)

        self.filter = QtGui.QComboBox(CampuiGui)
        self.filter.setObjectName("filter")
        self.hboxlayout4.addWidget(self.filter)

        self.refresh_btn = QtGui.QPushButton(CampuiGui)
        self.refresh_btn.setObjectName("refresh_btn")
        self.hboxlayout4.addWidget(self.refresh_btn)

        self.pushButton = QtGui.QPushButton(CampuiGui)
        self.pushButton.setObjectName("pushButton")
        self.hboxlayout4.addWidget(self.pushButton)
        self.vboxlayout.addLayout(self.hboxlayout4)

        self.retranslateUi(CampuiGui)
        QtCore.QObject.connect(self.pushButton,QtCore.SIGNAL("clicked()"),CampuiGui.accept)
        QtCore.QMetaObject.connectSlotsByName(CampuiGui)

    def retranslateUi(self, CampuiGui):
        CampuiGui.setWindowTitle(QtGui.QApplication.translate("CampuiGui", "Campui", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("CampuiGui", "Webcam", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_2.setTitle(QtGui.QApplication.translate("CampuiGui", "Guess and probability", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("CampuiGui", "%", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("CampuiGui", "%", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("CampuiGui", "%", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_4.setTitle(QtGui.QApplication.translate("CampuiGui", "Neural Net Input", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("CampuiGui", "Preprocess", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("CampuiGui", "Raw inputs", None, QtGui.QApplication.UnicodeUTF8))
        self.inverse.setText(QtGui.QApplication.translate("CampuiGui", "inverse image", None, QtGui.QApplication.UnicodeUTF8))
        self.box_digit.setText(QtGui.QApplication.translate("CampuiGui", "box digit", None, QtGui.QApplication.UnicodeUTF8))
        self.filter.addItem(QtGui.QApplication.translate("CampuiGui", "NONE", None, QtGui.QApplication.UnicodeUTF8))
        self.filter.addItem(QtGui.QApplication.translate("CampuiGui", "BLUR", None, QtGui.QApplication.UnicodeUTF8))
        self.filter.addItem(QtGui.QApplication.translate("CampuiGui", "BLACKWHITE", None, QtGui.QApplication.UnicodeUTF8))
        self.filter.addItem(QtGui.QApplication.translate("CampuiGui", "CONTOUR", None, QtGui.QApplication.UnicodeUTF8))
        self.filter.addItem(QtGui.QApplication.translate("CampuiGui", "DETAIL", None, QtGui.QApplication.UnicodeUTF8))
        self.filter.addItem(QtGui.QApplication.translate("CampuiGui", "EDGE_ENHANCE", None, QtGui.QApplication.UnicodeUTF8))
        self.filter.addItem(QtGui.QApplication.translate("CampuiGui", "EDGE_ENHANCE_MORE", None, QtGui.QApplication.UnicodeUTF8))
        self.filter.addItem(QtGui.QApplication.translate("CampuiGui", "EMBROSS", None, QtGui.QApplication.UnicodeUTF8))
        self.filter.addItem(QtGui.QApplication.translate("CampuiGui", "FIND_EDGES", None, QtGui.QApplication.UnicodeUTF8))
        self.filter.addItem(QtGui.QApplication.translate("CampuiGui", "SMOOTH", None, QtGui.QApplication.UnicodeUTF8))
        self.filter.addItem(QtGui.QApplication.translate("CampuiGui", "SMOOTH_MORE", None, QtGui.QApplication.UnicodeUTF8))
        self.filter.addItem(QtGui.QApplication.translate("CampuiGui", "SHARPEN", None, QtGui.QApplication.UnicodeUTF8))
        self.refresh_btn.setText(QtGui.QApplication.translate("CampuiGui", "&Refresh", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton.setText(QtGui.QApplication.translate("CampuiGui", "&Close", None, QtGui.QApplication.UnicodeUTF8))

