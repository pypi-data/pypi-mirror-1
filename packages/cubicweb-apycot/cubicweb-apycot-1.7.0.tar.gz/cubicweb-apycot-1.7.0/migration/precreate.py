create_entity('CWGroup', name=_('apycot'))
create_entity('CWUser', login=_('apycotbot'), upassword='apycot')
rql('SET U in_group G WHERE U login "apycotbot", G name "apycot"')
rql('SET U in_group G WHERE U login "apycotbot", G name "guests"')
