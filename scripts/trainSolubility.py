# -*- coding: utf-8 -*-
"""
Created on Nov 12 15:22:30 2015

@author: frickjm
"""


import matplotlib.pyplot as plt
import skimage.io as io
from skimage.transform import resize 
import numpy as np

from os import listdir
from os.path import isdir
from os import mkdir
from os.path import isfile
from random import shuffle
import cPickle
import sys

from sklearn.metrics import mean_squared_error

from keras.preprocessing.image import ImageDataGenerator
from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation, Flatten
from keras.layers.convolutional import Convolution2D, MaxPooling2D
from keras.optimizers import SGD, Adadelta, Adagrad


sys.setrecursionlimit(10000)
np.random.seed(0)

"""get the solubility for training"""
def getTargets():
    out     = {}
    with open("../data/sols.pickle",'rb') as f:
        d =  cPickle.load(f)
    for k,v in d.iteritems():
        out[k] = [float(v)]
    return out

"""Dump the weights of the model for visualization"""
def dumpWeights(model):     
    layercount  = 0
    for layer in model.layers:
        try:
            weights     = model.layers[layercount].get_weights()[0]
            size        = len(weights)
            if size < 100:
                with open(folder+"layer"+str(layercount)+".pickle",'wb') as f:
                    cp = cPickle.Pickler(f)
                    cp.dump(weights)
            else:
                pass
                
        except IndexError:
            pass
        layercount  +=1


"""Find out the RMSE of just guessing the mean solubility for comparison purposes"""
def testAverages(direct,targets):
    means = np.mean(targets.values(),axis=0)  
    s     = len(means)
    ld    = listdir(direct)
    shuffle(ld)
    num     = 20000
    preds   = np.zeros((num,s),dtype=np.float)
    y       = np.zeros((num,s),dtype=np.float)
    count   = 0
    for x in ld[:num]:
        CID     = x[:x.find(".png")]
        y[count]  = targets[CID]
        preds[count] = means
        count+=1
   
    print "RMSE of guessing: ", np.sqrt(mean_squared_error(y, preds))



"""Require an argument specifying whether this is an update or a new model"""
if len(sys.argv) <= 1:
    print "needs 'update' or 'new' as first argument"
    sys.exit(1)


"""If we are continuing to train a model, require size and input size params"""
if sys.argv[1].lower().strip() == "update":
    UPDATE     = True    
    if len(sys.argv) < 4:
        print "needs image size, layer size as other inputs"
        sys.exit(1)
    else:
        size = int(sys.argv[2])     #size of the images
        lay1size = int(sys.argv[3]) #size of the first receptive field
        print size, lay1size
        
   
else:
    """If this is a new model, define the model below"""   
    UPDATE  = False
    size    = 200                               #size of the images
    lay1size= 5      
    depth   = 2                           #size of the first receptive field




imdim   = size - 20                         #strip 10 pixels buffer from each size
direct  = "../data/images"+str(size)+"/"    #directory containing the images
ld      = listdir(direct)                   #contents of that directory
numEx   = len(ld)                           #number of examples in the directory
DUMP_WEIGHTS = True                         # will we dump the weights of conv layers for visualization
trainTestSplit     = 0.90

"""Define the folder to store the model and the train/test split in"""
folder  = "../solubility/"+str(size)+"_"+str(lay1size)+"/"
if not isdir(folder):
    mkdir(folder)
    
if (not UPDATE) and (isdir(folder)):
    i=1
    oldfolder = folder
    while isdir(folder):
        i+=1
        folder  = oldfolder[:-1]+"_"+str(i)+'/'
        print folder
    mkdir(folder)




shuffle(ld)  #shuffle the examples


"""Load the train/test split information if update, else split and write out which images are in which dataset"""
if not UPDATE:
    trainFs = ld[:int(numEx*trainTestSplit)]
    testFs  = ld[int(numEx*trainTestSplit):]
    with open(folder+"traindata.csv",'wb') as f:
        f.write('\n'.join(trainFs))
    with open(folder+"testdata.csv",'wb') as f:        
        f.write('\n'.join(testFs))
