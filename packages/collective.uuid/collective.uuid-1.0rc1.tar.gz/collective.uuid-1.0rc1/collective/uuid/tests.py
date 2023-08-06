"""Tests for the uuid utility.
"""
import unittest

from persistent import Persistent
from persistent.interfaces import IPersistent
from ZODB.interfaces import IConnection

from zope.interface import implements
from zope.interface.verify import verifyObject
from zope.location.interfaces import ILocation

from zope.app.testing import setup, ztapi
from zope.app import zapi
from zope.app.component.hooks import setSite

from collective.uuid.interfaces import IUUIDs, IUUID
from collective.uuid import UUIDs, UUID
from zope.app.keyreference.persistent import KeyReferenceToPersistent
from zope.app.keyreference.persistent import connectionOfPersistent
from zope.app.keyreference.interfaces import IKeyReference


class P(Persistent):
    implements(ILocation)


class ConnectionStub(object):
    next = 1

    def db(self):
        return self

    database_name = 'ConnectionStub'
    
    def add(self, ob):
        ob._p_jar = self
        ob._p_oid = self.next
        self.next += 1


class ReferenceSetupMixin(object):
    """Registers adapters ILocation->IConnection and IPersistent->IReference"""
    def setUp(self):
        self.root = setup.placefulSetUp(site=True)
        ztapi.provideAdapter(IPersistent, IConnection, connectionOfPersistent)
        ztapi.provideAdapter(IPersistent, IKeyReference,
                             KeyReferenceToPersistent)
        ztapi.provideAdapter(IPersistent, IUUID, UUID)

    def tearDown(self):
        setup.placefulTearDown()


class TestUUIDs(ReferenceSetupMixin, unittest.TestCase):

    def test_interface(self):
        verifyObject(IUUIDs, UUIDs())

    def test_non_keyreferences(self):
        u = UUIDs()
        obj = object()

        self.assert_(u.queryId(obj) is None)
        self.assert_(u.unregister(obj) is None)
        self.assertRaises(KeyError, u.getId, obj)

    def test(self):
        u = UUIDs()
        obj = P()
        
        obj._p_jar = ConnectionStub()

        self.assertRaises(KeyError, u.getId, obj)
        self.assertRaises(KeyError, u.getId, P())

        self.assert_(u.queryId(obj) is None)
        self.assert_(u.queryId(obj, 42) is 42)
        self.assert_(u.queryId(P(), 42) is 42)
        self.assert_(u.queryObject(42) is None)
        self.assert_(u.queryObject(42, obj) is obj)

        uid = u.register(obj)
        self.assert_(u.getObject(uid) is obj)
        self.assert_(u.queryObject(uid) is obj)
        self.assertEquals(u.getId(obj), uid)
        self.assertEquals(u.queryId(obj), uid)

        uid2 = u.register(obj)
        self.assertEquals(uid, uid2)

        u.unregister(obj)
        self.assertRaises(KeyError, u.getObject, uid)
        self.assertRaises(KeyError, u.getId, obj)

    def test_len_items(self):
        u = UUIDs()
        obj = P()
        obj._p_jar = ConnectionStub()

        self.assertEquals(len(u), 0)
        self.assertEquals(u.items(), [])
        self.assertEquals(list(u), [])

        uid = u.register(obj)
        ref = KeyReferenceToPersistent(obj)
        self.assertEquals(len(u), 1)
        self.assertEquals(u.items(), [(uid, ref)])
        self.assertEquals(list(u), [uid])

        obj2 = P()
        obj2.__parent__ = obj

        uid2 = u.register(obj2)
        ref2 = KeyReferenceToPersistent(obj2)
        self.assertEquals(len(u), 2)
        result = u.items()
        expected = [(uid, ref), (uid2, ref2)]
        result.sort()
        expected.sort()
        self.assertEquals(result, expected)
        result = list(u)
        expected = [uid, uid2]
        result.sort()
        expected.sort()
        self.assertEquals(result, expected)

        u.unregister(obj)
        u.unregister(obj2)
        self.assertEquals(len(u), 0)
        self.assertEquals(u.items(), [])

