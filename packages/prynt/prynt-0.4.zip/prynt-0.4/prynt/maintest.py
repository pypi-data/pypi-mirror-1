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

import unittest
import sys
import pryntrest



import doctest
doctest.testmod(pryntrest, verbose=True)#verbose=True)


class PryntTest(unittest.TestCase):
    def testFile(selfself):
        #make sure the redirected standard output isn't altered
        print('this is a test')
        #prynt.prynt('html', False, 'test')
        print('this is a second test')
        #prynt.prynt('html', False, 'test')
        #self.assertNotEqual('test.html', 'test-2.html') #@TODO make it working
        

class PryntRestTest(unittest.TestCase):
    def atestHyperlink_reference(self):
        #make sure the hyperlink is working
        pryntrest.hyperlink_reference("testlink", "http://www.google.com")
        for a in range(10):
            print "buffer is : ",sys.stdout.buffer
        
