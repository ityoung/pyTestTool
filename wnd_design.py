import wx
import wx.html
import os
import re
import threading
import subprocess

class startAppiumThread(threading.Thread):
    def __init__(self, window):
        threading.Thread.__init__(self)
        self.window = window
        self.timeToQuit = threading.Event()
        self.timeToQuit.clear()
        self.startCmd = '"G:/Appium/node.exe" \"G:/Appium/node_modules/appium/bin/Appium.js\" --no-reset --local-timezone'
    def stop(self):
        self.fstart.terminate()
        os.system("taskkill /f /t /im node.exe")
        self.timeToQuit.set()
    def run(self):
        self.window.appiumLog.Clear()
        self.window.appiumLog.SetValue("running...")
        try:
            self.fstart = subprocess.Popen(self.startCmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=0x08)
        except:
            os.system("taskkill /f /t /im node.exe")
            self.fstart = subprocess.Popen(self.startCmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=0x08)
        while True:
            output = self.fstart.stdout.readline()
            self.window.appiumLog.AppendText(output)
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
        global isConn
        while 1:
            checkdevicecmd = "adb devices"
            deviceLine = os.popen(checkdevicecmd).readlines()
            if len(deviceLine)==2:
                isConn = False
                self.timeToQuit.wait(0.1)
                wx.CallAfter(self.window.showDeviceInfo)
            else:
                isConn = True
                self.timeToQuit.wait(0.1)
                wx.CallAfter(self.window.showDeviceInfo)
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
            if self.timeToQuit.isSet():
                break

class updateScreenThread(threading.Thread):
    def __init__(self, window):
        threading.Thread.__init__(self)
        self.window = window
        self.timeToQuit = threading.Event()
        self.timeToQuit.clear()
        self.cmd1 = "adb shell /system/bin/screencap -p /sdcard/sstemp.png"
        self.cmd2 = "adb pull /sdcard/sstemp.png F://"
        image2 = wx.Image("F://welcome.png", wx.BITMAP_TYPE_PNG, index=-1)
        self.w = 270
        self.h = 490
#         image = image2.Scale(self.w,self.h)
#         self.bmp = wx.StaticBitmap(self.window.panel1, -1, wx.BitmapFromImage(image), pos=(10, 80), size=(self.w,self.h+10))
    def stop(self):
        self.timeToQuit.set()
    def run(self):
        while True:
            os.system(self.cmd1)
            os.system(self.cmd2)
            image2 = wx.Image("F://sstemp.png", wx.BITMAP_TYPE_PNG, index=-1)
            image = image2.Scale(self.w,self.h)
            self.bmp = wx.StaticBitmap(self.window.panel1, -1, wx.BitmapFromImage(image),pos=(5, 70), size=(self.w,self.h+10))
            self.timeToQuit.wait(1)
            if self.timeToQuit.isSet():
                break
            
class mainFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)
        self.SetSize((900,605))
        
#--------------- split window ---------------
        self.sp = wx.SplitterWindow(self, id=-1)
        self.panel1 = wx.Panel(self.sp, style=wx.SUNKEN_BORDER)
        self.panel2 = wx.Panel(self.sp, style=wx.SUNKEN_BORDER)
        self.sp.Initialize(self.panel1)
        self.sp.SplitVertically(self.panel1, self.panel2, 285)
        
#--------------- device info ----------------        
        self.deviceInfoText = wx.TextCtrl(self.panel1, -1,size=(200,70),style=wx.TE_MULTILINE|wx.TE_NO_VSCROLL)
        self.listenScreenBtn = wx.Button(self.panel1, -1, "show screen\nReal-tiem",size=(80,70))
        thread = checkDeviceThread(self)
        thread.setDaemon(True)      #terminate child thread when main thread ends.
        thread.start()              #check devices until die
        d_sizer = wx.BoxSizer(wx.HORIZONTAL)
        d_sizer.Add(self.deviceInfoText,7,0)
        d_sizer.Add(self.listenScreenBtn,0,0)
        self.panel1.SetSizer(d_sizer)
        self.deviceInfoText.SetEditable(False)
        self.listenScreenBtn.SetDefault()
        self.listenScreenBtn.Bind(wx.EVT_BUTTON, self.listenScreen)
        self.listenDevice = True
        global isConn
        isConn = False
        self.isUpdateScreen = False
        image2 = wx.Image("F://welcome.png", wx.BITMAP_TYPE_PNG, index=-1)
        self.w = 270
        self.h = 490
        
#--------------- tab ------------------------
        notebook = wx.Notebook(self.panel2)
        notebook.AddPage(logTool(notebook), "logTool")
        notebook.AddPage(appiumTool(notebook), "appiumTool")
        p_sizer = wx.BoxSizer(wx.HORIZONTAL)
        p_sizer.Add(notebook, 1, wx.EXPAND | wx.ALL, 7) 
        self.panel2.SetSizer(p_sizer)
         

        
    def showDeviceInfo(self):
        if isConn == True and self.listenDevice == True:
            self.listenDevice = False
            self.deviceInfoText.SetValue("Connected!\n")
            getdeviceinfocmd = 'adb shell "cat /system/build.prop | grep \"product\""'
            deviceinfo = os.popen(getdeviceinfocmd).read()
            device_mf = re.findall('ro.product.manufacturer=(.*)', deviceinfo)
            device_model = re.findall('ro.product.model=(.*)', deviceinfo)
            self.deviceInfoText.AppendText("manufacturer:"+device_mf[0]+"\ndevice model:"+device_model[0])
        elif isConn == False and self.listenDevice == False:
            self.listenDevice = True
            self.deviceInfoText.SetValue("Disconnected!")

