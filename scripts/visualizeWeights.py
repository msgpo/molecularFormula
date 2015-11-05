# -*- coding: utf-8 -*-
"""
Created on Thu Oct 22 16:42:29 2015

@author: frickjm
"""

import matplotlib.pyplot as plt
import skimage.io as io
from skimage.transform import resize 
import numpy as np
from os.path import isfile

from os import listdir
from random import shuffle
import cPickle

from sklearn.metrics import mean_squared_error

from keras.preprocessing.image import ImageDataGenerator
from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation, Flatten
from keras.layers.convolutional import Convolution2D, MaxPooling2D
from keras.optimizers import SGD, Adadelta, Adagrad





""" VISUALIZATION """

for i in range(0,100):
    if isfile("../layer"+str(i)+".pickle"):
        with open("../layer"+str(i)+".pickle",'rb') as f:
            weights     = cPickle.load(f)
        greymap     = plt.get_cmap('gray')
        size        = len(weights)
        if size < 100:
            print "visualizing layer ", i
            rows        = size/8
            f, axarr    = plt.subplots(rows,8)
            count       = 0
            for x in weights:
                row     = count/8
                col     = count%8
                p   = x[0,:,:]
                axarr[row,col].axis('off')
                axarr[row,col].imshow(p,cmap = greymap)
                count   +=1
                
            plt.suptitle("Layer "+str(i))
            plt.savefig("../layer"+str(i)+".jpg")
    


        