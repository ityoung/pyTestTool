import wx
import wx.html2
import os
import re
import threading
import subprocess
import time
import wx.lib.plot as plot

class getFlowThread(threading.Thread):
    def __init__(self, window):
        threading.Thread.__init__(self)
        self.window     = window
        self.packagename = self.window.packagename
        self.timeToQuit = threading.Event()
        self.timeToQuit.clear()
        self.bytes = [[],[]]
        
    def stop(self):
        self.timeToQuit.set()
        
    def getPID(self):
        cmd = 'adb shell "ps|grep '+self.packagename+'"'
        op = os.popen(cmd).readline()
        ops = op.split()
        return ops[1]
    
    def getUID(self):        
        pid = self.getPID()
        cmd = 'adb shell cat /proc/'+pid+'/status'
        op  = os.popen(cmd)
        opr = op.readline()
        while 'Uid' not in opr:
            opr = op.readline()
        ops = opr.split()
        return ops[1]
    
    def drawFlowPlot(self):
        line_rx_bytes = plot.PolyLine(self.bytes[0], colour='red', width=1)
        line_tx_bytes = plot.PolyLine(self.bytes[1], colour='green', width=1)
        gc= plot.PlotGraphics([line_rx_bytes, line_tx_bytes], 'Flow Utilization', 'time/s', 'utilization/kb')
        self.window.Flowplotter.Draw(gc)
         
    def run(self):
        uid = self.getUID()
        cmd = 'adb shell "cat /proc/net/xt_qtaguid/stats | grep '+uid+'"'
        i = 0
        while True:
            rx_bytes = 0
            tx_bytes = 0
            op  = os.popen(cmd)
            opr = op.readline()
            while '0' in opr:
                ops = opr.split()
                rx_bytes += int(ops[5])
                tx_bytes += int(ops[7])
                opr = op.readline()
            if i == 0:
                self.rx_kB = rx_bytes/1000
                self.tx_kB = tx_bytes/1000
            self.bytes[0].append([i, rx_bytes/1000-self.rx_kB])
            self.bytes[1].append([i, tx_bytes/1000-self.tx_kB])
            i+=1
            self.drawFlowPlot()
            if self.timeToQuit.isSet():
                break

class monitorPerformanceThread(threading.Thread):
    def __init__(self, window):
        threading.Thread.__init__(self)
        self.window      = window
        self.packagename = self.window.packagename
        self.timeToQuit  = threading.Event()
        self.timeToQuit.clear()
        self.cmd = "adb shell \"top |grep "
        self.kindsNum = 0
        self.kvActivities = {}
        self.CPUData = [[],[],[],[],[],[],[]]
        self.MEMData = [[],[],[],[],[],[],[]]
        
    def stop(self):
        self.fstart.terminate()
        self.timeToQuit.set()
    
    def run(self):
        self.calcKinds()
        self.splitValue()

    def splitValue(self):
        self.fstart = subprocess.Popen(
           self.cmd+self.packagename+'"', 
           stdin=subprocess.PIPE, 
           stdout=subprocess.PIPE, 
           stderr=subprocess.PIPE, 
           creationflags=0x08)
        i = 0
        times = 0
        value = 0
        while True:
            output = self.fstart.stdout.readline()
            opArray = output.split()
            if value<self.kindsNum:
                self.kvActivities[opArray[-1]] = value
                value+=1
            self.CPUData[self.kvActivities[opArray[-1]]].append(\
                                        [i,opArray[2].strip("%")])
            self.MEMData[self.kvActivities[opArray[-1]]].append(\
                                        [i,opArray[6].strip("K")])
            self.drawCPUPlot(self.window.processSelection)
            self.drawMEMPlot(self.window.processSelection)
            times+=1
            if times >= self.kindsNum:
                times = 0
                i    += 1
            if self.timeToQuit.isSet():
                break
            
    def calcKinds(self):
        cmd = 'adb shell "top -n 1 |grep "'+self.packagename+'"'
        kindsNum = os.popen(cmd).readlines()
        processChoice = ['All']
        for item in kindsNum:
            processChoice.append(item.split()[-1])
            self.kindsNum+=1
        self.window.showChoice.Set(processChoice)
        self.window.showChoice.SetStringSelection("All")
            
    def drawCPUPlot(self, ps):
        lines = []
        if ps=='All':
            for index in range(self.kindsNum):
                line= plot.PolyLine(self.CPUData[index], colour='red', width=1)
                lines.append(line)
        else:
            line = plot.PolyLine(self.CPUData[self.kvActivities[ps]], colour='blue', width=1)
            lines.append(line)
        gc= plot.PlotGraphics(lines, 'CPU Utilization', 'time/s', 'utilization/%')
        self.window.CPUplotter.Draw(gc)
        
    def drawMEMPlot(self, ps):
        lines = []
        if ps=='All':
            for index in range(self.kindsNum):
                line= plot.PolyLine(self.MEMData[index], colour='blue', width=1)
                lines.append(line)
        else:
            line = plot.PolyLine(self.MEMData[self.kvActivities[ps]], colour='blue', width=1)
            lines.append(line)
        gc= plot.PlotGraphics(lines, 'MEM Utilization', 'time/s', 'utilization/KB')
        self.window.MEMplotter.Draw(gc)
        
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
                      
class mainFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)
        icon = wx.Icon("E.png", wx.BITMAP_TYPE_PNG)  
        self.SetIcon(icon)
        self.SetSize((900,642))
        self.listenDevice = True
        global isConn
        isConn = False
        self.cmd1 = "adb shell /system/bin/screencap -p /sdcard/sstemp.png"
        self.cmd2 = "adb pull /sdcard/sstemp.png F://"
#         self.isUpdateScreen = False
        self.w = 270
        self.h = 490
        
#--------------- split window ---------------
        self.sp     = wx.SplitterWindow(self, id=-1)
        self.panel1 = wx.Panel(self.sp, style=wx.SUNKEN_BORDER)
        self.panel2 = wx.Panel(self.sp, style=wx.SUNKEN_BORDER)
        self.sp.Initialize(self.panel1)
        self.sp.SplitVertically(self.panel1, self.panel2, 285)
         
#--------------- device info ----------------        
        self.deviceInfoText  = wx.TextCtrl(self.panel1, -1,size=(285,70),style=wx.TE_MULTILINE|wx.TE_NO_VSCROLL)

        thread = checkDeviceThread(self)
        thread.setDaemon(True)      #terminate child thread when main thread ends.
        thread.start()              #check devices until die
        self.deviceInfoText.SetEditable(False)
        
        self.refleshBtn = wx.Button(self.panel1, -1, "Refresh")
        self.saveBtn = wx.Button(self.panel1, -1, "Save")
        self.copyBtn = wx.Button(self.panel1, -1, "Copy")
        
        self.refleshBtn.SetDefault()
        self.refleshBtn.Bind(wx.EVT_BUTTON, self.refleshScreen)
        self.saveBtn.Bind(wx.EVT_BUTTON, self.savePic)
        self.copyBtn.Bind(wx.EVT_BUTTON, self.copyPic)
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_sizer.Add(self.refleshBtn,1,0)
        btn_sizer.Add(self.saveBtn,1,0)
        btn_sizer.Add(self.copyBtn,1,0)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.deviceInfoText,0,0)
        sizer.Add(btn_sizer,1,wx.EXPAND)
#         d_sizer.Add(self.listenScreenBtn,0,0)
        self.panel1.SetSizer(sizer)
