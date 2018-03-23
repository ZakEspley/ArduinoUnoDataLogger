from PyQt5 import QtCore, QtGui, QtWidgets
from DataLoggerUI import Ui_DataLoggerMainWindow
import serial
import serial.tools.list_ports as list_ports
import sys
from DataLogger_backend import DataCollector
from collections import deque
import time
import numpy as np
import struct 

class DataLogger(QtWidgets.QMainWindow, Ui_DataLoggerMainWindow):

    def __init__(self):
        super(DataLogger, self).__init__()

        self.setupUi(self)
        self.mpl_plot.compute_initial_figure()
        self.arduino_list = self.find_arduino()
        self.arduino = serial.Serial(port=self.arduino_list[0].device, baudrate=2000000)
        self.mpl_plot.arduino = self.arduino
        self.arduinosCombo.addItems([d.description for d in self.arduino_list])

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.mpl_plot.update_figure)
        self.savefile = ""
        self.t0 = 0
        self.j = 0
        self.results = []
        self.queue_length = 320000
        self.xdata = deque(maxlen=self.queue_length)
        self.ydata = deque(maxlen=self.queue_length)
        self.interval = 1
        self.datacollector = DataCollector(self)
        self.line = None
        self.BUF_SIZE = 6*170
        self.raw_data = b''
        # self.proportion = 10/1024
        self.proportion = 10/256
        self.prescalar = 16
        self.delta = 60
        self.sample_rates = [(4).to_bytes(1, "big"), (5).to_bytes(1, "big"), (6).to_bytes(1, "big"), (7).to_bytes(1, "big")]
        self.prescalars = [16, 32, 64, 128]
        self.rate = 8000
        self.state = False
    
    def find_arduino(self):
        arduino_ports = [p for p in list_ports.comports() if ('USB UART' in p.description or 'Arduino' in p.description)]
        return arduino_ports
    
    def  start(self):
        # if self.t0 == 0:
        #     self.t0 = time.time()
        # self.arduino.write(b"3")
        # self.rate = self.SampleRateSpinbox.value()
        # b1 = int(np.floor(self.rate/256))
        # b2 = self.rate%256
        # print(self.rate)
        # print(b1,b2)
        # self.arduino.write(struct.pack("B", b1))
        # time.sleep(0.1)
        # self.arduino.write(struct.pack("B", b2))
        # time.sleep(0.2)

        # print(self.arduino.read(size=self.arduino.in_waiting))
        # self.datacollector.start()
        if not self.state:
            self.startButton.setText(QtCore.QCoreApplication.translate("DataLoggerMainWindow", 'Pause'))
            self.state = True
            self.arduino.write(b"1")
            self.timer.start(self.interval)
            self.datacollector.start()
        else:
            self.stop()

    def stop(self, *args):
        self.state = False
        self.startButton.setText(QtCore.QCoreApplication.translate("DataLoggerMainWindow",'Start'))
        self.timer.stop()
        self.datacollector.quit()
        self.arduino.write(b'0')
        time.sleep(0.1)
    
    def save(self, *args):
        self.savefile = QtWidgets.QFileDialog.getSaveFileName(filter="*.csv")
        np.savetxt(self.savefile[0], self.results, fmt="%1.8f", delimiter=",")
    
    def refresh(self, *args):
        self.ydata = deque(maxlen=self.queue_length)
        self.xdata = deque(maxlen=self.queue_length)
        self.raw_data = b''
        self.j = 0
        self.mpl_plot.ax.cla()
        self.mpl_plot.ax.set_xlim(-self.delta, 0)
        self.mpl_plot.ax.grid(color='gray', linestyle='--')
        self.mpl_plot.draw()

    def delta_update(self, i):
        self.delta = i*10**self.windowSizeMultiSpinbox.value()
        if not self.state:
            if len(self.xdata) == 0:
                self.mpl_plot.ax.set_xlim(-self.delta, 0)
            else:
                self.mpl_plot.ax.set_xlim(-self.delta+self.xdata[len(self.xdata)-1], self.xdata[len(self.parent.xdata)-1])
            
            self.mpl_plot.draw()

    def deltamulti_update(self, i):
        self.delta = self.windowSizeSpinbox.value() * 10**i
        if not self.state:
            if len(self.xdata) == 0:
                self.mpl_plot.ax.set_xlim(-self.delta, 0)
            else:
                self.mpl_plot.ax.set_xlim(-self.delta+self.xdata[len(self.xdata)-1], self.xdata[len(self.parent.xdata)-1])
            
            self.mpl_plot.draw()
    
    def sample_rate_change(self, index):
        rate = self.sample_rates[index]
        self.prescalar = self.prescalars[index]
        current_state = self.state
        if self.state:
            self.stop()
        self.arduino.write(b'3')
        self.arduino.write(rate)
        time.sleep(0.01)
        if current_state:
            self.start()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = DataLogger()
    window.show()
    sys.exit(app.exec_())