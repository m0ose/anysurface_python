from BaseHTTPServer import BaseHTTPRequestHandler
import urlparse
import cameraStuff as cs
import time
from PIL import Image
import StringIO
import json
import math

myport = 8080

class GetHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        parsed_path = urlparse.urlparse(self.path)
        realPath = parsed_path.path.lower()
        argums = urlparse.parse_qs( parsed_path.query.lower())

        shutter = -999
        gain = -999
        delay = -999
        if argums.get('delay'):
            #print( 'delay', argums.get('delay'))
            delay = float( argums.get('delay')[0] )
        if argums.get('shutter'):
            #print( 'shutter', argums.get('shutter'))
            shutter = float( argums.get('shutter')[0])
        if argums.get('gain'):
            #print( 'gain', argums.get('gain'))
            gain = float( argums.get('gain')[0])

        parseArguments( shutter = shutter, gain = gain, delay=delay)


        if 'shot' in realPath or 'image' in realPath:
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            if '.png' in realPath:
                self.wfile.write(getFormattedImage('PNG'))
            else:
                self.wfile.write(getFormattedImage('JPEG'))
        elif 'brightestpoint.json' in realPath:
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            jsn = json.dumps( cs.brightestPoint( cs.cam))
            self.wfile.write(jsn)
        elif 'stresstest.html' in realPath:
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            f = open( u'stressTest.html')
            self.wfile.write(f.read())
            f.close()
        else: #index file
            message_parts = [
                ' ' + getIndex(),
                ' Camera : ' + cs.getInfo( cs.cam),
                '\n\nCLIENT VALUES:',
                'client_address=%s (%s)' % (self.client_address,
                                            self.address_string()),
                'command=%s' % self.command,
                'path=%s' % self.path,
                'real path=%s' % parsed_path.path,
                'query=%s' % parsed_path.query,
                'request_version=%s' % self.request_version,
                '',
                'SERVER VALUES:',
                'server_version=%s' % self.server_version,
                'sys_version=%s' % self.sys_version,
                'protocol_version=%s' % self.protocol_version,
                '',
                'HEADERS RECEIVED:',
                ]
            for name, value in sorted(self.headers.items()):
                message_parts.append('%s=%s' % (name, value.rstrip()))
            message_parts.append('')
            message = '\r\n'.join(message_parts)
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(message)
        return


def parseArguments( shutter = -999, gain = -999, delay = -999):
    shutter = float( shutter)
    gain = float( gain)
    delay = float( delay)
    if( shutter < 0.000001):
        shutter = 0
    if( delay < 0.000001):
        delay = 0
    if( gain < 0.000001):
        gain = 0

    if gain > -999:
        cs.setGain( cs.cam, gain)
    if shutter > -999:
        cs.setShutter( cs.cam, float(shutter)/10.0 )
        #i think this driver is slightly different as far as shutter values
        # a division by 10 seems to be about correct, but more testing should be done
    if delay > -999:
        cs.setDelay( cs.cam, delay)

def getFormattedImage(imgFormat):
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
    global myport
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
    responseString += "<br><br><pre>" + cs.getInfo(cs.cam) +"</pre>"
    responseString += "</BODY></HTML>"
    return responseString


if __name__ == '__main__':
    from BaseHTTPServer import HTTPServer
    server = HTTPServer(('localhost', myport), GetHandler)
    print 'Starting server, use <Ctrl-C> to stop'
    try: 
        server.serve_forever()
    except:
        cs.cam.stop()