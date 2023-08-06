from zc.buildout import testing
import doctest, unittest
from zope.testing import doctest, renormalizing

def setUp(test):
    testing.buildoutSetUp(test)
    testing.install('zope.testing', test)
    testing.install_develop('zc.recipe.egg', test)
    testing.install_develop('pb.recipes.pydev', test)

def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('README.txt',
                             setUp=setUp,
                             tearDown=testing.buildoutTearDown,
                             checker=renormalizing.RENormalizing([
        testing.normalize_path,
        testing.normalize_script,
        testing.normalize_egg_py])
                             )))