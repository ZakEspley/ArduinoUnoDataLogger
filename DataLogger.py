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
from scipy.signal import lfilter_zi, butter

class DataLogger(QtWidgets.QMainWindow, Ui_DataLoggerMainWindow):

    def __init__(self):
        super(DataLogger, self).__init__()


        self.config = configparser.ConfigParser()
        self.config.read('settings.ini')


        self.sample_rates = [(4).to_bytes(1, "big"), (5).to_bytes(1, "big"), (6).to_bytes(1, "big"), (7).to_bytes(1, "big")]
        self.adc_prescalars = [16, 32, 64, 128]
        self.rate = 8000



        self.state = False
        self.lp_state = 0

        self.arduino_list = self.find_arduino()
        self.arduino = serial.Serial(port=self.arduino_list[0].device, baudrate=2000000)


        self.timer = QtCore.QTimer(self)


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
        self.BUF_SIZE = 6
        self.raw_data = b''


        self.filter_buffer = deque(maxlen=20000)
        self.filter_buffer.append(0)
        self.time_buffer = deque(maxlen=20000)
        self.time_buffer.append(0)

        self.packet_length = deque(maxlen=10000)
        self.filter_z = 0
        
        self.adc_prescalar = 16
        self.timer_prescaler = 64
        self.timer_top = 6249
        self.sample_rate = 16e6/(self.timer_prescaler*(1+self.timer_top))
        self.butter_b, self.butter_a = butter(4, 10/self.sample_rate)
        
        self.sample_dict = {
                        10: (256, ((4).to_bytes(1, 'big'))),     ### This is equivilent to 256 prescaler in Arduino TCCR1B Register
                        15625: (64, ((3).to_bytes(1, 'big'))),   ### This is equivilent to  64 prescaler in Arduino TCCR1B Register
                        125000: (8, ((2).to_bytes(1, 'big')))    ### This is equivilent to   8 prescaler in Arduino TCCR1B Register
            }
        self.sample_rate_indexes = [1, 2, 4, 5, 10, 25, 40, 80, 100, 125, 200, 250, 500, 625, 1000, 2500, 3125, 5000, 6250, 10000, 12500, 25000, 31250, 62500]

        self.setupUi(self)
        self.mpl_plot.compute_initial_figure()
        self.mpl_plot.arduino = self.arduino
        self.arduinosCombo.addItems([d.description for d in self.arduino_list])
        self.timer.timeout.connect(self.mpl_plot.update_figure)

        time.sleep(2)
        self.load_default_settings()
        self.mpl_plot.update_figure()

    def find_arduino(self):
        arduino_ports = [p for p in list_ports.comports() if ('USB UART' in p.description or 'Arduino' in p.description or 'COM' in p.description)]
        return arduino_ports
    
    def  start(self):
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
        self.arduino.write(b'6')
        time.sleep(0.1)
    
    def save(self, *args):
        self.savefile, _ = QtWidgets.QFileDialog.getSaveFileName(filter="*.csv")
        if self.savefile != '':
            np.savetxt(self.savefile, self.results, fmt="%1.8f", delimiter=",")
    
    def refresh(self, *args):
        current_state = self.state
        if self.state:
            self.stop()
        self.ydata = deque(maxlen=self.queue_length)
        self.xdata = deque(maxlen=self.queue_length)
        self.ydata.append(0)
        self.xdata.append(0)
        self.time_buffer = deque(maxlen=1001)
        self.filter_buffer = deque(maxlen=1001)
        self.time_buffer.clear()
        self.filter_buffer.clear()
        self.time_buffer.append(0)
        self.filter_buffer.append(0)
        self.results = []
        self.raw_data = b''
        self.j = 0
        self.arduino.write(b'7')
        self.mpl_plot.update_figure()
        self.mpl_plot.ax.cla()
        self.mpl_plot.ax.set_xlim(-self.delta, 0)
        self.mpl_plot.ax.grid(color='gray', linestyle='--')
        self.mpl_plot.draw()
        if current_state:
            self.start()

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

        if self.lp_state and self.sample_rate_indexes[index] <= 10:
            warn = QtWidgets.QMessageBox(self.centralwidget)
            warn.setText("The cut-off frequency is 5Hz. Sample rate must be greater than the Nyquist Frequency (10 samples/s) to use the lowpass filter")
            warn.setIcon(QtWidgets.QMessageBox.Warning)
            warn.show()
        
        else:
            self.arduino.write(b'6')
            self.sample_rate = self.sample_rate_indexes[index]

            for freq in self.sample_dict:
                if self.sample_rate <= freq:
                    self.timer_prescaler = self.sample_dict[freq][0]
                    prescaler_byte = self.sample_dict[freq][1]
                    break
            
            self.timer_top = int(16e6/(self.timer_prescaler*self.sample_rate)-1)
            timer_top_bytes = ((self.timer_top).to_bytes(2, "big"))
            current_state = self.state
            if self.state:
                self.stop()
            self.arduino.write(b'3')
            self.arduino.write(prescaler_byte)
            self.arduino.write(timer_top_bytes)
            time.sleep(1.1)
            self.BUF_SIZE = min(max(8, int(self.sample_rate/8)), 1000)

            if self.sample_rate > 10:
                self.butter_b, self.butter_a = butter(4, 10/self.sample_rate)

            if current_state:
                self.start()

    def voltage_update(self, voltage):
        self.ylim = voltage
        if not self.state:
            self.mpl_plot.ax.set_ylim(0+self.voltage_offset, self.ylim+self.voltage_offset)
            self.mpl_plot.draw()
    
    def voltage_offset_update(self, offset):
        self.voltage_offset = offset
        if not self.state:
            self.mpl_plot.ax.set_ylim(0+self.voltage_offset, self.ylim+self.voltage_offset)
            self.mpl_plot.draw()
    
    def toggle_lpfilter(self, lp_state):
        if self.sample_rate <= 10:
            warn = QtWidgets.QMessageBox(self.centralwidget)
            warn.setText("The cut-off frequency is 5Hz. Sample rate must be greater than the Nyquist Frequency (10 samples/s) to use the lowpass filter")
            warn.setIcon(QtWidgets.QMessageBox.Warning)
            warn.show()
            self.lpFilterCheckbox.setChecked(False)
        else:
            current_state = self.state
            self.butter_b, self.butter_a = butter(4, 10/self.sample_rate)
            if lp_state == 2:
                self.lp_state = 1
            else:
                self.lp_state = lp_state
            
    
    def  save_settings(self):
        
        user_settings = self.config["UserSettings"]

        user_settings['y_lim'] = str(self.ylim)
        user_settings['delta_base'] = str(self.delta_base)
        user_settings['delta_multiplyer'] = str(self.delta_multiplyer)
        user_settings['voltage_reference'] = str(self.voltage_reference)
        user_settings['sample_rate'] = str(self.sample_rate_indexes.index(self.sample_rate))
        user_settings['lp_filter_status'] = str(True if self.lp_state else False)
        user_settings['voltage_offset'] = str(self.voltage_offset)

        with open('settings.ini', 'w') as f:
            self.config.write(f)
        
    
    def __load_settings(self, settings_name):

        self.ylim = int(self.config[settings_name]['y_lim'])
        self.voltage_reference = float(self.config[settings_name]['voltage_reference'])
        self.delta_base = int(self.config[settings_name]['delta_base'])
        self.delta_multiplyer = int(self.config[settings_name]['delta_multiplyer'])
        self.delta = self.delta_base * 10**self.delta_multiplyer
        self.voltage_offset = float(self.config[settings_name]['voltage_offset'])

        self.proportion = self.voltage_reference/256

        self.SampleRateCombo.setCurrentIndex(int(self.config[settings_name]['sample_rate']))
        self.voltageSizeSpinbox.setValue(self.ylim)
        self.timeSizeSpinbox.setValue(self.delta_base)
        self.timeSizeMultiSpinbox.setValue(self.delta_multiplyer)
        self.lpFilterCheckbox.setChecked(self.config[settings_name].getboolean('lp_filter_status'))


    def load_user_settings(self):
        self.__load_settings("UserSettings")
    
    def load_default_settings(self):
        self.__load_settings("Default")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = DataLogger()
    window.show()
    sys.exit(app.exec_())