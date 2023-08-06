"template automatic tests"

from logilab.common.testlib import TestCase, unittest_main

from cubicweb.devtools.testlib import AutomaticWebTest

class AutomaticWebTest(AutomaticWebTest):
    no_auto_populate = ('Repository', 'Revision', 'VersionedFile',
                        'VersionContent', 'DeletedVersionContent', )

if __name__ == '__main__':
    unittest_main()
