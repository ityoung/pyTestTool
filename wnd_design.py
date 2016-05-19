import threading
import subprocess
import wx
import os
import re

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
        self.wndSize = wx.Size(550,400)
        thread = checkDeviceThread(self)
        thread.setDaemon(True)      #terminate child thread when main thread ends.
        thread.start()              #check devices until die
        
        self.isCatting = False
        self.isconn = False
        self.listenDevice = True
        self.packageName =""

    def show(self):
        self.frame = wx.Frame(None,title="testTool", size=self.wndSize)  
        panel = wx.Panel(self.frame, 1)
        
        #-------------- button ---------------
        #self.connButton = wx.Button(panel, -1, "show device info", pos=(10, 10))
        #self.connButton.SetDefault()
        self.logClearBtn = wx.Button(panel, -1, "logcat clear", pos = (220, 10))
        self.logClearBtn.SetDefault()
        self.logCatAllBtn = wx.Button(panel, -1, "logcat all", pos = (320, 10))
        self.logCatSelectBtn = wx.Button(panel, -1, "logcat select", pos = (420, 10))
        
        #self.logClearBtn.Disable()
        #self.logCatAllBtn.Disable()
        #self.logCatSelectBtn.Disable()
        
        #-------------- text view ---------------
        self.deviceInfoText = wx.TextCtrl(panel, -1, pos=(10,50),size=(200,70),style=wx.TE_MULTILINE|wx.TE_NO_VSCROLL)
        self.deviceInfoText.SetEditable(False)
        self.logMessageText = wx.TextCtrl(panel, -1, pos = (220, 50), size=(300,300),style=wx.TE_MULTILINE|wx.TE_LINEWRAP)
        
        #-------------- bind -------------
        #self.connButton.Bind(wx.EVT_BUTTON,self.clickConn)
        self.logClearBtn.Bind(wx.EVT_BUTTON, self.logClear)
        self.logCatAllBtn.Bind(wx.EVT_BUTTON, self.logCatAll)
        self.logCatSelectBtn.Bind(wx.EVT_BUTTON, self.logCatSelect)
        
        self.frame.Show()
    
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