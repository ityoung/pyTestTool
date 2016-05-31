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

######page 4 - **performance testing**:
1. get CPU info
2. get Memory info
3. get flow(u/d) info
4. get current app packagename
5. enter packagename and do 123
6. draw broken line graph
7. auto-analysis the result
8. test APP run-up time

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
   * timestamp for filename, and doing save work. __unfinished__
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

######page 3:
1. 
   * get x/y coordinate with command 'adb shell getevent'(5-26)
2. 
   * show on screen(5-26)
   * still need some change.
3. 
   * save as A appropriate format file unfinished.
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

