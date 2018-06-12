# Data Logger for the Arduino Uno R3

![Screen Shot of App](https://github.com/ZakEspley/ArduinoUnoDataLogger/blob/master/DataLoggerScreenShot2.png?raw=true "3.75kHz")

This has only been tested on the Arduino R3 but you could try it on a different Arduino, just change the code and commands to match the USB Controller (AtMega16U2) on your Arduino.

This 8-Bit Data Logger can run at a 23 different sample rates from 1 Sample/Second to 62500 Samples/Second. It will write the data to a CSV file that you specifiy. Capable of saving settings profiles for quick load to return to last saved state.

## Installing
Installation is done in three steps. First you need to update your AtMega16U2 chip so I can communicate at a rate of 2 MBaud. Second you need to upload the Arduino Sketch located in the DataLogger folder to your arduino. Then you just need to download the and run executable in the WindowsDataLogger folder.

Once installed there is some hardware setup that you must do before you are capable of plotting voltages.

Start by cloning this repo and then proceed onward.

### Update AtMega16U2

If you are on OSX or Linux you should start by getting dfu-programmer. Do that by going to the [dfu-progammer repo](https://github.com/dfu-programmer/dfu-programmer) and following the instructions.

They also have a way to compile dfu-progammer for Windows but I have heard you can use Atmel's own flashing software [FLIP](https://www.microchip.com/developmenttools/ProductDetails/flip#additional-summary). I have not flashed the AtMega16U2 on Windows using FLIP, so you will have to do some translation between this guide and the FLIP commands.

You are going to use the fast-usbserial.hex file to flash to your Arduino. This was created by Urjaman in his repo, [fast-usb-serial](https://github.com/urjaman/fast-usbserial). I have it packaged it in to this repo for your convenience.

Once you have dfu-progammer installed you need to connect your Arduino to your computer. Open Terminal and CD to the this repo. Then while holding down the RESET button, run the following commands in Terminal.

```bash
sudo dfu-programmer atmega16u2 erase
sudo dfu-programmer atmega16u2 flash fast-usbserial.hex
sudo dfu-programmer atmega16u2 reset
```
Then unplug your Arduino for 10 seconds and plug it back it. You should be able see it and upload Arduino Sketches at this point.

### Load Sketch onto Arduino

If you haven't already installed the Arduino IDE you can find that [here](https://www.arduino.cc/en/Main/Software). Download and install that if you don't have it already. You may need to unplug and plug back in the Arduino after installation.

Open the Data-Logger.ino in the Data-Logger in the Arduino IDE and upload it to your Arduino.

### Run the executable

Now just go to the WindowsDataLogger  folder and run the executable. You should be able to start collecting data.

## Usage

There are a few things of note about using the Data Logger.

### Hardware Setup
Currently, the only input that is readable is A2. So anything that you hook up needs to have its signal go to that port. It is also needs a reference voltage plugged into AREF. This is the top voltage that is measurable by the ADC. You can either put in a custom refernce voltage or use the 5V/3.3V output on the arduino itself.

### Software Setup
Once you run the exectuable once you should find a Settings.ini file in the folder. Here is where you can set your reference voltage. Simply open the file with a text editor and change the value from "reference_voltage = 2.4440" to "reference_voltage = custom_value". Make sure to do this with both the Default profile and the UserSettings profile.

### Highspeed Issues
When running this at at high sample rates, 25000 samples/second and above, you may notice that there are gaps in your data. You will be recieving it in chunks. This is do to the delay in transmission of data from the Arduino to the PC. This is normal, but during those moments you won't be measureing anything. 

### Low Pass Filter
There is a Low Pass filter option that is used for looking noisey voltages near DC. It applies a filter 4 Pole Digital Butterworth FIR filter with a cutoff frequency of 5Hz. 

### Profiles
If you are commonly using the same sample rates, voltage offsets, etc. You can save those settings manually or through the software.

If you click the "Save Current Settings" button it will save the current configuration so that next time you only need to click "Load Settings" button to recover where you were. This doesn't save any data, just the Arduino and GUI configuration.

If you wanted, you could change these things manually in by opening the Settings.ini file in a text editor and manually making them whatever you wanted. If you do this and something goes wrong, you can always delete the Settings.ini file and a new default one will be created for you.

Enjoy and happy logging.
