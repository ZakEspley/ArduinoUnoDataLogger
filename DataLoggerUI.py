# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'DataLogger.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
from DataLogger_backend import *

class Ui_DataLoggerMainWindow(object):
    def setupUi(self, DataLoggerMainWindow):
        DataLoggerMainWindow.setObjectName("DataLoggerMainWindow")
        DataLoggerMainWindow.resize(1138, 732)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(DataLoggerMainWindow.sizePolicy().hasHeightForWidth())
        DataLoggerMainWindow.setSizePolicy(sizePolicy)
        DataLoggerMainWindow.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
        self.centralwidget = QtWidgets.QWidget(DataLoggerMainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.mpl_plot = DynamicMplCanvas(parent=self)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.mpl_plot.sizePolicy().hasHeightForWidth())
        self.mpl_plot.setSizePolicy(sizePolicy)
        self.mpl_plot.setObjectName("mpl_plot")
        self.verticalLayout_3.addWidget(self.mpl_plot)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")

        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")

        self.SampleRateLabel = QtWidgets.QLabel(self.centralwidget)
        self.SampleRateLabel.setObjectName("SampleRateLabel")
        self.horizontalLayout_3.addWidget(self.SampleRateLabel)

        self.lpFilterLabel = QtWidgets.QLabel(self.centralwidget)
        self.lpFilterLabel.setObjectName("lpFilterLabel")
        self.lpFilterCheckbox = QtWidgets.QCheckBox(self.centralwidget)

        self.SampleRateCombo = QtWidgets.QComboBox(self.centralwidget)
        self.SampleRateCombo.setObjectName("SampleRateCombo")
        self.SampleRateCombo.addItems([
            "{0}".format(1), 
            "{0}".format(2),
            "{0}".format(4),
            "{0}".format(5),
            "{0}".format(10),
            "{0}".format(25),
            "{0}".format(40),
            "{0}".format(80),
            "{0}".format(100),
            "{0}".format(125),
            "{0}".format(200),
            "{0}".format(250),
            "{0}".format(500),
            "{0}".format(625),
            "{0}".format(1000),
            "{0}".format(2500),
            "{0}".format(3125),
            "{0}".format(5000),
            "{0}".format(6250),
            "{0}".format(10000),
            "{0}".format(12500),
            "{0}".format(25000),
            "{0}".format(31250),
            "{0}".format(62500),
            ])
        self.horizontalLayout_3.addWidget(self.SampleRateCombo)
        self.horizontalLayout_3.addWidget(self.lpFilterLabel)
        self.horizontalLayout_3.addWidget(self.lpFilterCheckbox)

        
        self.timeSizeLabel = QtWidgets.QLabel(self.centralwidget)
        self.timeSizeLabel.setObjectName("timeSizeLabel")
        self.horizontalLayout_2.addWidget(self.timeSizeLabel)
        self.timeSizeSpinbox = QtWidgets.QSpinBox(self.centralwidget)
        self.timeSizeSpinbox.setMinimum(1)
        self.timeSizeSpinbox.setMaximum(9)
        self.timeSizeSpinbox.setProperty('value', 6)
        self.timeSizeSpinbox.setObjectName("timeSizeSpinbox")
        self.horizontalLayout_2.addWidget(self.timeSizeSpinbox)
        self.timeSizeMultiLabel = QtWidgets.QLabel(self.centralwidget)
        self.timeSizeMultiLabel.setObjectName("timeSizeMultiLabel")
        self.horizontalLayout_2.addWidget(self.timeSizeMultiLabel)
        self.timeSizeMultiSpinbox = QtWidgets.QSpinBox(self.centralwidget)
        self.timeSizeMultiSpinbox.setMinimum(-5)
        self.timeSizeMultiSpinbox.setMaximum(2)
        self.timeSizeMultiSpinbox.setProperty('value', 1)
        self.timeSizeMultiSpinbox.setObjectName('timeSizeMultiSpinbox')
        self.horizontalLayout_2.addWidget(self.timeSizeMultiSpinbox)

        self.voltageSizeLabel = QtWidgets.QLabel(self.centralwidget)
        self.voltageSizeLabel.setObjectName("voltageSizeLabel")
        self.horizontalLayout_2.addWidget(self.voltageSizeLabel)
        self.voltageSizeSpinbox = QtWidgets.QSpinBox(self.centralwidget)
        self.voltageSizeSpinbox.setMinimum(1)
        self.voltageSizeSpinbox.setMaximum(10)
        self.voltageSizeSpinbox.setProperty('value', 10)
        self.voltageSizeSpinbox.setObjectName("voltageSizeSpinbox")
        self.horizontalLayout_2.addWidget(self.voltageSizeSpinbox)
        self.voltageSizeMultiLabel = QtWidgets.QLabel(self.centralwidget)

        self.voltageOffsetLabel = QtWidgets.QLabel(self.centralwidget)
        self.voltageOffsetLabel.setObjectName("voltageOffsetLabel")
        self.horizontalLayout_2.addWidget(self.voltageOffsetLabel)
        self.voltageOffsetSpinbox = QtWidgets.QDoubleSpinBox(self.centralwidget)
        self.voltageOffsetSpinbox.setMinimum(0)
        self.voltageOffsetSpinbox.setMaximum(10)
        self.voltageOffsetSpinbox.setDecimals(1)
        self.voltageOffsetSpinbox.setSingleStep(0.2)
        self.voltageOffsetSpinbox.setProperty('value', 0)
        self.voltageOffsetSpinbox.setObjectName("voltageOffsetSpinbox")
        self.horizontalLayout_2.addWidget(self.voltageOffsetSpinbox)

        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem)
        self.horizontalLayout_2.addItem(spacerItem)
        self.verticalLayout_3.addLayout(self.horizontalLayout_3)
        self.verticalLayout_3.addLayout(self.horizontalLayout_2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.startButton = QtWidgets.QPushButton(self.centralwidget)
        self.startButton.setObjectName("startButton")
        self.horizontalLayout.addWidget(self.startButton)
        
        self.refreshButton = QtWidgets.QPushButton(self.centralwidget)
        self.refreshButton.setObjectName("refreshButton")
        self.horizontalLayout.addWidget(self.refreshButton)
        
        self.stopButton = QtWidgets.QPushButton(self.centralwidget)
        self.stopButton.setObjectName("stopButton")
        self.horizontalLayout.addWidget(self.stopButton)
        self.saveButton = QtWidgets.QPushButton(self.centralwidget)
        self.saveButton.setObjectName("saveButton")
        self.horizontalLayout.addWidget(self.saveButton)
        self.arduinosCombo = QtWidgets.QComboBox(self.centralwidget)
        self.arduinosCombo.setObjectName("arduinosCombo")
        self.horizontalLayout.addWidget(self.arduinosCombo)

        self.saveSettingsButton = QtWidgets.QPushButton(self.centralwidget)
        self.saveSettingsButton.setObjectName("saveSettingsButton")
        self.horizontalLayout.addWidget(self.saveSettingsButton)
        self.loadSettingsButton = QtWidgets.QPushButton(self.centralwidget)
        self.loadSettingsButton.setObjectName("loadSettingsButton")
        self.horizontalLayout.addWidget(self.loadSettingsButton)

        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.verticalLayout_3.addLayout(self.horizontalLayout)
        DataLoggerMainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(DataLoggerMainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1138, 22))
        self.menubar.setObjectName("menubar")
        self.menuDatalogger = QtWidgets.QMenu(self.menubar)
        self.menuDatalogger.setObjectName("menuDatalogger")
        DataLoggerMainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(DataLoggerMainWindow)
        self.statusbar.setObjectName("statusbar")
        DataLoggerMainWindow.setStatusBar(self.statusbar)
        self.menubar.addAction(self.menuDatalogger.menuAction())

        self.retranslateUi(DataLoggerMainWindow)
        self.startButton.clicked.connect(self.start)
        self.refreshButton.clicked.connect(self.refresh)
        self.stopButton.clicked.connect(self.stop)
        self.saveButton.clicked.connect(self.save)
        self.timeSizeSpinbox.valueChanged.connect(self.delta_update)
        self.timeSizeMultiSpinbox.valueChanged.connect(self.deltamulti_update)
        self.voltageSizeSpinbox.valueChanged.connect(self.voltage_update)
        self.SampleRateCombo.currentIndexChanged.connect(self.sample_rate_change)
        self.lpFilterCheckbox.clicked.connect(self.toggle_lpfilter)
        self.lpFilterCheckbox.stateChanged.connect(self.toggle_lpfilter)
        self.saveSettingsButton.clicked.connect(self.save_settings)
        self.loadSettingsButton.clicked.connect(self.load_user_settings)
        self.voltageOffsetSpinbox.valueChanged.connect(self.voltage_offset_update)
        QtCore.QMetaObject.connectSlotsByName(DataLoggerMainWindow)

    def retranslateUi(self, DataLoggerMainWindow):
        _translate = QtCore.QCoreApplication.translate
        DataLoggerMainWindow.setWindowTitle(_translate("DataLoggerMainWindow", "MainWindow"))
        self.SampleRateLabel.setText(_translate("DataLoggerMainWindow", "Samples/Second"))
        self.startButton.setText(_translate("DataLoggerMainWindow", "Start"))
        self.refreshButton.setText(_translate("DataLoggerMainWindow", "Refresh"))
        self.stopButton.setText(_translate("DataLoggerMainWindow", "Stop"))
        self.saveButton.setText(_translate("DataLoggerMainWindow", "Save Data"))
        self.timeSizeLabel.setText(_translate("DataLoggerMainWindow", "Time Axis [s]"))
        self.timeSizeMultiLabel.setText(_translate('DataLoggerMainWindow', 'x 10^'))
        self.voltageSizeLabel.setText(_translate("DataLoggerMainWindow", "Voltage Axis [V]"))
        self.lpFilterLabel.setText(_translate("DataLoggerMainWindow", "Low Pass Filter:"))
        self.loadSettingsButton.setText(_translate('DataLoggerMainWindow', 'Load Settings'))
        self.saveSettingsButton.setText(_translate('DataLoggerMainWindow', "Save Current Settings"))
        self.voltageOffsetLabel.setText(_translate('DataLoggerMainWindow', "Voltage DC Offset [V]"))
        self.menuDatalogger.setTitle(_translate("DataLoggerMainWindow", "Datalogger"))

