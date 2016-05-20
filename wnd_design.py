import threading
import subprocess
import wx
import os
import re
import time

class updateScreenThread(threading.Thread):
    def __init__(self, window):
        threading.Thread.__init__(self)
        self.window = window
        self.timeToQuit = threading.Event()
        self.timeToQuit.clear()
        self.cmd1 = "adb shell /system/bin/screencap -p /sdcard/sstemp.png"
        self.cmd2 = "adb pull /sdcard/sstemp.png F://"
        image2 = wx.Image("F://sstemp.png", wx.BITMAP_TYPE_PNG, index=-1)
        self.w = image2.GetWidth()/4
        self.h = image2.GetHeight()/4
    def stop(self):
        self.timeToQuit.set()
    def run(self):
        while True:
            os.system(self.cmd1)
            os.system(self.cmd2)
            image2 = wx.Image("F://sstemp.png", wx.BITMAP_TYPE_PNG, index=-1)
            image = image2.Scale(self.w,self.h)
            self.bmp = wx.StaticBitmap(self.window.panel, -1, wx.BitmapFromImage(image), pos=(10, 80), size=(self.w,self.h+10))
            if self.timeToQuit.isSet():
                break
            
class showLogThread(threading.Thread):
    def __init__(self, window, cmd):
        threading.Thread.__init__(self)
        self.window = window
        self.cmd = cmd
        self.timeToQuit = threading.Event()
        self.timeToQuit.clear()
    def stop(self):
        self.flogcat.terminate()
        self.timeToQuit.set()
    def run(self):
        self.window.logMessageText.Clear()
        self.flogcat = subprocess.Popen(self.cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=0x08)
        while True:
            output = self.flogcat.stdout.readline()
            if self.window.packageName!="":
                if re.search(self.window.packageName,output):
                    self.window.logMessageText.AppendText(output)
            else:
                self.window.logMessageText.AppendText(output)
                print output
            if self.timeToQuit.isSet():
                break
    
class checkDeviceThread(threading.Thread):
    def __init__(self, window):
        threading.Thread.__init__(self)
        self.window = window
        self.timeToQuit = threading.Event()
        self.timeToQuit.clear()
    def stop(self):
        self.timeToQuit.set()
    def run(self):
        while 1:
            checkdevicecmd = "adb devices"
            deviceLine = os.popen(checkdevicecmd).readlines()
            if len(deviceLine)==2:
                self.window.isconn = False
                self.timeToQuit.wait(0.1)
                wx.CallAfter(self.window.LogMessage)
            else:
                self.window.isconn = True
                self.timeToQuit.wait(0.1)
                wx.CallAfter(self.window.LogMessage)
            if self.timeToQuit.isSet():
                break
         
