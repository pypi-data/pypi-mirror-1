"""this module contains server side hooks for notification about test status
changes

:organization: Logilab
:copyright: 2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
:license: General Public License version 2 - http://www.gnu.org/licenses
"""
__docformat__ = "restructuredtext en"

from datetime import datetime

from cubicweb.selectors import implements
from cubicweb.common.uilib import text_cut
from cubicweb.server import hooksmanager, pool
from cubicweb.sobjects import notification

from cubes.vcsfile.entities import _MARKER
from cubes.apycot.entities import bot_proxy

# automatic test launching #####################################################

def start_test(session, period):
    tostart = set()
    rql = ('Any TC, PE, PEN, TCN, TCS '
           'WHERE TC use_environment PE, PE name PEN, '
           'TC start_mode %(sm)s, TC in_state S, S name "activated", '
           'TC name TCN, TC start_rev_deps TCS')
    for tc in session.execute(rql, {'sm': period}).entities():
        env = tc.environment
        if not env.repository:
            tostart.add((env.name, tc.name, tc.start_rev_deps, None))
        else:
            # XXX check every active branch if no branch specified
            branch = tc.apycot_configuration.get('branch', _MARKER)
            head = env.repository.branch_head(branch)
            if head is None:
                # No head found (in the case of branch specific test config)
                continue
            # only start test if this config hasn't been
            # executed against current branch head
            if session.execute(
                'Any TE WHERE TE using_revision REV, REV eid %(rev)s, '
                'TE using_config TC, TC eid %(tc)s',
                {'rev': head.eid, 'tc': tc.eid},
                ('rev', 'tc')):
                # This rev have already been tested
                continue
            tostart.add((env.name, tc.name, tc.start_rev_deps, head.branch))
    return tostart


class ServerStartupHook(hooksmanager.Hook):
    """add looping task to automatically start tests
    """
    events = ('server_startup',)
    def call(self, repo):
        # XXX use named args and inner functions to avoid referencing globals
        # which may cause reloading pb
        def check_test_to_start(repo, datetime=datetime, start_test=start_test,
                                StartTestsOp=StartTestsOp):
            now = datetime.now()
            tostart = set()
            session = repo.internal_session()
            try:
                # XXX only start task for environment which have changed in the
                # given interval
                tostart |= start_test(session, 'hourly')
                if now.hour == 1:
                    tostart |= start_test(session, 'daily')
                if now.isoweekday() == 1:
                    tostart |= start_test(session, 'weekly')
                if now.day == 1:
                    tostart |= start_test(session, 'monthly')
                if tostart:
                    StartTestsOp(session, tostart)
                session.commit()
            finally:
                session.close()
        repo.looping_task(60*60, check_test_to_start, repo)


class StartTestAfterAddVersionContent(hooksmanager.Hook):
    events = ('after_add_entity',)
    accepts = ('Revision',)

    def call(self, session, entity):
        vcsrepo = entity.repository
        for pe in vcsrepo.reverse_local_repository:
            if not pe.vcs_path:
                StartTestsOp(session, set(
                    (pe.name, tc.name, tc.start_rev_deps, entity.branch)
                    for tc in pe.reverse_use_environment
                    if tc.start_mode == 'on new revision'
                    and tc.match_branch(entity.branch)))
            else:
                StartTestsIfMatchOp(session, revision=entity, pe=pe)


class StartTestsIfMatchOp(pool.PreCommitOperation):

    def precommit_event(self):
        rql = ('Any TC, PE, PEN, TCN, TCS WHERE TC use_environment PE, REV eid %(rev)s,'
               'PE name PEN, PE eid %(pe)s, PE vcs_path PEP, TC name TCN, '
               'TC start_rev_deps TCS, '
               'TC start_mode %(sm)s, TC in_state S, S name "activated", '
               'VC from_revision REV, '
               'VC content_for VF, VF directory ~= PEP + "%"'
               )
        rset = self.session.execute(rql, {'sm': 'on new revision',
                                          'rev': self.revision.eid,
                                          'pe': self.pe.eid}, ('rev', 'pe'))
        if rset:
            branch = self.revision.branch
            testconfigs = set((row[2], row[3], row[4], self.revision.branch)
                               for i, row in enumerate(rset)
                               if rset.get_entity(i, 0).match_branch(branch))
            StartTestsOp(self.session, testconfigs)


class StartTestsOp(pool.SingleLastOperation):
    def __init__(self, session, tests):
        self.tests = tests
        super(StartTestsOp, self).__init__(session)

    def register(self, session):
        previous = super(StartTestsOp, self).register(session)
        if previous:
            self.tests |= previous.tests

    def commit_event(self):
        self.repo.threaded_task(self.start_tests)

    def start_tests(self):
        session = self.session
        try:
            bot = bot_proxy(self.config, session.transaction_data)
        except Exception, ex:
            self.error('cant contact apycot bot: %s', ex)
            # XXX create a TestExecution to report the attempt to launch test
            return
        # XXX make start_rev_deps=True configurable
        for envname, tcname, startrevdeps, branch in self.tests:
            try:
                full_pyro_id = ':%(pyro-ns-group)s.%(pyro-instance-id)s' % self.config
                bot.queue_task(envname, tcname,
                               branch=branch, start_rev_deps=startrevdeps,
                               cwid=full_pyro_id)
            except Exception, ex:
                self.error('cant start test %s: %s', tcname, ex)
                # XXX create a TestExecution to report the attempt to launch test
                return


