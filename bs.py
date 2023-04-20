import subprocess
import sys

# Find the path to the Blender Python executable
blender_python = sys.executable

# Install the BeautifulSoup library using pip
subprocess.call([blender_python, "-m", "ensurepip"])
subprocess.call([blender_python, "-m", "pip", "install", "beautifulsoup4"])
