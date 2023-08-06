import os
__version__ = "1.3.2"
filename = ".".join(["jquery-" + __version__, "min" , "js"])

path = os.sep.join([os.path.dirname(__file__), filename])
canonical_url = "http://jqueryjs.googlecode.com/files/jquery-1.3.2.min.js"

def main():
    print(path)
