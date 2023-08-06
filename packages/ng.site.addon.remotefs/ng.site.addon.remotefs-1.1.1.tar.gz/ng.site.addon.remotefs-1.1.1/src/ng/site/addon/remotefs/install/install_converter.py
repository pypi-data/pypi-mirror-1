### -*- coding: utf-8 -*- #############################################
#######################################################################
"""installMapper scripts for the Zope 3 based
ng.site.addon.remotefs package

$Id: product.py 49265 2008-01-08 12:18:26Z cray $
"""
__author__  = "Yegor Shershnev, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49265 $"


from zope.app.zapi import getUtility

from ng.app.converter.mapper.mapperobject.mapperobject import MapperObject
from ng.app.converter.mapper.mapperobject.interfaces import IMapperObject
from ng.app.converter.mapper.mapperinterface.mapperinterface import MapperInterface
from ng.app.converter.mapper.mapperattribute.mapperattribute import MapperAttribute
from ng.app.converter.mapper.mapperattributeitem.mapperattributeitem import MapperAttributeItem


def installMapper(context, **kw):
    """ Устанавливает MapperObject со всеми его внутренностями
    """

    mo = getUtility(IMapperObject,context=context) 

    names = (
       [u'ng.app.remotefs.remotecontainer.interfaces.IRemoteContainer',
        u'ng.app.converter.object2psadapter.interfaces.IPropertySheet',
        {
         u'title': (u'title',u'reference'),
       }],
    )
    
    for i in range(len(names)):
        mo[names[i][0]] = MapperInterface()
        mo[names[i][0]][names[i][1]] = MapperAttribute()
        for j in names[i][2].keys():
            mai = mo[names[i][0]][names[i][1]][j] = MapperAttributeItem()
            mai.attr = names[i][2][j][0]
            mai.converter = names[i][2][j][1]
    
    return "Success"
