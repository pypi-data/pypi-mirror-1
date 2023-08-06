# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: mailman.py 235 2008-06-10 20:21:40Z crocha $
#
# end: Platecom header
"""Definition of the Adqnews content type.
"""
import datetime
import re
import urllib

import MySQLdb

from zope.component import queryUtility, getUtility
from zope.interface import implements, implementer
from zope.component import adapts, adapter
from zope.app.schema.vocabulary import IVocabularyFactory

from Products.CMFCore.utils import getToolByName
from Products.Archetypes import atapi
from Products.ATContentTypes.content.base import ATCTContent, registerATCT
from Products.ATContentTypes.content.schemata import ATContentTypeSchema

from icnews.acquire.interfaces import IAdqnews, IAdqnewsDB, INewsFromURL, \
    IicNewsManagementAcquireSQLServer
from icnews.acquire.config import PROJECTNAME
from icnews.acquire import ICNewsAquireMessageFactory as _

import logging
logger = logging.getLogger('icnews.acquire')

AdqnewsSchema = atapi.BaseSchema.copy() + atapi.Schema((
    atapi.StringField('source',
        required=True,
        default='',
        validators=('isURL',),
        widget=atapi.StringWidget(
            label_msgid='label_adqnews_source',
            label='Source',
            description_msgid='help_adqnews_source',
            description='A URL from where to acquire news.')
    ),
    atapi.StringField('re',
        required=False,
        default='',
        widget=atapi.LinesWidget(
            label_msgid='label_adqnews_re',
            label='Regular Expresion',
            description_msgid='help_adqnews_re',
            description='A regular expresion to parse the web page.')
    ),
    atapi.StringField('encoding',
        required=True,
        default='',
        vocabulary='encodings_vocabulary',
        widget=atapi.SelectionWidget(
            label="Encoding",
            label_msgid='label_adqnews_encoding',
            description_msgid='help_adqnews_encoding',
            description='The encoding of the source page.')
    ),
    atapi.BooleanField('store',
        default=False,
        widget=atapi.BooleanWidget(
            label="Store in relational database?",
            label_msgid='label_adqnews_store',
            description_msgid='help_adqnews_store',
            description='Check this box if you want the acquired news to be '
                        'stored in a relational database.')
    ),
))

AdqnewsSchema['description'].schemata = 'default'


class Adqnews(ATCTContent):
    """Implementation of the Adqnews type"""
    implements(IAdqnews)

    portal_type = "Adqnews"
    _at_rename_after_creation = True
    schema = AdqnewsSchema

    #source = atapi.ATFieldProperty('source')
    #re = atapi.ATFieldProperty('re')

    def encodings_vocabulary(self):
        """Just a wrapper for the encodings vocabulary in
        icsemantic.thesaurus
        """
        vocab = queryUtility(IVocabularyFactory,
                             name=u'icsemantic.core.encodings')
        simple_vocab = [(i.token, i.title) for i in
                        vocab(None)]
        return atapi.DisplayList(simple_vocab)

registerATCT(Adqnews, PROJECTNAME)


class AdqnewsDB:
    """An adapter for Adqnews that takes care of the DB backend"""

    adapts(IAdqnews)
    implements(IAdqnewsDB)

    def __init__(self, context):
        """Connect to the DB"""
        self.context = context
        settings = getUtility(IicNewsManagementAcquireSQLServer,
                              name='icnews.configuration',
                              context=context)

        try:
            db = MySQLdb.connect(host=settings.hostname,
                                 user=settings.username,
                                 passwd=settings.password,
                                 db=settings.database)
        except Exception, m:
            self.db = None
            logger.info("Couldn't connect to database. " + str(m))
            return

        self.db = db
        self.cursor = db.cursor()

    def store(self):
        """Store the news items in the DB"""
        if self.db is None:
            logger.info("There is no database conection.")
            return []

        insert = 'INSERT INTO acquire VALUES (%(values)s) ;'

        news = INewsFromURL(self.context)

        today = datetime.date.today()
        for item in news:
            values = ", ".join((
                self.db.literal('/'.join(self.context.getPhysicalPath())),
                self.db.literal(item['link']),
                self.db.literal(item['title']),
                self.db.literal(item['description']),
                self.db.literal(str(today))))
            query = insert % {'values': values}
            try:
                self.cursor.execute(query)
            except Exception,  m:
                logger.info("Values: " + values + " couldn't be inserted in " 
                            "the DB. " + str(m))
        return news

    def retrieve(self, date):
        """Retrieve news items from the DB matcing a specific date"""
        if self.db is None:
            logger.info("There is no database conection.")
            return []

        today = datetime.date.today()
        select = 'SELECT * FROM acquire WHERE DATE(date) = %(today)s AND ' \
                 'path = %(path)s;'
        query = select % {'today': self.db.literal(today), \
            'path': self.db.literal('/'.join(self.context.getPhysicalPath()))}

        try:
            self.cursor.execute(query)
        except Exception, m:
            logger.info("Couldn't execute query. " + str(m))
            return []

        results = self.cursor.fetchall()
        return [{'path': i[0], 'link': i[1], 'title': i[2], 'description': i[3],
                'date': i[4]} for i in results]


@adapter(IAdqnews)
@implementer(INewsFromURL)
def url2news(context):
    """Return a list of dictionaries of the form
    {'title': t, 'description': d, 'link': l} from a URL.
    """
    link = context.getSource()
    regexp = "".join(context.getRe())

    f=urllib.urlopen(link)
    s=''.join(f.readlines())

    o_rss = re.compile(regexp, re.S)

    r = o_rss.finditer(s)

    return [i.groupdict() for i in r]

