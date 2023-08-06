"""this module contains the cube-specific entities' classes

:organization: Logilab
:copyright: 2008-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
:license: General Public License version 2 - http://www.gnu.org/licenses
"""
__docformat__ = "restructuredtext en"

from logilab.common.decorators import cached
from logilab.common.textutils import TIME_UNITS, BYTE_UNITS, apply_units, splitstrip
from logilab.mtconverter import xml_escape

from cubicweb.interfaces import IPrevNext
from cubicweb.entity import _marker
from cubicweb.entities import AnyEntity, fetch_config

try:
    from cubes.nosylist.interfaces import INosyList
except ImportError:
    INosyList = None

def text_to_dict(text):
    """parse multilines text containing simple 'key=value' lines and return a
    dict of {'key': 'value'}. When the same key is encountered multiple time,
    value is turned into a list containing all values.

    >>> text_to_dict('''multiple=1
    ... multiple= 2
    ... single =3
    ... ''')
    {'single': '3', 'multiple': ['1', '2']}

    """
    res = {}
    if not text:
        return res
    for line in text.splitlines():
        line = line.strip()
        if line:
            key, value = [w.strip() for w in line.split('=', 1)]
            if key in res:
                try:
                    res[key].append(value)
                except AttributeError:
                    res[key] = [res[key], value]
            else:
                res[key] = value
    return res


class ProjectEnvironment(AnyEntity):
    __regid__ = 'ProjectEnvironment'

    if INosyList is not None:
        __implements__ = AnyEntity.__implements__ + (INosyList,)

    fetch_attrs, fetch_order = fetch_config(['name'])

    def parent(self):
        """hierarchy, used for breadcrumbs"""
        try:
            return self.reverse_has_apycot_environment[0]
        except (AttributeError, IndexError):
            return None

    def printable_value(self, attr, value=_marker, attrtype=None,
                        format='text/html', displaytime=True):
        """return a displayable value (i.e. unicode string) which may contains
        html tags
        """
        attr = str(attr)
        if value is _marker:
            value = getattr(self, attr)
        if value is None or value == '': # don't use "not", 0 is an acceptable value
            return u''
        if attr == 'vcs_path' and format == 'text/html':
            if '://' in value:
                return '<a href="%s">%s</a>' % (xml_escape(value),
                                                xml_escape(value))
            return xml_escape(value)
        return super(ProjectEnvironment, self).printable_value(
            attr, value, attrtype, format, displaytime)

    # cube specific logic #####################################################

    @property
    def repository(self):
        return self.local_repository and self.local_repository[0] or None

    def dependencies(self, _done=None):
        if _done is None:
            _done = set()
        _done.add(self.eid)
        result = []
        for pe in self.needs_checkout:
            if pe.eid in _done:
                continue
            result.append(pe)
            result += pe.dependencies(_done)
        return result

    # apycot bot helpers #######################################################

    @property
    def my_apycot_process_environment(self):
        return text_to_dict(self.check_environment)

    @property
    def my_apycot_configuration(self):
        return text_to_dict(self.check_config)

    @property
    def apycot_configuration(self):
        return self.my_apycot_configuration

    @property
    def apycot_preprocessors(self):
        return text_to_dict(self.check_preprocessors)

    @property
    def apycot_repository_def(self):
        if self.vcs_repository:
            vcsrepo = self.vcs_repository
            vcsrepotype = self.vcs_repository_type
        elif self.local_repository:
            vcsrepo = self.local_repository[0].path
            if self.local_repository[0].type == 'mercurial':
                vcsrepotype = 'hg'
            else:
                vcsrepotype = 'svn'
        else:
            vcsrepo = vcsrepotype = None
        return {
            'repository_type': vcsrepotype,
            'repository': vcsrepo,
            'path': self.vcs_path
            }

    # jpl integration #########################################################

    @property
    def project(self):
        if 'has_apycot_environment' in self._cw.vreg.schema:
            return self.reverse_has_apycot_environment[0]


