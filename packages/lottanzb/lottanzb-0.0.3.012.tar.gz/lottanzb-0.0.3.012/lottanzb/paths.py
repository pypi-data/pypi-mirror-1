import os
from pkg_resources import resource_filename

# Test if the application installed on the system
_installed = "site-packages" in __file__

def isInstalled ():
    return _installed

# Helper function
def _joinDir(dir, subpath=None):
    if subpath is None:
        return dir + "/"
    else:
        return os.path.join(dir, subpath)

# The data directory where glade and image files reside
_dataDir = resource_filename(__name__, "data")

def dataDir(subpath=None):
    return _joinDir(_dataDir, subpath)

# The locale directory where translation files reside
_localeDir = resource_filename(__name__, "po")

def localeDir(subpath=None):
    return _joinDir(_localeDir, subpath)

# Determine the user's home directory path
if os.name == "posix":
    _home = os.environ.get("HOME")
elif os.name == "nt":
    _home = os.environ.get("APPDATA")

def homeDir(subpath=None):
    return _joinDir(_home, subpath)

# Where to store the HellaNZB and LottaNZB configuration files
_clientDir = homeDir(".lottanzb")

def clientDir(subpath=None):
    return _joinDir(_clientDir, subpath)

def hasClientDir():
    return os.path.isdir(_clientDir)

def makeClientDir():
    if not hasClientDir():
        os.mkdir(_clientDir)

# Where place to store temporary files
if os.name == "posix":
    _temp = clientDir("tmp")
elif os.name == "nt":
    _temp = os.environ.get("TMP")

def tempDir(subpath=None):
    return _joinDir(_temp, subpath)

def makeTempDir():
    if not os.path.isdir(tempDir()):
        os.mkdir(tempDir())
