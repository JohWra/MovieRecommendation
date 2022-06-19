import subprocess
import sys

def install_2param(package, param, param2):
    subprocess.check_call([sys.executable, "-m", "pip", "install", param, param2, package])

def install_param(package, param):
    subprocess.check_call([sys.executable, "-m", "pip", "install", param, package])

updatePip = input("update pip? y/n \n")
if(updatePip == "y"):
    install_2param("--user", "--upgrade", "pip")
else:
    print("old pip version is used. Installation continues")
install_param("--user", "pandas")