class TestConfigGroup(AnyEntity):
    __regid__ = 'TestConfigGroup'

    fetch_attrs, fetch_order = fetch_config(['name'])

    def config_parts(self, _done=None):
        if _done is None:
            _done = set()
        _done.add(self.eid)
        result = [self]
        for group in self.use_group:
            if group.eid in _done:
                continue
            result += group.config_parts(_done)
        return result
    config_parts = cached(config_parts, keyarg=0)

    @property
    def all_checks(self):
        try:
            return self.all_checks_and_owner()[1]
        except TypeError:
            return None

    def all_checks_and_owner(self):
        for group in self.config_parts():
            if group.checks:
                return group, splitstrip(group.checks)

    # apycot bot helpers #######################################################

    @property
    def my_apycot_process_environment(self):
        return text_to_dict(self.check_environment)

    @property
    def my_apycot_configuration(self):
        return text_to_dict(self.check_config)

    # XXX for 1.4 migration
    @property
    def apycot_preprocessors(self):
        return text_to_dict(self.check_preprocessors)


class TestConfig(TestConfigGroup):
    __regid__ = 'TestConfig'

    if INosyList is not None:
        __implements__ = AnyEntity.__implements__ + (INosyList,)


    def dc_title(self):
        return '%s(%s)' % (self.name, self.environment.name)

    def parent(self):
        return self.environment

    # cube specific logic #####################################################

    @property
    def environment(self):
        return self.use_environment[0]

    def dependencies(self):
        _done = set()
        result = self.environment.dependencies(_done)
        for dpe in self.needs_checkout:
            if dpe.eid in _done:
                continue
            result.append(dpe)
            result += dpe.dependencies(_done)
        return result

    @cached
    def all_check_results(self):
        rset = self._cw.execute('Any MAX(X), XN GROUPBY XN, EXB ORDERBY XN '
                                'WHERE X is CheckResult, X name XN, '
                                'X during_execution EX, EX using_config C, '
                                'EX branch EXB, C eid %(c)s',
                                {'c': self.eid}, 'c')
        return list(rset.entities())

    def latest_execution(self):
        rset = self._cw.execute('Any X, C ORDERBY X DESC LIMIT 1'
                                'WHERE X is TestExecution, X using_config C, '
                                'C eid %(c)s', {'c': self.eid}, 'c')
        if rset:
            return rset.get_entity(0, 0)

    def latest_full_execution(self):
        rset = self._cw.execute('Any X, C, COUNT(CR) GROUPBY X, C '
                                'ORDERBY 3 DESC, X DESC LIMIT 1'
                                'WHERE X is TestExecution, X using_config C, '
                                'C eid %(c)s, CR during_execution X',
                                {'c': self.eid}, 'c')
        if rset:
            return rset.get_entity(0, 0)

    def latest_check_result_by_name(self, name, branch):
        for cr in self.all_check_results():
            if cr.name == name and cr.execution.branch == branch:
                return cr

    def match_branch(self, branch):
        return self.apycot_configuration.get('branch', branch) == branch

    # apycot bot helpers #######################################################

    def _regroup_dict(self, prop):
        regroup = getattr(self.environment, prop).copy()
        for group in reversed(self.config_parts()):
            regroup.update(getattr(group, prop))
        return regroup

    @property
    def apycot_process_environment(self):
        return self._regroup_dict('my_apycot_process_environment')

    @property
    @cached
    def apycot_configuration(self):
        config = self._regroup_dict('my_apycot_configuration')
        for option in (u'max-cpu-time', u'max-reprieve', u'max-time'):
            if option in config:
                config[option] = apply_units(config[option], TIME_UNITS)
        if u'max-memory' in config:
            config[u'max-memory'] = apply_units(config[u'max-memory'],
                                                BYTE_UNITS)
        return config

    # jpl integration #########################################################

    @property
    def project(self):
        """jpl integration"""
        return self.parent().project


