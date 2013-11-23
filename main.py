#Image Slideshow Viewer
#Usage Information
#  - Click Mouse/Touch Screen to show info and pause slideshow
#  - Touch again to hide info and continue slideshow
#  - Escape key will halt execution

import random, os, glob, sys
from kivy.config import Config
from kivy import platform
#print "Platform = " + str(platform())
#platform() will return win, linux, android, macosx, ios, or unknown
if False and platform() == 'win':
    #Use Config.set to enable fullscreen view in Windows
    #Config.set('graphics', 'show_cursor', '0')
    Config.set('graphics', 'fullscreen', '1')
    Config.set('graphics', 'width', '1920')
    Config.set('graphics', 'height', '1080')
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ListProperty
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.base import EventLoop
#from kivy.properties.Property import NumericProperty

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
global bShowInfo
global bShowNext
global bPlaying
global bBindKeyboard
global strFontSize
global iCurrentIndex
global iShownLength
#Device Independent (Default) Settings
sngInterval = 5.002
bBuildCache = True
bReschedule = True # False
bPaused = False
sngWidth = 1920.0
sngHeight = 1080.0
bShowInfo = False
bPlaying = True
bShowNext = False
bBindKeyboard = True
strFontSize = '24dp'
iCurrentIndex = 0
iShownLength = 0
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
    sngInterval = 7.0
    strFontSize = '18dp'
    bBindKeyboard = False
#Galaxy Note 2
if os.path.isdir('/mnt/extSdCard/PhotoAlbums/apod/'):
    strDir = '/mnt/extSdCard/PhotoAlbums/apod/'
    strTemp = '/mnt/extSdCard/PhotoAlbums/apod/Temp.jpg'
    strCache = '/mnt/extSdCard/PhotoAlbums/apod/cache/'
    strData = '/mnt/extSdCard/PhotoAlbums/apod/data/'
    sngInterval = 7.0
    bBindKeyboard = False
    strFontSize = '10dp'
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
        self.shown = []
        self.photos = glob.glob(strDir + "*.jpg")
        global intCount
        #global sngInterval
        intCount = len(self.photos)
        strImage = random.choice(self.photos)
        img = Image(source=strImage, id='MainImage')
        #Turn on allow_stretch to upscale smaller images to fullscreen
        img.allow_stretch = True
        self.add_widget(img)
        cb = CustomBtn(size_hint=(1,1), font_size=strFontSize)
        cb.bind(pressed=self.btn_pressed)
        #cb.text = 'This is a test.'
        cb.id = 'MainButton'
        cb.bind(texture_size=cb.setter('size'))
        cb.bind(size=cb.setter('text_size')) 
        self.add_widget(cb)
        self.next_image()
        if not bReschedule:
            Clock.schedule_interval(self.next_image, sngInterval)
        #if bReschedule:
        #    Clock.schedule_once(self.next_image, sngInterval)

    def btn_pressed(self, instance, pos):    
        print "btn_pressed"    

        img = None #Image() #Using object name enables autocomplete in Visual Studio, but causes errors at runtime
        btn = None #ToggleButton()

        for child in self.children:
            if child.id == 'MainButton':
                btn = child 

        if bShowInfo:
            if False:
                print "Showing Info..."
                Clock.unschedule(self.next_image)
                #bPaused = True
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
                if (not bPlaying) and bShowNext:
                    print "calling next_image"
                    self.next_image()
            else:
                if bPlaying == True:
                    Clock.unschedule(self.next_image)
                    self.next_image()
                else:
                    Clock.unschedule(self.next_image)
                    self.show_current_image()
        else:
            btn.text = ""
           
            if bPlaying:
                #self.next_image()
                Clock.schedule_once(self.next_image, sngInterval)
            else:
                Clock.unschedule(self.next_image)
                self.show_current_image()

    def next_image(self, *largs): # whatever = None):
        print "Showing next image"
        global iCurrentIndex
        global iShownLength

        if (iCurrentIndex == (iShownLength - 1)) or (iShownLength == 0):       
            strRandom = random.choice(self.photos)
            EventLoop.window.title = str(len(self.photos)) + '/' + str(intCount) + ' Loading:' + strRandom    

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
                            imgHeight = int(sngHeight)
                            imgWidth = int(imgWidth * sngChange)
                        if imgWidth > sngWidth:
                            bResized = True
                            sngChange = sngWidth / imgWidth
                            imgWidth = int(sngWidth)
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
                                        print "save cache file problem: " + e.message        
                                        strCached = ""
                                else:
                                    print "save cache file found"        
                        #else:
                        #    im.save(strTemp)
                    if not strCached == "":
                        #img.source = strCached
                        try:
                            self.shown.remove(strCached)
                        except:
                            print "error removing image from cache"
                        self.shown.append(strCached)
                        iShownLength = len(self.shown)
                        iCurrentIndex = iShownLength - 1
                    else:        
                        #img.source = strRandom
                        try:
                            self.shown.append(strRandom)
                        except:
                            print "error removing image from cache"
                        self.shown.append(strRandom)
                        iShownLength = len(self.shown)
                        iCurrentIndex = iShownLength - 1
                        #img.reload()
                except Exception as e:
                    print "Error(" + e.message + ") loading image " + strRandom
            #continue with the logic
        
            self.photos.remove(strRandom)                                       
            if len(self.photos) < 1:
                self.photos = glob.glob(strDir + "*.jpg")
            #global bReschedule
        else:
            iCurrentIndex += 1

        self.show_current_image()

    def show_current_image(self, *largs):
        #global iCurrentIndex        
        print "showing current image"
        img = None #Image()
        btn = None #ToggleButton()
        
        #get Widgets from list of children
        for child in self.children:
            #print child.id
            if child.id == 'MainImage':
                img = child
            if child.id == 'MainButton':
                btn = child 

        if bShowInfo:
            strFileName = os.path.basename(self.shown[iCurrentIndex])
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
                btn.text = strTitle + ': ' + strInfo

        img.source = self.shown[iCurrentIndex]
        if bReschedule and bPlaying:
            Clock.schedule_once(self.next_image, sngInterval)

