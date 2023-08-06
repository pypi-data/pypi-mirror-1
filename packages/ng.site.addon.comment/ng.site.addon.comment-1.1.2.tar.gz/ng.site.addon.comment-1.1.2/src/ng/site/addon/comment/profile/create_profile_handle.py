### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Creation handle used to treat profile for use with comment

$Id: create_profile_handle.py 52427 2009-01-31 16:37:41Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 52427 $"
 
from zope.interface import implements
from zope.interface import alsoProvides
from zope.app.securitypolicy.interfaces import IPrincipalPermissionManager

from zope.app.zapi import getUtility
from zope.app.container.interfaces import IContainer 

from ng.content.profile.profileannotation.interfaces import IProfileAnnotation

def create_profile_handle(ob,event) :
    root_perms = IPrincipalPermissionManager(getUtility(IContainer,name='Main'))
    
    root_perms.grantPermissionToPrincipal("dreambot.AddComment",IProfileAnnotation(ob).userid)

