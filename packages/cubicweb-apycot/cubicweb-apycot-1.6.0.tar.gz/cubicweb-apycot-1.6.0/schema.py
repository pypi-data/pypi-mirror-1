"""apycot cube's specific schema

:organization: Logilab
:copyright: 2008-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"
_ = unicode

from yams.buildobjs import (EntityType, RelationType, RelationDefinition,
                            SubjectRelation, ObjectRelation,
                            String, Int, Datetime, Boolean)
from yams.reader import context

from cubicweb.schema import RQLConstraint, RRQLExpression, RQLUniqueConstraint,\
     make_workflowable

from cubes.vcsfile.schema import Repository


# jpl extension
if 'Project' in context.defined:

    class has_apycot_environment(RelationDefinition):
        permissions = {
            'read':   ('managers', 'users', 'guests'),
            'add':    ('managers', 'staff',
                       RRQLExpression('U has_update_permission S', 'S'),),
            'delete': ('managers', 'staff',
                       RRQLExpression('U has_update_permission S', 'S'),),
            }
        subject = 'Project'
        object = 'ProjectEnvironment'
        cardinality = '*?'
        composite = 'subject'

    CONF_WRITE_GROUPS = ('managers', 'staff')

else:

    CONF_WRITE_GROUPS = ('managers', )

Repository.permissions['read'] += ('apycot',)

class ProjectEnvironment(EntityType):
    permissions = {
        'read':   ('managers', 'users', 'guests', 'apycot'),
        'add':    CONF_WRITE_GROUPS,
        'update': CONF_WRITE_GROUPS,
        'delete': CONF_WRITE_GROUPS,
        }

    name = String(
        required=True, unique=True, maxsize=128,
        description=_('name for this environment')
        )

    vcs_repository_type = String(
        required=True,
        vocabulary=(u'hg', u'svn', u'cvs', u'fs'),
        description=_('kind of version control system (vcs): hg (mercurial), '
                      'svn (subversion), cvs (CVS), fs (file system, eg no '
                      'version control)')
        )
    vcs_repository = String(
        required=True,
        description=_('path or url to the vcs repository containing the project')
        )
    vcs_path = String(
        description=_('relative path to the project into the repository')
        )

    check_preprocessors = String(
        description=_('preprocessors to use for this project for install, '
                      'debian, build_doc... (one per line)'),
        fulltextindexed=True
        )
    check_environment = String(
        description=_('environment variables to be set in the check process '
                      'environment (one per line)'),
        fulltextindexed=True
        )
    check_config = String(
        description=_('preprocessor/checker options (one per line)'),
        fulltextindexed=True
        )

    local_repository = SubjectRelation(
        'Repository', cardinality='?*',
        description=_('link to a vcsfile repository, may be used to replace '
                      'vcs_repository_type / vcs_repository to have deeper '
                      'integration.')
        )
    needs_checkout = SubjectRelation(
        'ProjectEnvironment',
        description=_('project\'s environments on which this one depends'),
        )#constraints=[RQLConstraint('NOT S identity O')])


class TestConfigGroup(EntityType):
    """regroup some common configuration used by multiple projects"""
    permissions = {
        'read':   ('managers', 'users', 'guests', 'apycot'),
        'add':    CONF_WRITE_GROUPS,
        'update': CONF_WRITE_GROUPS,
        'delete': CONF_WRITE_GROUPS,
        }

    name = String(
        required=True, unique=True, maxsize=128,
        description=_('name for this configuration group'),
        )
    checks = String(
        description=_('comma separated list of checks to execute in this test config'),
        fulltextindexed=True
        )
    check_environment = String(
        description=_('environment variables to be set in the test process '
                      'environment (one per line)'),
        fulltextindexed=True
        )
    check_config = String(
        description=_('preprocessor/checker options (one per line)'),
        fulltextindexed=True
        )
    use_group = SubjectRelation('TestConfigGroup')#, constraints=[RQLConstraint('NOT S identity O')])


class TestConfig(TestConfigGroup):
    """apycot configuration to register a project branch to test"""
    permissions = {
        'read':   ('managers', 'users', 'guests', 'apycot'),
        'add':    CONF_WRITE_GROUPS,
        'update': CONF_WRITE_GROUPS,
        'delete': CONF_WRITE_GROUPS,
        }
    name = String(
        override=True, required=True, maxsize=128, indexed=True,
        description=_('name for this configuration'),
        constraints=[RQLUniqueConstraint('S name N, S use_environment E, '
                                         'Y use_environment E, Y name N', 'Y')]
        )

    start_mode = String(
        required=True, indexed=True,
        vocabulary=(_('manual'), _('on new revision'),
                    _('hourly'), _('daily'),_('weekly'), _('monthly')),
        default='manual',
        description=_('when this test config should be started')
        )
    start_rev_deps = Boolean(
        default=False,
        description=_("should tests for project environment depending on this "
                      "test's environment be started when this test is "
                      "automatically triggered")
        )
    # simply use 'branch=XXX' in check_config field. Get back documentation
    # before to remove code below
    # vcs_branch  = String(
    #     description=_('branch to use for test\'s checkout. In case of '
    #                   'subversion repository, this should be the relative path '
    #                   'of the branch into the repository (vcs_path won\'t be '
    #                   'considered then).'),
    #     maxsize=256
    #     )
    subpath = String(
        description=_('path relative to the checkout directory to be considered by tests')
        )

    use_environment = SubjectRelation(
        'ProjectEnvironment', cardinality='1*', composite='object',
        description=_('project environment in which this test config should be launched'),
        constraints=[RQLUniqueConstraint('S name N, Y use_environment O, Y name N', 'Y')],
        inlined=True
        )
    needs_checkout = SubjectRelation(
        'ProjectEnvironment',
        description=_('project\'s environments that should be installed from '
                      'their repository to execute test on this configuration'),
        )#constraints=[RQLConstraint('NOT S identity O')])

make_workflowable(TestConfig, in_state_descr=_('automatic test status'))


BOT_ENTITY_PERMS = {
        'read':   ('managers', 'users', 'guests', 'apycot'),
        'add':    ('apycot',),
        'update': ('apycot',),
        'delete': ('managers',),
        }

class TestExecution(EntityType):
    permissions = BOT_ENTITY_PERMS

    status = String(required=True, internationalizable=True, indexed=True,
                    default=u'set up',
                    vocabulary=(_('set up'), _('running tests'), _('cleaning'),
                                _('archived'), _('done'),
                                _('not removed'))) #"not removed" value is deprecated
    starttime = Datetime(required=True)
    endtime   = Datetime()
    branch = String(indexed=True)
    log = String()
    using_config = SubjectRelation('TestConfig', cardinality='1*', composite='object')
    using_revision = SubjectRelation(
        'Revision',
        description=_('link to revision which has been used in the test '
                      'environment for configurations which are linked to a '
                      'repository.'))


class CheckResult(EntityType):
    """group results of execution of a specific test on a project"""
    permissions = BOT_ENTITY_PERMS

    name      = String(required=True, indexed=True, maxsize=128, description=_('check name'))
    status    = String(required=True,
                       vocabulary=(_('success'), _('partial'),  _('failure'), _('error'), _('nodata'),
                                   _('missing'), _('skipped'), _('killed'),
                                   _('processing')))
    starttime = Datetime()
    endtime   = Datetime()
    log = String()
    during_execution = SubjectRelation('TestExecution', cardinality='1*',
                                       composite='object')


class CheckResultInfo(EntityType):
    """arbitrary information about execution of a specific test on a project"""
    permissions = BOT_ENTITY_PERMS

    type = String(internationalizable=True)
    label = String(required=True, internationalizable=True)
    value = String(required=True, internationalizable=True)

    for_check = SubjectRelation(('CheckResult', 'TestExecution'), cardinality='1*', composite='object')


class use_group(RelationType):
    permissions = {
        'read':   ('managers', 'users', 'guests',),
        'add':    CONF_WRITE_GROUPS,
        'delete': CONF_WRITE_GROUPS,
        }

class using_config(RelationType):
    permissions = BOT_ENTITY_PERMS
    inlined = True

class during_execution(RelationType):
    permissions = BOT_ENTITY_PERMS
    inlined = True

class for_check(RelationType):
    permissions = BOT_ENTITY_PERMS
    inlined = True

class using_revision(RelationType):
    permissions = BOT_ENTITY_PERMS


if 'nosy_list' in context.defined:

    class interested_in(RelationDefinition):
        '''users to notify of changes concerning this entity'''
        subject = 'CWUser'
        object = ('ProjectEnvironment', 'TestConfig')

    class nosy_list(RelationDefinition):
        subject = ('ProjectEnvironment', 'TestConfig', 'TestExecution')
        object = 'CWUser'
