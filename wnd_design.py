import signal
import wx
import os
import subprocess
import sys
import time
import re

#from StartMRService import StartMRService

class TestTool(object):
    def __init__(self):
        self.wndSize = wx.Size(600,400)

    def show(self):
        app = wx.App()
        self.frame = wx.Frame(None,title="testTool", size=self.wndSize)  
        panel = wx.Panel(self.frame, 1)
        
        #-------------- button ---------------
        self.connButton = wx.Button(panel, -1, "show device info", pos=(10, 10))
        self.connButton.SetDefault()
        self.logClearBtn = wx.Button(panel, -1, "logcat clear", pos = (220, 10))
        self.logClearBtn.SetDefault()
        self.logCatAllBtn = wx.Button(panel, -1, "logcat all", pos = (320, 10))
        self.logCatSelectBtn = wx.Button(panel, -1, "logcat select", pos = (420, 10))
        
        #self.logClearBtn.Disable()
#         self.logCatAllBtn.Disable()
#         self.logCatSelectBtn.Disable()
        
        #-------------- text view ---------------
        self.deviceInfoText = wx.TextCtrl(panel, -1, pos=(10,50),size=(200,50),style=wx.TE_MULTILINE|wx.TE_NO_VSCROLL)
        self.deviceInfoText.SetEditable(False)
        self.packgeNameText = wx.TextCtrl(panel, -1, pos = (220, 50), size=(300,300),style=wx.TE_MULTILINE|wx.TE_LINEWRAP)
        
        #-------------- bind -------------
        self.connButton.Bind(wx.EVT_BUTTON,self.clickConn)
        self.logClearBtn.Bind(wx.EVT_BUTTON, self.logClear)
        self.logCatAllBtn.Bind(wx.EVT_BUTTON, self.logCatAll)
        self.logCatSelectBtn.Bind(wx.EVT_BUTTON, self.logCatSelect)
        
        self.isCatting = False
        self.packageName =""
        
        self.frame.Show()
        app.MainLoop()
        
    def clickConn(self,even):
        checkdevicecmd = "adb devices"
        isconn = os.popen(checkdevicecmd).readlines()
        if len(isconn) ==3:
            getdeviceinfocmd = 'adb shell "cat /system/build.prop | grep \"product\""'
            deviceinfo = os.popen(getdeviceinfocmd).read()
            device_brand = re.findall('ro.product.brand=(.*)', deviceinfo)
            device_model = re.findall('ro.product.model=(.*)', deviceinfo)
            self.deviceInfoText.SetValue("device brand:"+device_brand[0]+"\ndevice model:"+device_model[0])
            self.connButton.SetLabel("Connected")
            self.connButton.Disable()
            self.logClearBtn.Enable()
            self.logCatAllBtn.Enable()
            self.logCatSelectBtn.Enable()
        else:
            dialog = wx.MessageDialog(self.frame,"please connect your device!",style=wx.OK_DEFAULT)
            dialog.ShowModal()
            self.deviceInfoText.Clear()
            
    def startAppium(self,even):
        import os
        appium = os.system('adb logcat > E:/log/a.txt')
        self.appiumRunText.SetValue(appium)
        #handler = AppiumLogHandler(self.appiumRunText)
        #logging.getLogger().addHandler(handler)
            
    def logClear(self,even):
        dlg = wx.MessageDialog(None, 'Confirm clear old-log?',
                          'Warning', wx.YES_NO | wx.ICON_QUESTION)
        result = dlg.ShowModal()
        # if choose no then exit
        if result == wx.ID_NO:
            os.system("explorer E:/log")
            pass
        else:
            cmd = "adb logcat -c"
            os.system(cmd)
        dlg.Destroy()
            
    def logCatAll(self,even):
        if self.isCatting == False:
            self.packgeNameText.Clear()
            filename = "E:/log/t.txt"
            #fp = open(filename, 'w+')
            cmd = 'adb logcat -v time'
            self.flogcat = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=0x08)
            #self.flogcat = subprocess.Popen(cmd,stdout = fp, stderr=subprocess.PIPE)
            self.isCatting = True
            self.logCatAllBtn.SetLabel("Stop logcat")
            self.logClearBtn.Disable()
            self.logCatSelectBtn.Disable()
            wx.CallAfter(self.doLogging)
        else:
            self.flogcat.terminate()
            self.isCatting = False
            self.logCatAllBtn.SetLabel("logcat all")
            self.logClearBtn.Enable()
            self.logCatSelectBtn.Enable()
    
    def logCatSelect(self,even):
        if self.isCatting == False:
            self.packgeNameText.Clear()
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
                filename = "E:/log/ttt.txt"
                fp = open(filename, 'w+')
                cmd = 'adb shell logcat -v time'
                #cmd = 'adb shell "logcat -v time|grep '+self.packageName+'"'
                self.flogcat = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=0x08)
                self.logCatSelectBtn.SetLabel("Stop logcat")
                self.logClearBtn.Disable()
                self.logCatAllBtn.Disable()
                wx.CallAfter(self.doLogging)
            else:
                return
        else:
            self.flogcat.terminate()
            self.packageName=""
            self.isCatting = False
            self.logCatSelectBtn.SetLabel("logcat select")
            self.logClearBtn.Enable()
            self.logCatAllBtn.Enable()

    def doLogging(self):
        if self.isCatting:
            try:
                output = self.flogcat.stdout.readline()
                if self.packageName!="":
                    if re.search(self.packageName,output):
                        self.packgeNameText.AppendText(output)
                else:
                    self.packgeNameText.AppendText(output)
                    print output
                wx.CallLater(100,self.doLogging)
            except:
                return

if __name__ == '__main__':
    TestTool().show()