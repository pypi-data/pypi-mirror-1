#!/usr/bin/env python


"""
Autogenerated by CHEETAH: The Python-Powered Template Engine
 CHEETAH VERSION: 1.0
 Generation time: Wed Aug 16 22:58:25 2006
   Source file: atom.tmpl
   Source file last modified: Wed Aug 16 22:58:22 2006
"""

__CHEETAH_genTime__ = 'Wed Aug 16 22:58:25 2006'
__CHEETAH_src__ = 'atom.tmpl'
__CHEETAH_version__ = '1.0'

##################################################
## DEPENDENCIES

import sys
import os
import os.path
from os.path import getmtime, exists
import time
import types
import __builtin__
from Cheetah.Template import Template
from Cheetah.DummyTransaction import DummyTransaction
from Cheetah.NameMapper import NotFound, valueForName, valueFromSearchList, valueFromFrameOrSearchList
from Cheetah.CacheRegion import CacheRegion
import Cheetah.Filters as Filters
import Cheetah.ErrorCatchers as ErrorCatchers
from cgi import escape

##################################################
## MODULE CONSTANTS

try:
    True, False
except NameError:
    True, False = (1==1), (1==0)
VFFSL=valueFromFrameOrSearchList
VFSL=valueFromSearchList
VFN=valueForName
currentTime=time.time

##################################################
## CLASSES

class atom(Template):
    """
    
    Autogenerated by CHEETAH: The Python-Powered Template Engine
    """

    ##################################################
    ## GENERATED METHODS


    def __init__(self, *args, **KWs):
        """
        
        """

        Template.__init__(self, *args, **KWs)

    def respond(self,
            trans=None,
            VFFSL=valueFromFrameOrSearchList,
            VFN=valueForName):


        """
        This is the main method generated by Cheetah
        """

        if not trans: trans = self.transaction # is None unless self.awake() was called
        if not trans:
            trans = DummyTransaction()
            dummyTrans = True
        else: dummyTrans = False
        write = trans.response().write
        SL = self._searchList
        globalSetVars = self._globalSetVars
        filter = self._currentFilter
        
        ########################################
        ## START - generated method body
        
        write('''<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">

    <title type="html">''')
        __v = VFFSL(SL,"title",True)
        if __v is not None: write(filter(__v, rawExpr='$title')) # from line 5, col 24.
        write('</title>\n    <link rel="self" href="')
        __v = VFFSL(SL,"feed",True)
        if __v is not None: write(filter(__v, rawExpr='$feed')) # from line 6, col 28.
        write('"/>\n    <updated>')
        __v = VFN(VFFSL(SL,"updated",True),"strftime",False)('%Y-%m-%dT%H:%M:%SZ')
        if __v is not None: write(filter(__v, rawExpr="$updated.strftime('%Y-%m-%dT%H:%M:%SZ')")) # from line 7, col 14.
        write('''</updated>
    <author>
        <name>Roberto De Almeida</name>
        <email>roberto@dealmeida.net</email>
        <uri>http://dealmeida.net</uri>
    </author>
    <id>''')
        __v = VFFSL(SL,"home",True)
        if __v is not None: write(filter(__v, rawExpr='$home')) # from line 13, col 9.
        write('</id>\n\n')
        for entry in VFFSL(SL,"entries",True):
            write('    <entry>\n        <title>')
            __v = VFFSL(SL,"entry.title",True)
            if __v is not None: write(filter(__v, rawExpr='$entry.title')) # from line 17, col 16.
            write('</title>\n        <link href="')
            __v = VFFSL(SL,"entry.id",True)
            if __v is not None: write(filter(__v, rawExpr='$entry.id')) # from line 18, col 21.
            write('"/>\n        <id>')
            __v = VFFSL(SL,"entry.id",True)
            if __v is not None: write(filter(__v, rawExpr='$entry.id')) # from line 19, col 13.
            write('</id>\n        <updated>')
            __v = VFN(VFFSL(SL,"entry.updated",True),"strftime",False)('%Y-%m-%dT%H:%M:%SZ')
            if __v is not None: write(filter(__v, rawExpr="$entry.updated.strftime('%Y-%m-%dT%H:%M:%SZ')")) # from line 20, col 18.
            write('</updated>\n        <content type="html">')
            __v = VFFSL(SL,"escape",False)(VFFSL(SL,"entry.content.content",True))
            if __v is not None: write(filter(__v, rawExpr='$escape($entry.content.content)')) # from line 21, col 30.
            write('''</content>
    </entry>

''')
        write('</feed>\n')
        
        ########################################
        ## END - generated method body
        
        return dummyTrans and trans.response().getvalue() or ""
        
    ##################################################
    ## GENERATED ATTRIBUTES


    __str__ = respond

    _mainCheetahMethod_for_atom= 'respond'


# CHEETAH was developed by Tavis Rudd, Mike Orr, Ian Bicking and Chuck Esterbrook;
# with code, advice and input from many other volunteers.
# For more information visit http://www.CheetahTemplate.org

##################################################
## if run from command line:
if __name__ == '__main__':
    atom().runAsMainProgram()

