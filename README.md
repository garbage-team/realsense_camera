# realsense_camera
Code for creating ground truth depth estimation data
as well as measuring articles/volume inside a pallet using a Intel RealSense camera
and the RealSense SDK python wrapper

Dependencies:
* Python  3.7 or higher
* Intel RealSense SDK

Libraries:
* pyrealsense2
* python-opencv
* numpy

(for pallet case)
* scipy 
* tkinter
* PIL 


For running on Raspberry Pi 3/4, installation of RealSense SDK can be done using the following guide: https://github.com/acrobotic/Ai_Demos_RPi/wiki/Raspberry-Pi-4-and-Intel-RealSense-D435

 

# Guide: Setup pallet measurement 

1. Ensure the RPi is connected to the Intel RealSense camera with a USB 3.0 cable in the USB 3.0 port, and that the power adapter is plugged in and that the RPi is running. 

2. On the host computer (that will be connected to the screen during the live demo), connect to the “scania-smartlab” network and run “VNC viewer”. Connect to “139.122.242.72” using the login credentials.

3. When connected to the RPi, start the terminal and navigate to the /realsense_camera folder (“cd /realsense_camera”). Then run the application using “python3 Application.py” 

4. When the program has started, fill the pallet with the maximum desired amount of articles (say two wheels), and adjust the max number of articles using the buttons. Then press the “Calibrate Full” button and wait while the program calibrates an avg volume (to minimize impact of noise). This may take up to a minute. 

5. The program is now up and running! Take a measure manually using the button or wait for the automated updated every X second (configurable in the file “config.csv”). Close the application to close the program, or use “ctrl + c” in the terminal. 

**If the pallet and camera have been moved relative to each other, or taller objects are to be measured, proceed as below:**

1. Run the program and toggle the “Display Point Cloud” box. 

2. If the point cloud appears to show all pallet walls, no unnecessary points, and seems to be horizontally aligned no extra calibration is needed. 

  * If the point cloud does not fulfill the criteria's above, adjust the parameters as necessary in the file “Application.py”. The parameters are found in the initializer, adjust accordingly and verify using “Display Point Cloud”. Alignment does not have to be perfect but should not visually indicate any issue mentioned above. 

3. For tall objects place the object inside of the pallet,run a measurement, then display point cloud and verify that the object is measured in its entirety. Change parameters in the same way as above if necessary. Note that objects cannot be closer than ~20 cm to the camera. 
