"""Defines the RSS2 views
"""
import sys
import datetime
import urlparse

from Acquisition import aq_inner
from zope.component import getUtility
from Products.Five.browser import BrowserView

from icnews.acquire.interfaces import IAdqnewsDB, INewsFromURL
from icnews.acquire.interfaces import IicNewsManagementAcquireSQLServer

class BaseRSS2View(BrowserView):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def rss2(self, news):
        """Genera un contenido rss a partir de una url y una expresión
        regular. La expresión regular (regexp) debe tener grupos de
        matching nombrados como:
        title: titulo de la noticia.
        link: url que nos lleva a la noticia
        description: descripción de la noticia.

        El title (titulo) de la función corresponde al titulo del canal
        rss de donde se saco la noticia. También hay que definir la url
        (link) de la página a parsear, y una descripción del canal
        (description). Muchas páginas no tienen definido la
        codificación de los caracteres (encoding), con lo que es
        recomendable asigarnle uno.
        """

        context = aq_inner(self.context)
        title = context.Title()
        link = context.getSource()
        description = context.Description()
        encoding = context.getEncoding()
        l = news
        s = """\
<?xml version="1.0" encoding="%s"?>
<rss version="2.0">
  <channel>
    <title>%s</title>
    <link>%s</link>
    <description>%s</description>
""" % (encoding, unicode(title, sys.stdin.encoding),
       unicode(link, sys.stdin.encoding),
       unicode(description, sys.stdin.encoding))
        for si in l:
            if 'title' in si and si['title']:
                s += "  <item>\n"
                s += "     <title>%s</title>\n" % si['title'].decode(encoding)
                if 'link' in si and si['link']:
                    s += "     <link>%s</link>\n" % urlparse.urljoin(link, si['link'])
                if 'description' in si and si['description']:
                    s += "     <description>%s</description>\n" % si['description'].decode(encoding)
                s += "  </item>\n"
        s += """
  </channel>
</rss>"""

        return s


class RSS2View(BaseRSS2View):
    """RSS2 view generated on the fly"""

    def __call__(self):
        """Use the RSS2 adapter to return the RSS2"""
        response = self.request.response
        response.setHeader('Content-Type', 'text/xml')

        if self.context.getStore():
            dba = IAdqnewsDB(self.context)
            news = dba.store()
        else:
            news = INewsFromURL(self.context)

        return self.rss2(news)


class StoredNews(BaseRSS2View):
    """RSS2 view generated from the DB"""

    def __call__(self):
        """Use the RSS2 adapter to return the RSS2 from DB"""
        response = self.request.response
        response.setHeader('Content-Type', 'text/xml')
        dba = IAdqnewsDB(self.context)
        news = dba.retrieve(datetime.date.today())
        return self.rss2(news)
