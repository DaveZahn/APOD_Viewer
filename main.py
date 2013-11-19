#Image Slideshow Viewer
#Usage Information
#  - Click Mouse/Touch Screen to show info and pause slideshow
#  - Touch again to hide info and continue slideshow
#  - Escape key will halt execution

import random, os, glob, sys
from kivy.config import Config
#Use Config.set to enable fullscreen view in Windows
#Config.set('graphics', 'show_cursor', '0')
#Config.set('graphics', 'fullscreen', '1')
#Config.set('graphics', 'width', '1920')
#Config.set('graphics', 'height', '1080')
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ListProperty
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.base import EventLoop

global strDir
#strTemp can be used to have one Temp.jpg instead of an image cache directory
global strTemp
global strCache
global strData
global sngInterval
global intCount
global bPaused
global bBuildCache
global bReschedule
global strFileName
global sngWidth
global sngHeight
#Device Independent (Default) Settings
sngInterval = 0.002
bBuildCache = True
bReschedule = True # False
bPaused = False
sngWidth = 1920
sngHeight = 1080
strDir = ""
strTemp = ""
strCache = ""
#Setting For Various Devices
#Create a set of paths for each device you plan to support
#Windows 7 Notebook
if os.path.isdir("C:\\Users\\Dave\\Pictures\\apod\\"):
    strDir = "C:\\Users\\Dave\\Pictures\\apod\\"
    strTemp = "C:\\Users\\Dave\\Pictures\\Temp.jpg"
    strCache = "C:\\Users\\Dave\\Pictures\\apod\\cache\\"
    strData = "C:\\Users\\Dave\\Pictures\\apod\\data\\"
#NookHD+
if os.path.isdir('/mnt/ext_sdcard/Pictures/apod/'):
    strDir = '/mnt/ext_sdcard/Pictures/apod/'
    strTemp = '/mnt/ext_sdcard/Pictures/Temp.jpg'
    strCache = '/mnt/ext_sdcard/Pictures/apod/cache/'
    strData = '/mnt/ext_sdcard/Pictures/apod/data/'
#Galaxy Note 2
if os.path.isdir('/mnt/extSdCard/PhotoAlbums/apod/'):
    strDir = '/mnt/extSdCard/PhotoAlbums/apod/'
    strTemp = '/mnt/extSdCard/PhotoAlbums/apod/Temp.jpg'
    strCache = '/mnt/extSdCard/PhotoAlbums/apod/cache/'
    strData = '/mnt/extSdCard/PhotoAlbums/apod/data/'
#Raspberry Pi
if os.path.isdir('/home/pi/pishare/'):
    strDir = '/home/pi/pishare/'
    strTemp = '/home/pi/Temp.jpg'
    strCache = '/home/pi/pishare/cache/'
    strData = '/home/pi/pishare/data/'
    sngInterval = 10.002
#set strCache to blank string to skip using cached images
#strCache = ""

