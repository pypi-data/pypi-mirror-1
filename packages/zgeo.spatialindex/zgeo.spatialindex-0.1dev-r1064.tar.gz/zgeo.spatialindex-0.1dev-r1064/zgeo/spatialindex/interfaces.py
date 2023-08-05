
from zope.interface import Interface


class ISpatiallyIndexable(Interface):
    """Marker for containers that are to be indexed.
    """


class ISpatialIndex(Interface):
    
    """Local spatial index for Zope containers.

    The index is a set-like collection of records, which are 2-tuples of
    container-local names and geographic bounding box like:

    ('foo', (-112.0, 37.0, -110.0, 39.0))
    """

    def __len__():
        """Return the number of records in the index."""

    def __iter__():
        """Support the iterator protocol."""

    def add(ob):
        """Add a record to the index.
        
        The ob parameter may be either a record tuple (described above), or
        an object that implements zgeo.geographer.interfaces.IGeoItem.
        """
    
    def remove(ob):
        """Remove a record from the index.
        
        The ob parameter may be either a record tuple (described above), or
        an object that implements zgeo.geographer.interfaces.IGeoItem. In the
        case of a record tuple, the bounding box can be optionally omitted.
        """

    def intersects(bbox):
        """Returns an iterator over records for objects which intersect the
        provided bounding box.
        
        Records are tuples of zope name and bounding box.

        Parameters
        ----------
        bbox : tuple
            (left, bottom, right, top)

        Example
        -------
        Content object 'foo' (folder/foo) is georeferenced with
        point (-105, 40).

        >>> index = ISpatialIndex(folder)
        >>> hits = index.intersects((-110,35,-100,45))
        >>> [h for h in hits]
        [('foo', (-105, 40, -105, 40))]
        """

    def destroy():
        """Irreversibly delete annotations and index files on disk."""
