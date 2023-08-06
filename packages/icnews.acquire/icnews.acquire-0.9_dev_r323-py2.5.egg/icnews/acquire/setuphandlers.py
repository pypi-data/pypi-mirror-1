""" icnews.acquire setup handlers.
"""
import interfaces
from preferences import icNewsManagementAcquireSQLServer
from config import HAS_PLONE3
from config import DEPENDENCIES

import transaction

def setup_site(context):
    """Site setup"""
    sm = context.getSiteManager()

    if not sm.queryUtility(interfaces.IicNewsManagementAcquireSQLServer,
                           name='icnews.configuration'):
        if HAS_PLONE3:
            sm.registerUtility(icNewsManagementAcquireSQLServer(),
                               interfaces.IicNewsManagementAcquireSQLServer,
                               'icnews.configuration')
        else:
            sm.registerUtility(interfaces.IicNewsManagementAcquireSQLServer,
                               icNewsManagementAcquireSQLServer(),
                               'icnews.configuration')


def setup_various(context):
  """Import various settings.

  This provisional handler will be removed again as soon as full handlers
  are implemented for these steps.
  """
  site = context.getSite()
  setup_site(site)

