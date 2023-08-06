=================
 iMesh Interface
=================

.. module:: itaps.iMesh
   :synopsis: Basic services to manage a discrete mesh composed of sets of
              entities.

Mesh
====

.. class:: Mesh([options])

   Return a new :class:`Mesh` object with any implementation-specific options
   defined in `options`.

   :param options: Implementation-specific options string

   .. attribute:: rootSet

      Return the handle of the root set for this instance. The entire mesh in
      this instance can be accessed from this set.

   .. attribute:: geometricDimension

      Get/set the geometric dimension of mesh represented in this instance.
      When setting the dimension, an application should not expect this
      function to succeed unless the mesh database is empty (no vertices
      created, no files read, etc.)

   .. attribute:: defaultStorage

      Return the default storage order used by this implementation.

   .. attribute:: adjTable

      Return the adjacency table for this implementation.  This table is a 4x4
      matrix, where `adjTable[i][j]` represents the relative cost of retrieving
      adjacencies between entities of dimension `i` to entities of dimension
      `j`.

   .. method:: areEHValid(reset)

      Return whether entity handles have changed since last reset or since
      instance construction. If true, it is not guaranteed that a handle from
      before the last call to this function represents the same entity as the
      same handle value does now. If `reset` is true, resets the starting
      point for this function.

      :param reset: If true, perform a reset on the starting point after
                    which handles are invariant.
      :return: True iff entity handles have changed

   .. method:: getVtxCoords(entities[, storage_order])

      Get coordinates of specified vertices. If `entities` is an array of
      entity handles, `storage_order` is required. Otherwise, it is unused.

      :param entities: Entity or array of entities being queried
      :param storage_order: Storage order of vertices to be returned
      :return: If `entities` is a single :class:`~itaps.iBase.Entity`, the
               coordinates of the vertex. Otherwise, an array of coordinates.

   .. method:: getEntType(entities)

      Get the entity type for the specified entities.

      :param entities: Entity or array of entities being queried
      :return: If `entities` is a single :class:`~itaps.iBase.Entity`, the type
               of the entity. Otherwise, an array of the entity types.

   .. method:: getEntTopo(entities)

      Get the entity topology for the specified entities.

      :param entities: Entity or array of entities being queried
      :return: If `entities` is a single :class:`~itaps.iBase.Entity`, the
               topology of the entity. Otherwise, an array of the entity
               topologies.

   .. method:: getEntAdj(entities, type)

      Get entities of the specified type adjacent to elements of `entities`. If
      `entities` is a single :class:`~itaps.iBase.Entity`, returns an array of
      adjacent entities. If `entities` is an array of entities, return an
      :class:`~itaps.helpers.OffsetListSingle` instance.

      :param entities: Entity or array of entities being queried
      :param type: Type of adjacent entities being requested
      :return: If `entities` is a single :class:`~itaps.iBase.Entity` an array
               of adjacent entities. Otherwise, an
               :class:`~itaps.helpers.OffsetListSingle` instance.

   .. method:: getEnt2ndAdj(entities, bridge_type, type)

      Get "2nd order" adjacencies to an array of entities, that is, from each 
      entity, through other entities of a specified "bridge" dimension, to
      other entities of another specified "to" dimension. If `entities` is a
      single :class:`~itaps.iBase.Entity`, returns an array of adjacent
      entities. If `entities` is an array of entities, return an
      :class:`~itaps.helpers.OffsetListSingle` instance.

      :param entities: Entity or array of entities being queried
      :param bridge_type: Type of bridge entity for 2nd order adjacencies
      :param type: Type of adjacent entities being requested
      :return: If `entities` is a single :class:`~itaps.iBase.Entity`, an array
               of adjacent entities. Otherwise, an
               :class:`~itaps.helpers.OffsetListSingle` instance.

   .. method:: createEntSet(ordered)

      Create an :class:`EntitySet`, either ordered or unordered. Unordered
      entity sets can contain a given entity or set only once.

      :param ordered: True if the list should be ordered, false otherwise
      :return: The newly-created :class:`EntitySet`

   .. method:: destroyEntSet(set)

      Destroy an entity set.

      :param set: Entity set to be destroyed

   .. method:: setVtxCoords(entities, coords[, storage_order])

      Set the coordinates for the specified vertex or array of vertices. If
      `entities` is an array of vertices, `storage_order` must be specified;
      otherwise it is ignored.

      :param entities: Vertex handle or array of vertex handles being set
      :param coords: New coordinates to assign to vertices
      :param storage_order: Storage order of coordinates to be assigned

   .. method:: createVtx(coords[, storage_order])

      Create a vertex or array of vertices with the specified coordinates. If
      creating multiple vertices, `storage_order` must be specified; otherwise
      it is ignored.

      :param coords: Coordinates of new vertices to create
      :param storage_order: Storage order of coordinates

   .. method:: createEnt(topo, entities)

      Create a new entity with the specified lower-order topology.

      :param topo: Topology of the entity to be created
      :param entities: Array of lower order entity handles used to construct
                       new entity
      :return: Tuple containing the created entity and its creation status

   .. method:: createEntArr(topo, entitites)

      Create an array of new entities with the specified lower-oder topology.

      :param topo: Topology of the entities to be created
      :param entities: Array of lower order entity handles used to construct
                       new entities
      :return: Tuple containing the created entities and their creation statuses

   .. method:: deleteEnt(entities)

      Delete the specified entity or array of entities.

      :param entities: An entity or array of entities to delete

   .. method:: createTag(name, size, type)

      Create a :class:`Tag` with specified `name`, `size`, and `type`. The tag's
      `size` is the number of values of type `type` that can be held. `type` is
      one of the following:

      +-------+---------------+
      | ``i`` | Integer       |
      +-------+---------------+
      | ``d`` | Double        |
      +-------+---------------+
      | ``E`` | Entity handle |
      +-------+---------------+
      | ``b`` | Binary data   |
      +-------+---------------+

      :param name: Tag name
      :param size: Size of tag in number of values
      :param type: Character representing the tag's type
      :return: The created :class:`Tag`

   .. method:: destroyTag(tag, force)

      Destroy a :class:`Tag`. If `force` is true and entities still have
      values set for this tag, the tag is deleted anyway and those values
      disappear. Otherwise the tag is not deleted if entities still have values
      set for it.

      :param tag: :class:`Tag` to delete
      :param forced: True if the tag should be deleted even if there are values
                     set for it

   .. method:: getTagHandle(name)

      Get the handle of an existing tag with the specified `name`.

      :param name: The name of the tag to find
      :return: The :class:`Tag` with the specified name

   .. method:: getAllTags(entities)

      Get all the tags associated with a specified entity or entity set.

      :param entities: Entity or entity set being queried
      :return: Array of :class:`Tag`\ s associated with `entities`

