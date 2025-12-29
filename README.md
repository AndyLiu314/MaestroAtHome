# Maestro At Home
## Made By: Andy Liu

### **Overview:**
A computer vision project mapping hand gestures to modular sound synthesis through OSC channels. Users are given the ability to generate and direct synthesized sounds using the position and movement of their hands. The gesture-capture script for this project was written in Python using the MediaPipe and OpenCV computer vision libraries. Sound synthesis was done virtually using a custom-built VCV Rack patch. The scripts and software communicate using OSC. 

### **Gesture Inputs:**
Vertical movements of the right hand map directly to volume control, while horizontal movement is dedicated to left and right channel panning. Pinching the index finger and thumb together "squeezes" the frequency, increasing the pitch and octave of the sound. Finally, the left hand toggles playback. Opening the left hand enables sound while closing it disables all sound from playing. 

<br>![The Left Hand](/media/left-hand.jpg)
![The Right Hand](/media/right-hand.jpg)

### **VCV Rack Example:**
<br>![Rack](/media/rack-example.jpg)

### **Movement Demo:**
<br>![Demo](/media/demo.gif)
