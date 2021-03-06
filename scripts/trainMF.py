# -*- coding: utf-8 -*-
"""
Created on Thu Oct 15 15:22:30 2015

@author: frickjm
"""

from helperFuncs import *

import matplotlib.pyplot as plt
import skimage.io as io
from skimage.transform import resize 
import numpy as np

from os import listdir
from random import shuffle
import cPickle
import sys

from sklearn.metrics import mean_squared_error

from keras.preprocessing.image import ImageDataGenerator
from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation, Flatten
from keras.layers.convolutional import Convolution2D, MaxPooling2D
from keras.optimizers import SGD, Adadelta, Adagrad





def getTargetMeans(mfs):
    x   = np.mean(mfs.values(),axis=0)
    y   = np.std(mfs.values(),axis=0)
    print "means", x
    print "stds", y
#    np.savetxt("../targetMeans.txt",x,delimiter=',')
#    stop=raw_input("")
    return x,y
        


def testWAverages(direct,mfs,means):
    ld  = listdir(direct)
    shuffle(ld)
    num     = 20000
    preds   = np.zeros((num,16),dtype=np.float)
    y       = np.zeros((num,16),dtype=np.float)
    count   = 0
    for x in ld[:num]:
        CID     = x[:x.find(".png")]
        y[count,:]  = mfs[CID]
        preds[count,:] = means
        count+=1
   
    print "RMSE of guessing: ", np.sqrt(mean_squared_error(y, preds))

size    = 200
imdim   = size - 20                         #strip 10 pixels buffer from each size
direct  = "../data/images"+str(size)+"/"
ld      = listdir(direct)
numEx   = len(ld)


DUMP_WEIGHTS = True

shuffle(ld)

trainFs = ld[:int(numEx*0.8)]
testFs  = ld[int(numEx*0.8):]
trainL  = len(trainFs)
testL   = len(testFs)

print "number of examples: ", numEx
print "training examples : ", trainL
print "test examples : ", testL

batch_size      = 32
chunkSize       = 2048
testChunkSize   = 256
numTrainEx      = min(trainL,chunkSize)

with open("../cidsMF.pickle",'rb') as f:
    mfs    = cPickle.load(f)
    
outsize         = len(mfs[mfs.keys()[0]])

trainImages     = np.zeros((numTrainEx,1,imdim,imdim),dtype=np.float)
trainTargets    = np.zeros((numTrainEx,outsize),dtype=np.float)
testImages      = np.zeros((numTrainEx/10,1,imdim,imdim),dtype=np.float)
testTargets     = np.zeros((numTrainEx/10,outsize),dtype=np.float)

targetMeans,stds= getTargetMeans(mfs)


if len(sys.argv) <= 1:
    print "needs 'update' or 'new' as first argument"
    sys.exit(1)
    
if sys.argv[1].lower().strip() == "new":
    model = Sequential()
    
    model.add(Convolution2D(32, 1, 5, 5, border_mode='full')) 
    model.add(Activation('relu'))
    
    model.add(MaxPooling2D(poolsize=(2, 2)))
    
    model.add(Convolution2D(32, 32, 5, 5))
    model.add(Activation('relu'))
    
    model.add(MaxPooling2D(poolsize=(2, 2)))
    
    model.add(Convolution2D(64, 32, 5, 5)) 
    model.add(Activation('relu'))
    
    model.add(MaxPooling2D(poolsize=(2, 2)))
    
    model.add(Convolution2D(64, 64, 4, 4)) 
    model.add(Activation('relu'))
    
    model.add(MaxPooling2D(poolsize=(2, 2)))
    model.add(Dropout(0.25))
    
    model.add(Flatten())
    model.add(Dense(4096, 512, init='normal'))
    model.add(Activation('relu'))
    model.add(Dropout(0.5))
    
    model.add(Dense(512, outsize, init='normal'))
    
    
    model.compile(loss='mean_squared_error', optimizer='adadelta')

elif sys.argv[1].lower().strip() == "update":
    with open("../molecularFormula/wholeModel.pickle",'rb') as f:
        model     = cPickle.load(f)
        
else:
    print "needs 'update' or 'new' as first argument"
    sys.exit(1)



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
                trainTargets[count]         = np.divide(np.subtract(mfs[CID],targetMeans),stds)
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
                testTargets[count]         = np.divide(np.subtract(mfs[CID],targetMeans),stds)
                count +=1
        
        preds   = model.predict(testImages)
        RMSE    = np.sqrt(mean_squared_error(testTargets, preds))         
        print RMSE
        if RMSE < 3:
            for ind1 in range(0,len(preds)):
                if ind1 < 2:
                    p   = [ex for ex in preds[ind1]]
                    p   = [p[ind2]*stds[ind2]+targetMeans[ind2] for ind2 in range(0,len(targetMeans))]
                    t   = [x for x in testTargets[ind1]]
                    t   = [int(t[ind2]*stds[ind2]+targetMeans[ind2]) for ind2 in range(0,len(targetMeans))]
                    print p, t
        
        if DUMP_WEIGHTS:
            dumpWeights(model)

        with open("../molecularFormula/wholeModel.pickle", 'wb') as f:
            cp     = cPickle.Pickler(f)
            cp.dump(model)

del trainTargets, trainImages
""" END TRAINING """