class CustomBtn(ToggleButton):
    pressed = ListProperty([0, 0])
    background_down='button_down.png'
    background_normal='button_normal.png'
    #background_normal='button_down.png'

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            print "on_touch_down"
            print ('pressed at {pos}'.format(pos=touch.pos))
            print ('Window size: {pos}'.format(pos=Window.size))
            global bShowInfo
            global bPlaying
            global bShowNext
            global iCurrentIndex
      
            bShowNext = False
            intX, intY = touch.pos
            if intY < (Window.height * 0.25):
                print "Clicked Bottom" # toggle info
                if bShowInfo:
                    bShowInfo = False
                    bPlaying = True
                    print "bShowInfo set to False"
                else:
                    bShowInfo = True
                    bPlaying = False
                    print "bShowInfo set to True"
            else:
                print "Clicked Above Bottom"
                #clicking top right corner exits
                if (intY > (Window.height * 0.8)) and (intX > (Window.width * 0.8)):
                    sys.exit()
                else:
                    if (intX < (Window.width * 0.3)):
                        print "Show the previous slide"
                        bPlaying = False
                        if iCurrentIndex > 0:
                            iCurrentIndex -= 1
                    else:
                        #this controls the pause/play/next?
                        if iCurrentIndex < (iShownLength - 1):
                            iCurrentIndex += 1
                        elif iCurrentIndex == (iShownLength - 1):
                            bPlaying = True
                            bShowInfo = False
                        #else:
                        #    if (bShowInfo) and (not bPlaying):
                        #        print "Setting bShowNext to True"
                        #        bShowNext = True

            if bShowInfo:
                print "button state = down"
                self.state = 'down'
            else:
                print "button state = normal"
                self.state = 'normal'

            self.pressed = touch.pos
            #call Super to handle toggling the background_color
            #return super(CustomBtn, self).on_touch_down(touch)
            return False

        return super(CustomBtn, self).on_touch_down(touch)

    def on_pressed(self, instance, pos):
        print ('pressed at {pos}'.format(pos=pos))

class TestApp(App):
    def build(self):
        #these lines may cause keybaord to show in Android, so you may want to comment them out as you can use the back button to exit the App
        if bBindKeyboard:
            keyb = Window.request_keyboard(self.stop, self)
            keyb.bind(on_key_down = self.key_pressed)
        return RootWidget()
    
    def key_pressed(self, keyboard, keycode, text, modifiers):
        #if keycode[1] == 'w':
        #    self.player1.center_y += 10
        #elif keycode[1] == 's':
        #    self.player1.center_y -= 10
        #elif keycode[1] == 'up':
        #    self.player2.center_y += 10
        #elif keycode[1] == 'down':
        #    self.player2.center_y -= 10
        sys.exit()

if __name__ == '__main__':
    TestApp().run()
