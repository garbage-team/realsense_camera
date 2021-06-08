# realsense_camera
Code for creating ground truth depth estimation data
as well as measuring articles/volume inside a container using an Intel RealSense camera
and the RealSense SDK python wrapper

Dependencies:
* Python  3.7 or higher
* Intel RealSense SDK
* pyrealsense2
* opencv-python
* numpy
* scipy 
* tkinter
* Pillow
* matplotlib

## Installation
Below are installation instructions for running measurements

### Fill rate measurements with Raspberry Pi and RealSense camera
For running on Raspberry Pi 3/4, installation of RealSense SDK can be done using the following guide: https://github.com/acrobotic/Ai_Demos_RPi/wiki/Raspberry-Pi-4-and-Intel-RealSense-D435

After setting up the RealSense SDK install all the necessary dependencies. Now connect the RealSense camera and proceed with the steps below. 

The `depth_camera_capture` module can be used to see what the depth camera sees, use it to make sure the camera can see the complete contents and the walls of the container.
When the camera and the container is set up, calibrate the sensor's physical parameters to line up the digital representation with the physical:
1. Empty the container and check that nothing obscures the view of the camera
2. Either run the `Application` module and show the point cloud or measure the physical properties of the setup to make sure the point cloud's z-direction is in line with the container's up-direction
3. If it is not aligned, adjust the parameters in the config.csv file that begin with "var_rot_". Positive values rotate the point cloud counter-clockwise around the given axis
4. Take a new measurement and make sure that the top of the pallet is approximately close to z=0 (this gives the best precision when measuring)
5. If the top of the pallet is not at z=0, adjust the parameter "var_shift_z" in the config.csv file. Positive values shift the point cloud upwards
6. Take a new measurement and make sure that no points outside of the pallet exist in the point cloud. 
7. If points outside of the pallet shows in the point cloud, adjust the parameters that begin with "var_border_" to filter out points outside the region of interest. 
8. Run the `Application` module and make sure that the point cloud now only shows the empty container

When the physical parameters are calibrated, the empty volume of the container should be calibrated:
1. Run the `calibrate_sensor_empty` module using `calibrate_sensor_empty.calibrate_sensor_empty()`
2. The calibration should run by itself, check the measurement error in the output from the calibration script

Now, everything should be set up to run fill rate measurements of the container

### Taking depth images as ground truth for supervised learning
The code base in this repository can be used for simply taking aligned depth and rgb images. 
These images can then be used for training machine learning models in supervised mode. 

To do this, the module `depth_camera_capture` should be used. 
1. Install all the necessary dependencies on your system and connect the RealSense camera (the RealSense SDK is necessary, make sure to install that as well, see above)
2. Run the application by `depth_camera_capture.main()`
3. A window should show with the RGB image to the left and the depth image to the right. The depth image displays as a heat map where larger depths are encoded as brighter colors.
4. To save an image pair, press `s` on the keyboard. The command prompt should write out where the files were saved. The depth map has file extension `.raw` and the rgb image `.png`
5. To exit the program, press `[esc]`

 

## Running the measurement application
To start the measurement application with the graphical user interface, run `Application.Application().main_loop()`. This creates an `Application` object and starts its `main_loop` activity.
The program is single-threaded and blocking so it will not be possible to run parallell tasks in the same thread. 
For the program to work, all necessary dependencies need to be installed and the camera needs to be connected. 

The GUI should show when the program starts running, for it to display proper data, calibration should already have been made according to the steps above. 
The calibration for a full container is done during run-time. 

1. When the GUI starts, check that the sensor is measuring the correct region by inspecting the point cloud 
2. To calibrate the sensor, fill the container and press the `Calibrate Full` button in the GUI
3. When the calibration is done, adjust the maximum number of articles by pressing the `+` and the `-` buttons
4. Now take a new measurement by pressing the `Take Measurement` button
5. The sensor should now show the correct readings, verify by taking some articles out and running a new measurement

The sensor periodically takes new measurements automatically to stay updated, the time between these automatic measurements can be adjusted in the config file under "update_period". 
Enter the number of seconds between each measurement, since measuring takes a couple of seconds, a minimum of 10 seconds is recommended. 


## Considerations and future improvements
Below are listed a number of considerations to take into account when setting up the sensor as well as some points that could be further investigated.

### Materials and noise
The RealSense camera uses infrared projectors and stereo cameras to find the depth in the scene. 
Therefore the sensor does not work well on materials that do not scatter infrared light.
This could be for example very dark/absorbent materials, computer/television screens, some liquids. 
The sensor should also not be able to work on reflective surfaces, such as mirrors or glass, although this is not always the case. 

Noise will always be present in the sensor readings, to avoid measurement errors when calibrating, several measurements are taken and the mean of these is used for the calibrated value.
This is one of the main reasons why calibrating is slow. 

### Accuracy of sensor
We have not run structured tests evaluating the accuracy of the sensor, this would be interesting to investigate however, specifically if you are able to put the camera further away from the container while retaining a high enough accuracy.
If it is possible to sacrifice spatial resolution while retaining volume accuracy it should be possible to use the camera to measure more than one container which would decrease the implementation costs drastically. 

### Dynamically finding the container in the scene
The current implementation of the sensor uses manual control for setting the region of interest, it would however be beneficial if this region of interest could be dynamically determined through some smart system. 
Object detection might be a possible way to solve this problem by finding the container in the RGB image and from the bounding box in RGB space convert that into a region of interest bounding box in 3D-space.
Factors such as robustness to changes in the scene need to be taken into accound however as if the bounding box is far different from when it was calibrated, the volumes could be too large or too small leading to inaccurate measurements.
For now, setting a bounding box that is a bit larger than the actual container should work well as long as the container is always placed at the same height every time compared to the sensor position. 

### Detecting anomalies
One of the main reasons why RGB cameras are interesting when it comes to smart waste management is their ability to classify the type of waste in the container. 
While our work has been more focused on the possibility of measuring volume within containers, classification of anomalies is still interesting and deserves further investigation. 
In our work, we have shown that a somewhat complex deep convolutional neural network for image segmentation can be effectively run on the Raspberry Pi hardware, therefore it should be possible to run a similar system looking for anomalies within the container. 

### Dense depth maps (important for machine learning)
The outputs from the RealSense camera are not dense, meaning that some pixels in the depth image does not have a valid value. 
This is the result of the technology used (infrared stereo depth camera) and can give rise to some serious bugs if not handled correctly.
The depth value for all invalid pixels are 0.0, this leads to incorrect depth images when using bilinear interpolation when downscaling or upscaling the images. 

## Authors and Contributors
Jonas Jungåker, jungaker@kth.se

Victor Hanefors

Copyright, 2021