#--------------- tab ------------------------
        notebook = wx.Notebook(self.panel2)
        notebook.AddPage(logTool(notebook), "logTool")
        notebook.AddPage(monitorTool(notebook), "Monitor")
        p_sizer = wx.BoxSizer(wx.HORIZONTAL)
        p_sizer.Add(notebook, 1, wx.EXPAND | wx.ALL, 7) 
        self.panel2.SetSizer(p_sizer)
         
    def copyPic(self, evt):
        import pyperclip
        pyperclip.copy("sss")
        temp = pyperclip.paste()
        print temp
         

    def savePic(self, evt):
        import shutil
        try:
            fileDlg = wx.FileDialog(self, defaultFile="screenshot-"+time.strftime('%Y%m%d%H%M%S',time.localtime()),wildcard='*.png',style=wx.SAVE)
            if fileDlg.ShowModal() == wx.ID_OK:
                shutil.copy("F:\sstemp.png", fileDlg.GetPath())
        except:
            wnDlg = wx.MessageDialog(self, "Please get screen capture first!", "Warning", style=wx.OK)
            wnDlg.ShowModal()
         
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
 
    def refleshScreen(self,evt):
        os.system(self.cmd1)
        os.system(self.cmd2)
        image2 = wx.Image("F://sstemp.png", wx.BITMAP_TYPE_PNG, index=-1)
        image = image2.Scale(self.w,self.h)
        self.bmp = wx.StaticBitmap(self.panel1, -1, wx.BitmapFromImage(image),pos=(5, 99), size=(self.w,self.h+10))
             
class monitorTool(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self,parent)
        self.isMonitoring = False
        self.packagename  = ''
        self.processSelection = 'All'
        
        #--------- BTN ----------
        self.getCurPackagenameBtn = wx.Button(self, -1, "get current packagename")
        self.startMonitorBtn      = wx.Button(self, -1, "start listen")
        self.startMonitorBtn.Disable()
        
        #--------- Choice -------
        choiceInit = ["All"]
        self.showChoice = wx.Choice(self, -1, choices=choiceInit, size=(180,28))
        self.showChoice.SetStringSelection("All")
        self.showChoice.Bind(wx.EVT_CHOICE, self.processChoose)
        
        #--------- TEXT ---------
        self.packagenameText = wx.TextCtrl(self, -1, size=(180,28))
        
        #--------- plot ---------
        self.CPUplotter = plot.PlotCanvas(self)
        self.CPUplotter.SetInitialSize(size=(600,170))
        self.MEMplotter = plot.PlotCanvas(self)
        self.MEMplotter.SetInitialSize(size=(600,170))
        self.Flowplotter = plot.PlotCanvas(self)
        self.Flowplotter.SetInitialSize(size=(600,170))
        
        data= [[0,0]]
        line= plot.PolyLine(data, colour='red', width=1)
        gc= plot.PlotGraphics([line], 'CPU Utilization', 'time/s', 'utilization/%')
        gc2= plot.PlotGraphics([line], 'MEM Utilization', 'time/s', 'utilization/KB')
        gc3= plot.PlotGraphics([line], 'Flow Utilization', 'time/s', 'utilization/kb')
        self.CPUplotter.Draw(gc)
        self.MEMplotter.Draw(gc2)
        self.Flowplotter.Draw(gc3)
        
        #--------- BIND ---------
        self.getCurPackagenameBtn.Bind(wx.EVT_BUTTON, self.getCurPackagename)
        self.startMonitorBtn.Bind(wx.EVT_BUTTON, self.startMonitor)
        
        #--------- sizer --------
        line1_sizer = wx.BoxSizer(wx.HORIZONTAL)
        line1_sizer.Add(self.getCurPackagenameBtn, 0, 0)
        line1_sizer.Add(self.packagenameText, 1, wx.EXPAND)
        line1_sizer.Add(self.startMonitorBtn, 0, 0)
        line1_sizer.Add(self.showChoice, 0, wx.EXPAND)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddMany([line1_sizer, self.CPUplotter, self.MEMplotter, self.Flowplotter])
        self.SetSizer(sizer)
        
    def processChoose(self, evt):
        self.processSelection = self.showChoice.GetString(self.showChoice.GetSelection())
        
    def getCurPackagename(self, evt):
        cmd = "adb shell \"dumpsys window windows | grep -E 'mFocusedApp'\""
        result = os.popen(cmd).readlines()
        cur_pkg = re.findall('u0 .*/', result[0])
        cur_pkg[0] = cur_pkg[0].strip('u0 ')
        cur_pkg[0] = cur_pkg[0].strip('/')
        self.packagename = cur_pkg[0]
        self.packagenameText.SetValue(self.packagename)
        self.startMonitorBtn.Enable()
        
    def startMonitor(self, evt):
        if self.isMonitoring == False:
            self.fstart = monitorPerformanceThread(self)
            self.fstart.setDaemon(True)
            self.fstart.start()
            self.fgetFlow = getFlowThread(self)
            self.fgetFlow.setDaemon(True)
            self.fgetFlow.start()
            self.startMonitorBtn.SetLabel("stop monitor")
            self.getCurPackagenameBtn.Disable()
            self.isMonitoring = True
        else:
            self.fstart.stop()
            self.fgetFlow.stop()
            self.startMonitorBtn.SetLabel("start monitor")
            self.getCurPackagenameBtn.Enable()
            self.isMonitoring = False
            
