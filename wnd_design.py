import wx
import logging
#from StartMRService import StartMRService

class AppiumLogHandler(logging.Handler):
    def __init__(self, obj):
        logging.Handler.__init__(self)
        self.object = obj
        
    def show(self,record):
        self.object.AppendText(record.getMessage())
        

class TestTool(object):
    def __init__(self):
        self.wndSize = wx.Size(600,400)

    def show(self):
        app = wx.App()
        self.frame = wx.Frame(None,title="testTool", size=self.wndSize)  
        panel = wx.Panel(self.frame, 1)
        #panel2 = wx.Panel(self.frame, 2)    
        
        self.connButton = wx.Button(panel, 1, "show device info", pos=(50, 20))
        self.connButton.SetDefault()
        self.startAppiumButton = wx.Button(panel, 2, "Start Appium", pos=(200, 20))
        self.startAppiumButton.SetDefault()
        
        self.deviceInfoText = wx.TextCtrl(panel, 1, pos=(50,80),size=(200,50),style=wx.TE_MULTILINE|wx.TE_NO_VSCROLL)
        self.appiumRunText = wx.TextCtrl(panel, 2, pos=(50,150),size=(500,200),style=wx.TE_AUTO_SCROLL|wx.TE_MULTILINE)
        self.connButton.Bind(wx.EVT_BUTTON,self.clickConn)
        self.startAppiumButton.Bind(wx.EVT_BUTTON, self.startAppium)
        
        self.frame.Show()
        app.MainLoop()
        
    def clickConn(self,even):
        import os
        checkdevicecmd = "adb devices"
        isconn = os.popen(checkdevicecmd).readlines()
        if len(isconn) ==3:
            getdeviceinfocmd = 'adb shell "cat /system/build.prop | grep \"product\""'
            deviceinfo = os.popen(getdeviceinfocmd).read()
            import re
            device_brand = re.findall('ro.product.brand=(.*)', deviceinfo)
            device_model = re.findall('ro.product.model=(.*)', deviceinfo)
            #print device_brand[0]
            self.deviceInfoText.SetValue("device brand:"+device_brand[0]+"\ndevice model:"+device_model[0])
            #monkeyrunnerThread = StartMRService()
            #monkeyrunnerThread.start()
        else:
            #monkeyrunnerThread = StartMRService()
           # monkeyrunnerThread.start()
            dialog = wx.MessageDialog(self.frame,"please connect your device!",style=wx.OK_DEFAULT)
            dialog.ShowModal()
            self.deviceInfoText.Clear()  #clear text
            
    def startAppium(self,even):
        import os
        appium = os.popen('adb logcat > E:/log/a.text').read()
        self.appiumRunText.SetValue(appium)
        #handler = AppiumLogHandler(self.appiumRunText)
        #logging.getLogger().addHandler(handler)
            

if __name__ == '__main__':
    TestTool().show()