class RootWidget(FloatLayout):
    def __init__(self, **kwargs):
        super(RootWidget, self).__init__(**kwargs)
        self.photos = []
        self.photos = glob.glob(strDir + "*.jpg")
        global intCount
        #global sngInterval
        intCount = len(self.photos)
        strImage = random.choice(self.photos)
        img = Image(source=strImage, id='MainImage')
        #Turn on allow_stretch to upscale smaller images to fullscreen
        #img.allow_stretch = True
        self.add_widget(img)
        cb = CustomBtn(size_hint=(1,1)) #, font_size='24dp')
        cb.bind(pressed=self.btn_pressed)
        #cb.text = 'This is a test.'
        cb.id = 'MainButton'
        cb.bind(texture_size=cb.setter('size'))
        cb.bind(size=cb.setter('text_size')) 
        self.add_widget(cb)
        self.change_image()
        if not bReschedule:
            Clock.schedule_interval(self.change_image, sngInterval)
        #if bReschedule:
        #    Clock.schedule_once(self.change_image, sngInterval)

    def btn_pressed(self, instance, pos):
        print "Button Pressed"
        img = None #Image() #Using object name enables autocomplete in Visual Studio, but causes errors at runtime
        btn = None #ToggleButton()

        for child in self.children:
            if child.id == 'MainButton':
                btn = child 
        global bPaused
        if not bPaused:
            if bReschedule:
                print "Pausing..."
                Clock.unschedule(self.change_image)
                bPaused = True
                global strData
                global strFileName
                strTitle = strData + strFileName.replace('.jpg', '_Title.txt')
                #load the btnText?
                if (os.path.isdir(strData)) and (os.path.isfile(strTitle)):
                    f = open(strData + strFileName.replace('.jpg', '_Title.txt'))
                    strTitle = f.read()
                    f.close
                    f = open(strData + strFileName.replace('.jpg', '_Info.txt'))
                    strInfo = f.read()
                    f.close
                    btn.text = strTitle + ': ' + strInfo                                        

        elif bPaused:
            bPaused = False
            print "Resuming..."
            #btn.text = "Resuming..."
            btn.text = ""
            self.change_image()

    def change_image(self, whatever = None):
        strRandom = random.choice(self.photos)
        EventLoop.window.title = str(len(self.photos)) + '/' + str(intCount) + ' Loading:' + strRandom    

        img = None #Image()
        btn = None #ToggleButton()
        
        #get Widgets from list of children
        for child in self.children:
            #print child.id
            if child.id == 'MainImage':
                img = child
            if child.id == 'MainButton':
                btn = child 

        try:
            #comment out the exception to try loading by setting image source
            raise Exception("Processing with PIL")
            img.source = strRandom
        except Exception:
            try:
                global strCache
                global bBuildCache
                global strFileName
                strCached = ""
                strFileName = os.path.basename(strRandom)

                strTitle = strData + strFileName.replace('.jpg', '_Title.txt')
                #load the btnText?
                if (os.path.isdir(strData)) and (os.path.isfile(strTitle)):
                    f = open(strData + strFileName.replace('.jpg', '_Title.txt'))
                    strTitle = f.read()
                    f.close
                    f = open(strData + strFileName.replace('.jpg', '_Info.txt'))
                    strInfo = f.read()
                    f.close
                    #This is where we choose what to load into the button text when loading images
                    btn.text = '' # strTitle # + ': ' + strInfo

                if (os.path.isdir(strCache)) and (os.path.isfile(strCache + strFileName)):
                    strCached = strCache + strFileName
                elif (os.path.isdir(strCache)) and (bBuildCache == True):
                    print "Adding image to cache..."
                    from PIL import Image
                    im = Image.open(strRandom)
                    imgWidth, imgHeight = im.size
                    bResized = False
                    #wndWidth, wndHeight =
                    if imgHeight > sngHeight:
                        bResized = True
                        sngChange = sngHeight / imgHeight
                        imgHeight = sngHeight
                        imgWidth = int(imgWidth * sngChange)
                    if imgWidth > sngWidth:
                        bResized = True
                        sngChange = sngWidth / imgWidth
                        imgWidth = sngWidth
                        imgHeight = int(imgHeight * sngChange)
                    szNew = imgWidth, imgHeight
                    #if bResized:
                    #set to true to save all images to the cache
                    if True:
                        im=im.resize(szNew, Image.ANTIALIAS)
                        if not (strCache == ""):
                            if not os.path.exists(strCache):
                                os.makedirs(strCache)
                            strCached = strCache + os.path.basename(strRandom)
                            if (not os.path.isfile(strCached)):
                                try:
                                    im.save(strCached)      
                                except Exception as e:
                                    print "save cache file found: " + e.message        
                                    strCached = ""
                            else:
                                print "save cache file found"        
                    #else:
                    #    im.save(strTemp)
                if not strCached == "":
                    img.source = strCached
                else:        
                    img.source = strRandom
                    #img.reload()
            except Exception as e:
                print "Error(" + e.message + ") loading image " + strRandom
        #continue with the logic
        self.photos.remove(strRandom)                                       
        if len(self.photos) < 1:
            self.photos = glob.glob(strDir + "*.jpg")
        #global bReschedule
        if bReschedule:
            Clock.schedule_once(self.change_image, sngInterval)


class CustomBtn(ToggleButton):
    pressed = ListProperty([0, 0])
    background_down='button_down.png'
    background_normal='button_normal.png'

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.pressed = touch.pos
            #call Super to handle toggling the background_color
            return super(CustomBtn, self).on_touch_down(touch)

        return super(CustomBtn, self).on_touch_down(touch)

    def on_pressed(self, instance, pos):
        print ('pressed at {pos}'.format(pos=pos))

class TestApp(App):
    def build(self):
        keyb = Window.request_keyboard(self.stop, self)
        keyb.bind(on_key_down = self.key_pressed)
        return RootWidget()
    
    def key_pressed(self, keyboard, keycode, text, modifiers):
        sys.exit()

if __name__ == '__main__':
    TestApp().run()
