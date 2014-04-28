#APOD Slideshow Viewer for RPi
#Usage Information
#  - Click Mouse/Touch Screen to show info and pause slideshow
#  - Touch again to hide info and continue slideshow
#  - Escape key will halt execution

import random, os, glob, sys

global bHooking
bHooking = False
#no longer attempting to use pyxhook for mouse and keyboard on RPi
if False and os.name == 'posix':
    bHooking = True
    print "Found POSIX: bHooking = True"
    import pyxhook as hooklib

global bUseLCD
bUseLCD = True
if bUseLCD:
    from Adafruit_CharLCDPlate import Adafruit_CharLCDPlate

#setup environment for windows visual studio
if os.path.isdir("C:\\"):
    os.environ['GST_PLUGIN_PATH'] = "C:\Kivy-1.7.2-w32\gstreamer\lib\gstreamer-0.10"
    os.environ['GST_REGISTRY'] = "C:\Kivy-1.7.2-w32\gstreamer\registry.bin"
    os.environ['PATH'] = "C:\Kivy-1.7.2-w32;C:\Kivy-1.7.2-w32\Python;C:\Kivy-1.7.2-w32\gstreamer\bin;C:\Kivy-1.7.2-w32\MinGW\bin;%PATH%"
#print "Platform = " + str(platform())
#platform() will return win, linux, android, macosx, ios, or unknown
from kivy.config import Config
from kivy import platform

if False and platform() == 'win':
    #Use Config.set to enable fullscreen view in Windows
    Config.set('graphics', 'show_cursor', '0')
    Config.set('graphics', 'fullscreen', '1')
    Config.set('graphics', 'width', '1920')
    Config.set('graphics', 'height', '1080')
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.togglebutton import ToggleButton
#from kivy.uix.label import Label
from kivy.uix.image import Image
from PIL import Image as PILImage
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.properties import ListProperty
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.base import EventLoop
#from kivy.properties.Property import NumericProperty

global strDir
#strTemp can be used to have one Temp.jpg instead of an image cache directory
global strTemp
global strCache
global strCacheText
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
global intCharsPerLine
global intLastX
global intLastY
global strButtonDown
global bUsePIL
global intLastButton
intLastButton = -100
#Device Independent (Default) Settings
sngInterval = 6.002
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
intLastX = 0
intLastY = 0
strDir = ""
strTemp = ""
strCache = ""
strCacheText = ""
strButtonDown = 'button_down.png'
intCharsPerLine = 100 #rough estimate
bUsePIL = True
#Setting For Various Devices
#Create a set of paths for each device you plan to support
#Windows 7 Notebook
if os.path.isdir("C:\\Users\\David\\Pictures\\apod\\"):
    strDir = "C:\\Users\\David\\Pictures\\apod\\"
    strTemp = "C:\\Users\\David\\Pictures\\Temp.jpg"
    strCache = "C:\\Users\\David\\Pictures\\apod\\cache\\"
    strData = "C:\\Users\\David\\Pictures\\apod\\data\\"
    strFontSize = '24dp'
    intCharsPerLine = 135 # 170 #rough estimate
    sngInterval = 5.03
#Windows 8.1 Notebook
if os.path.isdir("G:\\apod\\"):
    strDir = "G:\\apod\\"
    strTemp = "G:\\Temp.jpg"
    strCache = "G:\\apod\\cache\\"
    strCacheText = "G:\\apod\\cache_text\\"
    strData = "G:\\apod\\data\\"
    strFontSize = '24dp'
    intCharsPerLine = 120 # 170 #rough estimate
    sngInterval = 9.03
    if False:
        #Nexus7 Cache Build 4786
        sngInterval = 0.0003
        sngWidth = 1920.0
        sngHeight = 1104.0
        strCache = "G:\\apod\\cache_Nexus7_2013\\"
    if False:
        #NookHD+ Cache Build 0
        sngInterval = 0.0003
        sngWidth = 1920.0
        sngHeight = 1280.0
        strCache = "G:\\apod\\cache_NookHD+\\"
#NookHD+
if os.path.isdir('/mnt/ext_sdcard/apod/'):
    strDir = '/mnt/ext_sdcard/apod/'
    strTemp = '/mnt/ext_sdcard/Temp.jpg'
    strCache = '/mnt/ext_sdcard/apod/cache/'
    strData = '/mnt/ext_sdcard/apod/data/'
    sngInterval = 9.0
    strFontSize = '18dp'
    bBindKeyboard = False
