import os.path
import z3c.testsetup
import d2m.wsgiapp
from zope.app.testing.functional import ZCMLLayer


ftesting_zcml = os.path.join(
    os.path.dirname(d2m.wsgiapp.__file__), 'ftesting.zcml')
FunctionalLayer = ZCMLLayer(ftesting_zcml, __name__, 'FunctionalLayer')

test_suite = z3c.testsetup.register_all_tests('d2m.wsgiapp')

