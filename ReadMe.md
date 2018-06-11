# Data Logger for the Arduino Uno R3
This has only been tested on the Arduino R3 but you could try it on a different Arduino, just change the code and commands to match the USB Controller (AtMega16U2) on your Arduino.

This Data Logger can run at a 23 different sample rates from 1 Sample/Second to 62500 Samples/Second. It will write the data to a CSV file that you specifiy. Capable of saving settings profiles for quick load to return to last saved state.

## Installing
Installation is done in three steps. First you need to update your AtMega16U2 chip so I can communicate at a rate of 2 MBaud. Second you need to upload the Arduino Sketch located in the DataLogger folder to your arduino. Then you just need to download the and run executable in the WindowsDataLogger folder.

### Update AtMega16U2

If you are on OSX or Linux you should start by getting dfu-programmer. Do that by going to the [dfu-progammer repo](https://github.com/dfu-programmer/dfu-programmer) and following the instructions.

They also have a way to compile dfu-progammer for Windows but I have heard you can use Atmel's own flashing software [FLIP](https://www.microchip.com/developmenttools/ProductDetails/flip#additional-summary). I have not flashed the AtMega16U2 on Windows using FLIP, so you will have to do some translation between 

Once you have dfu-progammer installed you need to connect your Arduino to your computer. Then while holding down the RESET button, run the following commands in Terminal.

