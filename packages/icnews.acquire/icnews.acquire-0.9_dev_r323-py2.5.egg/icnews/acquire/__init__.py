# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: __init__.py 252 2008-06-12 01:18:58Z esmenttes $
#
# end: Platecom header

from AccessControl import ModuleSecurityInfo
from zope.i18nmessageid import MessageFactory

from Products.Archetypes import atapi
from Products.CMFCore import utils

from icnews.acquire import config

ICNewsAquireMessageFactory = MessageFactory('icnews.acquire')
ModuleSecurityInfo('icnews.acquire').declarePublic('ICNewsAquireMessageFactory')

def initialize(context):
    """Initializer called when used as a Zope 2 product."""
    from content import adqnews

    content_types, constructors, ftis = atapi.process_types(
        atapi.listTypes(config.PROJECTNAME),
        config.PROJECTNAME)

    utils.ContentInit(
        config.PROJECTNAME + ' Content',
        content_types      = content_types,
        permission         = config.DEFAULT_ADD_CONTENT_PERMISSION,
        extra_constructors = constructors,
        fti                = ftis,
        ).initialize(context)

    #for atype, constructor in zip(content_types, constructors):
        #utils.ContentInit("%s: %s" % (config.PROJECTNAME, atype.portal_type),
            #content_types = (atype,),
            #permission = config.DEFAULT_ADD_CONTENT_PERMISSION,
            #extra_constructors = (constructor,),
            #).initialize(context)