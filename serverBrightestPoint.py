import time
import threading
import json
import cherrypy
import cameraStuff as cs
import StringIO
from PIL import Image
import myglobals



myport = 8080
#myglobals.whiteDelay = 0.0050  
#myglobals.whiteShutter = 3
#myglobals.darkDelay = 0.0005
#myglobals.darkShutter = 1.9

import signal
import sys
def signal_handler(signal, frame):
        print('You pressed Ctrl+C!')
        cs.cam.stop()
        sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)


class Root(object):
    #global myglobals.whiteShutter, myglobals.whiteDelay, myglobals.darkShutter, myglobals.darkDelay
    @cherrypy.expose        
    def index(self, shutter=-999, gain=-999, delay=-999):
        cherrypy.response.headers["Access-Control-Allow-Origin"] = "*" 
        parseArguments( shutter, gain, delay)
        return getIndex()
        return cs.getInfo( cs.cam)
    @cherrypy.expose      
    def image_png(self, shutter=-999, gain=-999, delay=-999):
        parseArguments( shutter, gain, delay)
        return getFormattedImage('PNG')
    def image_jpg(self, shutter=-999, gain=-999, delay=-999):
        parseArguments( shutter, gain, delay)
        return getFormattedImage('JPEG')
    @cherrypy.expose      
    def shot_png(self, shutter=-999, gain=-999, delay=-999):
        parseArguments( shutter, gain, delay)
        return getFormattedImage('PNG')
    @cherrypy.expose          
    def shot_jpg(self, shutter=-999, gain=-999, delay=-999):
        parseArguments( shutter, gain, delay)
        return getFormattedImage('JPEG')
    @cherrypy.expose      
    def  brightestPoint_json(self, shutter=-999, gain=-999, delay=-999):
        cherrypy.response.headers["Access-Control-Allow-Origin"] = "*" 
        parseArguments( shutter, gain, delay)
        return json.dumps( cs.brightestPoint( cs.cam))
    @cherrypy.expose      
    def  brightestpoint_json(self, shutter=-999, gain=-999, delay=-999):
        cherrypy.response.headers["Access-Control-Allow-Origin"] = "*" 
        parseArguments( shutter, gain, delay)
        return json.dumps( cs.brightestPoint( cs.cam))
    @cherrypy.expose
    def stressTest_html(self):
        return open( u'stressTest.html')



      
def parseArguments( shutter, gain, delay):
    if gain > -999:
        cs.setGain( cs.cam, gain)
    if shutter > -999:
        cs.setShutter( cs.cam, float(shutter)/10.0 )
        #i think this driver is slightly different as far as shutter values
        # a division by 10 seems to be about correct, but more testing should be done
    if delay > -999:
        cs.setDelay( cs.cam, delay)


def getFormattedImage(imgFormat):
    cherrypy.response.headers["Access-Control-Allow-Origin"] = "*" 
    cherrypy.response.headers['Content-Type'] = 'image/' + imgFormat.lower()
    outimg = getImage()
    output = StringIO.StringIO()
    outimg.save(output, format=imgFormat)
    message = output.getvalue()
    return message

def getImage():
    cs.lastPictureTime = time.time()
    currimg = cs.showImg(cs.cam)
    print('image.png taken at', cs.lastPictureTime)
    outimg = Image.fromarray(currimg)
    return outimg

def getIndex():
    port = str(myport)
    responseString = "<HTML><BODY><h3> Your connected to<h1> Web camera server</h1></h3>" 
    responseString += "<hr>Usage:<li><b><a href='http://127.0.0.1:" + port + "/shot.jpg'>http://127.0.0.1:" + port + "/shot.jpg</a> </b>"
    responseString += " <li><b><a href='http://127.0.0.1:" + port + "/shot.jpg?shutter=4&gain=0'>http://127.0.0.1:" + port + "/shot.jpg?shutter=4&gain=0</a></b>. Shutter and Gain can be set absolutely"
    responseString += " <li><b><a href='http://127.0.0.1:" + port + "/shot.jpg?delay=0.002'>http://127.0.0.1:" + port + "/shot.jpg?delay=0.002</a></b>. The delay in seconds afer GPIO trigger signal"
    responseString += " <li><b><a href='http://127.0.0.1:" + port + "/shot.jpg?shutter=-1&gain=-1&delay=-1'>http://127.0.0.1:" + port + "/shot.jpg?shutter=-1&gain=-1&delay=-1</a></b>. Negative numbers turn on automatic mode"
    responseString += " <li><b><a href='http://127.0.0.1:" + port + "/?shutter=4&gain=0&delay=0.002'>http://127.0.0.1:" + port + "/?shutter=4&gain=0&delay=0.002</a></b>. You don't need to take a picture to set the parameters "
    responseString += " <li><b><a href='http://127.0.0.1:" + port + "/shot.png'>http://127.0.0.1:" + port + "/shot.png</a></b>. Different formats based on extension. Supported extensions are jpg, png, and bmp."
    responseString += " <li><b><a href='http://127.0.0.1:" + port + "/brightestpoint.json'>http://127.0.0.1:" + port + "/brightestpoint.json</a></b>. Find the brightest Point"
    responseString += " <li><b><a href='http://127.0.0.1:" + port + "/brightestpoint.json?shutter=40&gain=0'>http://127.0.0.1:" + port + "/brightestpoint.json?shutter=40&gain=0</a></b>. Find the brightest Point"
    responseString += " <li><b><a href='http://127.0.0.1:" + port + "/stressTest.html'>http://127.0.0.1:" + port + "/stressTest.html</a></b>... more tests ..."
    responseString += "</BODY></HTML>"
    return responseString


if __name__ == '__main__':
    cherrypy.config.update({
                            'engine.autoreload_on': False,
                            'engine.threadCount': 1 ,
                            "server.logToScreen" : True,
                            })
    config = {  }
    cherrypy.quickstart(Root(), '/', config)



