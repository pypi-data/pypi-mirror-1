from BTrees.OOBTree import OOBTree
from persistent import Persistent
from persistent.dict import PersistentDict
from persistent.mapping import PersistentMapping
from zope.component import adapts, getMultiAdapter
from zope.interface import implements, Interface

# be compatible with Zope 3.4, but prefer the modern package structure
try:
    from zope.container.folder import Folder
except ImportError:
    from zope.app.folder import Folder # BBB
try:
    from zope.container.sample import SampleContainer
except ImportError:
    from zope.app.container.sample import SampleContainer # BBB
try:
    from zope.container.btree import BTreeContainer
except ImportError:
    from zope.app.container.btree import BTreeContainer # BBB
try:
    from zope.container.ordered import OrderedContainer
except ImportError:
    from zope.app.container.ordered import OrderedContainer # BBB

from zodbbrowser.interfaces import IStateInterpreter
from zodbbrowser.history import loadState


class GenericState(object):
    """Most persistent objects represent their state as a dict."""
    adapts(Interface, dict, None)
    implements(IStateInterpreter)

    def __init__(self, type, state, tid):
        self.state = state
        self.tid = tid

    def getName(self):
        return self.state.get('__name__', '???')

    def getParent(self):
        parent = self.state.get('__parent__')
        if self.tid and isinstance(parent, Persistent):
            parent.__setstate__(loadState(parent, self.tid))
        return parent

    def listAttributes(self):
        return self.state.items()

    def listItems(self):
        return None

    def asDict(self):
        return self.state


class OOBTreeState(object):
    """Non-empty OOBTrees have a complicated tuple structure."""
    adapts(OOBTree, tuple, None)
    implements(IStateInterpreter)

    def __init__(self, type, state, tid):
        self.btree = OOBTree()
        self.btree.__setstate__(state)
        # Large btrees have more than one bucket; we have to load old states
        # to all of them
        while state and len(state) > 1:
            bucket = state[1]
            state = loadState(bucket, tid=tid)
            bucket.__setstate__(state)

    def getName(self):
        return '???'

    def getParent(self):
        return None

    def listAttributes(self):
        return None

    def listItems(self):
        return self.btree.items()

    def asDict(self):
        return self.btree # it's dict-like enough


class EmptyOOBTreeState(OOBTreeState):
    """Empty OOBTrees pickle to None."""
    adapts(OOBTree, type(None), None)
    implements(IStateInterpreter)


class PersistentDictState(GenericState):
    """Convenient access to a persistent dict's items."""
    adapts(PersistentDict, dict, None)

    def listItems(self):
        return sorted(self.state.get('data', {}).items())


class PersistentMappingState(GenericState):
    """Convenient access to a persistent mapping's items."""
    adapts(PersistentMapping, dict, None)

    def listItems(self):
        return sorted(self.state.get('data', {}).items())


class FolderState(GenericState):
    """Convenient access to a Folder's items"""
    adapts(Folder, dict, None)

    def listItems(self):
        data = self.state.get('data')
        if not data:
            return []
        # data will be an OOBTree
        loadedstate = loadState(data, tid=self.tid)
        return getMultiAdapter((data, loadedstate, self.tid),
                               IStateInterpreter).listItems()


class SampleContainerState(GenericState):
    """Convenient access to a SampleContainer's items"""
    adapts(SampleContainer, dict, None)

    def listItems(self):
        data = self.state.get('_SampleContainer__data')
        if not data:
            return []
        # data will be a PersistentDict
        loadedstate = loadState(data, tid=self.tid)
        return getMultiAdapter((data, loadedstate, self.tid),
                               IStateInterpreter).listItems()


class BTreeContainerState(GenericState):
    """Convenient access to a BTreeContainer's items"""
    adapts(BTreeContainer, dict, None)

    def listItems(self):
        # This is not a typo; BTreeContainer really uses
        # _SampleContainer__data, for BBB
        data = self.state.get('_SampleContainer__data')
        if not data:
            return []
        # data will be an OOBTree
        loadedstate = loadState(data, tid=self.tid)
        return getMultiAdapter((data, loadedstate, self.tid),
                               IStateInterpreter).listItems()


class OrderedContainerState(GenericState):
    """Convenient access to an OrderedContainer's items"""
    adapts(OrderedContainer, dict, None)

    def listItems(self):
        container = OrderedContainer()
        container.__setstate__(self.state)
        container._data.__setstate__(loadState(container._data,
                                               tid=self.tid))
        container._order.__setstate__(loadState(container._order,
                                                tid=self.tid))
        return container.items()


class FallbackState(object):
    """Fallback when we've got no idea how to interpret the state"""
    adapts(Interface, Interface, None)
    implements(IStateInterpreter)

    def __init__(self, type, state, tid):
        self.state = state

    def getName(self):
        return '???'

    def getParent(self):
        return None

    def listAttributes(self):
        return [('pickled state', self.state)]

    def listItems(self):
        return None

    def asDict(self):
        return dict(self.listAttributes())
