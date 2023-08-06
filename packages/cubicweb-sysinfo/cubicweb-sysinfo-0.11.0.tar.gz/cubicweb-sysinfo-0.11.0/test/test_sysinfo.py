from logilab.common.testlib import unittest_main
from cubicweb.devtools.testlib import AutomaticWebTest

class AutomaticWebTest(AutomaticWebTest):
    no_auto_populate = ('Repository', 'Revision', 'VersionedFile',
                        'VersionContent', 'DeletedVersionContent')

    def to_test_etypes(self):
        return set(('Host','Application', 'NetworkService', 'Service'))

    def list_startup_views(self):
        return ('index',)

if __name__ == '__main__':
    unittest_main()
