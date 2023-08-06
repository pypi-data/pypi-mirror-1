import unittest

class ZODBEvolutionManagerTests(unittest.TestCase):
    def _evolve(self, *arg, **kw):
        from repoze.evolution import evolve_to_latest
        return evolve_to_latest(*arg, **kw)

    def _getTargetClass(self):
        from repoze.evolution import ZODBEvolutionManager
        return ZODBEvolutionManager

    def _makeOne(self, root, sw_version, initial_db_version=None):
        klass = self._getTargetClass()
        context = DummyPersistent(root)
        manager = klass(context, 'repoze.evolution.tests.fixtureapp.evolve',
                        sw_version, initial_db_version)
        manager.transaction = DummyTransaction()
        return manager

    def test_verify(self):
        from repoze.evolution import IEvolutionManager
        from zope.interface.verify import verifyClass
        from zope.interface.verify import verifyObject
        klass = self._getTargetClass()
        verifyClass(IEvolutionManager, klass)
        inst = klass(None, None, None)
        verifyObject(IEvolutionManager, inst)

    def test_failure_no_db_version(self):
        root = {}
        manager = self._makeOne(root, 1)
        self.assertRaises(ValueError, self._evolve, manager)

    def test_success_initial_db_version(self):
        root = {}
        manager = self._makeOne(root, 1, 0)
        version = self._evolve(manager)
        self.assertEqual(version, 1)
        self.assertEqual(manager.context.evolved, 1)
        self.assertEqual(manager.transaction.committed, 1)
        reg = root['repoze.evolution']
        self.assertEqual(reg['repoze.evolution.tests.fixtureapp.evolve'], 1)

    def test_success_with_db_version(self):
        root = {'repoze.evolution':
                {'repoze.evolution.tests.fixtureapp.evolve':1}}
        manager = self._makeOne(root, 2)
        version = self._evolve(manager)
        self.assertEqual(version, 2)
        self.assertEqual(manager.context.evolved, 2)
        self.assertEqual(manager.transaction.committed, 1)
        reg = root['repoze.evolution']
        self.assertEqual(reg['repoze.evolution.tests.fixtureapp.evolve'], 2)

    def test_evolve_error(self):
        root = {'repoze.evolution':
                {'repoze.evolution.tests.fixtureapp.evolve':0}}
        manager = self._makeOne(root, 3)
        self.assertRaises(ValueError, self._evolve, manager)
        self.assertEqual(manager.context.evolved, 2)
        self.assertEqual(manager.transaction.committed, 2)
        reg = root['repoze.evolution']
        self.assertEqual(reg['repoze.evolution.tests.fixtureapp.evolve'], 2)

    def test_noevolve(self):
        root = {'repoze.evolution':
                {'repoze.evolution.tests.fixtureapp.evolve':1}}
        manager = self._makeOne(root, 1)
        version = self._evolve(manager)
        self.assertEqual(version, 1)
        self.assertEqual(manager.context.evolved, None)
        self.assertEqual(manager.transaction.committed, 0)
        reg = root['repoze.evolution']
        self.assertEqual(reg['repoze.evolution.tests.fixtureapp.evolve'], 1)

    def test_evolve_swver_not_integer(self):
        root = {'repoze.evolution':
                {'repoze.evolution.tests.fixtureapp.evolve':1}}
        manager = self._makeOne(root, '1')
        self.assertRaises(ValueError, self._evolve, manager)

    def test_evolve_dbver_not_integer(self):
        root = {'repoze.evolution':
                {'repoze.evolution.tests.fixtureapp.evolve':'1'}}
        manager = self._makeOne(root, 1)
        self.assertRaises(ValueError, self._evolve, manager)

class Dummy(object):
    pass

class DummyPersistent(object):
    evolved = None
    def __init__(self, root):
        self._p_jar = Dummy()
        self._p_jar.root = lambda *arg: root
        self.error = False

class DummyTransaction(object):
    committed = 0
    begun = 0
    def commit(self):
        self.committed = self.committed + 1

    def begin(self):
        self.begun = self.begun + 1



