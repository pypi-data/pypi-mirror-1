"""Univerally unique id utility

This utility assigns RFC 4122 universally unique ids (UUIDs) to objects and
supports lookups by object and by id.
"""

from BTrees import OOBTree
from uuid import uuid1
from zope.app.keyreference.interfaces import IKeyReference
from zope.component import adapts, getUtility
from zope.interface import implements
from collective.uuid.interfaces import IUUIDs, \
    UUIDAddedEvent, UUIDRemovedEvent, IUUID
from collective.baseid import Ids, RemoveIdSubscriber, AddIdSubscriber

class UUIDs(Ids):
    """This utility provides a two way mapping between objects and 
    RFC 4122 universally unique ids (UUIDs).

    IKeyReferences to objects are stored in the indexes.
    """

    implements(IUUIDs)

    def __init__(self):
        self.ids = OOBTree.OOBTree()
        self.refs = OOBTree.OOBTree()
        self.id_added_event = UUIDAddedEvent

    def _generateId(self):
        """Generates a new UUID.
        """
        return str(uuid1())

addUUIDSubscriber = AddIdSubscriber(IUUIDs, UUIDAddedEvent)
removeUUIDSubscriber = RemoveIdSubscriber(IUUIDs, UUIDRemovedEvent)

class UUID(object):
    implements(IUUID)
    adapts(IKeyReference)

    def __init__(self, context):
        self.context = context

    @property
    def id(self):
        u = getUtility(IUUIDs, context=self.context)
        return u.getId(self.context)
