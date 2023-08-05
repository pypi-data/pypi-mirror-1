### -*- coding: utf-8 -*- #############################################
#######################################################################
"""ZCML Reference directive handler

$Id: metaconfigure.py 12647 2007-11-04 04:16:03Z cray $
"""
__author__  = "Andrey Orlov, 2007-02-20"
__license__ = "GPL" 
__version__ = "$Revision: 12647 $"
__date__ = "$Date: 2007-11-04 07:16:03 +0300 (Вск, 04 Ноя 2007) $"

from junction import Junction
from zope.component.zcml import adapter

metaconfigure = vars()
 
class JunctionDirective(object) :

    def __init__(self,_context, factory=[], classname=None, **kw) :
        self._context = _context
        if classname :
            classname = str(classname)
            self.factory =  metaconfigure[classname] = type(classname,tuple(factory)+(Junction,),{'_declaration' : {}})
        else :
            self.factory = type('Junction',tuple(factory)+(Junction,),{'_declaration' : {}})            
        self.kw = kw
        
    def property(self, _context, in_, out, default="") :
        self.factory._declaration[out] = (in_,default)
        
    def __call__(self) :
        adapter(self._context,
            factory = [self.factory],
            **self.kw
        )
