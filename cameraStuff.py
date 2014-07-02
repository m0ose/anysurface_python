import sys
import time
from pydc1394 import DC1394Library, Camera
from PIL import Image
import matplotlib
import decimal
import signal
import numpy as np
import cv2
import json
import random
import myglobals

currentShutter = None
currentDelay = None
currentGain = None
lastPictureTime = time.time()
lastPicture = None
background = None


def initCam(lib, mode=None, fps=30, shutter=6.1, gain=1, isospeed = 800):
    cams = lib.enumerate_cameras()
    if len(cams)<=0:
        print("ERROR: no Camera found. Make sure it is plugged into the computer")
        sys.exit(1)
    cam0_handle = cams[0]
    print(cams)
    cam0 = Camera(lib, guid=cam0_handle['guid'], mode=None, framerate=fps, shutter=shutter, gain=gain)
    cam0.mode = cam0.modes[3]# 3 is black and white
    cam0.start(interactive=True)
    setDefaults( cam0)
    print( "opening Camera")
    print(getInfo(cam0))
    return cam0

def setDefaults(cam0):
    cam0.gain.mode = 'auto'#looks like you need to set gain before exposure. weird?
    cam0.brightness.mode = 'auto'#'manual'
    cam0.exposure.mode = 'auto'
    cam0.shutter.mode='auto'
    cam0.trigger.on = False
    cam0.trigger_delay.on = False   

def restartCamera( cam0):
    myglobals.logger.info("restarting camera")
    cam0.stop()
    cam0.start( interactive=True)



def getInfo(cam0):
    result = ""
    result = result +  "Vendor:" + cam0.vendor + "\n"
    result = result +  "Model:" + cam0.model + "\n"
    result = result +  "GUID:" + str(cam0.guid) + "\n"
    result = result +  "Mode:" + str(cam0.mode)+ "\n"
    result = result +  "Framerate: " + str(cam0.fps)+ "\n"
    result = result +  "Available modes" + str(cam0.modes)+ "\n"
    result = result +  "Available features" + str(cam0.features)+ "\n"  
    for feat in cam0.features:
        myfeat = cam0.__getattribute__(feat)
        result = result +  ("feat: %s (cam0): %s" % (feat,myfeat.val))+ "\t"
        if hasattr(myfeat, 'range'):
            result = result +  "    range: " +  str(myfeat.range)+ "\n"
    result = result +  "trigger ON:" + str(cam0.trigger.on)+ "\n"
    return result

def showImg(cam0, filename=None):
    global imgshape
    matrix = cam0.current_image
    imgshape = matrix.shape     
    if filename != None:
        img1 = Image.fromarray(matrix) 
        img1.save(filename)
    lastPicture = matrix
    return matrix

def brightestPoint(cam):
    global background
    mat = showImg(cam) * 1.0
    if background == None:
        background = mat  
    fg = np.minimum( np.maximum(mat - background,0),255).astype('uint8')
    mm = cv2.minMaxLoc(fg)
    imgshape = mat.shape
    if myglobals.saveImages and random.uniform(0,1) > 0.99:
        print("saving")
        cv2.imwrite('./imgs/background.png', background)
        cv2.imwrite('./imgs/fg.png', fg)
    if mm[1] < 50:
        return {'x':0, 'y':0, 'x1':0, 'y1':0, 'i':0} 
    xy = [float(mm[3][0]+0.5)/imgshape[1], float(mm[3][1]+0.5)/imgshape[0] ]
    background = 0.99*background + 0.01 * mat 
    print(mm)
    return({'x':mm[3][0], 'y':mm[3][1], 'x1':xy[0], 'y1':xy[1], 'i':1000} )  

def setDelay(cam, delay):
    global currentDelay
    delay = float(delay)
    changed = False
    print( 'set delay called ', delay)
    if  currentDelay != delay:
        if delay <= 0 :
            print( 'going to auto trigger mode')
            cam.trigger.on = False
            cam.trigger_delay.on = False   
            print( 'going to auto trigger mode')
        else:
            cam.trigger.on = True
            cam.trigger_delay.on = True   
            cam.trigger_delay.val = delay
        currentDelay = delay
        changed = True
        print("set delay to", delay)
        #time.sleep(0.0030)
        showImg(cam)
    return changed

def setShutter(cam, shutter):
    shutter = float(shutter )
    global currentShutter
    changed = False
    if  currentShutter != shutter:
        if shutter <= -1 and shutter > -999:
            cam.shutter.mode='auto'
        elif shutter >= 0 :
            cam.shutter.mode='manual'
            cam.shutter.val = shutter
        currentShutter = shutter
        changed = True
        print("set shutter to", shutter)
        #time.sleep(0.0030)#take one picture 
        showImg(cam)
    return changed      

def setGain(cam, gain):
    gain = float(gain )
    global currentGain
    changed = False
    if  currentGain != gain:
        if gain <= -1 and gain > -999:
            cam.gain.mode='auto'
        elif gain >= 0 :
            cam.gain.mode='manual'
            cam.gain.val = gain
        currentGain = gain
        changed = True
        print("set gain to", gain)
        #time.sleep(0.0030)#take one picture 
        showImg(cam)
    return changed     



l = DC1394Library()
cam = initCam(l)
imgshape = (1,1)

