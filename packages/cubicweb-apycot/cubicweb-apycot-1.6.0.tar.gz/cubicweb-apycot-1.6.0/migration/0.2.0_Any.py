add_entity('CWGroup', name=_('apycot'))
add_entity('CWUser', login=_('apycotbot'), upassword='apycot')
rql('SET U in_group G WHERE U login "apycotbot", G name "apycot"')
rql('SET U in_group G WHERE U login "apycotbot", G name "guests"')

add_entity_type('ApycotConfigGroup')

add_relation_definition('ProjectApycotConfig', 'in_state', 'State')
add_relation_definition('TrInfo', 'wf_info_for', 'ProjectApycotConfig')

for etype in ('ProjectApycotConfig',
              'ApycotExecution', 'CheckResult',
              'CheckResultLog', 'CheckResultInfo'):
    synchronize_eschema(etype)
for rtype in ('has_apycot_config', 'for_check', 'using_config', 'during_execution'):
    if rtype in schema:
        synchronize_rschema(rtype)


activatedeid = add_state(_('activated'), 'ProjectApycotConfig', initial=True)
deactivatedeid = add_state(_('deactivated'), 'ProjectApycotConfig')
add_transition(_('deactivate'), 'ProjectApycotConfig',
               (activatedeid,), deactivatedeid,
               requiredgroups=('managers',))
add_transition(_('activate'), 'ProjectApycotConfig',
               (deactivatedeid,), activatedeid,
               requiredgroups=('managers',))
checkpoint()

rql('SET X in_state S WHERE X is ProjectApycotConfig, S name "activated", S state_of ET, X is ET')
checkpoint()
