"""this module contains some stuff to integrate the apycot cube into jpl

:organization: Logilab
:copyright: 2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
:license: General Public License version 2 - http://www.gnu.org/licenses
"""
__docformat__ = "restructuredtext en"
_ = unicode

from cubicweb.selectors import implements
from cubicweb.view import EntityView
from cubicweb.web import component, uicfg
from cubicweb.web.views import tabs

_pvs = uicfg.primaryview_section
_pvs.tag_subject_of(('Project', 'has_apycot_environment', '*'), 'hidden')

class ProjectTestResultsTab(tabs.EntityRelationView):
    """display project's documentation"""
    __regid__ = title = _('apycottestresults_tab')
    __select__ = tabs.EntityRelationView.__select__ & implements('Project')
    rtype = 'has_apycot_environment'
    target = 'object'

    def call(self, *args, **kwargs):
        entity = self.rset.get_entity(0,0)
        config = entity.related('has_apycot_environment')
        if config:
            self.wview('summary', config,
                       title=self.req._('Latest test results'))


# class VersionTestResultsVComponent(component.EntityVComponent):
#     """display the latest tests execution results"""
#     __regid__ = 'apycottestresults'
#     __select__ = component.EntityVComponent.__select__ & implements('Version')

#     context = 'navcontentbottom'
#     rtype = 'has_apycot_environment'
#     target = 'object'
#     title = _('Latest test results')
#     order = 11

#     def cell_call(self, row, col, **kwargs):
#         entity = self.entity(row, col)
#         configsrset = entity.related('has_apycot_environment')
#         if not configsrset:
#             return
#         self.wview('summary', configsrset, title=self.req._(self.title))


try:
    from cubes.tracker.views.project import ProjectPrimaryView
except ImportError:
    pass
else:
    if 'apycottestresults_tab' not in ProjectPrimaryView.tabs:
        ProjectPrimaryView.tabs.append('apycottestresults_tab')
