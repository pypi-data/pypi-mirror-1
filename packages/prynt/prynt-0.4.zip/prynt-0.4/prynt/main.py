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
import prynt

class prynter(object):
    rout=None
    
    def __init__(self, stdout):
        self.rout = stdout
        self.buffer = ""
        self.__prynt_count=1

    def write(self, text):
        self.rout.write(text)
        self.buffer+=text #@TODO improve buffer management
        
    def prynt(self, filetype='html', autoopen=True):
        """ transforms the buffer as rst to html or latex"""
        if prynt.config.filename==None: prynt.config.filename=self.__extract_calling_filename()
        if self.__prynt_count>1: prynt.config.filename += "-"+str(self.__prynt_count)
        out = prynt.config.filename+"."+filetype
        page = publish_string(self.buffer, writer_name=filetype)
        
        file = open(out, 'w')
        file.write(page)
        file.close()
        if autoopen: webbrowser.open(out)
        
        self.buffer=""
        self.__prynt_count+=1
        
    def __extract_calling_filename(self):
        filename = sys.argv[0]
        last_index = filename.rfind(".")
        filename = filename[:last_index]
        return filename
    

