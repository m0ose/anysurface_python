anysurface_python
=================

Webcam server written in python using libdc1394. 
Originally written for Point Grey firefly camera

supports REST requests for shutter, gain, and trigger delay.

<ul>
USAGE:
<li>http://127.0.0.1:8080/shot.jpg</li>
<li>http://127.0.0.1:8080/shot.jpg?shutter=4&gain=0. Shutter and Gain can be set absolutely</li>
<li>http://127.0.0.1:8080/shot.jpg?delay=0.002. The delay in seconds afer GPIO trigger signal</li>
<li>http://127.0.0.1:8080/shot.jpg?shutter=-1&gain=-1&delay=-1. Negative numbers turn on automatic mode</li>
<li>http://127.0.0.1:8080/?shutter=4&gain=0&delay=0.002. You don't need to take a picture to set the parameters</li>
<li>http://127.0.0.1:8080/shot.png. Different formats based on extension. Supported extensions are jpg, png, and bmp.</li>
<li>http://127.0.0.1:8080/brightestpoint.json. Find the brightest Point</li>
<li>http://127.0.0.1:8080/brightestpoint.json?shutter=40&gain=0. Find the brightest Point</li>
<li>http://127.0.0.1:8080/stressTest.html... more tests ...</li>
</ul>