#--------------- screen ---------------------
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
     
class appiumTool(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.appiumIsStart = False
        self.scriptPath=""
        
#----------------- btn -----------------
        self.startAppiumBtn = wx.Button(self, -1, "start appium")
        self.startAppiumBtn.SetDefault()
        self.loadScriptBtn = wx.Button(self, -1, "load script")
        self.runScriptBtn = wx.Button(self, -1, "run script")
#----------------- text view ----------------         
        self.appiumLog = wx.TextCtrl(self, -1, size=(700,200), style=wx.TE_MULTILINE)
        self.scriptPathText = wx.TextCtrl(self, -1, size=(180,28))
#----------------- html ----------------
        self.html = wx.html.HtmlWindow(self,size=(700, 600))
        if "gtk2" in wx.PlatformInfo:
            self.html.SetStandardFonts()
        self.html.LoadFile(r"F:\mhome\mhome_test\test_result.html")
#         self.html.LoadPage("http://www.wxpython.org/docs/api/wx.html.HtmlWindow-class.html")
#         self.html.SetBorders(20)
#----------------- sizer ----------------
        btn_sizer= wx.BoxSizer(wx.HORIZONTAL)
        btn_sizer.Add(self.startAppiumBtn, 0, 0)
        btn_sizer.Add(self.loadScriptBtn, 0, 0)
        btn_sizer.Add(self.scriptPathText, 0, 0)
        btn_sizer.Add(self.runScriptBtn, 0, 0)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(btn_sizer, 0, 0)
        sizer.Add(self.appiumLog, 0, 0)
        sizer.Add(self.html, 0, 0)
        self.SetSizer(sizer)
#----------------- bind ----------------
        self.startAppiumBtn.Bind(wx.EVT_BUTTON, self.starAppiumServer)
        self.loadScriptBtn.Bind(wx.EVT_BUTTON, self.selectScript)
        self.runScriptBtn.Bind(wx.EVT_BUTTON, self.runScript)
        
    def starAppiumServer(self, evt):
        if self.appiumIsStart == False:
            self.fstart = startAppiumThread(self)
            self.fstart.setDaemon(True)
            self.fstart.start()
            self.startAppiumBtn.SetLabel("stop appium")
            self.appiumIsStart = True
        else:
            self.startAppiumBtn.SetLabel("start appium")
            self.fstart.stop()
            self.appiumIsStart = False
        
    def selectScript(self, evt):
        scriptFD = wx.FileDialog(self, message="choose a test script", defaultDir="F:/")
        if scriptFD.ShowModal()==wx.ID_OK:
            self.scriptPath = scriptFD.GetPath()
            self.scriptPathText.SetValue(self.scriptPath)
        else:
            pass
        scriptFD.Destroy()
        
    def runScript(self, evt):
        scriptPath = self.scriptPathText.GetValue()
        if scriptPath!="":
            path = scriptPath.split("/")
            scriptpath = scriptPath.strip(path[-1])
            import sys
            sys.path.append(path)
            execfile(scriptPath)
        else:
            dlg = wx.MessageDialog(None,"warning!","Empty Path!",wx.OK|wx.ICON_WARNING)
            dlg.ShowModal()
        
class logTool(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.isCatting = False
        self.packageName =""
        self.isUpdateScreen = False
        #-------------- button -----------------
        self.logClearBtn = wx.Button(self, -1, "logcat clear")
        self.logClearBtn.SetDefault()
        self.logCatAllBtn = wx.Button(self, -1, "logcat all")
        self.logCatSelectBtn = wx.Button(self, -1, "logcat select")
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_sizer.Add(self.logClearBtn,0,0)
        btn_sizer.Add(self.logCatAllBtn,0,0)
        btn_sizer.Add(self.logCatSelectBtn,0,0)
        
#         self.logClearBtn.Disable()
#         self.logCatAllBtn.Disable()
#         self.logCatSelectBtn.Disable()
         
        #-------------- text view ---------------
        self.logMessageText = wx.TextCtrl(self, -1, size=(700,500),style=wx.TE_MULTILINE|wx.TE_LINEWRAP)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(btn_sizer, 0, 0)
        sizer.Add(self.logMessageText,0,0)
        self.SetSizer(sizer)
        #-------------- bind --------------------
        self.logClearBtn.Bind(wx.EVT_BUTTON, self.logClear)
        self.logCatAllBtn.Bind(wx.EVT_BUTTON, self.logCatAll)
        self.logCatSelectBtn.Bind(wx.EVT_BUTTON, self.logCatSelect)
        
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
            cur_pkg = re.findall('u0 .*/', result[0])
            cur_pkg[0] = cur_pkg[0].strip('u0 ')
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

app = wx.App()
frame = mainFrame(None)
frame.Show()
app.MainLoop()