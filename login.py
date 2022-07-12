# import all the relevant classes
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty
from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.camera import Camera
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.core.window import Window
import text2png, rot_img_and_send
import pandas as pd
from kivy.uix.boxlayout import BoxLayout
import cv2
import numpy as np
import math
from object_module import *
import sys
import aruco_module as aruco 
from my_constants import *
from utils import get_extended_RT
Builder.load_string('''

''')

global lname
  
# class to call the popup function
class PopupWindow(Widget):
    def btn(self):
        popFun()
  
# class to build GUI for a popup window
class P(FloatLayout):
    pass
  
# function that displays the content
def popFun():
    show = P()
    window = Popup(title = "popup", content = show,
                   size_hint = (None, None), size = (300, 300))
    window.open()


class mainWindow(Screen):
    pass
  
# class to accept user info and validate it
class loginWindow(Screen):
    email = ObjectProperty(None)
    pwd = ObjectProperty(None)
    def validate(self):
  
        # validating if the email already exists 
        if self.email.text not in users['Email'].unique():
            popFun()
        else:
  
            # switching the current screen to display validation result
            sm.current = 'logdata'
  
            # reset TextInput widget
            self.email.text = ""
            self.pwd.text = ""
  
  
# class to accept sign up info  
class signupWindow(Screen):
    name2 = ObjectProperty(None)
    email = ObjectProperty(None)
    pwd = ObjectProperty(None)
    def signupbtn(self):
  
        # creating a DataFrame of the info
        user = pd.DataFrame([[self.name2.text, self.email.text, self.pwd.text]],
                            columns = ['Name', 'Email', 'Password'])
        lname = self.name2.text
        if self.email.text != "":
            if self.email.text not in users['Email'].unique():
  
                # if email does not exist already then append to the csv file
                # change current screen to log in the user now 
                user.to_csv('login.csv', mode = 'a', header = False, index = False)
                sm.current = 'login'
                self.name2.text = ""
                self.email.text = ""
                self.pwd.text = ""
        else:
            # if values are empty or invalid show pop up
            popFun()

class CameraScreen(Screen):
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

      
# class to display validation result
class logDataWindow(Screen):
    msg = ObjectProperty(None)
    def sendmsg(self):
        print(self.msg.text)
        text2png.pngthetext(self.msg.text, 'data/3d_objects/test.png', "Teach", fontfullpath = "font.ttf")
        rot_img_and_send.work_on_img()
  
# class for managing screens
class windowManager(ScreenManager):
    pass
  
# kv file
kv = Builder.load_file('login.kv')
sm = windowManager()
  
# reading all the data stored
users=pd.read_csv('login.csv')
  
# adding screens
sm.add_widget(mainWindow(name='main'))
sm.add_widget(loginWindow(name='login'))
sm.add_widget(signupWindow(name='signup'))
sm.add_widget(logDataWindow(name='logdata'))
sm.add_widget(CameraScreen(name='camera'))
  
# class that builds gui
class loginMain(App):
    def build(self):
        return sm
  
# driver function
if __name__=="__main__":
    loginMain().run()