class TestTool(object):
    def __init__(self):
        self.wndSize = wx.Size(650,600)
        thread = checkDeviceThread(self)
        thread.setDaemon(True)      #terminate child thread when main thread ends.
        thread.start()              #check devices until die
        
        self.isCatting = False
        self.isconn = False
        self.listenDevice = True
        self.packageName =""
        self.isUpdateScreen = False

    def show(self):
        self.frame = wx.Frame(None,title="testTool", size=self.wndSize)  
        panel = wx.Panel(self.frame, 1)
        self.panel = panel
        
        #-------------- button -----------------
        self.logClearBtn = wx.Button(panel, -1, "logcat clear", pos = (320, 10))
        self.logClearBtn.SetDefault()
        self.logCatAllBtn = wx.Button(panel, -1, "logcat all", pos = (420, 10))
        self.logCatSelectBtn = wx.Button(panel, -1, "logcat select", pos = (520, 10))
        self.listenScreenBtn = wx.Button(panel, -1, "show screen\nReal-tiem", pos = (220,10), size=(80,60))
        
        self.logClearBtn.Disable()
        self.logCatAllBtn.Disable()
        self.logCatSelectBtn.Disable()
        
        #-------------- text view ---------------
        self.deviceInfoText = wx.TextCtrl(panel, -1, pos=(10,10),size=(200,70),style=wx.TE_MULTILINE|wx.TE_NO_VSCROLL)
        self.deviceInfoText.SetEditable(False)
        self.logMessageText = wx.TextCtrl(panel, -1, pos = (320, 50), size=(300,500),style=wx.TE_MULTILINE|wx.TE_LINEWRAP)
        
        #-------------- bind --------------------
        self.logClearBtn.Bind(wx.EVT_BUTTON, self.logClear)
        self.logCatAllBtn.Bind(wx.EVT_BUTTON, self.logCatAll)
        self.logCatSelectBtn.Bind(wx.EVT_BUTTON, self.logCatSelect)
        self.listenScreenBtn.Bind(wx.EVT_BUTTON, self.listenScreen)
        
        self.frame.Show()
        
    def listenScreen(self,evt):
        if self.isUpdateScreen ==False:
            self.listenScreenBtn.SetLabel("Stop Flush")
            self.isUpdateScreen = True
            self.fupdateScreen = updateScreenThread(self)
            self.fupdateScreen.setDaemon(True)
            self.fupdateScreen.start()
        else:
            self.listenScreenBtn.SetLabel("show screen\nReal-tiem")
            self.isUpdateScreen = False
            self.fupdateScreen.stop()
    
    def LogMessage(self):
        if self.isconn == True and self.listenDevice == True:
            self.listenDevice = False
            self.deviceInfoText.SetValue("Connected!\n")
            self.logClearBtn.Enable()
            self.logCatAllBtn.Enable()
            self.logCatSelectBtn.Enable()
            getdeviceinfocmd = 'adb shell "cat /system/build.prop | grep \"product\""'
            deviceinfo = os.popen(getdeviceinfocmd).read()
            device_brand = re.findall('ro.product.brand=(.*)', deviceinfo)
            device_model = re.findall('ro.product.model=(.*)', deviceinfo)
            self.deviceInfoText.AppendText("device brand:"+device_brand[0]+"\ndevice model:"+device_model[0])
        elif self.isconn == False and self.listenDevice == False:
            self.listenDevice = True
            self.deviceInfoText.SetValue("Disconnected!")
            
    def logClear(self,even):
        dlg = wx.MessageDialog(None, 'Confirm clear old-log?',
                          'Warning', wx.YES_NO | wx.ICON_QUESTION)
        result = dlg.ShowModal()
        if result == wx.ID_YES:
            cmd = "adb logcat -c"
            os.system(cmd)
            self.logMessageText.SetValue("Clear log successfully!")
        dlg.Destroy()
            
    def logCatAll(self,even):
        if self.isCatting == False:
            self.isCatting = True
            self.logCatAllBtn.SetLabel("Stop logcat")
            self.logClearBtn.Disable()
            self.logCatSelectBtn.Disable()
            cmd = 'adb logcat -v time'
            self.flogcat = showLogThread(self, cmd)
            self.flogcat.setDaemon(True)
            self.flogcat.start()
        else:
            self.isCatting = False
            self.logCatAllBtn.SetLabel("logcat all")
            self.logClearBtn.Enable()
            self.logCatSelectBtn.Enable()
            self.flogcat.stop()
            
    def logCatSelect(self,even):
        if self.isCatting == False:
            self.logMessageText.Clear()
            getpackagename = "adb shell \"dumpsys window windows | grep -E 'mFocusedApp'\""
            result = os.popen(getpackagename).readlines()
            cur_pkg = re.findall('com.*/', result[0])
            cur_pkg[0] = cur_pkg[0].strip('/')
            dlg = wx.TextEntryDialog(None, "Entry the pakage name(or key words) to cat log: ",
                    'pakageName', cur_pkg[0])
            if dlg.ShowModal() == wx.ID_OK:
                self.packageName = dlg.GetValue()
                dlg.Destroy()
                self.isCatting = True
                cmd = 'adb shell "logcat -v time|grep '+self.packageName+'"'
                self.flogcat = showLogThread(self, cmd)
                self.logCatSelectBtn.SetLabel("Stop logcat")
                self.logClearBtn.Disable()
                self.logCatAllBtn.Disable()
                self.flogcat.setDaemon(True)
                self.flogcat.start()
        else:
            self.packageName=""
            self.isCatting = False
            self.logCatSelectBtn.SetLabel("logcat select")
            self.logClearBtn.Enable()
            self.logCatAllBtn.Enable()
            self.flogcat.stop()
            
if __name__ == '__main__':
    app = wx.App()
    TestTool().show()
    app.MainLoop()