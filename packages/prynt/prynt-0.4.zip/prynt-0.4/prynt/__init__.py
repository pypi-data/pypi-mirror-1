import main
from matplotlib import show
import mathtext
import rest
import sys


class configuration(object):
    matplotlib = matplotlib.matplotlib()
    mathtext = mathtext.mathtext()
    filename = None
    path = "img"
    def __init__(self, **kwargs):
        for k,v in kwargs.items():
            self.__setattr__(k,v)
            
        
    
    def getfilepath(self, filename, filetype):
        from os import mkdir
        from os.path import join, exists
        if exists(self.path) == False : mkdir(self.path)
        return join(config.path, filename+"."+filetype)

    
__prynter = main.prynter(sys.stdout) 
sys.stdout=__prynter


       
config = configuration(mathtext = mathtext.__config, matplotlib=matplotlib.__config)
#rest.__config = config.rest

def prynt(filetype='html', autoopen=True):
    __prynter.prynt(filetype=filetype, autoopen=autoopen) 
def pryntonexit():
    import atexit
    atexit.register(prynt)    

