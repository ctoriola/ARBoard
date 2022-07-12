from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
import cv2
import numpy as np
import math
from object_module import *
import sys
import aruco_module as aruco 
from my_constants import *
from utils import get_extended_RT
import time
Builder.load_string('''
<CameraClick>:
    orientation: 'vertical'
    Camera:
        id: camera
        resolution: (640, 480)
        play: False
''')


class CameraClick(BoxLayout):
    def capture(self):
        

        obj = three_d_object('data/3d_objects/low-poly-fox-by-pixelmannen.obj', 'data/3d_objects/texture.png')
        marker_colored = cv2.imread('data/m1.png')
        assert marker_colored is not None, "Could not find the aruco marker image file"
        #accounts for lateral inversion caused by the webcam
        marker_colored = cv2.flip(marker_colored, 1)

        marker_colored =  cv2.resize(marker_colored, (480,480), interpolation = cv2.INTER_CUBIC )
        marker = cv2.cvtColor(marker_colored, cv2.COLOR_BGR2GRAY)

        print("trying to access the webcam")
        camera = self.ids['camera']
        
        h,w = marker.shape
        #considering all 4 rotations
        marker_sig1 = aruco.get_bit_sig(marker, np.array([[0,0],[0,w], [h,w], [h,0]]).reshape(4,1,2))
        marker_sig2 = aruco.get_bit_sig(marker, np.array([[0,w], [h,w], [h,0], [0,0]]).reshape(4,1,2))
        marker_sig3 = aruco.get_bit_sig(marker, np.array([[h,w],[h,0], [0,0], [0,w]]).reshape(4,1,2))
        marker_sig4 = aruco.get_bit_sig(marker, np.array([[h,0],[0,0], [0,w], [h,w]]).reshape(4,1,2))

        sigs = [marker_sig1, marker_sig2, marker_sig3, marker_sig4]

        rval, frame = camera.read()
        assert rval, "couldn't access the webcam"
        h2, w2,  _ = frame.shape

        h_canvas = max(h, h2)
        w_canvas = w + w2

        while rval:
            rval, frame = camera.read() #fetch frame from webcam
            key = cv2.waitKey(20) 
            if key == 27: # Escape key to exit the program
                break

            canvas = np.zeros((h_canvas, w_canvas, 3), np.uint8) #final display
            canvas[:h, :w, :] = marker_colored #marker for reference

            success, H = aruco.find_homography_aruco(frame, marker, sigs)
            # success = False
            if not success:
                # print('homograpy est failed')
                canvas[:h2 , w: , :] = np.flip(frame, axis = 1)
                cv2.imshow("webcam", canvas )
                continue

            R_T = get_extended_RT(A, H)
            transformation = A.dot(R_T) 
            
            augmented = np.flip(augment(frame, obj, transformation, marker), axis = 1) #flipped for better control
            canvas[:h2 , w: , :] = augmented



class TestCamera(App):

    def build(self):
        return CameraClick()


TestCamera().run()