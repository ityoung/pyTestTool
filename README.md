####Function:
1. check connected devices
2. logcat, ~~show on screen~~ in-time and save to PC
3. load python test code and run
4. take snapshot when error
5. show test result when finished

####Progress:
1. done
2. save is easy, while show is hard for blocking. <br>~~try wx.CallAfter() and pubsub(complex and not much work)~~ <br>~~try **anonymous pipe**(work better on non-block console,and still can't figure out how to make it work on block console)~~ 
   <br>use **subprocess** to make GUI run smoothly. (5-16)<br>start and stop logcatting all, done(5-17)<br>start and stop logcatting current app working on it...(5-17)<br>start and stop logcatting package name inputed working on it...(5-17)
3. appium
