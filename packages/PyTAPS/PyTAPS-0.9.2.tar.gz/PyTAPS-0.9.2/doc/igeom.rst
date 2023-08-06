=================
 iGeom Interface
=================

.. module:: itaps.iGeom
   :synopsis: Basic services to manage continuous geometry composed of sets of
              entities.

Geom
====

.. class:: Geom([options])

   Return a new :class:`Geom` object with any implementation-specific options
   defined in `options`.

   :param options: Implementation-specific options string

   .. attribute:: rootSet

      Return the handle of the root set for this instance. The entire geometry
      in this instance can be accessed from this set.

   .. attribute:: boundBox

      Return the bounding box of the entire model.

   .. attribute:: topoLevel

      Return the topology level of the geometry as an integer, where 0 = basic
      entities only, 1 = manifold entities, 2 = non-manifold entities.

   .. attribute:: parametric

      Return True if the interface has information about parameterization, False
      otherwise.

   .. attribute:: tolerance

      Return a tuple representing the tolerance at the modeler level. The first
      value is an integer representing the type of the tolerance, where 0 = no
      tolerance information, 1 = modeler-level tolerance, 2 = entity-level
      tolerances. If this value is 1, the second value returns the modeler-level
      tolerance. If this value is 2, use :meth:`getEntTolerance` to query the
      tolerance on a per-entity basis.

   .. method:: load(filename[, options])

      Load a geometry from a file.

      :param filename: File name from which the geometry is to be loaded
      :param options: Implementation-specific options string

   .. method:: save(filename[, options])

      Save the geometry to a file.

      :param filename: File name to which the geometry is to be saved
      :param options: Implementation-specific options string

   .. method:: getEntType(entities)

      Get the entity type for the specified entities.

      :param entities: Entity or array of entities being queried
      :return: If `entities` is a single :class:`~itaps.iBase.Entity`, the type
               of the entity. Otherwise, an array of the entity types.

   .. method:: getEntAdj(entities, type)

      Get entities of the specified type adjacent to elements of `entities`.
      If `entities` is a single :class:`~itaps.iBase.Entity`, returns an array
      of adjacent entities. If `entities` is an array of entities, return an
      :class:`~itaps.helpers.OffsetListSingle` instance.

      :param entities: Entity or array of entities being queried
      :param type: Type of adjacent entities being requested
      :return: If `entities` is a single :class:`~itaps.iBase.Entity`, an array
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

   .. method:: isEntAdj(entities1, entities2)

      Return an array indicating whether the entities in the array `entities1`
      are pairwise adjacent to those in `entities2`. If `entities1` is a single
      :class:`~itaps.iBase.Entity` or an array with one element, then return an
      array indicating that entity's adjacency with each entity in `entities2`
      (a similar case exists when `entities2` is a single entity).

      :param entities1: Entity or array of entities being queried
      :param entities2: Entity or array of entities being queried
      :return: If `entities1` and `entities2` are both single
               :class:`Entities <itaps.iBase.Entity>`, a boolean indicating
               whether they are adjacent. Otherwise, an array of booleans.

   .. method:: getEntClosestPt(entities, coords[, storage_order])

      Return the pairwise closest points on `entities` to the points specified
      in `coords`. If `entities` is a single :class:`~itaps.iBase.Entity` or an
      array with one element, return the closest points on that entity to the
      points in `coords`. Likewise, if `coords` is a single point, return the
      closest points on each of `entities` to that point.

      :param entities: Entity or array of entities being queried
      :param coords: XYZ coordinate(s) being queried
      :param storage_order: Storage order of the vertices supplied and returned
      :return: If `entities` is a single :class:`~itaps.iBase.Entity`, and
               `coords` is a vector, return a vector representing the closest 
               point. Otherwise, return an array of vectors.

   .. method:: getEntNormal(entities, coords[, storage_order, basis=Basis.xyz])

      Return the pairwise normals on `entities` at the points specified in
      `coords`. If `entities` is a single :class:`~itaps.iBase.Entity` or an
      array with one element, return the normals on that entity at the points
      in `coords`. Likewise, if `coords` is a single point, return the normals
      on each of `entities` at that point.

      :param entities: Entity or array of entities being queried
      :param coords: Coordinate(s) being queried
      :param storage_order: Storage order of the vertices supplied and returned
      :param basis: The :class:`Basis` of the supplied coordinates
      :return: If `entities` is a single :class:`~itaps.iBase.Entity`, and
               `coords` is a vector, return a vector representing the normal.
               Otherwise, return an array of vectors.

   .. method:: getEntNormalPl(entities, coords[, storage_order])

      Return the pairwise closest points and normals on `entities` to/at the
      points specified in `coords`. If `entities` is a single
      :class:`~itaps.iBase.Entity` or an array with one element, return the
      closest points/normals on that entity at the points in `coords`.
      Likewise, if `coords` is a single point, return the closest points/normals
      on each of `entities` at that point.

      :param entities: Entity or array of entities being queried
      :param coords: XYZ coordinate(s) being queried
      :param storage_order: Storage order of the vertices supplied and returned
      :return: If `entities` is a single :class:`~itaps.iBase.Entity`, and
               `coords` is a vector, return a tuple of the closest point and the
               normal. Otherwise, return a tuple of arrays of the closest points
               and normals.

   .. method:: getEntTangent(entities, coords[, storage_order, basis=Basis.xyz])

      Return the pairwise tangents on `entities` at the points specified in
      `coords`. If `entities` is a single :class:`~itaps.iBase.Entity` or an
      array with one element, return the tangents on that entity at the points
      in `coords`. Likewise, if `coords` is a single point, return the tangents
      on each of `entities` at that point.

      :param entities: Entity or array of entities being queried
      :param coords: Coordinate(s) being queried
      :param storage_order: Storage order of the vertices supplied and returned
      :param basis: The :class:`Basis` of the supplied coordinates
      :return: If `entities` is a single :class:`~itaps.iBase.Entity`, and
               `coords` is a vector, return a vector representing the tangent.
               Otherwise, return an array of vectors.

   .. method:: getEntCurvature(entities, coords[, storage_order, basis=Basis.xyz, type])

      Return the pairwise curvatures on `entities` at the points specified in
      `coords`. If `entities` is a single :class:`~itaps.iBase.Entity` or an
      array with one element, return the curvatures on that entity at the points
      in `coords`. Likewise, if `coords` is a single point, return the
      curvatures on each of `entities` at that point.

      If `type` is specified, this method assumes that the elements of
      `entities` are of that type. Otherwise, the type is inferred from the
      first element of `entities`.

      :param entities: Entity or array of entities being queried
      :param coords: Coordinate(s) being queried
      :param storage_order: Storage order of the vertices supplied and returned
      :param basis: The :class:`Basis` of the supplied coordinates
      :param type: The :class:`~itaps.iBase.Type` of the supplied entities
      :return: If `entities` or `coords` are arrays, a pair of arrays of vectors
               representing the two curvatures of each entity. Otherwise, either
               1) a single curvature vector when `entities` is a single
               :data:`~itaps.iBase.Type.edge`, a vector, or 2) a pair of
               curvature vectors when `entities` is a single
               :data:`~itaps.iBase.Type.face`.

      .. note::
         If `entities` or `coords` are arrays, this method will always return
         pairs of curvatures, even for edges. Only the first curvature is valid,
         however.

   .. method:: getEntEval(entities, coords[, storage_order, type])

      Return pairwise data about `entities` at the points specified in `coords`.
      If `entities` is a single :class:`~itaps.iBase.Entity` or an array with
      one element, return the data for that entity at the points in `coords`.
      Likewise, if `coords` is a single point, return the data for each of
      `entities` at that point.

      The data returned depends on the type of the entities. If `type` is
      :data:`~itaps.iBase.Type.edge`, return the closest point, tangent, and
      curvature of `entities` at `coords`. If `type` is
      :data:`~itaps.iBase.Type.face`, return the closest point, normal, and both
      curvatures of `entities` at `coords`. If `type` is unspecified, it is
      inferred from the first element of `entities`.

      :param entities: Entity or array of entities being queried
      :param coords: Coordinate(s) being queried
      :param storage_order: Storage order of the vertices supplied and returned
      :param type: The :class:`~itaps.iBase.Type` of the supplied entities
      :return: If `entities` or `coords` are arrays, a tuple of arrays of
               vectors representing the data for each entity. Otherwise, a tuple
               of vectors.

   .. method:: getEnt1stDerivative(entities, coords[, storage_order])

      Return pairwise data about the 1st deriviative of the specified `entities`
      at `coords` as an :class:`~itaps.helpers.OffsetListTuple` instance with 
      fields named `u` and `v`.

      :param entities: Entity or array of entities being queried
      :param coords: Coordinate(s) being queried
      :param storage_order: Storage order of the vertices supplied and returned
      :return: If `entities` is a single :class:`~itaps.iBase.Entity`, a pair of
               vectors representing the 1st derivative. Otherwise, an
               :class:`~itaps.helpers.OffsetListTuple` instance with fields
               named `u` and `v`.

   .. method:: getEnt2ndDerivative(entities, coords[, storage_order])

      Return pairwise data about the 2nd deriviative of the specified `entities`
      at `coords` as an :class:`~itaps.helpers.OffsetListTuple` instance with
      fields named `uu`, `vv`, and `uv`.

      :param entities: Entity or array of entities being queried
      :param coords: Coordinate(s) being queried
      :param storage_order: Storage order of the vertices supplied and returned
      :return: If `entities` is a single :class:`~itaps.iBase.Entity`, a triple
               of vectors representing the 2nd derivative. Otherwise, an
               :class:`~itaps.helpers.OffsetListTuple` instance with fields
               named `uu`, `vv`, and `uv`.

   .. method:: getEntBoundBox(entities[, storage_order])

      Return the bounding box for the specified entities. If `entities` is an
      array of entity handles, `storage_order` is required. Otherwise, it is
      unused.

      :param entities: Entity or array of entities being queried
      :param storage_order: Storage order of vertices to be returned
      :return: If `entities` is a single :class:`~itaps.iBase.Entity`, the
               coordinates of the bounding box. Otherwise, an array of
               coordinates.

   .. method:: getVtxCoords(src[, storage_order, dest])

      Get the coordinates of the vertices specified in `src`. If `entities` is
      an array of entity handles, `storage_order` is required. Otherwise, it is
      unused.

      If `dest` is supplied, return parameterized coordinates relative to the
      entity or entities specified in `dest`. `dest` may either be an entity (or
      array of entities) or a tuple of the entities and the basis of the
      parameterized coordinates. If the basis is not specified, it is inferred
      from the first entity in `dest`.

      With `dest` supplied, if `src` is a single :class:`~itaps.iBase.Entity`
      or an array with one element, return the coordinates of that entity
      relative to each entity in `dest`. Likewise, if `dest` is a single entity,
      return the coordinates of each of `src` relative to that entity.

      :param src: Vertex or array of vertices being queried
      :param storage_order: Storage order of vertices to be returned
      :param dest: Either 1) an entity or array of entities, or 2) a tuple
                   containing (1) followed by the expected basis of the
                   coordinates.
      :return: If `entities` and `dest` (if specified) are both single
               :class:`Entities <itaps.iBase.Entity>`, the coordinates of `src`.
               Otherwise, an array of coordinates.      

   .. method:: getEntCoords(coords[, storage_order, src, dest])

      Transform the supplied `coords` relative to the bases in `src` and `dest`.
      If `entities` is an array of entity handles, `storage_order` is required.
      Otherwise, it is unused.

      `src` and `dest`, if supplied, represent the parameterization of the input
      and output coordinates, respectively. Both may either be an entity (or
      array of entities) or a tuple of the entities and the basis of the
      parameterized coordinates. If the basis is not specified, it is inferred
      from the first entity in `src` or `dest`.

      If `src` is supplied, `coords` should be parameterized relative to the
      entities in `src`.  If `src` is a single :class:`~itaps.iBase.Entity`
      or an array with one element, transform the coordinates of each element in
      `coords` relative to that element. Likewise, if `coords` is a single
      vector, transform the its coordinates relative to that each entity in
      `src`.

      If `dest` is supplied, the resulting coordinates will be parameterized
      relative to the entities in `dest`. A similar relation between arrays and
      single elements of `dest` exists as with `src`.

      :param coords: Coordinate(s) being queried
      :param storage_order: Storage order of the coordinates supplied and
                            returned
      :param src: Either 1) an entity or array of entities, or 2) a tuple
                  containing (1) followed by the expected basis of the
                  coordinates.
      :param dest: Either 1) an entity or array of entities, or 2) a tuple
                   containing (1) followed by the expected basis of the
                   coordinates.
      :return: If `source` is a single vector, and `src` and `dest` (if
               specified) are both single
               :class:`Entities <itaps.iBase.Entity>`, then a single transformed
               coordinates. Otherwise, an array of coordinates.

   .. method:: getEntRange(entities[, storage_order, basis])

      Return the parametric range of the specified `entities`. If `basis` is
      specified, assume that the parameterization of `entities` is in that
      basis. Otherwise, infer the basis from the first element of `entities`.

      :param entities: Entity or array of entities being queried
      :param storage_order: Storage order of the vectors returned
      :param basis: The :class:`Basis` of the supplied coordinates
      :return: If `entities` is a single :class:`~itaps.iBase.Entity`, a pair
               of vectors representing the parametric range. Otherwise, A pair
               of arrays of vectors.

   .. method:: getPtRayIntersect(points, vectors, storage_order)

      Intersect a ray or rays with the model and return the entities
      intersected, the coordinates of intersection, and the distances along the
      ray(s) at which the intersection occurred. If `points` and `vectors` are
      single vectors, return a tuple containing the above data. If both are
      arrays of vectors, return an :class:`~itaps.helpers.OffsetListTuple`
      instance with fields named `entities`, `isect`, and `param`.

      :param points: Vector or array of vectors for the sources of the rays
      :param vectors: Vector or array of vectors for the direction of the rays
      :param storage_order: Storage order of the vectors returned
      :return: If `points` and `vectors` are single vectors, a tuple of
               intersection data. If both are arrays of vectors, an
               :class:`~itaps.helpers.OffsetListTuple` instance with fields
               named `entities`, `isect`, and `param`.

   .. method:: getPtClass(points[, storage_order])

      Return the entity (or entities) on which a point (or points) lies.

      :param points: Point or array of points to query
      :param storage_order: Storage order of the points supplied
      :return: If `points` is a single point, the entity on which it lies.
               Otherwise, an array of entities.

   .. method:: getEntNormalSense(faces, regions)

      Return the pairwise sense of a face or array of faces with respect to a
      region or array of regions. The sense is returned as -1, 0, or 1,
      representing "reversed", "both", or "forward". A sense value of "both"
      indicates that face bounds the region once with each sense.

      If `faces` is a single :class:`~itaps.iBase.Entity` or an array with one
      element, return the sense of that entity with respect to each entity in
      `regions`. Likewise, if `regions` is a single
      :class:`~itaps.iBase.Entity`, return the sense of each of `faces` with
      respect to that region.

      :param faces: The face or array of faces to query
      :param regions: The region or array of regions to query
      :return: If `faces` and `regions` are both single
               :class:`Entities <itaps.iBase.Entity>`, return the sense (as an
               integer). Otherwise, return an array of senses.

   .. method:: getEgFcSense(edges, faces)

      Return the pairwise sense of an edge or array of edges with respect to a
      faces or array of faces. The sense is returned as -1, 0, or 1,
      representing "reversed", "both", or "forward". A sense value of "both"
      indicates that edge bounds the face once with each sense.

      If `edges` is a single :class:`~itaps.iBase.Entity` or an array with one
      element, return the sense of that entity with respect to each entity in
      `faces`. Likewise, if `faces` is a single :class:`~itaps.iBase.Entity`,
      return the sense of each of `edges` with respect to that face.

      :param edges: The edge or array of edges to query
      :param faces: The face or array of faces to query
      :return: If `edges` and `faces` are both single
               :class:`Entities <itaps.iBase.Entity>`, return the sense (as an
               integer). Otherwise, return an array of senses.

   .. method:: getEgVtxSense(edges, vertices1, vertices2)

      Return the pairwise sense of a pair of vertices or pair of array of
      vertices with respect to an edge or array of edges. The sense is returned
      as -1, 0, or 1, representing "reversed", "both", or "forward". A sense
      value of "both" indicates that the vertices bound the edge once with each
      sense.

      If `vertices1` and `vertices2` are both single
      :class:`Entities <itaps.iBase.Entity>` or arrays with one element each,
      return the sense of those vertices with respect to each entity in
      `edges`. Likewise, if `edges` is a single :class:`~itaps.iBase.Entity`,
      return the sense of each of `vertices1` and `vertices2` with respect to
      that edge.

      :param edges: The edge or array of edges to query
      :param vertices1: The first vertex or array of vertices to query
      :param vertices2: The second vertex or array of vertices to query
      :return: If `edges`, `vertices1`, and `vertices2` are alll single
               :class:`Entities <itaps.iBase.Entity>`, return the sense (as an
               integer). Otherwise, return an array of senses.

   .. method:: measure(entities)

      Return the measure (length, area, or volume, as applicable) of the
      specified `entities`.

      :param entities: Entity or array of entities being queried
      :return: If `entities` is a single :class:`~itaps.iBase.Entity`, the
               measure of that entity. Otherwise, an array of measures.

   .. method:: getFaceType(entity)

      Return an implementation-defined string describing the type of the
      specified face.

      :param entity: The entity to query
      :return: A string describing the face's type

   .. method:: isEntParametric(entities)

      Return whether the specified `entities` have parameterization.

      :param entities: Entity or array of entities being queried
      :return: If `entities` is a single :class:`~itaps.iBase.Entity`, a boolean
               representing whether the entity has parameterization. Otherwise,
               an array of booleans.

   .. method:: isEntPeriodic(entities)

      Return whether the specified `entities` are periodic.

      :param entities: Entity or array of entities being queried
      :return: If `entities` is a single :class:`~itaps.iBase.Entity`, a boolean
               representing whether the entity is periodic. Otherwise, an array
               of booleans.

   .. method:: isFcDegenerate(entities)

      Return whether the specified faces are degenerate.

      :param entities: Entity or array of entities being queried
      :return: If `entities` is a single :class:`~itaps.iBase.Entity`, a boolean
               representing whether the face is degenerate. Otherwise, an array
               of booleans.

   .. method:: getEntTolerance(entities)

      Return the tolerance for the specified `entities`.

      :param entities: Entity or array of entities being queried
      :return: If `entities` is a single :class:`~itaps.iBase.Entity`, the
               tolerance (as a `float`). Otherwise, an array of tolerances.

   .. method:: copyEnt(entity)

      Copy the specified `entity` and return the duplicate.

      :param entity: The entity to copy
      :return: The created entity

   .. method:: sweepEntAboutAxis(entity, angle, axis)

      Sweep (extrude) the specified `entity` about an axis.

      :param entity: The entity to entity
      :param angle: The angle (in degrees) to sweep the entity
      :param axis: The axis about which to sweep the entity
      :return: The created entity

   .. method:: deleteAll()

      Delete all entities in the model.

   .. method:: deleteEnt(entity)

      Delete the specified entity.

      :param entity: An entity to delete

   .. method:: createSphere(radius)

      Create a sphere with the specified `radius`.

      :param radius: The radius of the sphere
      :return: The created entity

   .. method:: createPrism(height, sides, major_rad, minor_rad)

      Create a prism with the specified `height`, `sides`, `major_rad`, and
      `minor_rad`.

      :param height: The height of the prism
      :param sides: The number of sides of the prism
      :param major_rad: The prism's major radius
      :param minor_rad: The prism's minor radius
      :return: The created entity

   .. method:: createBrick(dimensions)
               createBrick(...)

      Create a sphere with the x, y, and z dimensions specified in `dimensions`.
      You may also call this method with ``createBrick(x, y, z)``.

      :param dimensions: The dimensions of the brick
      :return: The created entity

   .. method:: createCylinder(height, major_rad, minor_rad)

       Create a cylinder with the specified `height`, `major_rad`, and 
       `minor_rad`.

      :param height: The height of the cylinder
      :param major_rad: The cylinder's major radius
      :param minor_rad: The cylinder's minor radius
      :return: The created entity

   .. method:: createCone(height, major_rad, minor_rad, top_rad)

       Create a cylinder with the specified `height`, `major_rad`, `minor_rad`,
       and `top_rad`.

      :param height: The height of the cone
      :param major_rad: The cone's major radius
      :param minor_rad: The cone's minor radius
      :param minor_rad: The cone's top radius
      :return: The created entity

   .. method:: createTorus(major_rad, minor_rad)

       Create a torus with the specified `major_rad` and `minor_rad`.

      :param major_rad: The torus's major radius
      :param minor_rad: The torus's minor radius
      :return: The created entity

   .. method:: moveEnt(entity, direction)

      Translate an entity in a particular direction.

      :param entity: The entity to translate
      :param direction: A vector representing the displacement

   .. method:: rotateEnt(entity, angle, axis)

      Rotate an entity about an axis.

      :param entity: The entity to rotate
      :param angle: The angle (in degrees) to rotate the entity
      :param axis: The axis about which to rotate the entity

   .. method:: reflectEnt(entity, axis)

      Reflect an entity about an axis.

      :param entity: The entity to reflect
      :param axis: The axis about which to reflect the entity

   .. method:: scaleEnt(entity, scale)

      Scale an entity in the x, y, and z directions.

      :param entity: The entity to scale
      :param scale: A vector of the x, y, and z scaling factors

   .. method:: uniteEnts(entities)
               uniteEnts(...)

      Geometrically unite the specified `entities` and return the result. This
      method may also be called with ``uniteEnts(ent1, ent2, ent3)``.

      :param entities: The entities to unite
      :return: The resulting entity

   .. method:: subtractEnts(entity1, entity2)

      Geometrically subtract `entity2` from `entity1` and return the result.

      :param entity1: The entity to be subtracted from
      :param entity2: The entity to subtract
      :return: The resulting entity

   .. method:: intersectEnts(entity1, entity2)

      Geometrically intersect `entity1` and `entity2` and return the result.

      :param entity1: An entity to intersect
      :param entity2: An entity to intersect
      :return: The resulting entity

   .. method:: sectionEnt(entity, normal, offest, reverse)

      Section an entity along a plane and return the result.

      :param entity: The entity to section
      :param normal: The normal of the plane
      :param offset: The plane's offset from the origin
      :param reverse: True is the resulting entity should be reversed, false
                      otherwise.
      :return: The resulting entity

   .. method:: imprintEnts(entities)

      Imprint the specified entities.

      :param entities: The entities to be imprinted

   .. method:: mergeEnts(entities, tolerance)

      Merge the specified `entities` if they are within the specified
      `tolerance`.

      :param entities: The entities to merge
      :param tolerance: Tolerance for determining if entities should be merged

   .. method:: createEntSet(ordered)

      Create an :class:`EntitySet`, either ordered or unordered. Unordered
      entity sets can contain a given entity or set only once.

      :param ordered: True if the list should be ordered, false otherwise
      :return: The newly-created :class:`EntitySet`

   .. method:: destroyEntSet(set)

      Destroy an entity set.

      :param set: Entity set to be destroyed

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
      :param force: True if the tag should be deleted even if there are values
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