Forwarding
----------

In addition to the methods listed above, :class:`Mesh` automatically forwards
method calls to the root :class:`EntitySet`. Thus, ::

  mesh.getEntities(iBase.Type.all, iMesh.Topology.all)

is equivalent to::

  mesh.rootSet.getEntities(iBase.Type.all, iMesh.Topology.all)

EntitySet
=========

.. class:: EntitySet(set[, instance])

   Return a new set referring to the handled contained in  `set`. If `set` is
   an :class:`itaps.iBase.EntitySet` instance, `instance` must also be
   specified.

   .. attribute:: instance

      Return the :class:`Mesh` instance from which this entity set was created.

   .. attribute:: isList

      Return whether this entity set is ordered.

   .. method:: load(filename[, options])

      Load a mesh from a file, adding it to this entity set.

      :param filename: File name from which the mesh is to be loaded
      :param options: Implementation-specific options string

   .. method:: save(filename[, options])

      Save the subset of the mesh contained in this entity set to a file.

      :param filename: File name to which the mesh is to be saved
      :param options: Implementation-specific options string

   .. method:: getNumOfType(type)

      Get the number of entities with the specified type in this entity set.

      :param type: Type of entity requested
      :return: The number of entities in entity set of the requested type

   .. method:: getNumOfTopo(topo)

      Get the number of entities with the specified topology in this entity set.

      :param type: Topology of entity requested
      :return: The number of entities in the entity set of the requested
               topology

   .. method:: getEntities(type, topo)

      Get entities of a specific type and/or topology in this entity set. All 
      entities of a given type or topology are requested by specifying
      :attr:`itaps.iBase.Type.all` or :attr:`itaps.iMesh.Topology.all`,
      respectively.

      :param type: Type of entities being requested
      :param topo: Topology of entities being requested
      :return: Array of entity handles from this entity set meeting the
               requirements of `type` and `topo`

   .. method:: getAdjEntIndices(type, topo, adj_type)

      Given an entity set and optionally a type or topology, return an
      :class:`~itaps.helpers.IndexedOffsetList` containing the following:

      * The entities in the set of the specified type and/or topology
      * An index buffer containing, for each entity in the first list,
        the indices of the entities adjacent to it
      * An array of offsets into the index buffer for each entity in the first
        list
      * The entities adjacent to those entities with the specified type
        `adj_type`, as a list of unique handles

      :param type: Type of entities being requested
      :param topo: Topology of entities being requested
      :param adjType: Type of adjacent entities being requested
      :return: An :class:`~itaps.helpers.IndexedOffsetList` instance

   .. method:: getNumEntSets(hops)

      Get the number of sets contained in this entity set. If this entity set is
      not the root set, `hops` indicates the maximum number of contained
      sets from this set to one of the contained sets, inclusive of this set.

      :param hops: Maximum number of contained sets from this sset to a
                   contained set, including itself
      :return: Number of entity sets found

   .. method:: getEntSets(hops)

      Get the sets contained in this entity set. If this entity set is not the
      root set, `hops` indicates the maximum number of contained sets from
      this set to one of the contained sets, inclusive of this set.

      :param hops: Maximum number of contained sets from this set to a
                   contained set, including itself
      :return: Array of entity sets found      

   .. method:: add(entities)

      Add an entity, entity set, or array of entities to this entity set.

      :param entities: The entity, entity set, or array of entities to add

   .. method:: remove(entities)

      Remove an entity, entity set, or array of entities from this entity set.

      :param entities: The entity, entity set, or array of entities to remove

   .. method:: contains(entities)

      Return whether an entity, entity set, or array of entities is contained
      in this entity set.

      :param entities: The entity, entity set, or array of entities to query
      :return: If `entities` is an array of entities, an array of booleans
               corresponding to each element of `entities`. Otherwise, a
               single boolean.

   .. method:: addChild(set)

      Add `set` as a child to this entity set.

      :param set: The entity set to add

   .. method:: removeChild(set)

      Remove `set` as a child from this entity set.

      :param set: The entity set to remove

   .. method:: isChild(set)

      Return whether an entity set is a child of this entity set.

      :param set: The entity set to query
      :return: True if `set` is a child of this entity set, false otherwise

   .. method:: getNumChildren(hops)

      Get the number of child sets linked from this entity set. If `hops`
      is non-zero, this represents the maximum hops from this entity set to any
      child in the count.

      :param hops: Maximum hops from this entity set to a child set,
                   inclusive of the child set
      :return: Number of children

   .. method:: getNumParents(hops)

      Get the number of parent sets linked from this entity set. If `hops`
      is non-zero, this represents the maximum hops from this entity set to any
      parents in the count.

      :param hops: Maximum hops from this entity set to a parent set,
                   inclusive of the parent set
      :return: Number of parents

   .. method:: getChildren(hops)

      Get the child sets linked from this entity set. If `hops` is
      non-zero, this represents the maximum hops from this entity set to any
      child in the result.

      :param hops: Maximum hops from this entity set to a child set,
                   inclusive of the child set
      :return: Array of children

   .. method:: getParents(hops)

      Get the parents sets linked from this entity set. If `hops` is
      non-zero, this represents the maximum hops from this entity set to any
      parent in the result.

      :param hops: Maximum hops from this entity set to a parent set,
                   inclusive of the parent set
      :return: Array of parents

   .. method:: iterate(type, topo[, count=1])

      Initialize an :class:`Iterator` over the specified entity type and
      topology for this entity set. If `count` is greater than 1, each step
      of the iteration returns an array of `count` entities. Equivalent to::

        itaps.iMesh.Iterator(self, type, topo, count)

      :param type: Type of entities being requested
      :param topo: Topology of entities being requested
      :param count: Number of entities to return on each step of iteration
      :return: An :class:`Iterator` instance

   .. method:: difference(set)

      Subtract contents of an entity set from this set. Equivalent to
      ``self - set``.

      :param set: Entity set to subtract
      :return: Resulting entity set

   .. method:: intersection(set)

      Intersect contents of an entity set with this set. Equivalent to
      ``self & set``.

      :param set: Entity set to intersect
      :return: Resulting entity set

   .. method:: union(set)

      Unite contents of an entity set with this set. Equivalent to
      ``self | set``.

      :param set: Entity set to unite
      :return: Resulting entity set


