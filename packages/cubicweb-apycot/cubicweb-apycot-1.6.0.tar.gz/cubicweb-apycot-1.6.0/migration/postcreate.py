# postcreate script. You could setup a workflow here for example

wf = add_workflow(u'Test configuration workflow', 'TestConfig')
activated = wf.add_state(_('activated'), initial=True)
deactivated = wf.add_state(_('deactivated'))
wf.add_transition(_('deactivate'), activated, deactivated,
                  requiredgroups=('managers',))
wf.add_transition(_('activate'), deactivated, activated,
                  requiredgroups=('managers',))

create_entity('Bookmark', title=_('quick tests summary'),
           path=u'view?rql=Any+X%2CXN+ORDERBY+XN+WHERE+X+is+TestConfig%2C+X+name+XN%2C+X+in_state+S%2C+S+name+%22activated%22&vid=summary')


if not config['pyro-server']:
    config.global_set_option('pyro-server', True)
    config.save()

