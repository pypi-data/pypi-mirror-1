"""some facets to filter test configurations

:organization: Logilab
:copyright: 2008-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
:license: General Public License version 2 - http://www.gnu.org/licenses
"""
__docformat__ = "restructuredtext en"

from cubicweb.selectors import implements
from cubicweb.web.facet import RelationFacet, AttributeFacet

class TestConfigEnvFacet(RelationFacet):
    id = 'tc-env-facet'
    __select__ = AttributeFacet.__select__ & implements('TestConfig')
    rtype = 'use_environment'
    target_attr = 'name'

class TestConfigNameFacet(AttributeFacet):
    id = 'tc-name-facet'
    __select__ = AttributeFacet.__select__ & implements('TestConfig')
    rtype = 'name'

class TestConfigStartModeFacet(AttributeFacet):
    id = 'tc-startmode-facet'
    __select__ = AttributeFacet.__select__ & implements('TestConfig')
    rtype = 'start_mode'

class TestConfigStartRevDepsFacet(AttributeFacet):
    id = 'tc-startrev-facet'
    __select__ = AttributeFacet.__select__ & implements('TestConfig')
    rtype = 'start_rev_deps'

# XXX facet to filter tc according to te's branch
