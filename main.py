import os
# import cv2
import numpy as np
from matplotlib import pyplot as plt

# This import registers the 3D projection, but is otherwise unused.
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 unused import
from scipy.ndimage import gaussian_filter

filename_sub_left = 'C:/Users/7zieg/Downloads/BioVision/cam0/events.txt'
filename_sub_right = 'C:/Users/7zieg/Downloads/BioVision/cam1/events.txt'

max_y = 180
max_x = 240
dis = 10
buffer_right = np.empty((max_y, 0)).tolist()
maximumTimeDifference = 0.0001
wmi = np.zeros((max_y, max_x, dis))
search_min = 0

def addtoBufferRight(data):
    global buffer_right
    y = int(data[2])
    tmp = (data[0], int(data[1]),data[2], int(data[3]))
    buffer_right[y].append(tmp)

def searchEvent(data):
    timestamp = data[0]
    y_value = int(data[2])
    pol = int(data[3])
    foundEvents = []
    global search_min
    for x in range(search_min,len(buffer_right[y_value])):
    #for value in enumerate(buffer_right[y_value]):
        if timestamp < buffer_right[y_value][x][0]:
            break
        elif timestamp - buffer_right[y_value][x][0] > maximumTimeDifference:
            continue
        elif abs(data[1] - buffer_right[y_value][x][1]) > (dis - 1):
            continue
        elif pol == buffer_right[y_value][x][3]:
            foundEvents.append(buffer_right[y_value][x])

    return foundEvents

def calculateMatchingCosts(timestampleft, timestampright, weightingfunction = 1):
    timediff = timestampleft-timestampright
    if weightingfunction == 1: #inverse linear
        return timediff
    elif weightingfunction == 2: #inverse quadratic
        a = 1
        weight = 1/(a*np.pow(timediff,2)+0.1)
        return weight
    elif weightingfunction == 3:
        mht = 10 #maximal considered hsitory events
        b = 1
        weight = mht * np.exp(-timediff/b)
        return weight
    else:
        return timediff

image = np.loadtxt(fname="C:/Users/7zieg/Downloads/BioVision/cam0/groundtruth.txt", delimiter=' ', dtype=np.float)[:]

with open("C:/Users/7zieg/Downloads/BioVision/cam0/groundtruth.txt") as file:
    array2d = [[float(digit) for digit in line.split()] for line in file]

#print(array2d.shape)
plt.imshow(array2d)
plt.show()


#load Events
events_left = np.genfromtxt(fname=filename_sub_left, delimiter=' ', dtype=np.float, skip_header=0)[:]
events_right =np.genfromtxt(fname=filename_sub_right, delimiter=' ', dtype=np.float, skip_header=0)[:]


#write Events into Buffer
n = events_right.shape[0]
for i in range(n):
    addtoBufferRight(events_right[i,:])
n = events_left.shape[0]
for i in range(n):
#for i in range(200):
    foundevents = searchEvent(events_left[i,:])
    #print(events_left[i,:])
    #print(foundevents)
    #print("ende")
    #wmi = wmi *0.9
    #wmi = wmi - 0.1
    #wmia = wmi.clip(min=0)

    for j in range(len(foundevents)):
        costs = calculateMatchingCosts(events_left[i,0],foundevents[j][0])*100000
        if costs < 0:
            print("start")
            print(events_left[i,:])
            print(foundevents[j][:])
            print("end")
        disparity = int(abs(events_left[i][1]-foundevents[j][1]))
        wmi[int(events_left[i][2]),int(events_left[i][1]),disparity] = costs
    if i%500 == 0:
        wmi = wmi *0.7
        wmia = wmi.clip(min=0)
        tmp = gaussian_filter(wmi, sigma=1)
        disp = np.argmax(tmp, 2)
        plt.imshow(disp, cmap = "hot")
        plt.show()


print("aaaaaaaaaaaaaaaaaaaaaaa")
disp = np.argmax(wmi,2)
print(np.amax(wmi))
print(np.amin(wmi))
print(disp.shape)
print(disp)


plt.imshow(disp)
plt.show()







