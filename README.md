####Function:
######page 1:
1. check connected devices
2. logcat, ~~show on screen in-time and~~ save to PC
3. real-time transmission device's image<br>
######page 2:<br>
1. start appium service(check)
2. show appium logmessage
3. load python test script
4. run script
5. take snapshot and catch log when error
6. show test result when finished

####Progress:
1. __done__(5-16)<br>use multithread to check device back end(5-19)
2. save is easy, while show is hard for blocking. <br>~~try wx.CallAfter() and pubsub(complex and not much work)~~ <br>~~try **anonymous pipe**(work better on non-block console,and still can't figure out how to make it work on block console)~~
   <br>use **subprocess** to make GUI run smoothly. (5-16)<br>**solved** with **subprocess.Popen.stdout.readline()**! Logcat all is easily done with that function, while 'adb shell "logcat|grep keywords"' still block! Finally have to cat first and then pick up the log contains key words.(5-17)
<br>clear log, confirm dialog, __done__(5-17)<br>start and stop logcatting all, __done__(5-17)<br>start and stop logcatting a certain app, defualt show current app's package name, __done__(5-17)<br>now the software runs PERFECT! with the other days' work, plus **multithread** and **subprocess**, I finally make the logMessage print on screen Real-	Time and **Non-Block**!(5-19)<br>timestamp for filename, and doing save work.
3. complete, still about 3.5 delay. Try multithread, which finally proves taking more time, and have to think about I/O lock, so just let it delay, may solve this when whole work done.(5-20)
