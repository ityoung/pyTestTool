####Function:
######page 1 - **logcat**:
1. check connected devices
2. logcat, show on screen in-time and save to PC
3. real-time transmission device's image

######page 2 - **appium**:
1. start appium service(check)
2. show appium logmessage
3. load python test script
4. run script
5. show test result when finished

######page 3 - **recorde/playback**:
1. get x/y coordinate and time interval
2. show on screen
3. save as A appropriate format file
4. interprete the operation file to a certain language
5. playback

######page 4 - **monitor**:
1. get CPU info
2. get Memory info
3. get flow(send/recieve) info
4. get current app packagename
5. enter packagename and do 123
6. draw broken line graph
7. auto-analysis the result
8. choose process/all of plot
9. ~~test APP run-up time~~(keep to other pages)

___

####Progress:
######page 1:
1. 
   * done(5-16)<br>
   * use multithread to check device back end(5-19)
2. 
   * save is easy, while show is hard for blocking. <br>
   * ~~try wx.CallAfter() and pubsub(complex and not much work)~~ <br>
   * ~~try anonymous pipe(work better on non-block console,and still can't figure out how to make it work on block console)~~<br>
   * use subprocess to make GUI run smoothly. (5-16)<br>
   * solved with subprocess.Popen.stdout.readline()! Logcat all is easily done with that function, while 'adb shell "logcat|grep keywords"' still block! Finally have to cat first and then pick up the log contains key words.(5-17)<br>
   * clear log, confirm dialog, done(5-17)<br>
   * start and stop logcatting all, done(5-17)<br>
   * start and stop logcatting a certain app, defualt show current app's package name, done(5-17)<br>
   * now the software runs PERFECT! with the other days' work, plus multithread and subprocess, I finally make the logMessage print on screen Real-	Time and Non-Block!(5-19)<br>
   * saving operator.(6-6)
3. 
   * complete, still about 3.5 delay. Try multithread, which finally proves taking more time, and have to think about I/O lock, so just let it delay, may solve this when whole work done.(5-20)

######page 2:
1. 
   * start appium back-end with subprocess.(5-24)
2. 
   * show appium log message with multithread.(5-24)
3. 
   * use wx.FileDialog to choose script path and show in TextCtrl.(5-24)
4. 
   * run script with function ~~'execfile'~~, and warning when path empty. (failed, cuz when execute script, the path which script imports is complicated to add.)(5-24)<br>
   * use 'os.system()', but shows many consoles(caused by appium calling adb.exe) and still cannot figure out how to solve this.(5-24)
5. 
   * finished with "wx.html.HtmlWindow", however, that module cannot parse CSS/JS. Maybe I should find some more effective method when whole work done.(5-25)
   * "wx.html2.WebView" module can solve that problem, work on it later. (5-31)
   * finished.(6-7)
   

######page 3:
1. 
   * get x/y coordinate with command 'adb shell getevent'(5-26)
2. 
   * show on screen(5-26)
   * still need some change.
3. 
   * save as A appropriate format file **unfinished**.
4. 
   * interprete the operation file to "CMD"(5-27)
   * need to interprete it to run with appium.
5. 
   * playback unfinished and can be postponed.

######page 4:
1. 
   * get CPU info(5-30)
2. 
   * get Memory info(5-30)<br>
   * with "adb shell top | grep packagename" command, and str.split() to get certain value.(5-30)
3. 
   * get PID with command "adb shell ps|grep packagename"<br>
   * get flow with command ~~'adb shell cat /proc/"+Pid+"/net/dev"'~~, while that can only get flow utilization of all applications.<br>
   * decide to get UID first with command "adb shell cat /proc/<pid>/status", and get the flow of that uid's process with command"adb shell cat /proc/net/xt_qtaguid/stats | grep uid"<br>
   * rx_bytes refer to recieved flow and tx_bytes refer to sent.
   * dive 1000 to change flow from b to kb
   * delete first value, and use different color to make graph more intuitional.(6-1)
4. 
   * done.(5-30)
5. 
   * now work well on fun.1 and fun.2(5-30)<br>
   * when show flow plot, the CPU/MEM will delay about 10 second, and still confused me.(6-1)
6. 
   * "wx.lib.plot" is working. and now can draw CUP/MEM utilization graph. if one app has more than one activity, it can draw serveral lines. the two-dimensional array really took much of my time.(5-31)
7. 
   * __unfinished__
8. 
   * use wx.Choice.(6-6)
