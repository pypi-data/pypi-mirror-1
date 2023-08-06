'''apycot reports'''

from cubicweb.web import uicfg, formwidgets as wdgs
from cubicweb.web.views import urlrewrite

from cubes.apycot.entities import bot_proxy


def anchor_name(data):
    """escapes XML/HTML forbidden characters in attributes and PCDATA"""
    return (data.replace('&', '').replace('<', '').replace('>','')
            .replace('"', '').replace("'", ''))

# ui configuration #############################################################


_afs = uicfg.autoform_section
_afs.tag_subject_of(('*', 'use_group', '*'), 'main', 'attributes')


# register generated message id
_('Available checkers:')
_('Available preprocessors:')
_('Available options:')

def build_help_func(attr, apycot_type, etype='TestConfigGroup'):
    def help_func(form, attr=attr, apycot_type=apycot_type, etype=etype):
        req = form.req
        help = form.schema.eschema(etype).rproperty(attr, 'description')
        help = '<div>%s.</div>' % req._(help)
        try:
            # ProtocolError may be called during method() call
            bot = bot_proxy(form.config, req.data)
            method = getattr(bot, 'available_%s' % apycot_type)
            available = ', '.join(defdict.get('id', defdict.get('name'))
                                  for defdict in method())
        except Exception, ex:
            form.warning('cant contact apycot bot: %s', ex)
            return help
        help += '<div>%s %s (<a href="%s">%s</a>)</div>' % (
            req.__('Available %s:' % apycot_type), available,
            req.build_url('apycotdoc#%s' % apycot_type),
            req._('more information')
            )
        return help
    return help_func

_affk = uicfg.autoform_field_kwargs
helpfunc = build_help_func('check_preprocessors', 'preprocessors', 'ProjectEnvironment')
_affk.tag_attribute(('ProjectEnvironment', 'check_preprocessors'),
                    {'help': helpfunc})
for attr, apycot_type in (('check_config', 'options'),):
    for etype in ('TestConfigGroup', 'ProjectEnvironment'):
        helpfunc = build_help_func(attr, apycot_type, etype=etype)
        _affk.tag_attribute((etype, attr), {'help': helpfunc})
for attr, apycot_type in (('checks', 'checkers'),):
    helpfunc = build_help_func(attr, apycot_type, 'TestConfigGroup')
    _affk.tag_attribute(('TestConfigGroup', attr), {
        'help': helpfunc, 'widget': wdgs.TextInput({'size': 100})})
    _affk.tag_attribute(('TestConfig', attr), {
        'help': helpfunc, 'widget': wdgs.TextInput({'size': 100})})
_affk.tag_attribute(('TestConfig', 'start_mode'), {'sort': False})

_affk.tag_attribute(('ProjectEnvironment', 'vcs_repository'), {'widget': wdgs.TextInput})
_affk.tag_attribute(('ProjectEnvironment', 'vcs_path'), {'widget': wdgs.TextInput})
_affk.tag_attribute(('TestConfig', 'subpath'), {'widget': wdgs.TextInput})
_affk.tag_attribute(('TestConfig', 'subpath'), {'widget': wdgs.TextInput})


_abba = uicfg.actionbox_appearsin_addmenu
_abba.tag_subject_of(('*', 'has_apycot_environment', '*'), True)
_abba.tag_object_of(('*', 'for_check', '*'), False)
_abba.tag_object_of(('*', 'during_execution', '*'), False)
_abba.tag_object_of(('*', 'using_config', '*'), False)


# urls configuration ###########################################################

class SimpleReqRewriter(urlrewrite.SimpleReqRewriter):
    rules = [
        (urlrewrite.rgx('/apycotdoc'), dict(vid='apycotdoc')),
        ]
