"""Package interfaces
"""

from zope.interface import Interface
from zope import schema

from icnews.acquire import ICNewsAquireMessageFactory as _


class IAdqnews(Interface):
    """Acquire news content type"""

    title = schema.TextLine(title=_('Title'), required=True)
    description = schema.Text(title=_('Description'), required=True)
    source = schema.URI(title=_(u"Source"), required=True)
    re = schema.Text(title=_(u'Regular Expresion'))
    encoding = schema.BytesLine(title=_('Encoding'))
    store = schema.Bool(title=_('Store in relational database?'))


class IAdqnewsDB(Interface):
    """Handle the DB aspect of Adqnews"""

    def store():
        """Store the news items in the DB"""

    def retrieve(date):
        """Retrieve news items from the DB matcing a specific date"""


class INewsFromURL(Interface):
    """Get news from URL"""


class IicNewsManagementAcquireSQLServer(Interface):
    """An interface for the SQL server configuration"""
    hostname = schema.DottedName(title=_(u"Host name"),
                                description=_(u"The database host name"),
                                default="localhost",
                                required=True)

    username = schema.ASCIILine(title=_(u"User name"),
                                description=_(u"The database user name"),
                                default="",
                                required=True)

    password = schema.Password(title=_(u"Password"),
                                description=_(u"The database password"),
                                required=True)

    database = schema.ASCIILine(title=_(u"Database name"),
                                description=_(u"The database name"),
                                default="",
                                required=True)

    dbprefix = schema.ASCIILine(title=_(u"Names prefix"),
                                description=_(u"The prefix of table names"),
                                default="",
                                required=False)