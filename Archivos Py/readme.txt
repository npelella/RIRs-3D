READ ME!

This read seeks to provide instructions and inform the user about the functionalities 
of the software.The interface has three .py files. One file called main, another called 
functions, and a last called gui. For the gui to run, you have to run the main.py file. 
In the folder are attached measurements both in format A and B with plant images of each one.

At first, the software allows you to import files in format A and format B. Also, if 
you want to locate the hedgehog in the plant, you can import the plant image and the 
hedgehog is automatically displayed with the possibility of scaling and rotating it 
if you did. lack.

Also, if some measurement parameters are known, the user is allowed to enter a custom 
direct sound time even though the software performs a default calculation. The user 
is also allowed to make an overlap in the window, configure a threshold level or include 
a low pass filter to limit the signal in band.

Things to consider: the plan image that is imported is scaled correctly if the size of 
the interface is maximized. On the other hand, to be able to interact correctly with 
the graphics, it is likely that version 3.4.2 of the matplotlib library is required. 
Below are the lines of code to update said library in  the anaconda cmd window (Spyder):

pip install -U matplotlib -- user




