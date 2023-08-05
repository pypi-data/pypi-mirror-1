
from zope.interface import Attribute, Interface
from zope.component.interfaces import IObjectEvent


class IBounded(Interface):
    """A spatially bounded object."""
    bounds = Attribute("""(minx, miny, maxx, maxy) tuple""")


class ISpatiallyCataloged(Interface):
    """Marker interface."""


class IAddSpatialContainerEvent(IObjectEvent):
    """Indicates that a folder is to be cataloged."""
