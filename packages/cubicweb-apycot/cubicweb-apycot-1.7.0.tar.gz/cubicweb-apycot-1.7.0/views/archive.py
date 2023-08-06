"""ui manipulation of archive containing the test execution directory

:organization: Logilab
:copyright: 2009-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
:license: General Public License version 2 - http://www.gnu.org/licenses
"""
__docformat__ = "restructuredtext en"
_ = unicode

from cubicweb.selectors import (
    objectify_selector, implements, match_user_groups,
    one_line_rset, score_entity)
from cubicweb.view import EntityView
from cubicweb.web import NotFound, action

from cubes.apycot.entities import bot_proxy


@objectify_selector
def bot_available(cls, req, **kwargs):
    try:
        if bot_proxy(req.vreg.config, req.data):
            return 1
    except:
        return 0

class ArchiveContentView(EntityView):
    __regid__ = "archive_content"
    __select__ = (match_user_groups('managers', 'staff')
                  & bot_available()
                  & implements('TestExecution') & one_line_rset()
                  & score_entity(lambda x: x.status == 'archived')
                  )
    title = _("Execution directory content")

    binary = True
    content_type = 'application/x-bzip2'

    def call(self):
        assert self.content_type == 'application/x-bzip2'
        test_exec = self.entity(0,0)
        content = test_exec.archive_content()
        if content is None:
            raise NotFound()
        self.w(content)

    def set_request_content_type(self):
        """overriden to set the correct filetype and filename"""
        entity = self.complete_entity(0)
        self._cw.set_content_type(self.content_type,
                         filename=entity.archive_name())


class DownloadArchiveAction(action.Action):
    __regid__ = 'download_archive'
    __select__ = (match_user_groups('managers', 'staff')
                  & bot_available()
                  & implements('TestExecution') & one_line_rset()
                  & score_entity(lambda x: x.status == 'archived')
                  )
    submenu = _("Execution directory content")
    title = _("download")

    def url(self):
        test_exec = self.rset.get_entity(self.cw_row or 0, self.cw_col or 0)
        return test_exec.absolute_url(vid='archive_content')


class ClearArchiveAction(action.Action):
    __regid__ = 'clear_archive'
    __select__ = (match_user_groups('managers', 'staff')
                  & bot_available()
                  & implements('TestExecution') & one_line_rset()
                  & score_entity(lambda x: x.status == 'archived')
                  )
    submenu = _("Execution directory content")
    title = _("clear")

    def url(self):
        test_exec = self.rset.get_entity(self.cw_row or 0, self.cw_col or 0)
        def clear_archive_callback(req, eid=test_exec.eid):
            test_exec = req.entity_from_eid(eid)
            test_exec.clear_archive()
        return self._cw.user_callback(clear_archive_callback, [])