class TestSubscribers(ReferenceSetupMixin, unittest.TestCase):

    def setUp(self):
        from zope.app.folder import Folder, rootFolder

        ReferenceSetupMixin.setUp(self)

        sm = zapi.getSiteManager(self.root)
        self.utility = setup.addUtility(sm, '1', IUUIDs, UUIDs())

        self.root['folder1'] = Folder()
        self.root._p_jar = ConnectionStub()
        self.root['folder1']['folder1_1'] = self.folder1_1 = Folder()
        self.root['folder1']['folder1_1']['folder1_1_1'] = Folder()

        sm1_1 = setup.createSiteManager(self.folder1_1)
        self.utility1 = setup.addUtility(sm1_1, '2', IUUIDs, UUIDs())

    def test_removeUUIDSubscriber(self):
        from collective.uuid import removeUUIDSubscriber
        from zope.app.container.contained import ObjectRemovedEvent
        from collective.uuid.interfaces import IUUIDRemovedEvent
        parent_folder = self.root['folder1']['folder1_1']
        folder = self.root['folder1']['folder1_1']['folder1_1_1']
        id = self.utility.register(folder)
        id1 = self.utility1.register(folder)
        self.assertEquals(self.utility.getObject(id), folder)
        self.assertEquals(self.utility1.getObject(id1), folder)
        setSite(self.folder1_1)

        events = []
        ztapi.subscribe([IUUIDRemovedEvent], None, events.append)

        # This should unregister the object in all utilities, not just the
        # nearest one.
        removeUUIDSubscriber(folder, ObjectRemovedEvent(parent_folder))

        self.assertRaises(KeyError, self.utility.getObject, id)
        self.assertRaises(KeyError, self.utility1.getObject, id1)

        self.assertEquals(len(events), 1)
        self.assertEquals(events[0].object, folder)
        self.assertEquals(events[0].original_event.object, parent_folder)

    def test_addUUIDSubscriber(self):
        from collective.uuid import addUUIDSubscriber
        from zope.app.container.contained import ObjectAddedEvent
        from collective.uuid.interfaces import IUUIDAddedEvent
        parent_folder = self.root['folder1']['folder1_1']
        folder = self.root['folder1']['folder1_1']['folder1_1_1']
        setSite(self.folder1_1)

        events = []
        ztapi.subscribe([IUUIDAddedEvent], None, events.append)

        # This should register the object in all utilities, not just the
        # nearest one.
        addUUIDSubscriber(folder, ObjectAddedEvent(parent_folder))

        # Check that the folder got registered
        id = self.utility.getId(folder)
        id1 = self.utility1.getId(folder)

        self.assertEquals(len(events), 1)
        self.assertEquals(events[0].original_event.object, parent_folder)
        self.assertEquals(events[0].object, folder)

class TestUUIDAdapter(ReferenceSetupMixin, unittest.TestCase):

    def setUp(self):
        from zope.app.folder import Folder, rootFolder

        ReferenceSetupMixin.setUp(self)

        sm = zapi.getSiteManager(self.root)
        self.utility = setup.addUtility(sm, '', IUUIDs, UUIDs())

        self.root['folder1'] = Folder()
        self.root._p_jar = ConnectionStub()
        self.root['folder1']['folder1_1'] = self.folder1_1 = Folder()
        self.root['folder1']['folder1_1']['folder1_1_1'] = Folder()

        sm1_1 = setup.createSiteManager(self.folder1_1)
        self.utility1 = setup.addUtility(sm1_1, '', IUUIDs, UUIDs())

    def test(self):
        from collective.uuid import addUUIDSubscriber
        from zope.app.container.contained import ObjectAddedEvent
        from collective.uuid.interfaces import IUUIDAddedEvent
        from collective.uuid import removeUUIDSubscriber
        from zope.app.container.contained import ObjectRemovedEvent
        from collective.uuid.interfaces import IUUIDRemovedEvent
        parent_folder = self.root['folder1']['folder1_1']
        folder = self.root['folder1']['folder1_1']['folder1_1_1']
        setSite(self.folder1_1)

        events = []
        ztapi.subscribe([IUUIDAddedEvent], None, events.append)

        self.assertRaises(KeyError, getattr, IUUID(folder), 'id')

        # This should register the object in all utilities, not just the
        # nearest one.
        addUUIDSubscriber(folder, ObjectAddedEvent(parent_folder))

        # Check that the folder got registered
        id = str(self.utility.getId(folder))
        id1 = str(self.utility1.getId(folder))
        self.assertEqual(IUUID(folder).id, id1)

        events = []
        ztapi.subscribe([IUUIDRemovedEvent], None, events.append)

        # This should unregister the object in all utilities, not just the
        # nearest one.
        removeUUIDSubscriber(folder, ObjectRemovedEvent(parent_folder))

        self.assertRaises(KeyError, self.utility.getObject, id)
        self.assertRaises(KeyError, self.utility1.getObject, id1)
        self.assertRaises(KeyError, getattr, IUUID(folder), 'id')

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestUUIDs))
    suite.addTest(unittest.makeSuite(TestSubscribers))
    suite.addTest(unittest.makeSuite(TestUUIDAdapter))
    return suite

if __name__ == '__main__':
    unittest.main()
