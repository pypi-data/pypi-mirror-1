"""cube automatic tests"""

from logilab.common.testlib import unittest_main

from cubicweb.devtools.fill import ValueGenerator
from cubicweb.devtools.testlib import AutomaticWebTest


class MyValueGenerator(ValueGenerator):
    def generate_ProjectEnvironment_check_preprocessors(self, index):
        return u'install=python_setup'
    def generate_Any_check_config(self, index):
        return u'pylint_threshold=70'
    def generate_Any_check_environment(self, index):
        return u'USE_SETUPTOOLS=0'


class AutomaticWebTest(AutomaticWebTest):
    no_auto_populate = ('Repository', 'Revision', 'VersionedFile',
                        'VersionContent', 'DeletedVersionContent',)
    ignored_relations = ('at_revision', 'parent_revision',
                         'from_repository', 'from_revision', 'content_for',)

    def setUp(self):
        super(AutomaticWebTest, self).setUp()
        for etype in ('TestExecution', 'CheckResult', 'CheckResultInfo',
                      'using_config', 'during_execution', 'for_check'):
            self.schema[etype].set_groups('add', ('managers',))

    def to_test_etypes(self):
        return set(('ProjectEnvironment', 'TestConfig', 'TestConfigGroup',
                    'TestExecution', 'CheckResult', 'CheckResultInfo'))

    def list_startup_views(self):
        return ()

if __name__ == '__main__':
    unittest_main()