else:
    with open(folder+"traindata.csv",'rb') as f:
        trainFs = f.read().split("\n")
    with open(folder+"testdata.csv",'rb') as f:        
        testFs  = f.read().split("\n")


trainL  = len(trainFs)
testL   = len(testFs)    

print "number of examples: ", numEx
print "training examples : ", trainL
print "test examples : ", testL


batch_size      = 32            #how many training examples per batch
chunkSize       = 5000          #how much data to ever load at once      
testChunkSize   = 600           #how many examples to evaluate per iteration
numTrainEx      = min(trainL,chunkSize)

targets           = getTargets() #get the ECFP vector for each CID
testAverages(direct,targets)   
    
outsize         = len(targets[targets.keys()[0]]) #this it the size of the target (# of targets)

"""Initialize empty matrices to hold our images and our target vectors"""
trainImages     = np.zeros((numTrainEx,1,imdim,imdim),dtype=np.float)
trainTargets    = np.zeros((numTrainEx,outsize),dtype=np.float)
testImages      = np.zeros((testChunkSize,1,imdim,imdim),dtype=np.float)
testTargets     = np.zeros((testChunkSize,outsize),dtype=np.float)


"""If we are training a new model, define it"""   
if sys.argv[1].lower().strip() == "new":
    model = Sequential()
    
    model.add(Convolution2D(32, 1, lay1size, lay1size, border_mode='full')) 
    model.add(Activation('relu'))
    
    model.add(Convolution2D(32, 32, 5, 5))
    model.add(Activation('relu'))
    
    model.add(MaxPooling2D(poolsize=(2, 2)))
    
    model.add(Convolution2D(32, 32, 2, 2))
    model.add(Activation('relu'))
    
    model.add(Convolution2D(64, 32, 2, 2)) 
    model.add(Activation('relu'))
    
    model.add(MaxPooling2D(poolsize=(3, 3)))
    
    model.add(Convolution2D(64, 64, 5, 5)) 
    model.add(Activation('relu'))
    
    model.add(MaxPooling2D(poolsize=(2, 2)))
    
    model.add(Flatten())
    model.add(Dense(9216, 512, init='normal'))
    model.add(Activation('relu'))
    model.add(Dropout(0.5))
    
    model.add(Dense(512, outsize, init='normal'))
    
    
    model.compile(loss='mean_squared_error', optimizer='adadelta')


"""If we are continuing to train an old model, load it"""
if UPDATE:
    with open(folder+"wholeModel.pickle",'rb') as f:
        model     = cPickle.load(f)



""" TRAINING """

    
numIterations   = trainL/chunkSize + 1
superEpochs     = 10
for sup in range(0,superEpochs):

    print "*"*80
    print "TRUE EPOCH ", sup
    print "*"*80    
    for i in range(0,numIterations):
        print "iteration ",i,": ", i*chunkSize," through ", (i+1)*chunkSize
        count   = 0
        for x in trainFs[i*chunkSize:(i+1)*chunkSize]:
            if x.find(".png") > -1:
                CID     = x[:x.find(".png")]
                image   = io.imread(direct+x,as_grey=True)[10:-10,10:-10]         
                image   = np.where(image > 0.1,1.0,0.0)
                trainImages[count,0,:,:]    = image
                trainTargets[count]         = targets[CID]
                count +=1
    
        model.fit(trainImages, trainTargets, batch_size=batch_size, nb_epoch=1)
        
        
        shuffle(testFs)
        count   = 0
        for x in testFs[:chunkSize/10]:
            if x.find(".png") > -1:
                CID     = x[:x.find(".png")]
                image   = io.imread(direct+x,as_grey=True)[10:-10,10:-10]         
                image   = np.where(image > 0.1,1.0,0.0)
                testImages[count,0,:,:]    = image
                testTargets[count]         = targets[CID]
                count +=1
        
        preds   = model.predict(testImages)
        RMSE    = np.sqrt(mean_squared_error(testTargets, preds))         
        print "RMSE of epoch: ", RMSE

        
        if DUMP_WEIGHTS:
            dumpWeights(model)

        with open(folder+"wholeModel.pickle", 'wb') as f:
            cp     = cPickle.Pickler(f)
            cp.dump(model)

del trainTargets, trainImages
""" END TRAINING """



