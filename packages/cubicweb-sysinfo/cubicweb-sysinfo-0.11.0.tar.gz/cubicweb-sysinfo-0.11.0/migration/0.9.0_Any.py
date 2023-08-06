#add_cube('vcsfile')
#add_cube('link')
#add_cube('tag')

add_entity_type('Host')
add_entity_type('NetworkService')
add_entity_type('Application')
add_entity_type('Service')

synchronize_rschema('comments')
add_cubes('tags', 'link', 'vcsfile')

#add_relation_definition('Service', 'has_entrypoint', 'Link')
#
#add_relation_definition('Service', 'hosted_by', 'Host')
#
#add_relation_definition('VersionedFile', 'admin_doc', 'Application')
#add_relation_definition('VersionedFile', 'admin_doc', 'Service')
#
#add_relation_definition('VersionedFile', 'user_doc', 'Application')
#add_relation_definition('VersionedFile', 'user_doc', 'Service')
#add_relation_definition('Link', 'user_doc', 'Application')
#add_relation_definition('Link', 'user_doc', 'Service')
#
add_attribute('Part', 'warranty_expires')
add_attribute('Device', 'warranty_expires')

