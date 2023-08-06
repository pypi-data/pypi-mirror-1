from zope.interface import implements
from zope.component import adapts

from plone.locking.interfaces import ILockable
from plone.locking.interfaces import ITTWLockable
from plone.locking.interfaces import STEALABLE_LOCK

class DummyTTWLockable(object):
    """ This class provides all methods needed of ILockable adapter.
    """

    implements(ILockable)
    adapts(ITTWLockable)

    def __init__(self, context):
        self.context = context

    def lock(self, lock_type=STEALABLE_LOCK, children=False):
        pass

    def unlock(self, lock_type=STEALABLE_LOCK, stealable_only=True):
        pass

    def clear_locks(self):
        pass

    def locked(self):
        return False

    def can_safely_unlock(self, lock_type=STEALABLE_LOCK):
        return True

    def stealable(self, lock_type=STEALABLE_LOCK):
        return True

    def lock_info(self):
        return []
