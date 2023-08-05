### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Juncton Base class for the Zope 3 based zcmljunction package

$Id: junction.py 12647 2007-11-04 04:16:03Z cray $
"""
__author__  = "Andrey Orlov, 2007 02 20"
__license__ = "GPL"
__version__ = "$Revision: 12647 $"
__date__ = "$Date: 2007-11-04 07:16:03 +0300 (Вск, 04 Ноя 2007) $"
 
from zope.interface import Interface
from zope.interface import implements,implementedBy
                
class Junction(object) :

    def __init__(self,ob) :
        self.ob = ob
        for key,(values,default) in self._declaration.items() :
            
            ln = len(values)
            if  1 < ln :
                setattr(self,key,"\n".join([y for y in [self.getvalue(x,default) for x in values] if type(y) is unicode]))
            elif 1 == ln :
                setattr(self,key,self.getvalue(values[0],default))
            else :
                setattr(self,key)
                
    def getvalue(self,name,default="") :
        try :
            res= getattr(self,name)
        except AttributeError :
            try :
                res = getattr(self.ob,name)
            except AttributeError :
                res =  default
        return res                