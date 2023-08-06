#===================================================================================#
#                                                 __                                #
#                                                /\ \__                             #
#                    _____   _ __   __  __    ___\ \ ,_\                            #
#                   /\ '__`\/\`'__\/\ \/\ \ /' _ `\ \ \/                            #
#                   \ \ \_\ \ \ \/ \ \ \_\ \/\ \/\ \ \ \_    __   __                #
#                    \ \  __/\ \_\  \/`____ \ \_\ \_\ \__\  /\_\ /\_\               #
#                     \ \ \/  \/_/   `/___/> \/_/\/_/\/__/  \/_/ \/_/               #
#                      \ \_\            /\___/                                      #
#                       \/_/            \/__/                                       #
#                                                                                   #
#===================================================================================#
#@copyright: 2008 by Jeremy Bouillanne
#@license: Apache Public Licence
__revision = '$Revision:  $'[11:-2]

import sys
import webbrowser
from docutils.core import publish_string
from prynt.rest import fig,img, substitution_image
from matplotlib.mathtext import MathTextParser

class matplotlib(object):
    showgraph = True
    default_image = 'image-'
    def __init__(self):
        pass

class mathtext(object):
    default_equation = 'equ-'
    inline_color='black' 
    inline_dpi=120 
    inline_fontsize=10
    figure_color='black'
    figure_dpi=120 
    figure_fontsize=14
    
class configuration(object):
    matplotlib = matplotlib()
    mathtext = mathtext()
    filename = None
    def __init__(self):
        pass
    
__conf = configuration()

class prynter(object):
    rout=None
    def __init__(self, stdout):
        self.rout = stdout
        self.buffer = ""
        
    def write(self, text):
        self.rout.write(text)
        self.buffer+=text #@TODO improve buffer management
 
__prynter = prynter(sys.stdout) 
sys.stdout=__prynter

__prynt_count=1
def prynt(filetype='html', autoopen=True):
    """ transforms the buffer as rst to html or latex"""
    global __prynt_count
    
    if __conf.filename==None: __conf.filename=__extract_calling_filename()
    if __prynt_count>1 :filename+="-"+str(__prynt_count)
    out = __conf.filename+"."+filetype
    page = publish_string(__prynter.buffer, writer_name=filetype)
    
    file = open(out, 'w')
    file.write(page)
    file.close()
    if autoopen: webbrowser.open(out)
    
    __prynter.buffer=""
    __prynt_count+=1

def __extract_calling_filename():
    filename = sys.argv[0]
    last_index = filename.rfind(".")
    filename = filename[:last_index]
    return filename
    
__show_count = 0
def show(filetype="png", **kwargs):
    global __show_count
    from pylab import savefig, show
    __show_count+=1
    savefig(__conf.matplotlib.default_image+str(__show_count)+"."+filetype)
    if __conf.matplotlib.showgraph: show(**kwargs)
    print fig(__conf.matplotlib.default_image+str(__show_count)+"."+filetype+"\n")

__equ_count = 1
def equ(equa, name):
    global __equ_count
    equation_name= __conf.mathtext.default_equation+str(__equ_count)+".png"
    MathTextParser("bitmap").to_png(equation_name, "$"+equa+" $", __conf.mathtext.inline_color, __conf.mathtext.inline_dpi, __conf.mathtext.inline_fontsize)
    __equ_count+=1
    return substitution_image(name,equation_name)
    
    
def fequ(equa):
    global __equ_count
    fequation_name = __conf.mathtext.default_equation+str(__equ_count)+".png"
    MathTextParser("bitmap").to_png(fequation_name, "$$"+equa+"$$", __conf.mathtext.figure_color, __conf.mathtext.figure_dpi, __conf.mathtext.figure_fontsize)
    return fig(__conf.mathtext.default_equation+str(__equ_count)+".png")
    __equ_count+=1

def pryntonexit():
    import atexit
    atexit.register(prynt)    