Iterator
========

.. class:: Iterator(set, type, topology[, count=1])

   Return a new iterator on the entity set `set` to iterate over entities of
   the specified `type` and `topology`. If `size` is greater than 1, each
   step of the iteration will return an array of `size` entities. All
   entities of a given type or topology are requested by specifying 
   :attr:`itaps.iBase.Type.all` or :attr:`itaps.iMesh.Topology.all`,
   respectively.

   :param set: Entity set to iterate over
   :param type: Type of entities being requested
   :param topo: Topology of entities being requested
   :param count: Number of entities to return on each step of iteration

   .. attribute:: instance

      Return the :class:`Mesh` instance from which this iterator was created.

   .. method:: reset()

      Resets the iterator to the beginning.


Tag
===

.. class:: Tag(tag[, instance])

   Return a new tag referring to the handled contained in  `tag`. If `tag` is
   an :class:`itaps.iBase.Tag` instance, `instance` must also be specified.

   .. attribute:: instance

      Return the :class:`Mesh` instance from which this tag was created.

   .. attribute:: name

      Get the name for this tag.

   .. attribute:: sizeValues

      Get the size in number of values for this tag.

   .. attribute:: sizeBytes

      Get the size in bytes for this tag.

   .. attribute:: type

      Get the data type for this tag as a character code (see above).

   .. method:: setData(entities, data[, type])

      Set value(s) for the tag on an entity, entity set, or array of entities.
      If `type` is not specified, this function will retrieve the tag type
      automatically.

      :param entities: Entity, entity set, or array of entities on which tag is
                       being set
      :param data: Data to set
      :param type: Character representing the tag's type (as above)

   .. method:: getData(entities[, type])

      Get value(s) for the tag on an entity, entity set, or array of entities.
      If `type` is not specified, this function will retrieve the tag type
      automatically.

      :param entities: Entity, entity set, or array of entities on which tag is
                       being retrieved
      :param type: Character representing the tag's type (as above)
      :return: The retrieved data

   .. method:: remove(entities)

      Remove the tag value from an entity, entity set, or array of entities.

      :param entities: Entity, entity set, or array of entities from which tag
                       is being removed

Topology
========

.. class:: Topology

   An enumeration of mesh element topologies corresponding to
   ``iMesh_EntityTopology``.

   .. data:: point

      A general zero-dimensional entity

   .. data:: line_segment

      A general one-dimensional entity

   .. data:: polygon

      A general two-dimensional element

   .. data:: triangle

      A three-sided, two-dimensional element

   .. data:: quadrilateral

      A four-sided, two-dimensional element

   .. data:: polyhedron

      A general three-dimensional element

   .. data:: tetrahedron

      A four-sided, three-dimensional element whose faces are triangles

   .. data:: hexahedron

      A six-sided, three-dimensional element whose faces are quadrilaterals

   .. data:: prism

      A five-sided, three-dimensional element which has three quadrilateral
      faces and two triangular faces

   .. data:: pyramid

      A five-sided, three-dimensional element which has one quadrilateral face
      and four triangular faces

   .. data:: septahedron

      A hexahedral entity with one collapsed edge

   .. data:: all

      Allows the user to request information about all the topology types
