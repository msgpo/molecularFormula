# -*- coding: utf-8 -*-
"""
Created on Tue Dec 15 13:44:36 2015

@author: test
"""

from helperFuncs import getOCRScaledTargets, getOCRTargets, getMeansStds
import helperFuncs

import cPickle
import sys
from os import listdir
import matplotlib.pyplot as plt
import skimage.io as io
from skimage import filters
#from skimage.transform import resize 
import numpy as np
from tabulate import tabulate
#from skimage.transform import resize
#import scipy.misc.imresize as resize
#import scipy.misc.imsave as imsave
from scipy.misc import imresize as resize
from scipy.misc import imsave as imsave
from PIL import Image
from scipy import misc
from sklearn.metrics import mean_squared_error

def convertIt(image):
    image   = np.ones(image.shape)*255 - image
    image   = np.divide(image,255)
    #return np.dot(image[...,:3], [0.299, 0.587, 0.144])
    return image

def minusOnes(image):
    return np.ones((image.shape)) - image

def myResize(image,size):
    #print "input pixel sum", np.sum(image)
    #plt.imshow(image)
    #plt.savefig("../evaluation"+CID+"whatever.jpg",format="jpg")
    output          = np.zeros((size,size))
    difference      = int(size-size*0.75)/2
    size            = int(size*0.75)
    curr_y, curr_x  = image.shape
    

    if curr_y > curr_x:
        #the image is wide
        ratio   = size*1./curr_y
        xsize   = int(ratio*curr_x)
        offset  = (size-xsize)/2
        im2     = resize(image,(size,xsize),interp="bicubic")
        #print im2.shape
        output[difference:difference+size , difference+offset:difference+offset+xsize]   = im2
        
    else:
        #The image is tall
        ratio   = size*1./curr_x
        ysize   = int(ratio*curr_y)
        offset  = (size-ysize)/2
        im2     = resize(image,(ysize,size),interp="bicubic")
        print im2.shape
        output[difference+offset:difference+offset+ysize,difference:difference+size]   = im2
    #print output.shape
    #print "output pixel sum", np.sum(output)
    return output
    
def putInSize(image,size):
    curr_y, curr_x  = image.shape
    output          = np.zeros((size,size))
    
    xoff    = int((size - curr_x)/2)
    yoff    = int((size - curr_y)/2)
    output[yoff:yoff+curr_y, xoff:xoff+curr_x] = image
    return output




def printFormula(p,t,atomlist,cid,means):
    print '\t',cid
    headers     = ["FEATURE","ACTUAL","PREDICTED","FLOAT","MEAN"]
    tab         = []
    for ind in range(0,len(atomlist)):
        if t[ind] > .1:
            tab.append([atomlist[ind],int(t[ind]),int(np.round(p[ind])),p[ind],means[ind]])
            #print atomlist[ind],'\t\t',int(t[ind]),'\t\t',int(np.round(p[ind])),'\t\t', p[ind],'\t',ind
        elif np.round(p[ind]) > 0:
            #print atomlist[ind],'\t\t',int(t[ind]),'\t',int(np.round(p[ind])),'\t', p[ind],'\t',ind
            tab.append([atomlist[ind],int(t[ind]),int(np.round(p[ind])),p[ind],means[ind]])
    print tabulate(tab,headers=headers)

def printFormula2(p,atomlist):
    headers     = ["FEATURE","PREDICTED","FLOAT"]
    tab         = []
    for ind in range(0,len(atomlist)):
        tab.append([atomlist[ind],int(np.round(p[ind])),p[ind]])
    print tabulate(tab,headers=headers)

def getSize(folder):
    fold 	= folder[folder[-1].rfind("/")+1:]
    fold 	= fold[:fold.find("_")]
    print fold
    fold 	= fold[fold.rfind("/")+1:]
    print fold
    return fold

with open(sys.argv[1]+"wholeModel.pickle",'rb') as f:
    model   = cPickle.load(f)
    
size 	= int(getSize(sys.argv[1]))
imdim   = size
#OCRfeatures, labels     = getOCRScaledTargets()
OCRTargets, labels  = getOCRTargets()
means,stds  = getMeansStds()
    
    
if True:
    ld  = listdir("/home/test/usan/")
    images  = np.zeros((1,1,imdim,imdim),dtype=np.float)
    for x in ld:
        print x
        try:
            CID     = x
            print "reading in"
            image   = io.imread("/home/test/usan/"+x,as_grey=True)
            image   = minusOnes(image)
            print "numpying"
            image   = np.array(image)
            #image   = convertIt(image)
            print "resizing"
            print image.shape
            
            image   = helperFuncs.processImage(None,"/",True,0.3,"random",300,noise=True,image=image)            
            
