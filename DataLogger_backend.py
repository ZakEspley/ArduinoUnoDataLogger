# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'DataLogger.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

'''
This file is used to run the back-end of the data collected. It creates
'''

from PyQt5 import QtCore, QtGui, QtWidgets
import matplotlib
import sys
matplotlib.use("Qt5Agg")
import numpy as np
import numpy.random as random
import serial
import warnings
from serial import SerialException, portNotOpenError, Serial
import serial.tools.list_ports as list_ports
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import time
from collections import deque
import struct
from scipy.signal import butter, filtfilt, lfilter, lfilter_zi

# class Ui_DataLoggerMainWindow(object):
#     def setupUi(self, DataLoggerMainWindow):
#         DataLoggerMainWindow.setObjectName("DataLoggerMainWindow")
#         DataLoggerMainWindow.resize(1138, 732)
#         self.centralwidget = QtWidgets.QWidget(DataLoggerMainWindow)
#         self.centralwidget.setObjectName("centralwidget")
#         self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.centralwidget)
#         self.verticalLayout_3.setObjectName("verticalLayout_3")
#         self.mpl_plot = DynamicMplCanvas(self.centralwidget)
#         sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
#         sizePolicy.setHorizontalStretch(0)
#         sizePolicy.setVerticalStretch(0)
#         sizePolicy.setHeightForWidth(self.mpl_plot.sizePolicy().hasHeightForWidth())
#         self.mpl_plot.setSizePolicy(sizePolicy)
#         self.mpl_plot.setObjectName("mpl_plot")

#         # self.verticalLayout_3.addWidget(self.mpl_plot)
#         # self.horizontalLayout = QtWidgets.QHBoxLayout()
#         # self.horizontalLayout.setObjectName("horizontalLayout")
#         # self.startButton = QtWidgets.QPushButton(self.centralwidget)
#         # # self.startButton.setObjectName("startButton")
#         # # self.horizontalLayout.addWidget(self.startButton)
#         # # self.stopButton = QtWidgets.QPushButton(self.centralwidget)
#         # # self.stopButton.setObjectName("stopButton")
#         # # self.horizontalLayout.addWidget(self.stopButton)
#         # # self.saveButton = QtWidgets.QPushButton(self.centralwidget)
#         # # self.saveButton.setObjectName("saveButton")
#         # # self.horizontalLayout.addWidget(self.saveButton)
#         # spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
#         # self.horizontalLayout.addItem(spacerItem)
#         # self.verticalLayout_3.addLayout(self.horizontalLayout)
#         # DataLoggerMainWindow.setCentralWidget(self.centralwidget)
#         # self.menubar = QtWidgets.QMenuBar(DataLoggerMainWindow)
#         # self.menubar.setGeometry(QtCore.QRect(0, 0, 1138, 22))
#         # self.menubar.setObjectName("menubar")
#         # self.menuDatalogger = QtWidgets.QMenu(self.menubar)
#         # self.menuDatalogger.setObjectName("menuDatalogger")
#         # DataLoggerMainWindow.setMenuBar(self.menubar)
#         # self.statusbar = QtWidgets.QStatusBar(DataLoggerMainWindow)
#         # self.statusbar.setObjectName("statusbar")
#         # DataLoggerMainWindow.setStatusBar(self.statusbar)
#         # self.menubar.addAction(self.menuDatalogger.menuAction())

#         # self.retranslateUi(DataLoggerMainWindow)
#         # self.startButton.clicked.connect(self.mpl_plot.start)
#         # self.stopButton.clicked.connect(self.mpl_plot.stop)
#         # self.saveButton.clicked.connect(self.mpl_plot.save)
#         # QtCore.QMetaObject.connectSlotsByName(DataLoggerMainWindow)

#     def retranslateUi(self, DataLoggerMainWindow):
#         _translate = QtCore.QCoreApplication.translate
#         DataLoggerMainWindow.setWindowTitle(_translate("DataLoggerMainWindow", "MainWindow"))
#         # self.startButton.setText(_translate("DataLoggerMainWindow", "Start"))
#         # self.stopButton.setText(_translate("DataLoggerMainWindow", "Stop"))
#         # self.saveButton.setText(_translate("DataLoggerMainWindow", "Save Data"))
#         # self.menuDatalogger.setTitle(_translate("DataLoggerMainWindow", "Datalogger"))


