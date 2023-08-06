from zope.interface import implements
from collective.baseid.interfaces import IIds, IIdRemovedEvent, \
     IdRemovedEvent, IIdAddedEvent, IdAddedEvent, IId
class IUUIDs(IIds):
    """A utility that assigns RFC 4122 universally unique ids to objects.

    Supports  querying object by id and id by object.
    """

class IUUIDRemovedEvent(IIdRemovedEvent):
    """A uuid will be removed.

    The event is published before the uuid is removed from the utility so that
    the indexing objects can unindex the object.
    """

class UUIDRemovedEvent(IdRemovedEvent):
    """The event which is published before the uuid is removed from
    the utility so that the catalogs can unindex the object.
    """

    implements(IUUIDRemovedEvent)

class IUUIDAddedEvent(IIdAddedEvent):
    """A uuid has been added.

    The event gets sent when an object is registered in a uuid utility.
    """

class UUIDAddedEvent(IdAddedEvent):
    """The event which gets sent when an object is registered in a uuid
    utility.
    """

    implements(IUUIDAddedEvent)

class IUUID(IId):
    """The interface which affords you a UUID.
    """