class TestExecution(AnyEntity):
    __regid__ = 'TestExecution'
    __implements__ = AnyEntity.__implements__ + (IPrevNext,)

    def dc_title(self):
        return self._cw._('Execution of %(config)s on %(date)s') % {
            'config': self.configuration.dc_title(),
            'date': self.printable_value('starttime')}

    def parent(self):
        """hierarchy, used for breadcrumbs"""
        return self.configuration

    # IPrevNext interface #####################################################

    def previous_entity(self):
        rql = ('Any X,C ORDERBY X DESC LIMIT 1 '
               'WHERE X is TestExecution, X using_config C, C eid %(c)s, X branch %(branch)s, '
               'X eid < %(x)s')
        rset = self._cw.execute(rql, {'c': self.configuration.eid, 'x': self.eid,
                                      'branch': self.branch}, 'c')
        if rset:
            return rset.get_entity(0, 0)

    def next_entity(self):
        rql = ('Any X,C ORDERBY X ASC LIMIT 1 '
               'WHERE X is TestExecution, X using_config C, C eid %(c)s, X branch %(branch)s, '
               'X eid > %(x)s')
        rset = self._cw.execute(rql, {'c': self.configuration.eid, 'x': self.eid,
                                      'branch': self.branch}, 'c')
        if rset:
            return rset.get_entity(0, 0)

    # cube specific logic #####################################################

    @property
    def configuration(self):
        return self.using_config[0]

    def check_result_by_name(self, name):
        for cr in self.reverse_during_execution:
            if cr.name == name:
                return cr

    @cached
    def status_changes(self):
        """return a dict containing status test changes between the previous
        execution and this one. Changes are described using a 2-uple:

          (previous status, current status)

        Return an empty dict if no previous execution is found or if nothing
        changed.
        """
        result = {}
        previous_exec = self.previous_entity()
        if previous_exec is None:
            return
        for cr in self.reverse_during_execution:
            previous_cr = previous_exec.check_result_by_name(cr.name)
            if previous_cr is not None and previous_cr.status != cr.status:
                result[cr.name] = (previous_cr.status, cr.status)
        return result

    def repository_revision(self, repository):
        for rev in self.using_revision:
            if rev.repository.eid == repository.eid:
                return rev

    # jpl integration #########################################################

    @property
    def project(self):
        return self.configuration.project

    def archive_name(self):
        rql = '''Any PATH
                 WHERE CRI for_check TE,
                       TE eid %(eid)s,
                       CRI type "archive",
                       CRI value PATH'''
        rset = self._cw.execute(rql, {'eid': self.eid})
        if rset:
            assert len(rset) == 1, 'More than one "archive" data'
            return rset[0][0]
        else:
            return None

    def _archive_id(self):
        full_pyro_id = ':%(pyro-ns-group)s.%(pyro-instance-id)s' % self.config
        return (full_pyro_id, self.eid)


    def archive_content(self, bot=None):
        if bot is None:
            bot = bot_proxy(self.config, self._cw.data)
        arch_id = self._archive_id()
        assert  arch_id is not None, "No archive path data for this Test Execution"
        return bot.get_archive(*arch_id)

    def clear_archive(self, bot=None):
        if bot is None:
            bot = bot_proxy(self.config, self._cw.data)
        arch_id = self._archive_id()
        assert  arch_id is not None, "No archive path data for this Test Execution"
        result = bot.clear_archive(*arch_id)
        # we should make a difference between archive that didn't existe and the one we failed to delete
        if result is not None:
            rql = '''DELETE CheckResultInfo CRI
                     WHERE CRI for_check TE,
                           TE eid %(eid)s,
                           CRI type "archive",
                           CRI value %(name)s'''
            self._cw.execute(rql, {'eid': self.eid, 'name': result})
        return result


class CheckResult(AnyEntity):
    __regid__ = 'CheckResult'
    __implements__ = AnyEntity.__implements__ + (IPrevNext,)
    fetch_attrs, fetch_order = fetch_config(['starttime', 'endtime',
                                             'name', 'status'])

    def parent(self):
        """hierarchy, used for breadcrumbs"""
        return self.execution

    # IPrevNext interface #####################################################

    def previous_entity(self):
        previous_exec = self.execution.previous_entity()
        if previous_exec:
            return previous_exec.check_result_by_name(self.name)

    def next_entity(self):
        next_exec = self.execution.next_entity()
        if next_exec:
            return next_exec.check_result_by_name(self.name)

    # cube specific logic #####################################################

    @property
    def execution(self):
        return self.during_execution[0]


from logilab.common.pyro_ext import ns_get_proxy

def bot_proxy(config, cache):
    if not 'botproxy' in cache:
        cache['botproxy'] = ns_get_proxy(config['bot-pyro-id'], 'apycot',
                                         nshost=config['bot-pyro-ns'])
    return cache['botproxy']