class logTool(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.isCatting = False
        self.packageName =""
        self.isUpdateScreen = False
        self.logLevel = "V"
        
        #-------------- button -----------------
        self.logClearBtn = wx.Button(self, -1, "logcat clear")
        self.logClearBtn.SetDefault()
        self.logCatAllBtn = wx.Button(self, -1, "logcat all")
        self.logCatSelectBtn = wx.Button(self, -1, "logcat select")
        self.saveBtn = wx.Button(self, -1, "save log")
        
        #-------------- choice -----------------
        choiceInit = ["V-Verbose","D-Debug","I-Info","W-Warning","E-Error","F-Fatal","S-Silent"]
        self.levelChoice = wx.Choice(self, -1, choices=choiceInit, size=(90,28))
        self.levelChoice.SetStringSelection("V-Verbose")
        
        #-------------- text -------------------
        self.saveResult = wx.StaticText(self,-1,size=(180,28),style=wx.TOP)
        
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_sizer.Add(self.logClearBtn,0,0)
        btn_sizer.Add(self.levelChoice, 0,wx.EXPAND)
        btn_sizer.Add(self.logCatAllBtn,0,0)
        btn_sizer.Add(self.logCatSelectBtn,0,0)
        btn_sizer.Add(self.saveBtn,0,0)
        btn_sizer.Add(self.saveResult, 0, 0)
        
         
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
        self.levelChoice.Bind(wx.EVT_CHOICE, self.changeLevel)
        self.saveBtn.Bind(wx.EVT_BUTTON, self.saveLog)
        
    def changeLevel(self, evt):
        self.logLevel = self.levelChoice.GetString(self.levelChoice.GetSelection())[0]
        
    def saveLog(self, evt):
        if self.logMessageText.GetValue():
            fileDlg = wx.FileDialog(self, defaultFile="logcat-"+time.strftime('%Y%m%d%H%M%S',time.localtime()),wildcard='*.txt',style=wx.SAVE)
            if fileDlg.ShowModal() == wx.ID_OK:
                fp = open(fileDlg.GetPath(), "w")
                fp.write(self.logMessageText.GetValue())
                fp.close()
                self.saveResult.SetLabel("saved!")
        else:
            wnDlg = wx.MessageDialog(self, "Log file is empty!\nPlease cat log first!", "Warning", style=wx.OK)
            wnDlg.ShowModal()
        
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
            cmd = 'adb logcat -v time *:' +self.logLevel
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
                cmd = 'adb shell "logcat -v time *:'+self.logLevel+'|grep '+self.packageName+'"'
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
frame = mainFrame(None,title="Easy Test for Android")
frame.Show()
app.MainLoop()
