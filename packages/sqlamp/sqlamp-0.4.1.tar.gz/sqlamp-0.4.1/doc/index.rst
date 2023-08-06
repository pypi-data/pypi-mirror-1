.. automodule:: sqlamp

----------
Quickstart
----------

.. code-block:: python

    import sqlalchemy, sqlalchemy.orm
    engine = sqlalchemy.create_engine('sqlite:///:memory:', echo=False)
    metadata = sqlalchemy.MetaData(engine)
    node_table = sqlalchemy.Table('node', metadata,
        sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
        sqlalchemy.Column('parent_id', sqlalchemy.ForeignKey('node.id')),
        sqlalchemy.Column('name', sqlalchemy.String)
    )

There is nothing special to :mod:`sqlamp` here. Note self-reference
"child to parent" ('parent_id' is foreign key to table's primary key)
just as in any other implementation of adjacency relations.

.. code-block:: python

    import sqlamp
    class Node(object):
        mp = sqlamp.MPManager(
            node_table, node_table.c.id, node_table.c.parent_id
        )
        def __init__(self, name, parent=None):
            self.name = name
            self.parent = parent
        def __repr__(self):
            return '<Node %r>' % self.name

Attach instance of :class:`~sqlamp.MPManager` to class that represents
node. Three required args for :class:`~sqlamp.MPManager` constructor
are the table object, the primary key field and the parent reference field.

Now we can create the table and define the mapper (it is important
to create table *after* :class:`~sqlamp.MPManager` was created as
created :class:`~sqlamp.MPManager` appends three new columns and one index
to the table):

.. code-block:: python

    node_table.create()

Setting up the mapper requires only one extra step --- providing an extension
`Node.mp.mapper_extension`:

.. code-block:: python

    mapper = sqlalchemy.orm.mapper(
        Node, node_table,
        extension=[Node.mp.mapper_extension],
        properties={
            'parent': sqlalchemy.orm.relation(
                Node, remote_side=[node_table.c.id]
            )
        }
    )

You may see value provided as `properties` argument: this is a way `recomended
<http://www.sqlalchemy.org/docs/05/mappers.html#adjacency-list-relationships>`_
by the official SQLAlchemy documentation to set up an adjacency relation.

Now all the preparation steps are done. Lets try to use it!

.. code-block:: python

    session = sqlalchemy.orm.sessionmaker(engine)()
    root = Node('root')
    child1 = Node('child1', parent=root)
    child2 = Node('child2', parent=root)
    grandchild = Node('grandchild', parent=child1)
    session.add_all([root, child1, child2, grandchild])
    session.flush()

We have just created a sample tree. This is all about `AL`, nothing
special to :mod:`sqlamp` here. The interesting part is fetching trees:

    >>> root.mp.query_children().all()
    [<Node 'child1'>, <Node 'child2'>]
    >>> root.mp.query_descendants().all()
    [<Node 'child1'>, <Node 'grandchild'>, <Node 'child2'>]
    >>> grandchild.mp.query_ancestors().all()
    [<Node 'root'>, <Node 'child1'>]
    >>> session.query(Node).order_by(Node.mp).all()
    [<Node 'root'>, <Node 'child1'>, <Node 'grandchild'>, <Node 'child2'>]
    >>> for node in root.mp.query_descendants(and_self=True):
    ...     print '  ' * node.mp_depth, node.name
    ...
    root
      child1
        grandchild
      child2

As you can see all `sqlamp` functionality is accessible via `MPManager`
descriptor (called `'mp'` in this example).

*Note*: ``Node.mp`` (a so-called "class manager") is not the same
as ``node.mp`` ("instance manager"). Do not confuse them as they are for
different purposes and their APIs has no similar. Class manager (see
:class:`MPClassManager`) used to features that are not intended
to particular node but for the whole tree: basic setup (mapper
extension) and tree-maintainance functions. And an instance managers
(:class:`MPInstanceManager`) are each unique to and bounded to a node.
They are implements a queries for a related nodes and other things
specific to concrete node.


----------------------
Implementation details
----------------------
:mod:`sqlamp` had borrowed some implementation ideas from `django-treebeard`_.
In particular, `sqlamp` uses the same alphabet (which consists of numeric
digits and latin-letters in upper case), `sqlamp` as like as `django-treebeard`
doesn't use path parts delimiter --- path parts has fixed adjustable length.
But unlike `django-treebeard` `sqlamp` stores each tree absolutelly
stand-alone --- two or more trees may (and will) have identical values in
`path` and `depth` fields and be different only by values in `tree_id` field.
This is the way that can be found in `django-mptt`_.

:mod:`sqlamp` works *only* on basis of Adjacency Relations. This solution
makes data more denormalized but more fault-tolerant. It is able to rebuild
all pathes for all trees using only `AL` data. Also it makes applying `sqlamp`
on existing project easer.

.. _`django-treebeard`: http://django-treebeard.googlecode.com/
.. _`django-mptt`: http://django-mptt.googlecode.com/


-------
Support
-------
Feel free to `email author <anton@angri.ru>`_ directly to send bugreports,
feature requests, patches, etc.


-------------
API Reference
-------------

.. autoexception:: PathOverflowError
.. autoexception:: TooManyChildrenError
.. autoexception:: PathTooDeepError


.. autoclass:: MPManager(table, pk_field, parent_id_field, path_field_name='mp_path', depth_field_name='mp_depth', tree_id_field_name='mp_tree_id', steplen=3, instance_manager_key='_mp_instance_manager')
    :members: __get__


.. autoclass:: MPClassManager
    :members:

    .. automethod:: __clause_element__


.. autoclass:: MPInstanceManager
    :members: filter_descendants, query_descendants, filter_children, query_children, filter_ancestors, query_ancestors

.. autofunction:: tree_recursive_iterator


---------
Changelog
---------
.. include:: ../CHANGES


.. toctree::
   :maxdepth: 2


