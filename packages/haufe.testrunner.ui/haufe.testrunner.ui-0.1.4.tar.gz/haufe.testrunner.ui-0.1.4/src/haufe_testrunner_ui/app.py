############################################################################
# haufe.testrunner.ui - a Grok-based web-frontend to the haufe.testrunner db
# (C) 2008, Haufe Mediengruppe, Freiburg
# Author: Andreas Jung, ZOPYX Ltd. & Co. KG
############################################################################


from cStringIO import StringIO
import grok
from zope import schema
from zope.interface import Interface, implements

from sqlalchemy import *
from sqlalchemy.orm import scoped_session, sessionmaker, relation
from sqlalchemy.ext.declarative import declarative_base
from zope.sqlalchemy import ZopeTransactionExtension, invalidate
import transaction

from haufe.testrunner.database import model


class ManageTestrunnerUI(grok.Permission):
    grok.name('haufe.testrunnerui.manage')


class ITestrunnerUI(Interface):
    dsn = schema.TextLine(title=u'DSN of Zope testrunner database', required=True)
    title = schema.TextLine(title=u'Title', required=True)


class haufe_testrunner_ui(grok.Application,grok.Model):
    implements(ITestrunnerUI)

    dsn = 'postgres://testrunner:testrunner@10.11.1.161/ZopeTestrunner'
    title = u'Haufe Testrunner'

    _v_engine = None
    _v_session = None
    _v_mappers = None

    @property
    def mappers(self):
        if self._v_mappers is None:
            Base, mappers = model.getModel(self._v_engine)
            self._v_mappers = dict(TestRunner=mappers[0],
                                   Run=mappers[1],
                                   Result=mappers[2])
        return self._v_mappers


    @property
    def engine(self):
        if self._v_engine is None:
            self._v_engine = create_engine(self.dsn, convert_unicode=True)
        return self._v_engine

    @property
    def session(self):
        if self._v_session is None:
            self._v_session = scoped_session(sessionmaker(bind=self.engine,
                                                          twophase=True,
                                                          autocommit=True,
                                                          autoflush=True,
                                                          extension=ZopeTransactionExtension()))
        return self._v_session()



class EditForm(grok.EditForm):
    """ Edit form """

    grok.name('edit')
    grok.require('haufe.testrunnerui.manage')
    form_fields = grok.AutoFields(ITestrunnerUI)

    @grok.action('Apply changes')
    def applyChanges(self, **data):
        self.applyData(self.context, **data)
        self.redirect(self.url(self.context))

    @grok.action('Cancel')
    def returnToIndex(self, **data):
        self.redirect(self.url(self.context))


class Index(grok.View):

    def getTestrunners(self):
        session = self.context.session
        TR = self.context.mappers.get('TestRunner')
        rows = session.query(TR).order_by(TR.name).all()
        return rows


class ShowRuns(grok.View):

    def getTestrunner(self):
        session = self.context.session
        TR = self.context.mappers.get('TestRunner')
        return session.query(TR).filter_by(id=self.request['testrunner_id'])[0]


    def getRuns(self):
        lst = []
        session = self.context.session
        Run = self.context.mappers.get('Run')
        for row in session.query(Run).filter_by(testrunner_id=self.request['testrunner_id']).order_by(desc('created')):
            lst.append(row)
        return lst

class ShowResults(ShowRuns):

    
    def getResults(self):
        lst = []
        session = self.context.session
        Result = self.context.mappers.get('Result')
        for row in session.query(Result).filter_by(run_id=self.request['run_id']).order_by(asc('module')):
            lst.append(row)
        return lst

    def getRun(self):
        session = self.context.session
        Run = self.context.mappers.get('Run')
        return session.query(Run).filter_by(id=self.request['run_id'])[0]


class ShowResultLog(ShowRuns):

    def getResult(self):
        lst = []
        session = self.context.session
        Result = self.context.mappers.get('Result')
        return session.query(Result).filter_by(id=self.request['result_id']).one()

    def getRun(self):
        session = self.context.session
        Run = self.context.mappers.get('Run')
        return session.query(Run).filter_by(id=self.request['run_id'])[0]


class RSS(grok.View):

    grok.name('rss')
    grok.context(haufe_testrunner_ui)

    def getTestrunner(self):
        session = self.context.session
        TR = self.context.mappers.get('TestRunner')
        return session.query(TR).filter_by(id=self.request['testrunner_id'])[0]


    def getRuns(self):
        lst = []
        session = self.context.session
        Run = self.context.mappers.get('Run')
        for row in session.query(Run).filter_by(testrunner_id==self.request['testrunner_id'],
                                                  order_by=desc(Run.c.created)):
            lst.append(row)
        return lst


    def render(self):

        xml = StringIO()
        TR = self.getTestrunner()

        xml.write('<?xml version="1.0" encoding="iso-8859-15"?>\n')
        xml.write('<rss version="0.91">\n')
        xml.write('  <channel>\n')
        xml.write('    <title>Testrunner -- %s</title>\n' % TR.name)
        xml.write('    <language>en</language>n')

        for run in self.getRuns():
            xml.write('      <item>\n')
            xml.write('        <title>Testrunner - %s - %s</title>\n' % (TR.name, run.created.strftime('%d.%m.%Y %H:%M:%S')))
            xml.write('        <link>%s/showresults?testrunner_id:int=%d&run_id:int=%d</link>\n' % (self.url(self.context), TR.id, run.id))
            xml.write('        <description><![CDATA[%s]]></description>\n' % run.description)
            xml.write('      </item>\n')

        xml.write('  </channel>\n')
        xml.write('</rss>\n')

        self.response.setHeader('content-type', 'application/rss+xml')
        return xml.getvalue()

class Master(grok.View):
    """ The master page template macro """
    # register this view for all objects
    grok.context(haufe_testrunner_ui)
