# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: config.py 319 2008-06-30 22:00:08Z esmenttes $
#
# end: Platecom header
import icnews.acquire

GLOBALS = globals()
try:
    import Products.CMFPlone.migrations.v3_0
    HAS_PLONE3 = True
except ImportError:
    HAS_PLONE3 = False

PROJECTNAME = 'icnews.acquire'
#PACKAGE = icnews.acquire
PACKAGENAME = 'icnews.acquire'
# TODO: remove this dependencies. The only thing needed from
# icsemantic.thesaurus is the icsemantic.core.encodings vocabulary.
# iccommunity.core is included here to have a place where to put the
# sql configlet.
DEPENDENCIES = ['icsemantic.thesaurus', 'icnews.core']
DEFAULT_ADD_CONTENT_PERMISSION = 'Add portal content'