# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: base.py 319 2008-06-30 22:00:08Z esmenttes $
#
# end: Platecom header
"""Test setup for integration and functional tests.

When we import PloneTestCase and then call setupPloneSite(), all of
Plone's products are loaded, and a Plone site will be created. This
happens at module level, which makes it faster to run each test, but
slows down test runner startup.
"""
import os, sys
from App import Common

from Products.Five import zcml
from Products.Five import fiveconfigure

from Testing import ZopeTestCase as ztc

from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

from icnews.acquire.config import *

import icnews.acquire
from icsemantic.langfallback.tests import utils

test_home = os.path.dirname(__file__)

if not HAS_PLONE3:
    ztc.installProduct('PloneLanguageTool')

ztc.installProduct('LinguaPlone')

#
# When ZopeTestCase configures Zope, it will *not* auto-load products
# in Products/. Instead, we have to use a statement such as:
#
#   ztc.installProduct('SimpleAttachment')
#
# This does *not* apply to products in eggs and Python packages (i.e.
# not in the Products.*) namespace. For that, see below.
#
# All of Plone's products are already set up by PloneTestCase.
#

@onsetup
def setup_icnews_adqnews():
    fiveconfigure.debug_mode = True
    zcml.load_config('configure.zcml', icnews.acquire)
    fiveconfigure.debug_mode = False

    # XXX monkey patch everytime (until we figure out the problem where
    # monkeypatch gets overwritten somewhere)
    try:
        from Products.Five import pythonproducts
        pythonproducts.setupPythonProducts(None)

        # MONKEYPATCH: arregla los problemas con el
        # control panel y la instalacion de Five...
        import App
        App.ApplicationManager.ApplicationManager.Five=utils.Five

        # MONKEYPATCH: arregla los problemas con el
        # HTTP_REFERER en los tests funcionales. Tiene la
        # contra de enviarnos al raiz del plone cada vez
        # que un metodo depende de esa variable, pero es
        # mejor que morir con una excepcion o llenar los
        # tests de try blocks...
        ztc.zopedoctest.functional.http=utils.http

    except ImportError:
        # Not needed in Plone 3
        ztc.installPackage('icsemantic.core')
        ztc.installPackage('icnews.core')
        #ztc.installPackage('icsemantic.thesaurus')
        ztc.installPackage(PROJECTNAME)

setup_icnews_adqnews()

ptc.setupPloneSite(products=[PROJECTNAME,])


class ICNewsAcquireTestCase(ptc.PloneTestCase):
    """We use this base class for all the tests in this package. If
    necessary, we can put common utility or setup code in here. This
    applies to unit test cases.
    """

class ICNewsAcquireFunctionalTestCase(ptc.FunctionalTestCase):
    """We use this class for functional integration tests that use
    doctest syntax. Again, we can put basic common utility or setup
    code in here.
    """

