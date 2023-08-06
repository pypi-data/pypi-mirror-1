
from Acquisition import aq_inner
from persistent import Persistent
from zope.interface import implements
from zope.component import getUtility
from OFS.SimpleItem import SimpleItem
from zope.schema.fieldproperty import FieldProperty

import interfaces


class icNewsManagementAcquireSQLServer(SimpleItem):
    implements(interfaces.IicNewsManagementAcquireSQLServer)

    hostname = FieldProperty(interfaces.IicNewsManagementAcquireSQLServer['hostname'])
    username = FieldProperty(interfaces.IicNewsManagementAcquireSQLServer['username'])
    password = FieldProperty(interfaces.IicNewsManagementAcquireSQLServer['password'])
    database = FieldProperty(interfaces.IicNewsManagementAcquireSQLServer['database'])
    dbprefix = FieldProperty(interfaces.IicNewsManagementAcquireSQLServer['dbprefix'])


def acquire_sql_server_adapter(context):
    return getUtility(interfaces.IicNewsManagementAcquireSQLServer,
                      name='icnews.configuration',
                      context=context)

