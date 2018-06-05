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
import configparser
from scipy.signal import lfilter_zi

class DataLogger(QtWidgets.QMainWindow, Ui_DataLoggerMainWindow):

    def __init__(self):
        super(DataLogger, self).__init__()


        self.config = configparser.ConfigParser()
        self.config.read('settings-old.ini')
        self.ylim = int(self.config['DataLogger']['y_lim'])
        self.voltage_reference = float(self.config['DataLogger']['voltage_reference'])
        self.delta_base = int(self.config["DataLogger"]['delta_base'])
        self.delta_multiplyer = int(self.config['DataLogger']['delta_multiplyer'])
        self.delta = self.delta_base * 10**self.delta_multiplyer

        self.sample_rates = [(4).to_bytes(1, "big"), (5).to_bytes(1, "big"), (6).to_bytes(1, "big"), (7).to_bytes(1, "big")]
        self.adc_prescalars = [16, 32, 64, 128]
        self.rate = 8000

        self.setupUi(self)
        self.mpl_plot.compute_initial_figure()

        self.state = False
        self.lp_state = 0

        
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
        self.xdata.append(0)
        self.ydata.append(0)
        self.interval = 1
        self.datacollector = DataCollector(self)
        self.line = None
        self.BUF_SIZE = 1000
        self.raw_data = b''
        # self.proportion = 10/1024

        self.filter_buffer = deque(maxlen=20000)
        self.filter_buffer.append(0)
        self.time_buffer = deque(maxlen=20000)
        self.time_buffer.append(0)

        self.packet_length = deque(maxlen=10000)
        self.filter_z = 0
        
        self.proportion = self.voltage_reference/256
        self.adc_prescalar = 16
        self.timer_prescaler = 8
        self.timer_top = 80
        self.sample_rate = 16e6/(self.timer_prescaler*(1+self.timer_top))

        self.sample_dict = {
                        10: (256, ((4).to_bytes(1, 'big'))),     ### This is equivilent to 256 prescaler in Arduino TCCR1B Register
                        15625: (64, ((3).to_bytes(1, 'big'))),   ### This is equivilent to  64 prescaler in Arduino TCCR1B Register
                        125000: (8, ((2).to_bytes(1, 'big')))    ### This is equivilent to   8 prescaler in Arduino TCCR1B Register
            }
        self.sample_rate_indexes = [1, 2, 4, 5, 10, 25, 40, 80, 100, 125, 200, 250, 500, 625, 1000, 2500, 3125, 5000, 6250, 10000, 12500, 25000, 31250, 62500, 125000]
        
        # self.sample_rate_change(int(self.config["DataLogger"]['sample_rate']))
        # self.voltage_update(self.ylim)
        self.SampleRateCombo.setCurrentIndex(int(self.config["DataLogger"]['sample_rate']))
        self.voltageSizeSpinbox.setValue(self.ylim)
        self.timeSizeSpinbox.setValue(self.delta_base)
        self.timeSizeMultiSpinbox.setValue(self.delta_multiplyer)
        self.lpFilterCheckbox.setChecked(self.config['DataLogger'].getboolean('lp_filter_status'))
        print(self.adc_prescalar)
        # print(config)
        # print()
        # print()
        # print(config["DataLogger"]['sample_rate'])
       
       

        
    
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
            self.arduino.write(b"5")
            self.timer.start(self.interval)
            self.datacollector.start()
        else:
            self.stop()

    def stop(self, *args):
        self.state = False
        self.startButton.setText(QtCore.QCoreApplication.translate("DataLoggerMainWindow",'Start'))
        self.timer.stop()
        self.datacollector.quit()
        print("FILTERED DATA:", len(self.ydata))
        self.arduino.write(b'6')
        time.sleep(0.1)
    
    def save(self, *args):
        self.savefile = QtWidgets.QFileDialog.getSaveFileName(filter="*.csv")
        np.savetxt(self.savefile[0], self.results, fmt="%1.8f", delimiter=",")
    
    def refresh(self, *args):
        self.ydata = deque(maxlen=self.queue_length)
        self.xdata = deque(maxlen=self.queue_length)
        self.ydata.append(0)
        self.xdata.append(0)
        self.results = []
        self.raw_data = b''
        self.j = 0
        self.mpl_plot.ax.cla()
        self.mpl_plot.ax.set_xlim(-self.delta, 0)
        self.mpl_plot.ax.grid(color='gray', linestyle='--')
        self.mpl_plot.draw()

    def delta_update(self, i):
        self.delta = i*10**self.timeSizeMultiSpinbox.value()
        self.delta_base = i
        if not self.state:
            if len(self.xdata) == 0:
                self.mpl_plot.ax.set_xlim(-self.delta, 0)
            else:
                self.mpl_plot.ax.set_xlim(-self.delta+self.xdata[len(self.xdata)-1], self.xdata[len(self.xdata)-1])
            
            self.mpl_plot.draw()

    def deltamulti_update(self, i):
        self.delta = self.timeSizeSpinbox.value() * 10**i
        self.delta_multiplyer = i
        if not self.state:
            if len(self.xdata) == 0:
                self.mpl_plot.ax.set_xlim(-self.delta, 0)
            else:
                self.mpl_plot.ax.set_xlim(-self.delta+self.xdata[len(self.xdata)-1], self.xdata[len(self.xdata)-1])
            
            self.mpl_plot.draw()
    
    def sample_rate_change(self, index):

        # - NEED TO ADD FIX FUNCTION TO UPDATE TO PROPER SAMPLE RATES
        # - NEED TO WRITE CORRESPONDING FIX TO ARDUINO
        self.arduino.write(b'6')
        self.sample_rate = self.sample_rate_indexes[index]

        # self.adc_prescalar = self.adc_prescalars[index]
        # print(self.adc_prescalar)
        for freq in self.sample_dict:
            if self.sample_rate <= freq:
                self.timer_prescaler = self.sample_dict[freq][0]
                prescaler_byte = self.sample_dict[freq][1]
                break
        
        self.timer_top = int(16e6/(self.timer_prescaler*self.sample_rate)-1)
        print(self.timer_top)
        timer_top_bytes = ((self.timer_top).to_bytes(2, "big"))
        print(timer_top_bytes)
        current_state = self.state
        if self.state:
            self.stop()
        self.arduino.write(b'3')
        # time.sleep(1)
        self.arduino.write(prescaler_byte)
        # time.sleep(1)
        self.arduino.write(timer_top_bytes)
        time.sleep(1.1)
        # while self.arduino.in_waiting == 0:
        #     print("Waiting...")
        #     time.sleep(1)
        # print("PRESCALER:", self.timer_prescaler)
        # print(self.arduino.in_waiting)
        # print("SENDSIZE=", self.arduino.read(self.arduino.in_waiting))

        # print(self.arduino.read(1))
        # while self.arduino.in_waiting < 2:
        #     print("Received... " + str(self.arduino.in_waiting)+ " bytes")
        #     time.sleep(1)
        # bt = self.arduino.read(size=2)
        # print("BYTES:")
        # print(bt)
        # print(bt[0]*256+bt[1])
        # print(self.arduino.read(2))
        self.BUF_SIZE = min(max(6, int(self.sample_rate/8)), 1000)
        print("BUF_SIZE = ", self.BUF_SIZE)
        print("SampleRate = ", self.sample_rate)
        if current_state:
            self.start()

    def voltage_update(self, voltage):
        self.ylim = voltage
        if not self.state:
            self.mpl_plot.ax.set_ylim(0, self.ylim)
            self.mpl_plot.draw()
    
    def toggle_lpfilter(self, lp_state):
        print("FILTER TOGGLED")
        current_state = self.state

        print(lp_state)
        if lp_state == 2:
            self.lp_state = 1
        else:
            self.lp_state = lp_state
        

        if self.state:
            self.stop()

        if self.lp_state:
            warn = QtWidgets.QMessageBox(self.centralwidget)
            warn.setText("Warning: Using the Lowpass Filter will reduce sample rate by ~60x.")
            warn.setIcon(QtWidgets.QMessageBox.Warning)
            warn.show()
        
        self.arduino.write(b'4')
        # self.arduino.write((self.lp_state).to_bytes(1, "big"))
        if self.lp_state:
            self.arduino.write(b'1')
        else:
            self.arduino.write(b'0')

        if current_state:
            self.start()


    def save_settings():
        pass
    
    def load_user_settings():
        pass

    def load_default_settings():
        pass

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = DataLogger()
    window.show()
    sys.exit(app.exec_())