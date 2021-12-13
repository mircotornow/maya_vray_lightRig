import maya.mel as mel
import maya.cmds as cmds
import os
from functools import partial

class MT_Window(object):
    
    #constructor    
    def __init__(self):
        
        
            
        self.window = "MT_LightRigWindow"
        self.title = "MT Light Rig"
        self.size = (400, 400)
        bgColor = [0.1, 0.1, 0.1]
        enColor = [1, 0.6, 0]
        self.cameraBtns= [] #buttons
        self.cameras = [] #cameras
        self.cameraGrps = []
        self.cameraLayouts = []
        myfilepath = os.path.expanduser('~/maya/' + cmds.about(version = True) + '/scripts/lightRigTool/')
        
        self.sunHDRI = myfilepath + '/HDRIs/sun.exr'
        self.cloudsHDRI = myfilepath + '/HDRIs/clouds.exr'
        self.nightHDRI = myfilepath + '/HDRIs/night.exr'
        self.studioHDRI = myfilepath + '/HDRIs/studio.exr'
        self.dome = ''
        self.domeRotate = 0
        self.fileTex = ''
        self.vrayPlaceEnvTex = ''
        self.ttRotateSlider = ''
        '''
        with open(myfilepath + 'Settings.txt', 'w') as file:
            file.writelines('% s\n' % paths for paths in ['sun:' + self.sunHDRI, 'clouds:' + self.cloudsHDRI, 'night:' + self.nightHDRI, 'studio:' + self.studioHDRI])
            fileclose()
        '''
        
        
        #menu functions       
        def sSun(*args):
            temp = cmds.fileDialog2(fileMode = 1, cap = 'Select SUN HDRI' ,startingDirectory = self.sunHDRI)
            self.sunHDRI = temp[0] if temp != None else self.sunHDRI
            
        def sClouds(*args):
            temp = cmds.fileDialog2(fileMode = 1, cap = 'Select CLOUDS HDRI' ,startingDirectory = self.cloudsHDRI)
            self.cloudsHDRI = temp[0] if temp != None else self.cloudsHDRI
        
        def sNight(*args):
            temp = cmds.fileDialog2(fileMode = 1, cap = 'Select NIGHT HDRI' ,startingDirectory = self.nightHDRI)
            self.nightHDRI = temp[0] if temp != None else self.nightHDRI
            
        def sStudio(*args):
            temp = cmds.fileDialog2(fileMode = 1, cap = 'Select STUDIO HDRI' ,startingDirectory = self.studioHDRI)
            self.studioHDRI = temp[0] if temp != None else self.studioHDRI
            
        def sAllHdris(*args):                
            sSun()
            sClouds()
            sNight()
            sStudio()    
        
        #button functions        
        def lightsOff(enabled, light, *args):
            cmds.button(sun_btn, e = True, en = enabled, backgroundColor = enColor if light == "sun" else bgColor)
            cmds.button(clouds_btn, e = True, en = enabled, backgroundColor = enColor if light == "clouds" else bgColor)
            cmds.button(night_btn, e = True, en = enabled, backgroundColor = enColor if light == "night" else bgColor)
            cmds.button(studio_btn, e = True, en = enabled, backgroundColor = enColor if light == "studio" else bgColor)
            
        def buttonsOff(enabled, *args):
            for thisCB in [hdri_cb
                            ###################################, backdrop_c
                            ]:
                cmds.checkBox(thisCB, e = True, en = enabled, value = False)
                
            ##################################cmds.button(plusCam_btn, e = True, en = enabled, backgroundColor = enColor if enabled == True else bgColor)
            cmds.button(ttCam_btn, e = True, en = enabled, backgroundColor = enColor if enabled == True else bgColor)
            
            for thisBtn in self.cameraBtns:
                cmds.button(thisBtn, e = True, en = enabled)    
        
        def lightRigOnOff(*args):
            #turn ON
            if cmds.button(buttonOnOff, q = True, label = True) == "OFF": 
                cmds.button(buttonOnOff, e = True, label = "ON", backgroundColor=enColor)
                lightsOff(True,"")
                buttonsOff(True) 
                createDomeLight()
                cmds.button(close_btn, e = True, en = False)
                addCam()
                cmds.intFieldGrp(myTextField, e = True, en = True)
                cmds.intFieldGrp(ttLengthField, e = True, en = True)
                self.ttRotateSlider = cmds.attrFieldSliderGrp('ttSlider', label = 'ROTATE HDRI',ad3 = 3, cw = [2,50], at = '{}.rotateY'.format(self.dome), min = 0, max = 360, pre = 0, parent = cameraColumn)
                
            #turn OFF
            else:
                if cmds.confirmDialog(title = "WARNING: Your about to turn off MT lightRig", button = ["Stop","Yes, Delete"], 
                    defaultButton = "Stop", cancelButton = "Yes, Delete", parent = self.window,
                    message = "The Lighting Setup will be removed from the Scene and your settings will be deleted!") == "Yes, Delete":
                        cmds.button(close_btn, e = True, en = True)
                        cmds.button(buttonOnOff, e = True, label = "OFF", backgroundColor=bgColor)  
                        lightsOff(False, "")
                        buttonsOff(False)
                        for thisCam in self.cameraBtns:
                            cmds.deleteUI(thisCam)
                        self.cameraBtns = []
                        for cam in self.cameraGrps:
                            cmds.delete(cam)
                        self.cameras = []
                        self.cameraGrps = []
                        for cam in self.cameraLayouts:
                            cmds.deleteUI(cam, layout = True)
                        self.cameraLayouts = []
                        cmds.delete(self.vrayPlaceEnvTex)
                        cmds.delete(self.fileTex)
                        cmds.deleteUI(self.ttRotateSlider)
                        cmds.intFieldGrp(myTextField, e = True, en = False)
                        cmds.intFieldGrp(ttLengthField, e = True, en = False)
                        cmds.lookThru('persp')
                        
                   

        def createDomeLight():            
            #create vray rect light
            domeLight = cmds.shadingNode('VRayLightDomeShape' , asLight=True)
         
            #rename light
            self.dome = cmds.rename(domeLight , 'MT_LightDome')
         
            #Set default attributes
            cmds.setAttr('%s.invisible' %(self.dome), 1)
            cmds.setAttr('%s.domeSpherical' %(self.dome), 1)
            cmds.setAttr('%s.locatorScale' %(self.dome), 3)
            
            #create file node and environment texture
            self.fileTex = cmds.shadingNode('file', name = self.dome + '_file', asTexture = True)
            self.vrayPlaceEnvTex = cmds.shadingNode('VRayPlaceEnvTex', name = 'vrayPlaceEnvTex', asUtility = True)
 
            #connect the selected image to the file node. Set filter type.
            cmds.setAttr('%s.filterType' %(self.fileTex), 0)
 
            #set environment texture to sphereical
            cmds.setAttr('%s.mappingType' %(self.vrayPlaceEnvTex), 2)
            #set environment texture to use transform
            cmds.setAttr('%s.useTransform' %(self.vrayPlaceEnvTex), 1)
 
            # connect VRayPlaceEnvTex node
            cmds.connectAttr(self.vrayPlaceEnvTex + '.outUV', self.fileTex + '.uvCoord')
            cmds.connectAttr(self.dome + '.worldMatrix[0]', self.vrayPlaceEnvTex + '.transform')
 
            #Turn on rect tex
            cmds.setAttr('%s.useDomeTex' %(self.dome), 1)
 
            #Get Light Shape Node
            domeLightShape = cmds.listRelatives(self.dome, shapes = True)
 
            #connect file to light
            cmds.connectAttr(self.fileTex + '.outColor', domeLightShape[0] + '.domeTex')
            
            myGroup = cmds.group(self.dome)
            self.cameraGrps.append(cmds.rename(myGroup, 'MT_Domelight_grp'))
            
            
        def domeLightTexture(selectedLight, *args):
            cmds.setAttr('%s.fileTextureName' %(self.fileTex), selectedLight, type = 'string')
           
    
        def sun(*args):
            if cmds.button(sun_btn, q = True, backgroundColor = True)[1] <= 0.2:
                lightsOff(True, "sun")
                domeLightTexture(self.sunHDRI)
                
        def clouds(*args):
            if cmds.button(clouds_btn, q = True, backgroundColor = True)[1] <= 0.2:
                lightsOff(True, "clouds")
                domeLightTexture(self.cloudsHDRI)

        
        def night(*args):
            if cmds.button(night_btn, q = True, backgroundColor = True)[1] <= 0.2:
                lightsOff(True, "night")
                domeLightTexture(self.nightHDRI)

       
        def studio(*args):
            if cmds.button(studio_btn, q = True, backgroundColor = True)[1] <= 0.2:
                lightsOff(True, "studio")
                domeLightTexture(self.studioHDRI)
                
        def hdriOn(*args):
            cmds.setAttr('%s.invisible' %(self.dome), 0)  
                
        def hdriOff(*args):
            cmds.setAttr('%s.invisible' %(self.dome), 1) 
        
        def selCam(*args):
            cmds.lookThru(self.cameras[-1])
                
        def delCam(*args):
            print "delete"
   
        
        def addCam(*args):
            if len(self.cameras) == 0:
                name = 'MT_TT_CAM'
                myCamera = cmds.camera(focalLength = 75)
                myGroup = cmds.group([myCamera[0],self.cameraGrps[0]])
                cmds.move(0, 0, 100, myCamera)
                cmds.camera(myCamera[0], e = True, centerOfInterest = 100)
                cmds.setAttr('%s.inheritsTransform' %(myCamera[0]), 0)
                cmds.setAttr('%s.inheritsTransform' %(myCamera[0]), 1)
                self.cameraGrps.append(cmds.rename(myGroup, name + '_grp'))
                setRotate()
            else:
                name = 'CAM' + str(len(self.cameraBtns)/2 + 1)
                cmds.select(clear = True)
                self.cameraLayouts.append(cmds.rowLayout(numberOfColumns = 2, adjustableColumn = 1, parent = cameraColumn))
                self.cameraBtns.append(cmds.button(name, backgroundColor = bgColor, c = selCam, en = True))
                self.cameraBtns.append(cmds.button('delete' + str(len(self.cameraBtns)), label = "-", width = 25, backgroundColor = enColor, c = delCam, po = True))
                myCamera = cmds.camera()
                myGroup = cmds.group(myCamera[0])
                self.cameraGrps.append(cmds.rename(myGroup, myCamera[0] + '_grp'))
            self.cameras.append(cmds.rename(myCamera[0], name))

            cmds.lookThru(self.cameras[-1])
            
        def setRotate(*args):
            cmds.delete(self.cameraGrps[1], expressions = True)
            frames = cmds.intFieldGrp(ttLengthField, q = True, v1 = True)
            cmds.playbackOptions(aet = frames * 2, min = 1, max = cmds.intFieldGrp(ttLengthField, q = True, v1 = True) * 2)
            time = 360.0 / (frames - 1)
            
            cmds.expression( s = self.cameraGrps[1] + '.rotateY = ((frame - 1) * {t} >= 360) ? 360 : (frame - 1) * {t}'.format(t = time), o = self.cameraGrps[1])
            cmds.expression( s = self.cameraGrps[0] + '.rotateY = (((frame - {v} - 1) * {t} <= 360) && (frame >= {v})) ? (frame - {v} - 1) * {t} : 0'.format(v = frames, t = time), o = self.cameraGrps[0])
            
            
        def changeFocalLength(*args):
            cmds.camera(self.cameras[0], e = True, focalLength = cmds.intFieldGrp(myTextField, q = True, v1 = True))            

            
        def closeWindow(*args):
            cmds.window(self.window, e = True, ret = False)
            cmds.deleteUI(self.window, window=True)
        
        #cmds.deleteUI(self.window, window=True)
        # close old window if open
        if cmds.window(self.window, exists = True):
            cmds.showWindow()            #cmds.deleteUI(self.window, window=True)
        #create new window
        else: 
            self.window = cmds.window(self.window, title=self.title, widthHeight=self.size, ret = True)
        
            '''
            *
            * Menu
            *
            '''
            menuBar = cmds.menuBarLayout()
            #presets
            ####################################presetMenu = cmds.menu("Presets")
            ####################################saveOption = cmds.menuItem("savePreset")
            ####################################loadOption = cmds.menuItem("loadPreset", subMenu = True)
            ####################################defaultOption = cmds.menuItem("setDefaultPreset", parent = "Presets", subMenu = True)
            
            #settings
            settingsMenu = cmds.menu("Settings")
            hdris = cmds.menuItem("set HDRIs", subMenu = True)
            setAll = cmds.menuItem("set All", c = sAllHdris)
            divider = cmds.menuItem(d = True)
            setSun = cmds.menuItem("set Sun", c = sSun)
            setClouds = cmds.menuItem("set Clouds", c = sClouds)
            setNight = cmds.menuItem("set Night", c = sNight)
            setStudio = cmds.menuItem("set Studio", c = sStudio)
            
            
           
            
            '''
            *
            * UI
            *
            '''
            #OnoffButton
            cmds.columnLayout(adjustableColumn = True, rowSpacing = 10)
            buttonOnOff = cmds.button("OnOff", label = "OFF", height = 30, command = lightRigOnOff, backgroundColor=bgColor)     
            
            
            cmds.separator(style = "none")
            #different Lighting Setups Buttons
            margin1 = 5
            form = cmds.formLayout(numberOfDivisions=100)
            sun_btn = cmds.button("SUN", backgroundColor=bgColor, c = sun, en = False)
            clouds_btn = cmds.button("CLOUDS", backgroundColor=bgColor, c = clouds, en = False)
            cmds.formLayout(form, edit=True, 
                    attachForm=[(sun_btn, "left", 0),(clouds_btn, "right", 0)], 
                    attachPosition=[(sun_btn, "right", margin1, 50),(clouds_btn, "left", margin1, 50)])
            cmds.setParent("..")
            form = cmds.formLayout(numberOfDivisions=100)
            night_btn = cmds.button("NIGHT", backgroundColor=bgColor, c = night, en = False)
            studio_btn = cmds.button("STUDIO", backgroundColor=bgColor, c = studio, en = False)
            cmds.formLayout(form, edit=True, 
                    attachForm=[(night_btn, "left", 0),(studio_btn, "right", 0)], 
                    attachPosition=[(night_btn, "right", margin1, 50),(studio_btn, "left", margin1, 50)])
            
            cmds.setParent("..")
            ###############################backdrop_cb = cmds.checkBox("BACKDROP", en = False)              
            hdri_cb = cmds.checkBox("HDRI VISIBLE", en = False, onCommand = hdriOn, offCommand = hdriOff)
            
            
            
            cmds.separator(style = "none")
            cameraColumn = cmds.columnLayout(adjustableColumn = True, rowSpacing = 10)
            
            #Camera Setting
            cmds.rowLayout(numberOfColumns = 2, adjustableColumn = 1, parent = cameraColumn)
            ttCam_btn = cmds.button("TT CAM", backgroundColor = bgColor, c = selCam, en = False)
            ##################################plusCam_btn = cmds.button("Plus", label = "+", width = 25, backgroundColor = bgColor, c = addCam, en = False)
            cmds.setParent("..")
            myTextField = cmds.intFieldGrp('FocalLengthTTCAm', columnWidth = [2,25], ad2 = 1, v1 = 75, label = "FOCAL LENGTH", cc = changeFocalLength, en = False)
            ttLengthField = cmds.intFieldGrp('ttLength', columnWidth = [2,25], ad2 = 1, v1 = 50, label = "TURNTABLE LENGTH", cc = setRotate, en = False)
            cmds.setParent("..")
            
            close_btn = cmds.button("Close", backgroundColor = bgColor, c = closeWindow, en = True)
            
            
            #display new window
            cmds.showWindow()
        

if cmds.menu("MT_Tools", exists = True):
    cmds.deleteUI("MT_Tools", menu = True)
myfilepath = os.path.expanduser('~/maya/' + cmds.about(version = True) + '/scripts/lightRigTool/')
cmds.menu("MT_Tools", parent = "MayaWindow", tearOff = True)
cmds.menuItem("Light Rig", c = 'MT_Window()', image = myfilepath + '/icons/globeicon.png')