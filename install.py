import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
	
if __name__ == "__main__":
	packages = ("Pillow", "Desktopmagic", "numpy", "pyautogui", "scikit-image", "opencv-python", "configparser", "psutil", "pywebview[cef]", "scikit-learn")
	for p in packages:
		install(p)