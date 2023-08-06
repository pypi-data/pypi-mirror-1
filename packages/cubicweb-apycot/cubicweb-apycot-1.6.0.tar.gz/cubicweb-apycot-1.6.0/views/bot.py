"""this module contains views related to bot status and activity

:organization: Logilab
:copyright: 2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
:license: General Public License version 2 - http://www.gnu.org/licenses
"""
__docformat__ = "restructuredtext en"

from logilab.common.tasksqueue import REVERSE_PRIORITY
from logilab.mtconverter import xml_escape

from cubicweb import UnknownEid
from cubicweb.selectors import match_kwargs
from cubicweb.view import StartupView, View

from cubes.apycot.entities import bot_proxy

class ApycotHelpView(StartupView):
    id = 'apycotdoc'

    def page_title(self):
        return self.req._('apycot documentation')

    def call(self):
        _ = self.req._
        self.w(u'<h1>%s</h1>' % self.page_title())
        bot = bot_proxy(self.config, self.req.data)
        self.w(u'<p>%s</p>' % _(
            'First notice that you may miss some information if you\'re using '
            'some plugin not loaded by the apycot bot.'))
        self.section('checkers')
        headers = [_('checker'), _('need preprocessor'), _('description')]
        data = [(defdict['id'], defdict['preprocessor'], xml_escape(defdict['help']))
                 for defdict in bot.available_checkers()]
        self.wview('pyvaltable', pyvalue=data, headers=headers)
        self.section('preprocessors')
        headers = [_('preprocessor'), _('description')]
        data = [(defdict['id'], xml_escape(defdict['help']))
                 for defdict in bot.available_preprocessors()]
        self.wview('pyvaltable', pyvalue=data, headers=headers)
        self.section('options')
        headers = [_('option'), _('required'), _('type'), _('description')]
        data = [(defdict.get('id', defdict['name']),
                 defdict.get('required') and _('yes') or _('no'),
                 defdict['type'], xml_escape(defdict['help']))
                 for defdict in bot.available_options()]
        self.wview('pyvaltable', pyvalue=data, headers=headers)

    def section(self, name):
        self.w(u'<h2>%s</h2><a name="%s"/>' % (self.req._(name), name))


class BotStatusView(StartupView):
    """This view displays pending and running tasks when the bot is
       available, otherwise displays error message explaining why
       the bot is unavailable.
    """
    id = 'botstatus'
    title = _('Apycot bot status')

    def call(self):
        _ = self.req._
        # bot availability
        if not 'vtitle' in self.req.form:
            self.w(u'<h1>%s</h1>' % _(self.title))
        try:
            bot = bot_proxy(self.config, self.req.data)
            pending, running = bot.pending_tasks()
        except Exception, ex:
            msg = _(u'Bot is not available for the following reason:')
            self.w(u'<p>%s %s</p>' % (msg, ex))
            return
        self.w(u'<p>%s</p>' % _('Bot is up and available.'))
        # pending and running tasks
        headers = [_('TestConfig'), _('priority'), _('vcs_branch')]
        self.w(u'<h2>%s</h2>' % _('Pending tasks'))
        if pending:
            self.wview('pyvaltable',
                       pyvalue=table_from_tasks(self.req, pending),
                       headers=headers)
        else:
            self.w(u'<p>%s</p>' % _(u'No pending task'))
        self.w(u'<h2>%s</h2>' % _('Running tasks'))
        if running:
            self.wview('pyvaltable',
                       pyvalue=table_from_tasks(self.req, running),
                       headers=headers)
        else:
            self.w(u'<p>%s</p>' % _(u'No running task'))


def table_from_tasks(req, tdicts):
    data = []
    for tdict in tdicts:
        try:
            # don't specify etype so we detect if entity has been deleted
            tc = req.entity_from_eid(tdict['eid'])
        except UnknownEid:
            continue
        data.append( (tc.view('outofcontext'),
                      # XXX sortvalue
                      req._(REVERSE_PRIORITY[tdict['priority']]),
                      xml_escape(tdict['branch'] or u''))
                     )
    return data


