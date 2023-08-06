"""utilities to turn apycot raw logs into nice html reports

nn:organization: Logilab
:copyright: 2008-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
:license: General Public License version 2 - http://www.gnu.org/licenses
"""
__docformat__ = "restructuredtext en"
_ = unicode

import logging


REVERSE_SEVERITIES = {
    logging.DEBUG :   _('DEBUG'),
    logging.INFO :    _('INFO'),
    logging.WARNING : _('WARNING'),
    logging.ERROR :   _('ERROR'),
    logging.FATAL :   _('FATAL')
    }


def log_to_html(req, data, w):
    """format apycot logs data to an html table

    log are encoded by the apycotbot in the following format for each record:

      encodedmsg = u'%s\t%s\t%s\t%s<br/>' % (severity, path, line,
                                             xml_escape(msg))

    """
    # XXX severity filter / link to viewcvs or similar
    req.add_js('jquery.tablesorter.js')
    req.add_css('cubicweb.tablesorter.css')
    w(u'<table class="listing apylog">')
    w(u'<tr><th>%s</th><th>%s</th><th>%s</th><th>%s</th></tr>' % (
        req._('severity'), req._('path or command'), req._('line'), req._('message')))
    for record in data.split('<br/>'):
        record = record.strip()
        if not record:
            continue
        try:
            severity, path, line, msg = record.split('\t', 3)
        except:
            req.warning('badly formated apycot log %s' % record)
            continue
        severityname = REVERSE_SEVERITIES[int(severity)]
        w(u'<tr class="log%s">' % severityname.capitalize())
        w(u'<td class="logSeverity" cubicweb:sortvalue="%s">%s</td>' % (
            severity, req._(REVERSE_SEVERITIES[int(severity)])))
        w(u'<td class="logPath">%s</td>' % (path or u'&#160;'))
        w(u'<td class="logLine">%s</td>' % (line or u'&#160;'))
        w(u'<td class="logMsg"><pre class="rawtext">%s</pre></td>' % msg)
        w(u'</tr>\n')
    w(u'</table>')
