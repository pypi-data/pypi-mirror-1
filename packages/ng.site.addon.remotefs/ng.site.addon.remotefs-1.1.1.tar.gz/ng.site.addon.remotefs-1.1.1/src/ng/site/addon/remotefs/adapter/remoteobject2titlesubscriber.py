### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Product class for the Zope 3 based product package

$Id: remoteobject2titlesubscriber.py 51204 2008-06-26 14:42:28Z cray $
"""
__author__  = "Andrey Orlov, 2007"
__license__ = "GPL"
__version__ = "$Revision: 51204 $"

from zope.component import adapts
from ng.app.remotefs.interfaces import IRemoteObject
from ng.adapter.ianytitle.anytitlesubscriberbase import AnyTitleSubscriberBase

class RemoteObject2TitleSubscriber(AnyTitleSubscriberBase) :

    adapts(IRemoteObject)
    order = 2
        
    @property
    def title(self) :
        return IRemoteObject(self.context).title or u""
