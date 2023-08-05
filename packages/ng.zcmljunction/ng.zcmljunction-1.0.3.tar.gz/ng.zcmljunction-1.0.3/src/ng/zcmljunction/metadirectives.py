### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interface of ZCML metadirective "junction"

$Id: metadirectives.py 12647 2007-11-04 04:16:03Z cray $
"""
__author__  = "Andrey Orlov, 2007 02 20"
__license__ = "GPL" 
__version__ = "$Revision: 12647 $"
__date__ = "$Date: 2007-11-04 07:16:03 +0300 (Вск, 04 Ноя 2007) $"
 
from zope.interface import Interface
from zope.component.zcml import IAdapterDirective
from zope.configuration.fields import Tokens, GlobalObject
from zope.schema import TextLine 

_ = lambda x : x

class IJunctionDirective(IAdapterDirective) :
        factory = Tokens(
            title=_(u"Adapter factory/factories"),
            description=_(u"A list of factories (usually just one) that create"
                           " the adapter instance."),
            required=False,
            value_type=GlobalObject()
        )

        classname = TextLine(
            title=_(u"ClassName"),
            required=False
            )

    
    
class IPropertySubdirective(Interface) :

    in_ = Tokens(
        title=_(u"Input Attributes"),
        description=_(u"This should be a list of interface attribute"),
        required=True,
        value_type=TextLine()
        )
    
    out = TextLine(
        title=_(u"Output Attributes"),
        description=_(u"This should be a list of interface attribute"),
        required=True
        )

    default = TextLine(
        title=_(u"Default Value"),
        description=_(u"Default value for this attribute"),
        required=False
        )
        