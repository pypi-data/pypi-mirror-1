"""template automatic tests"""

from logilab.common.testlib import TestCase, unittest_main

from cubicweb.devtools.testlib import AutomaticWebTest

from logilab.common.testlib import unittest_main
from cubicweb.devtools.testlib import AutomaticWebTest

class AutomaticWebTest(AutomaticWebTest):

    def to_test_etypes(self):
        return set(('Activity', 'Resource', 'Resourcetype'))

    def list_startup_views(self):
        # XXX needs to specify req.form['project'| 'workcase'] to test
        # [prj-]acstats views
        return ('index',) # 'actstats', 'prj-actstats' 

if __name__ == '__main__':
    unittest_main()


if __name__ == '__main__':
    unittest_main()
