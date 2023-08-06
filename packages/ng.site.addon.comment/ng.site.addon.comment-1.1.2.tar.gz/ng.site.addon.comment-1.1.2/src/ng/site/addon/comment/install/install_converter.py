### -*- coding: utf-8 -*- #############################################
#######################################################################
"""installConverter and installMapper scripts for the Zope 3 based
ng.site.content.install package

$Id: product.py 49265 2008-01-08 12:18:26Z cray $
"""
__author__  = "Yegor Shershnev, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49265 $"


from zope.app.folder.folder import Folder

from zope.app.component.hooks import setSite
from zope.app.component import site
from zope.app.component.site import SiteManagementFolder

from ng.app.converter.mapper.mapperobject.mapperobject import MapperObject
from ng.app.converter.mapper.mapperobject.interfaces import IMapperObject
from ng.app.converter.mapper.mapperinterface.mapperinterface import MapperInterface
from ng.app.converter.mapper.mapperattribute.mapperattribute import MapperAttribute
from ng.app.converter.mapper.mapperattributeitem.mapperattributeitem import MapperAttributeItem


def install_Mapper(context, **kw):
    """ Устанавливает MapperObject со всеми его внутренностями
    """

    sm = context.getSiteManager()

    mo = sm['converter'][u'MapperObject'] 

    sm.registerUtility(mo, provided=IMapperObject)

    names = (
     [u'ng.content.comment.interfaces.IComment',
      u'ng.app.converter.object2psadapter.interfaces.IPropertySheet',
      {
       u'abstract': (u'abstract',u'converter:LightReST+WIKI'),
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
