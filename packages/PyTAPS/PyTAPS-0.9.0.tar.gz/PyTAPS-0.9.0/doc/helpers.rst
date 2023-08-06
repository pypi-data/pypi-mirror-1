================
 PyTAPS Helpers
================

.. module:: itaps.helpers
   :synopsis: Helper classes to simplify common operations.

OffsetList
==========

An OffsetList is a multi-dimensional jagged array. The data array is stored as a
one-dimensional array which is then indexed into with an array of offsets.

For example::

    >>> point = namedtuple('point', 'x y z')
    >>> o = OffsetList([0,2,4], point([1,2,3,4], [5,6,7,8], [9,0,1,2]))
    >>> o
    <itaps.helpers.OffsetListTuple object at 0x7f3d9922b110>
    >>> o[0]
    point(x=[1, 2], y=[5, 6], z=[9, 0])
    >>> o[0,1]
    point(x=2, y=6, z=0)
    >>> o.x
    <itaps.helpers.OffsetListSingle object at 0x7f3d9922b7d0>

.. function:: OffsetList(offsets, data)

   If `data` is a tuple, return a new :class:`OffsetListTuple` instance with the
   specified offsets and data. Otherwise, return a new :class:`OffsetListSingle`
   instance.

.. class:: OffsetListSingle(offsets, data)

   Return a new :class:`OffsetListSingle` with the specified offsets and data.

   .. describe:: len(o)

      Return the number of sub-arrays in the object `o`. Equivalent to
      ``o.length()``.

      :return: The number of sub-arrays

   .. describe:: o[i]

      Return the `i`\ th sub-array of `o`. Equivalent to
      ``o.data[ o.offsets[i]:o.offsets[i+1] ]``.

      :param i: Outer dimension of the list
      :return: The `i`\ th sub-array

   .. describe:: o[i, j]

      Return the element in the `j`\ th position of the `i`\ th sub-array of
      `o`. Equivalent to ``o.data[ o.offsets[i]+j ]``.

      :param i: Outer dimension of the list
      :param j: Index into the `i`\ th array's sub-array
      :return: The `j`\ th elements of the `i`\ th sub-array

   .. attribute:: offsets

      Return the raw offset array.

   .. attribute:: raw

      Return the raw data array.

   .. method:: length([i])

      Return the number of sub-arrays that are stored in this object.
      If `i` is specified, return the number of elements for the `i`\ th
      sub-array.

      :param i: Index of the sub-array to query
      :return: If `i` is `None`, the number of sub-arrays stored in this
               object. Otherwise, the number of elements for the `i`\ th
               sub-array.


.. class:: OffsetListTuple(offsets, data)

   Return a new :class:`OffsetListTuple` with the specified offsets and data.
   This is a subclass of :class:`OffsetListSingle`. In addition to the methods
   defined in ``OffsetListSingle``, ``OffsetListTuple`` provides the following
   methods.
   
   .. describe:: o.x

      Return a new :class:`OffsetListSingle` with the same offsets as `o` and
      data equal to ``o.data.x``. Equivalent to ``o.slice('x')``. Requires
      Python 2.6+.

      :return: A new :class:`OffsetListSingle`

   .. attribute:: fields

      Return the fields of the namedtuple used by this instance. Requires Python
      2.6+.

   .. method:: slice(field)

      Return a new :class:`OffsetListSingle` derived from this instance. If
      `field` is an integer, set the :class:`OffsetListSingle`\ 's data to
      ``data[field]``. Otherwise, set the data to ``getattr(data, field)``.
      Using non-integer values requires Python 2.6+.

      :return: A new :class:`OffsetListSingle`

   .. describe:: o[i]
                 o[i, j]

      These methods work as in an :class:`OffsetListSingle`, but return a tuple
      (or namedtuple in Python 2.6+) of the requested data.


IndexedOffsetList
=================

.. class:: IndexedOffsetList(entities, adj, indices, offsets)

   .. describe:: len(a)

      Return the number of entities in the object `a`. Equivalent to
      ``a.length()``.

   .. describe:: a[i]
                 a[i, j]

      Return the entities adjacent to the `i`\ th entity. If `j` is specified,
      returns only the `j`\ th entity of the preceding array.

      .. note::
         This method is equivalent to ``a.raw[ a.index(i, j) ]``, and relies on
         the special indexing features of NumPy arrays.

      :param i: Index of the entity to query for adjacencies
      :param j: Index into the `i` th entity's adjacency array
      :return: If `j` is specified, a single entity. Otherwise, an array of
               entities.

   .. attribute:: entities

      A one-dimensional array of entities

   .. attribute:: indices

      An index buffer into :attr:`adj`

   .. attribute:: offsets

      An array of offsets into :attr:`indices` for each of the queried entities

   .. attribute:: raw

      A one-dimensional array of all the data referenced by the elements of
      :attr:`entities`

   .. method:: index(i[, j])

      Return the indices of the entities adjacent to the `i`\ th entity. If `j`
      is specified, returns only the `j`\ th index of the preceding array.

      :param i: Index of the entity to query for adjacencies
      :param j: Index into the `i`\ th entity's adjacency array
      :return: If `j` is specified, a single index. Otherwise, an array of
               indices.

      .. note::
         This method is equivalent to ``indices[ offsets[i]:offsets[i+1] ]``
         when only `i` is specified, and is equivalent to
         ``indices[ offsets[i]+j ]`` when both `i` and `j` are specified.

   .. method:: length([i])

      Return the number of entities whose adjacencies are stored in this object.
      If `i` is specified, return the number of adjacencies for the `i`\ th
      entity.

      :param i: Index of the entity to query
      :return: If `i` is `None`, the number of entities whose adjacencies
               are stored. Otherwise, the number of adjacencies for the
               `i`\ th entity.