#Nexus7
if os.path.isdir('/sdcard/Pictures/apod/'):
    strDir = '/sdcard/Pictures/apod/cache/'
    strTemp = '/sdcard/Pictures/Temp.jpg'
    #strCache = '/sdcard/Pictures/apod/cache/'
    bUsePIL = False
    strData = '/sdcard/Pictures/apod/data/'
    sngInterval = 9.0
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
    strCacheText = '/home/pi/pishare/cache_text_new/'
    strData = '/home/pi/pishare/data/'
    sngInterval = 10.002

    if bUseLCD:
        # Initialize the LCD plate.  Should auto-detect correct I2C bus.  If not,
        # pass '0' for early 256 MB Model B boards or '1' for all later versions
        lcd = Adafruit_CharLCDPlate()

        # Clear display and show greeting, pause 1 sec
        lcd.clear()
        #lcd.message("Adafruit RGB LCD\nPlate w/Keypad!")
        lcd.message("APOD Viewer on\nRPi, Kivy & Python!")
        lcd.backlight(lcd.OFF)


#set strCache to blank string to skip using cached images
#strCache = ""

class RootWidget(FloatLayout):
    def __init__(self, **kwargs):
        super(RootWidget, self).__init__(**kwargs)

        if bHooking:
            print "bHooking is true"
            self.hm = hooklib.HookManager()
            print "HookManager set to self.hm"
            self.hm.HookKeyboard()
            self.hm.KeyDown = self.OnKeyDownEvent
            self.hm.start()

        self.photos = []
        self.shown = []
        self.photos = glob.glob(strDir + "*.jpg")
        global intCount
        #global sngInterval
        intCount = len(self.photos)
        strImage = random.choice(self.photos)
        img = Image(source=strImage, id='MainImage')
        img.nocache = True
        #img.canvas.color = (1, 1, 1)
        #Turn on allow_stretch to upscale smaller images to fullscreen
        img.allow_stretch = True
        
        self.add_widget(img)

        if True:
            cb = CustomBtn(size_hint=(1,1), font_size=strFontSize)
            cb.bind(pressed=self.btn_pressed)
            #cb.text = 'This is a test.'
            cb.id = 'MainButton'
            cb.bind(texture_size=cb.setter('size'))
            cb.bind(size=cb.setter('text_size')) 
            self.add_widget(cb)
        
        self.show_next_image()
        if not bReschedule:
            Clock.unschedule(self.show_next_image)
            Clock.schedule_interval(self.show_next_image, sngInterval)
        if bUseLCD:
            Clock.schedule_interval(self.CheckLCD, 0.1)
        #if bReschedule:
        #    Clock.schedule_once(self.show_next_image, sngInterval)

    def CheckLCD(self, *largs):
        global bShowInfo
        global bPlaying
        global intLastButton
        #print "Checking LCD"
        if lcd.buttonPressed(lcd.LEFT):
            print "LCD.LEFT"
            if intLastButton == lcd.LEFT:
                lcd.clear()
                lcd.message("Left Again\nNot Processing")
            else:
                #sys.exit()
                print "Show Previous"
                lcd.clear()
                lcd.message("Left Recognized\nShow Previous")
                self.show_previous_image()
            intLastButton = lcd.LEFT
        elif lcd.buttonPressed(lcd.RIGHT):
            print "LCD.RIGHT"
            if intLastButton == lcd.RIGHT:
                lcd.clear()
                lcd.message("Right Again\nNot Processing")
            else:
                #sys.exit()
                lcd.clear()
                lcd.message("Right Recognized\nShow Next")
                print "Show Next"
                #self.next_image()
                self.show_next_image()    
            intLastButton = lcd.RIGHT
        elif lcd.buttonPressed(lcd.UP):
            print "LCD.UP"
            if intLastButton == lcd.UP:
                lcd.clear()
                lcd.message("Up Again\nNot Processing")
            else:
                lcd.clear()
                #sys.exit()
                #self.next_image()
                if bPlaying == False:
                    lcd.clear()
                    lcd.message("Up Recognized\nResuming...")
                    bPlaying = True
                    self.show_next_image()

            intLastButton = lcd.UP
        elif lcd.buttonPressed(lcd.DOWN):
            print "LCD.DOWN"
            if intLastButton == lcd.DOWN:
                lcd.clear()
                lcd.message("Down Again\nNot Processing")
            else:
                lcd.clear()
                #sys.exit()
                lcd.message("Down Recognized\nToggle Info")
                print "Down"
                print "Toggle Info"
                bShowInfo = not bShowInfo
                if bShowInfo == True:
                    print "bShowInfo = True"
                    bPlaying = False
                else:
                    print "bShowInfo = False"
                    bPlaying = True
                self.show_current_image()
            intLastButton = lcd.DOWN
        elif lcd.buttonPressed(lcd.SELECT):
            lcd.clear()
            lcd.message("Raspberry Pi\nAPOD Enabled")
            lcd.backlight(lcd.OFF)
            self.hm.cancel()
            print "Exiting Script"
            sys.exit()
            print "Exit called"
            return False
        else:
            #print "LCD no button"
            #-100 is nothing
            intLastButton = -100

        
    def OnKeyDownEvent(self, event):
        #should only get called if bHooking
        strEvent = str(event)
        print "OnKeyDownEvent called with " + strEvent
        if "Key Pressed: x" in strEvent:
            self.hm.cancel()
            print "Exiting Script"
            sys.exit()
            print "Exit called"
            return False
        elif "Key Pressed: Right" in strEvent:
            print "Show Next"
            self.show_next_image()
        elif "Key Pressed: Left" in strEvent:
            print "Show Previous"
            self.show_previous_image()
        elif "Key Pressed: Down" in strEvent:
            print "Toggle Info"
            global bShowInfo
            global bPlaying
            bShowInfo = not bShowInfo
            if bShowInfo == True:
                print "bShowInfo = True"
                bPlaying = False
            else:
                print "bShowInfo = False"
                bPlaying = True
            self.show_current_image()
        elif "Key Pressed: Up" in strEvent:
            print "Up Key Pressed"
            if bPlaying == False:
                bPlaying = True
                self.show_next_image
        else:
            print "keystroke not programmed"
            
        return True

    def btn_pressed(self, instance, pos):    
        print "btn_pressed"    

        img = None #Image() #Using object name enables autocomplete in Visual Studio, but causes errors at runtime
        btn = None #ToggleButton()

        for child in self.children:
            if child.id == 'MainButton':
                btn = child 

        if bShowInfo:
            if bPlaying == True:
                Clock.unschedule(self.show_next_image)
                self.show_next_image()
            else:
                Clock.unschedule(self.show_next_image)
                self.show_current_image()
        else:
            btn.text = ""           

            if bPlaying:
                #self.show_next_image()
                Clock.unschedule(self.show_next_image)
                Clock.schedule_once(self.show_next_image, sngInterval)
            else:
                Clock.unschedule(self.show_next_image)
                self.show_current_image()

    def show_previous_image(self, *largs): # whatever = None):
        print "show previous image"
        global bPlaying
        global iCurrentIndex
        bPlaying = False
        if iCurrentIndex > 0:
            iCurrentIndex -= 1
        self.show_current_image()

    def show_next_image(self, *largs): # whatever = None):
        print "Showing next image"
        global iCurrentIndex
        global iShownLength
        global bPlaying
        #bPlaying = False

        if (iCurrentIndex == (iShownLength - 1)) or (iShownLength == 0):
            bPlaying = True
            strRandom = random.choice(self.photos)
            EventLoop.window.title = str(len(self.photos)) + '/' + str(intCount) + ' Loading:' + strRandom    

            try:
                if bUsePIL:
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
                        #from PIL import Image
                        im = PILImage.open(strRandom)
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
                            im=im.resize(szNew, PILImage.ANTIALIAS)
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
        intLineEstimate = 1

        #get Widgets from list of children
        for child in self.children:
            #print child.id
            if child.id == 'MainImage':
                img = child
            if child.id == 'MainButton':
                btn = child 

        btn.state = 'normal'
        btn.text = ''
        if bShowInfo and strCacheText == "":
            #do not autorun while displaying info
            global bPlaying
            bPlaying = False
            strFileName = os.path.basename(self.shown[iCurrentIndex])
            strTitle = strData + strFileName.replace('.jpg', '_Title.txt')
            #load the btnText?
            if (os.path.isdir(strData)) and (os.path.isfile(strTitle)):
                strText = ""
                if os.path.isfile(strData + strFileName.replace('.jpg', '_Title.txt')):
                    f = open(strData + strFileName.replace('.jpg', '_Title.txt'))
                    strTitle = f.read()
                    strText = strTitle
                    f.close
                else:
                    strText = strTitle
                if os.path.isfile(strData + strFileName.replace('.jpg', '_Info.txt')):
                    f = open(strData + strFileName.replace('.jpg', '_Info.txt'))
                    strInfo = f.read()
                    strText = strText + ": " + strInfo
                    f.close
                #This is where we choose what to load into the button text when loading images
                btn.text = strText # strTitle + ': ' + strInfo # + ' [' + str(len(strTitle + strInfo) / intCharsPerLine) + '][' + strFileName + ']'
                intLineEstimate = len(strText) / intCharsPerLine

                #create the proper button background if it does not exist
                strTempButtonDown = strButtonDown.replace(".png", "_" + str(intLineEstimate) + ".png")
                if not os.path.isfile(strTempButtonDown):
                    print "making button_down background"
                    intRectHeight = intLineEstimate * 28 # 250 # calced by length of text
                    intGradHeight = 40
                    sngGradVal = 0
                    intGradMaxOpacity = 190
                    intX = 1920
                    intY = 1080

                    bgimg = PILImage.new('RGBA',(intX, intY), 'black')
                    gradient = PILImage.new('L', (1,intY))

                    for y in range(intY):
                        if (y < (intY - (intRectHeight + intGradHeight))):
                            gradient.putpixel((0,y),0)
                        elif (y < (intY - intRectHeight)):
                            gradient.putpixel((0,y),int(sngGradVal))
                            sngGradVal = sngGradVal + ((intGradMaxOpacity * 1.0) / intGradHeight)
                        else:
                            gradient.putpixel((0,y),intGradMaxOpacity)

                    # resize the gradient to the size of im...
                    alpha = gradient.resize(bgimg.size)
                    # put alpha in the alpha band of im...
                    bgimg.putalpha(alpha)
                    bgimg.save(strTempButtonDown)

                btn.background_down=strTempButtonDown
                btn.state = 'down'
            else:
                btn.text = "Info not found - playback paused: " + strFileName
            #load the image
            img.source = self.shown[iCurrentIndex]
        elif bShowInfo and strCacheText <> "":
            print "showing cache_text image"
            strFileName = os.path.basename(self.shown[iCurrentIndex])
            #show the cache_text image
            img.source = strCacheText + strFileName
        else:
            #load the image
            img.source = self.shown[iCurrentIndex]

        if bReschedule and bPlaying:
            #unschedule any currently scheduled references
            Clock.unschedule(self.show_next_image)
            Clock.schedule_once(self.show_next_image, sngInterval)
        elif not bPlaying:
            Clock.unschedule(self.show_next_image)

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
                if True:
                    print "Clicked Bottom" # toggle info
                    bShowInfo = not bShowInfo
                    if bShowInfo == True:
                        print "bShowInfo = True"
                        bPlaying = False
                    else:
                        print "bShowInfo = False"
                        bPlaying = True
                    self.parent.show_current_image()
                else:
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
                    sys.exit("exiting on user click")
                else:
                    if (intX < (Window.width * 0.3)):
                        if True:
                            self.parent.show_previous_image()
                        else:
                            print "Show the previous slide"
                            bPlaying = False
                            if iCurrentIndex > 0:
                                iCurrentIndex -= 1
                    else:
                        if True:
                            self.parent.show_next_image()
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

            global intLastX
            global intLastY
            intX, intY = touch.pos
            if (intX == intLastX) and (intY == intLastY):
                if intX < Window.width:
                    intX = intX + 1
                else:
                    intX = intX - 1
        
            intLastX = intX
            intLastY = intY
            
            self.pressed = (intX, intY)
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

    def show_previous(self, *largs):
        #print "Show Previous Sub"
        print "Show the previous slide"

    def show_next(self, *largs):
        print "Show Next Sub"
    
    def key_pressed(self, keyboard, keycode, text, modifiers):
        #if keycode[1] == 'w':
        #    self.player1.center_y += 10
        #elif keycode[1] == 's':
        #    self.player1.center_y -= 10
        #elif keycode[1] == 'up':
        #    self.player2.center_y += 10
        #elif keycode[1] == 'down':
        #    self.player2.center_y -= 10
        for child in self.root.children:
            print "Self.Root.Child: " + child.id
        
        global bPlaying
        if keycode[0] == 315:
            print "not exiting on open lid keycode"
        elif keycode[0] == 120: # x
            sys.exit("exiting on X key press")
        elif keycode[0] == 276: # left arrow
            print "left arrow"
            #self.show_previous()
            self.root.show_previous_image()            
        elif keycode[0] == 275: # right arrow
            print "right arrow"
            #self.show_next()
            self.root.show_next_image()
        elif keycode[0] == 273:
            print "up arrow"            
            if bPlaying == False:
                bPlaying = True
                self.root.show_next_image()
        elif keycode[0] == 32 or keycode[0] == 274: #spacebar
            print "spacebar or down arrow"
            global bShowInfo
            #global bPlaying
            bShowInfo = not bShowInfo
            if bShowInfo == True:
                print "bShowInfo = True"
                bPlaying = False
            else:
                print "bShowInfo = False"
                bPlaying = True
            self.root.show_current_image()
        else:
            if True:
                print "key press[" + str(keycode[0]) + "," + keycode[1] + "]"
            else:
                sys.exit("exiting on key press[" + str(keycode[0]) + "]")

if __name__ == '__main__':
    TestApp().run()
