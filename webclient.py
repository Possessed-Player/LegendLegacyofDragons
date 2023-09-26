import os
import psutil
import webview
import controlGui
import botAlgo
import tkinter as tk
from webview.platforms.cef import settings
	
def launchCG(webwin):
	botAlgo.Bot(webwin, controlGui.MainGui)
	
if __name__ == '__main__':
	webwin = webview.create_window("Hisham Moe's Bot Client - v0.95", 'http://warofdragons.com/')
	settings.update({
    'cache_path': (os.getcwd() + "\\cache")
	})
	try:
		webview.start(launchCG, webwin, gui='edgechromium')
	finally:
		PROCNAME = "subprocess.exe"
		
		for proc in psutil.process_iter():
			# check whether the process name matches
			if proc.name() == PROCNAME:
				proc.kill()
		
		os._exit(-1)