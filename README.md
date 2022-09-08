Development of software to get a 3D impulse response graphic interpretation
============================================

This repository contains all the neccessary files to check out the RIRs 3D software. In the 'Archivos Py' folder theres a readme.txt to check out the functioning of the soft. 

# RIRs-3D

## Abstract

The purpose of this article is to detail the procedure that was carried out to develop a software that allows the processing of impulse responses in three dimensions. As main functions, this software supports audio files that are recorded both in format A and in format B, since it has a conversion algorithm from A to B format. Then, as the main features, the software allows the visualization of a hedgehog graph, the impulse response in two dimensions, and a table showing the intensity values as a function of time. The hedgehog is a three-dimensional graph that represents the intensity vectors according to where the reflection in space comes from. Finally, the software allows the user to configure some parameters, such as filtering intensities based on a threshold, percentage of overlap of the window to calculate the intensity, configure the window size, and specify the arrival time of the direct sound. The software code was written in Python and its purpose is to facilitate the user understanding of the acoustic characteristics of an enclosure based on the processing of impulse responses recorded with soundfield or ambisonic microphones and that it’s features allows to make a deep analysis of sound field evolution.

## Software layout

![image](https://user-images.githubusercontent.com/82551055/189023784-5b6d4aac-c36a-4b15-9522-4fe8b880fbf6.png)
