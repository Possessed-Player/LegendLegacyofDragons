from cx_Freeze import setup, Executable

base = None    

executables = [Executable("webclient.py", base=base)]

packages = ["idna", "os", "psutil", "webview", "controlGui", "botAlgo" ,"tkinter", 
			"time", "threading", "random", "configparser", "cefpython3", "pyautogui"]
options = {
    'build_exe': {    
        'packages':packages,
    },    
}

setup(
    name = "Bot",
    options = options,
    version = "0.95",
    description = '<any description>',
    executables = executables
)