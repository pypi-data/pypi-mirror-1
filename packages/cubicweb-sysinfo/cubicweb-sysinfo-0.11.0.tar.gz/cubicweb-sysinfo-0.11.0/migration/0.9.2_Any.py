
add_relation_type('has_instance')

synchronize_eschema('Service')
synchronize_eschema('Host')
synchronize_eschema('Application')
synchronize_eschema('Device')
add_attribute('Device','klass')
