from cubicweb.view import EntityView
from cubicweb.web.action import Action
from cubicweb.selectors import (implements, match_user_groups,
                                one_line_rset, score_entity)
from cubicweb.web import NotFound


_ = unicode

class ArchiveContentView(EntityView):
    id = "archive_content"
    title = _("Execution directory content")
    __select__ = match_user_groups('managers', 'staff') \
               & implements('TestExecution') & one_line_rset() \
               & score_entity(lambda x: x.status == 'archived')

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
        self.req.set_content_type(self.content_type,
                         filename=entity.archive_name())


class DownloadArchiveAction(Action):
    id = 'download_archive'
    __select__ = match_user_groups('managers', 'staff') \
               & implements('TestExecution') & one_line_rset() \
               & score_entity(lambda x: x.status == 'archived')
    submenu = _("Execution directory content")
    title = _("download")

    def url(self):
        test_exec = self.rset.get_entity(self.row or 0, self.col or 0)
        return test_exec.absolute_url(vid='archive_content')

class ClearArchiveAction(Action):
    id = 'clear_archive'
    __select__ = match_user_groups('managers', 'staff') \
               & implements('TestExecution') & one_line_rset() \
               & score_entity(lambda x: x.status == 'archived')
    submenu = _("Execution directory content")
    title = _("clear")

    def url(self):
        test_exec = self.rset.get_entity(self.row or 0, self.col or 0)
        def clear_archive_callback(req, eid=test_exec.eid):
            test_exec = req.entity_from_eid(eid)
            test_exec.clear_archive()

        return self.user_callback(clear_archive_callback, [])