In addition to the methods listed above, :class:`Geom` automatically forwards
method calls to the root :class:`EntitySet`. Thus, ::

  geom.getEntities(iBase.Type.all)

is equivalent to::

  geom.rootSet.getEntities(iBase.Type.all)

EntitySet
=========

.. class:: EntitySet(set[, instance])

   Return a new set referring to the handled contained in  `set`. If `set` is
   an :class:`itaps.iBase.EntitySet` instance, `instance` must also be
   specified.

   .. attribute:: instance

      Return the :class:`Geom` instance from which this entity set was created.

   .. attribute:: isList

      Return whether this entity set is ordered.

   .. method:: getNumOfType(type)

      Get the number of entities with the specified type in this entity set.

      :param type: Type of entity requested
      :return: The number of entities in this entity set of the requested type

   .. method:: getEntities(type)

      Get entities of a specific type in this entity set. All entities of a
      given type are requested by specifying :attr:`itaps.iBase.Type.all`.

      :param type: Type of entities being requested
      :return: Array of entity handles from this entity set meeting the
               requirements of `type`

   .. method:: getNumEntSets(hops)

      Get the number of sets contained in this entity set. If this entity set is
      not the root set, `hops` indicates the maximum number of contained sets
      from this set to one of the contained sets, inclusive of this set.

      :param hops: Maximum number of contained sets from this set to a
                   contained set, including itself.
      :return: Number of entity sets found

   .. method:: getEntSets(hops)

      Get the sets contained in this entity set. If this entity set is not the
      root set, `hops` indicates the maximum number of contained sets from
      this set to one of the contained sets, inclusive of this set.

      :param hops: Maximum number of contained sets from this set to a
                   contained set, including itself.
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

      :param entSet: The entity set to add

   .. method:: removeChild(set)

      Remove `set` as a child from this entity set.

      :param entSet: The entity set to remove

   .. method:: isChild(set)

      Return whether an entity set is a child of this entity set.

      :param entSet: The entity set to query:
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

   .. method:: iterate(type[, count=1])

      Initialize an :class:`Iterator` over the specified entity type for this
      entity set. If `count` is greater than 1, each step of the iteration
      returns an array of `count` entities. Equivalent to::

        itaps.iGeom.Iterator(self, type, count)

      :param type: Type of entities being requested
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

.. class:: Iterator(set, type[, count=1])

   Return a new iterator on the entity set `set` to iterate over entities of
   the specified `type`. If `count` is greater than 1, each step of the
   iteration will return an array of `count` entities. All entities of a given
   type are requested by specifying :attr:`itaps.iBase.Type.all`.

   :param set: Entity set to iterate over
   :param type: Type of entities being requested
   :param count: Number of entities to return on each step of iteration

   .. attribute:: instance

      Return the :class:`Geom` instance from which this iterator was created.

   .. method:: reset()

      Resets the iterator to the beginning.


Tag
===

.. class:: Tag(tag[,instance])

   Return a new tag referring to the handled contained in  `tag`. If `tag` is
   an :class:`itaps.iBase.Tag` instance, `instance` must also be specified.

   .. attribute:: instance

      Return the :class:`Geom` instance from which this tag was created.

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


Basis
=====

.. class:: Basis

   An enumeration of geometric bases for use in querying different coordinate
   systems.

   .. data:: xyz

      Standard (world-space) coordinates

   .. data:: uv

      Parametric coordinates for two-dimensional objects (faces)

   .. data:: u

      Parametric coordinates for one-dimensional objects (edges)
