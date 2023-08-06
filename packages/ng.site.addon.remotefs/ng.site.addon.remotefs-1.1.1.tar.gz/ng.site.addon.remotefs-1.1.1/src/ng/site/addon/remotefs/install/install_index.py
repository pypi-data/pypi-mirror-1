### -*- coding: utf-8 -*- #############################################
#######################################################################
"""InstallIndex script for the Zope 3 based ng.site.addon.remotefs package

$Id: install_index.py 51204 2008-06-26 14:42:28Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51204 $"

from zope.app.catalog.interfaces import ICatalog

from zope.app.catalog.field import FieldIndex
from ng.app.remotefs.interfaces import IRemoteObject
from zope.app.zapi import getUtilitiesFor

def installIndex(context, **kw):
    """ Install Catalog and all indexes that them need """

    for name, ob in getUtilitiesFor(ICatalog,context) :
        ob['path'] = FieldIndex(field_name=u'path', interface=IRemoteObject, field_callable=False)
        ob['prefix'] = FieldIndex(field_name=u'prefix', interface=IRemoteObject, field_callable=False)

    return "Success"
