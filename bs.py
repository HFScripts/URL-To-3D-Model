import subprocess
import sys

# Find the path to the Blender Python executable
blender_python = sys.executable

# Install required packages using pip
subprocess.call([blender_python, "-m", "ensurepip"])
subprocess.call([blender_python, "-m", "pip", "install", "beautifulsoup4"])
subprocess.call([blender_python, "-m", "pip", "install", "requests"])
subprocess.call([blender_python, "-m", "pip", "install", "Pillow"])
subprocess.call([blender_python, "-m", "pip", "install", "urllib3"])