#            image   = myResize(image,imdim)
            #image   = putInSize(image,imdim)
#            image   = np.where(image >0.05, 1.,0)
#            image   = filters.gaussian_filter(image,0.2)
#            image   = 0.05*np.random.rand(image.shape[0], image.shape[1]) + image

            #image   = filters.gaussian_filter(image,0.2)
            #print "binarizing"
            print image.shape
            #image   = np.where(image>0.2,1,0)
#            for countzor in range(0,image.shape[0]):
#                print image[countzor,:]
#                stop=raw_input("")
            #image   = np.where(image > 0.1,1.0,0.0)
            #trainTarget        = OCRfeatures[CID]
            #notScaled       = OCRTargets[CID]
            images[0,0,:,:]     = image

            
            #plt.imshow(image)
            #plt.savefig("../evaluation/"+x+".jpg",format="jpg")
            imsave("../evaluation/"+x+".jpg",image)  
            
            pred    = model.predict(images)
            stop=raw_input("")
    #        print "Label","Actual", "Pred", "Mean"
    #        for i in range(0,len(pred[0])):
    #            if (notScaled[i] > 0.01) or (pred[0][i] > 0.5):
    #                print labels[i], notScaled[i], pred[0][i], means[i]
            printFormula2(pred[0],labels)
            #RMSE    = np.sqrt(mean_squared_error(notScaled, pred[0]))         
            #print "RMSE: ", RMSE      
    
        except (KeyError,ValueError) as e:
            print e    
        
if len(sys.argv) < 3:    
        
    ld  = listdir(sys.argv[1]+"/tempTest/")
    images          =  np.zeros((1,1,imdim,imdim),dtype=np.float)
    for x in ld:
        print x
        try:
            CID     = x[:x.find(".sdf")]
            image   = io.imread(sys.argv[1]+"tempTest/"+x,as_grey=True)[10:-10,10:-10]   
#            for countzor in range(0,image.shape[0]):
#                print image[countzor,:]
#                stop=raw_input("")
            image   = np.where(image > 0.1,1.0,0.0)
            #trainTarget        = OCRfeatures[CID]
            notScaled       = OCRTargets[CID]
            images[0,0,:,:]     = image
            pred    = model.predict(images)
            
            plt.imshow(image)
            print np.sum(image)
            plt.savefig("../evaluation/nopad"+CID+".jpg",format="jpg")
    #        print "Label","Actual", "Pred", "Mean"
    #        for i in range(0,len(pred[0])):
    #            if (notScaled[i] > 0.01) or (pred[0][i] > 0.5):
    #                print labels[i], notScaled[i], pred[0][i], means[i]
            printFormula(pred[0],notScaled,labels,CID,means)
            RMSE    = np.sqrt(mean_squared_error(notScaled, pred[0]))         
            print "RMSE: ", RMSE
            
    
        except (KeyError,ValueError) as e:
            pass
        
else:
    

    ld  = listdir("../data/INNimages/")
    images  = np.zeros((1,1,imdim,imdim),dtype=np.float)
    for x in ld:
        print x
        try:
            CID     = x
            print "reading in"
            #image   = misc.imread("../data/INNimages/"+x,flatten=1)
            image   = Image.open("../data/INNimages/"+x)
            #image   = image.convert("LA", image)
            print "numpying"
            image   = np.array(image)
            image   = convertIt(image)
            print image[int(image.shape[0]/2.),:]
            stop=raw_input("stop")
            print "resizing"
            print image.shape
            image   = myResize(image,imdim)
            #image   = putInSize(image,imdim)
            image   = np.where(image >0.05, 1.,0)
            image   = filters.gaussian_filter(image,0.2)
            print "binarizing"
            print image.shape
            #image   = np.where(image>0.2,1,0)
#            for countzor in range(0,image.shape[0]):
#                print image[countzor,:]
#                stop=raw_input("")
            #image   = np.where(image > 0.1,1.0,0.0)
            #trainTarget        = OCRfeatures[CID]
            notScaled       = OCRTargets[CID]
            images[0,0,:,:]     = image
            pred    = model.predict(images)
            
            plt.imshow(image)
            plt.savefig("../evaluation/"+CID+".jpg",format="jpg")
    #        print "Label","Actual", "Pred", "Mean"
    #        for i in range(0,len(pred[0])):
    #            if (notScaled[i] > 0.01) or (pred[0][i] > 0.5):
    #                print labels[i], notScaled[i], pred[0][i], means[i]
            printFormula(pred[0],notScaled,labels,CID,means)
            RMSE    = np.sqrt(mean_squared_error(notScaled, pred[0]))         
            print "RMSE: ", RMSE
            
    
        except (KeyError,ValueError) as e:
            print e
    
    