class MplCanvas(FigureCanvas):
    
    def __init__(self, parent=None):
        fig = Figure()
        self.ax = fig.add_subplot(111)
        self.compute_initial_figure()
        super().__init__(fig)

        self.setParent(parent)
        FigureCanvas.setSizePolicy(self, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def compute_initial_figure(self):
        pass

class DynamicMplCanvas(MplCanvas):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent = kwargs["parent"]
    
    def compute_initial_figure(self):
        self.ax.set_ylim(0,10)
        self.ax.set_facecolor("black")
        self.ax.grid(color='gray', linestyle='--')
    
    def update_figure(self):


        unpacked = struct.unpack("B"*len(self.parent.raw_data), self.parent.raw_data)

        if len(unpacked) > 0:

            self.parent.raw_data = b''
            i = 0
            while i < len(unpacked):
                if i%(self.parent.BUF_SIZE) == 0 and i !=self.parent.BUF_SIZE:
                    t = (unpacked[i] + unpacked[i+1]*256 + unpacked[i+2]*256**2
                        +unpacked[i+3]*256**3)/1e6
                    i += 4
                    if abs(t - self.parent.time_buffer[-1]) < 1/(self.parent.sample_rate*1.05):
                        t = self.parent.time_buffer[-1] + 1/self.parent.sample_rate
                    voltage = unpacked[i]*self.parent.proportion

                else:
                    voltage = unpacked[i]*self.parent.proportion

                    t = self.parent.time_buffer[-1] + 1/(self.parent.sample_rate)
                    

                self.parent.time_buffer.append(t)
                self.parent.filter_buffer.append(voltage)

                i += 1

            self.ax.cla()


            if self.parent.j == 0:
                self.parent.filter_z = lfilter_zi(self.parent.butter_b, self.parent.butter_a)
            self.parent.time_buffer.popleft()
            self.parent.filter_buffer.popleft()
            if self.parent.lp_state:
                temp, self.parent.filter_z = lfilter(self.parent.butter_b, self.parent.butter_a,self.parent.filter_buffer, zi=self.parent.filter_z)
                self.parent.ydata.extend(temp)
                self.parent.filter_buffer.clear()
                self.parent.filter_buffer.append(temp[-1])
                k = 0
                while k < len(temp): 
                    self.parent.results.append([self.parent.time_buffer[k], temp[k]])
                    k += 1
            else:
                self.parent.ydata.extend(self.parent.filter_buffer)
                k = 0

                while k < len(self.parent.time_buffer): 
                    self.parent.results.append([self.parent.time_buffer[k], self.parent.filter_buffer[k]])
                    k += 1
                last_voltage = self.parent.filter_buffer.pop()
                self.parent.filter_buffer.clear()
                self.parent.filter_buffer.append(last_voltage)
            
            self.parent.xdata.extend(self.parent.time_buffer)
            
            last_time = self.parent.time_buffer.pop()
            self.parent.time_buffer.clear()
            self.parent.time_buffer.append(last_time)
            
            self.parent.j = i

            self.ax.plot(self.parent.xdata, self.parent.ydata, "y-")
            self.ax.set_xlim(-self.parent.delta+self.parent.xdata[len(self.parent.xdata)-1], self.parent.xdata[len(self.parent.xdata)-1])
            self.ax.set_ylim(0+self.parent.voltage_offset,self.parent.ylim+self.parent.voltage_offset)
            self.ax.set_facecolor("black")
            self.ax.grid(color='gray', linestyle='--')
            self.draw()

class DataCollector(QtCore.QThread):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
    
    
    def run(self):
        while True:
            if self.parent.arduino.in_waiting >= self.parent.BUF_SIZE:

                self.parent.raw_data += self.parent.arduino.read(size=self.parent.BUF_SIZE)
           



if __name__ == "__main__":
    ser = find_arduino()
    app = QtWidgets.QApplication(sys.argv)
    window = DataLogger()
    # ui = Ui_DataLoggerMainWindow()
    # ui.setupUi(window)
    window.show()

    arduino = find_arduino()
    if not arduino:
        err = QtWidgets.QErrorMessage()
        err.showMessage("No arduinos found! Are you sure it is connected properly?")
        # raise IOError("No Arduino")
    if len(arduino) > 1:
        warn = QtWidgets.QMessageBox()
        warn.setText("Multiple Arduinos found. Usinig the first one.")
        warn.setIcon(QtWidgets.QMessageBox.Warning)
        warn.show()
    
    if arduino:
        arduino = Serial(port=arduino[0], baudrate=2000000)
        window.mpl_plot.arduino = arduino
    

    
    sys.exit(app.exec_())


