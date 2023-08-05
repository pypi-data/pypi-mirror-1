#!/usr/bin/env python




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
__CHEETAH_docstring__ = 'Autogenerated by CHEETAH: The Python-Powered Template Engine'
__CHEETAH_genTime__ = 'Sun Jan 15 20:47:52 2006'
__CHEETAH_version__ = '2.0rc2'

##################################################
## CLASSES

class DynamicallyCompiledCheetahTemplate(Template):

    ##################################################
    ## CHEETAH GENERATED METHODS


    def __init__(self, *args, **KWs):

        Template.__init__(self, *args, **KWs)
        if not self._CHEETAH__instanceInitialized:
            cheetahKWArgs = {}
            allowedKWs = 'searchList namespaces filter filtersLib errorCatcher'.split()
            for k,v in KWs.items():
                if k in allowedKWs: cheetahKWArgs[k] = v
            self._initCheetahInstance(**cheetahKWArgs)


    def respond(self, trans=None):



        ## CHEETAH: main method generated for this template
        if (not trans and not self._CHEETAH__isBuffering and not callable(self.transaction)):
            trans = self.transaction # is None unless self.awake() was called
        if not trans:
            trans = DummyTransaction()
            _dummyTrans = True
        else: _dummyTrans = False
        write = trans.response().write
        SL = self._CHEETAH__searchList
        _filter = self._CHEETAH__currentFilter

        ########################################
        ## START - generated method body


        ## START CACHE REGION: _34823658. line, col (2, 1) in the source.
        _RECACHE_34823658 = False
        _cacheRegion__34823658 = self.getCacheRegion(regionID='_34823658', cacheInfo={'interval': 9000.0, 'type': 2, 'ID': 'cache1'})
        if _cacheRegion__34823658.isNew(): _RECACHE_34823658 = True
        _cacheItem__34823658 = _cacheRegion__34823658.getCacheItem('_34823658')
        if (not _cacheItem__34823658.getRefreshTime()) or (currentTime() > _cacheItem__34823658.getRefreshTime()):
            _cacheItem__34823658.setRefreshTime(currentTime() +9000.0)
            _RECACHE_34823658 = True
        if _RECACHE_34823658 or not _cacheItem__34823658.hasData():
            _orig_trans_34823658 = trans
            trans = _cacheCollector__34823658 = DummyTransaction()
            write = _cacheCollector__34823658.response().write
            _v = VFFSL(SL,"anInt",True) # '$anInt' on line 3, col 1
            if _v is not None: write(_filter(_v, rawExpr='$anInt')) # from line 3, col 1.
            write('\n')
            trans = _orig_trans_34823658
            write = trans.response().write
            _cacheItem__34823658.setData(_cacheCollector__34823658.response().getvalue())
            del _cacheCollector__34823658
        write(_cacheItem__34823658.getOutput())
        ## END CACHE REGION: _34823658


        ## START CACHE REGION: cache2. line, col (5, 1) in the source.
        _RECACHEcache2 = False
        _cacheRegion_cache2 = self.getCacheRegion(regionID='cache2', cacheInfo={'interval': 15.0, 'type': 2, 'id': 'cache2'})
        if _cacheRegion_cache2.isNew(): _RECACHEcache2 = True
        _cacheItem_cache2 = _cacheRegion_cache2.getCacheItem('cache2')
        if (not _cacheItem_cache2.getRefreshTime()) or (currentTime() > _cacheItem_cache2.getRefreshTime()):
            _cacheItem_cache2.setRefreshTime(currentTime() +15.0)
            _RECACHEcache2 = True
        if _RECACHEcache2 or not _cacheItem_cache2.hasData():
            _orig_transcache2 = trans
            trans = _cacheCollector_cache2 = DummyTransaction()
            write = _cacheCollector_cache2.response().write
            for i in range(5):
                _v = VFFSL(SL,"i",True) # '$i' on line 7, col 1
                if _v is not None: write(_filter(_v, rawExpr='$i')) # from line 7, col 1.
            trans = _orig_transcache2
            write = trans.response().write
            _cacheItem_cache2.setData(_cacheCollector_cache2.response().getvalue())
            del _cacheCollector_cache2
        write(_cacheItem_cache2.getOutput())
        ## END CACHE REGION: cache2

        _v = VFFSL(SL,"aStr",True) # '$aStr' on line 10, col 1
        if _v is not None: write(_filter(_v, rawExpr='$aStr')) # from line 10, col 1.

        ########################################
        ## END - generated method body

        return _dummyTrans and trans.response().getvalue() or ""

    ##################################################
    ## CHEETAH GENERATED ATTRIBUTES


    _CHEETAH__instanceInitialized = False

    def __str__(self): return self.respond()

    _mainCheetahMethod_for_DynamicallyCompiledCheetahTemplate= 'respond'
if not hasattr(DynamicallyCompiledCheetahTemplate, '_initCheetahAttributes'):
    templateClass = getattr(DynamicallyCompiledCheetahTemplate, '_CHEETAH_templateClass', Template)
    templateClass._assignRequiredMethodsToClass(DynamicallyCompiledCheetahTemplate)


# CHEETAH was developed by Tavis Rudd and Mike Orr
# with code, advice and input from many other volunteers.
# For more information visit http://www.CheetahTemplate.org/

##################################################
## if run from command line:
if __name__ == '__main__':
    from Cheetah.TemplateCmdLineIface import CmdLineIface
    CmdLineIface(templateObj=DynamicallyCompiledCheetahTemplate()).run()