# notifications ################################################################

class ExecStatusChangeView(notification.NotificationView):
    id = 'exstchange'
    __select__ = implements('TestExecution')

    content = '''The following changes occured between executions on branch %(branch)s:

%(changelist)s

Imported changes occured between %(ex1time)s and %(ex2time)s:
%(vcschanges)s

URL: %(url)s
'''

    def subject(self):
        entity = self.entity(0, 0)
        changes = entity.status_changes()
        testconfig = entity.configuration.dc_title()
        if entity.branch:
            testconfig = u'%s@%s' % (testconfig, entity.branch)
        if len(changes) == 1:
            subject = self.req._('%s: %s status changed to %s')
            name, (fromstate, tostate) = changes.items()[0]
            subject %= (testconfig, name, self.req._(tostate))
        else:
            count = {}
            for fromstate, tostate in entity.status_changes().values():
                try:
                    count[tostate] += 1
                except KeyError:
                    count[tostate] = 1
            resume = ', '.join('%s %s' % (num, self.req._(state))
                               for state, num in count.items())
            subject = self.req._('%s now has %s') % (testconfig, resume)
        return '[%s] %s' % (self.config.appid, subject)

    def context(self):
        entity = self.entity(0, 0)
        prevexec = entity.previous_entity()
        ctx  = super(ExecStatusChangeView, self).context()
        ctx['ex1time'] = prevexec.printable_value('starttime')
        ctx['ex2time'] = entity.printable_value('starttime')
        ctx['branch'] = entity.branch
        chgs = []
        _ = self.req._
        for name, (fromstate, tostate) in sorted(entity.status_changes().items()):
            name = _(name)
            fromstate, tostate = _(fromstate), _(tostate)
            chg = _('%(name)s status changed from %(fromstate)s to %(tostate)s')
            chgs.append('* ' + (chg % locals()))
        ctx['changelist'] = '\n'.join(chgs)
        vcschanges = []
        for env in [entity.configuration.environment] + entity.configuration.dependencies():
            if env.repository:
                vcsrepo = env.repository
                vcsrepochanges = []
                lrev1 = prevexec.repository_revision(env.repository)
                lrev2 = entity.repository_revision(env.repository)
                if lrev1 and lrev2:
                    for rev in self.req.execute(
                        'Any REV, REVA, REVD, REVR, REVC ORDERBY REV '
                        'WHERE REV from_repository R, R eid %(r)s, REV branch %(branch)s, '
                        'REV revision > %(lrev1)s, REV revision <= %(lrev2)s, '
                        'REV author REVA, REV description REVD, '
                        'REV revision REVR, REV changeset REVC',
                        {'r': env.repository.eid,
                         'branch': lrev2.branch or env.repository.default_branch(),
                         'lrev1': lrev1.revision, 'lref2': lrev2.revision}, 'r').entities():
                        msg = text_cut(revision.description)
                        vcsrepochanges.append('  - %s by %s:%s' % (
                            revision.dc_title(), revision.author, msg))
                    if vcsrepochanges:
                        vcschanges.append('* in repository %s: \n%s' % (
                            env.repository.path, '\n'.join(vcsrepochanges)))
        if vcschanges:
            ctx['vcschanges'] = '\n'.join(vcschanges)
        else:
            ctx['vcschanges'] = self.req._('* no change found in known repositories')
        return ctx


class ExecStatusChangeHook(hooksmanager.Hook):
    events = ('after_update_entity',)
    accepts = ('TestExecution',)

    def call(self, session, entity):
        # end of test execution : set endtime
        if 'endtime' in entity.edited_attributes and entity.status_changes():
            view = session.vreg['views'].select(
                'exstchange', session, rset=entity.rset, row=entity.row,
                col=entity.col)
            notification.RenderAndSendNotificationView(session, view=view)

class ClearArchiveChangeHook(hooksmanager.Hook):
    events = ('after_delete_relation',)
    accepts = ('for_check',)

    def call(self, session, fromeid, rtype, toeid):
        exec_data = session.entity_from_eid(fromeid)
        test_exec = session.entity_from_eid(toeid)
        if not toeid in session.transaction_data.get('pendingeids', ()) and \
           exec_data.type == "archive" and test_exec.status == "archived":
            session.execute('''SET TE status "done"
                                WHERE TE eid %(eid)s''',
                             {'eid': test_exec.eid})

try:
    from cubes.nosylist import hooks as nosylist
except ImportError:
    pass
else:
    # XXX that does not mean the nosylist cube is used by the instance, but it
    # shouldn't matter anyway
    nosylist.S_RELS |= set(('has_apycot_environment',))
    nosylist.O_RELS |= set(('use_environment', 'using_config'))

    nosylist.INotificationBaseAddedHook.accepts.append('ProjectEnvironment')
    nosylist.INotificationBaseAddedHook.accepts.append('TestConfig')
