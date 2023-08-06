# coding: utf-8
"""
    :mod:`sqlamp` --- Materialized Path for SQLAlchemy
    ==================================================

    :author: `Anton Gritsay <anton@angri.ru>`_
    :version: %(version)s
    :license: 2-clause BSD (see LICENSE)
    :download: http://sqlamp.angri.ru/sqlamp-%(version)s.tar.gz

    :mod:`sqlamp` is an implementation of an efficient algorithm for working
    with hierarchical data structures --- `Materialized Path`. :mod:`sqlamp`
    uses (and depends of) `SQLAlchemy <http://sqlalchemy.org>`_.

    `Materialized Path` is a way to store (and fetch) a trees in a relational
    databases. It is the compromise between `Nested Sets` and `Adjacency
    Relations` in respect to simplicity and efficiency. Method was proposed
    by `Vadim Tropashko`_ in his book `SQL Design Patterns`_. Vadim's
    description of the method can be read in his article `Trees in SQL:
    Nested Sets and Materialized Path (by Vadim Tropashko)`_.

    Implemented features:

        * Saving node roots --- if no parent set for node. The tree will have
          a new `tree_id`.
        * Saving child nodes --- if node has some parent. The whole dirty job
          of setting values in `tree_id`, `path` and `depth` fields is done
          by `sqlamp`.
        * Fetching node's descendants, ancestors and children using the most
          efficient way available (see :class:`MPInstanceManager`)
        * Autochecking exhaustion of tree size limits --- maximum number of
          children, maximum nesting level (see :class:`MPManager` to learn
          more about limits fine-tuning) is done during session flush.
        * Rebuilding all trees (see :meth:`MPClassManager.rebuild_all_trees`)
          and any subtree (:meth:`MPClassManager.rebuild_subtree`) on the
          basis of Adjacency Relations.

    Moving of nodes is not yet implemented.

    Known-to-work supported DBMS include `sqlite`_ (tested with 3.6.14),
    `MySQL`_ (tested using both MyISAM and InnoDB with server version 5.1.34)
    and `PostgreSQL`_ (tested with 8.3.7), but sqlamp should work with any
    other DBMS supported by SQLAlchemy.

    .. _`Vadim Tropashko`: http://vadimtropashko.wordpress.com
    .. _`Sql Design Patterns`:
       http://www.rampant-books.com/book_2006_1_sql_coding_styles.htm
    .. _`Trees in SQL: Nested Sets and Materialized Path (by Vadim Tropashko)`:
       http://www.dbazine.com/oracle/or-articles/tropashko4
    .. _`sqlite`: http://sqlite.org
    .. _`MySQL`: http://mysql.com
    .. _`PostgreSQL`: http://postgresql.org
"""
import weakref
import sqlalchemy, sqlalchemy.orm


__all__ = [
    'MPManager',
    'PathOverflowError', 'TooManyChildrenError', 'PathTooDeepError'
]

__version__ = (0, 3)
__doc__ %= {'version': '.'.join(map(str, __version__))}


ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
PATH_FIELD_LENGTH = 255


class PathOverflowError(Exception):
    "Base class for exceptions in calculations of node's path."

class TooManyChildrenError(PathOverflowError):
    "Maximum children limit is exceeded. Raised during flush."

class PathTooDeepError(PathOverflowError):
    "Maximum depth of nesting limit is exceeded. Raised during flush."


def inc_path(path, steplen):
    """
    Simple arithmetical operation --- incrementation of an integer number
    (with radix of `len(ALPHABET)`) represented as string.

    :param path:
        `str`, the path to increment.
    :param steplen:
        `int`, the number of maximum characters to carry overflow.
    :returns:
        new path wich is greater than `path` by one.
    :raises PathOverflowError:
        when incrementation of `path` cause to carry overflow by number
        of characters greater than `steplen`.

    >>> inc_path('0000', 4)
    '0001'
    >>> inc_path('3GZU', 4)
    '3GZV'
    >>> inc_path('337Z', 2)
    '3380'
    >>> inc_path('GWZZZ', 5)
    'GX000'
    >>> inc_path('ABZZ', 2)
    Traceback (most recent call last):
        ...
    PathOverflowError
    """
    parent_path, path = path[:-steplen], path[-steplen:]
    path = path.rstrip(ALPHABET[-1])
    if not path:
        raise PathOverflowError()
    zeros = steplen - len(path)
    path = path[:-1] + \
           ALPHABET[ALPHABET.index(path[-1]) + 1] + \
           ALPHABET[0] * zeros
    return parent_path + path


class MPOptions(object):
    """
    A container for options for one tree.

    :parameters: see :class:`MPManager`.
    """
    def __init__(self, table, pk_field, parent_id_field,
                 path_field_name='mp_path',
                 depth_field_name='mp_depth',
                 tree_id_field_name='mp_tree_id',
                 steplen=3):
        self.table = table

        def _check_field(field):
            """
            Check field argument (`pk_field`, `parent_id_field`) and
            convert it from field name to `Column` object if needed.
            """
            if isinstance(field, basestring):
                return table.c[field]
            else:
                assert field.table is table
                return field

        self.pk_field = _check_field(pk_field)
        self.parent_id_field = _check_field(parent_id_field)
        self.steplen = steplen

        self.max_children = len(ALPHABET) ** steplen
        self.max_depth = PATH_FIELD_LENGTH / steplen

        self.path_field = sqlalchemy.Column(
            path_field_name, PathField(PATH_FIELD_LENGTH), nullable=False
        )
        self.depth_field = sqlalchemy.Column(
            depth_field_name, DepthField(), nullable=False
        )
        self.tree_id_field = sqlalchemy.Column(
            tree_id_field_name, TreeIdField(), nullable=False
        )
        self.fields = (self.path_field, self.depth_field, self.tree_id_field)
        map(table.append_column, self.fields)

        self.indices = [
            sqlalchemy.Index(
                '%s__%s' % (tree_id_field_name, path_field_name),
                self.tree_id_field, self.path_field, unique=True
            ),
        ]
        map(table.append_constraint, self.indices)

    def order_by_clause(self):
        """
        Get an object applicable for usage as an argument for
        `Query.order_by()`. Used to sort subtree query
        by `tree_id` and `path`.
        """
        return sqlalchemy.sql.expression.ClauseList(
            self.tree_id_field,
            self.path_field
        )


class _InsertionsParamsSelector(object):
    """
    Instances of this class used as values for :class:`TreeIdField`,
    :class:`PathField` and :class:`DepthField` when tree nodes are
    created. It makes a "lazy" query to determine actual values for
    this fields.

    :param opts: instance of :class:`MPOptions`.
    :param session: session which will be used for query.
    :param parent_id: parent's node primary key, may be `None`.
    """
    def __init__(self, opts, session, parent_id):
        self._mp_opts = opts
        self.parent_id = parent_id
        self.session = session
        self._query_result = None

    def _perform_query(self):
        """
        Make a query, get an actual values for `path`, `tree_id`
        and `depth` fields and put them in dict `self._query_result`.
        """
        opts = self._mp_opts
        if self.parent_id is not None:
            # a new instance has at least one ancestor.
            # `tree_id` can be used from parent's value,
            # `depth` is parent's depth plus one,
            # `path` will be calculated from two values -
            # the path of the parent node itself and it's
            # last child's path.
            query = sqlalchemy.select(
                [
                    opts.tree_id_field.label('tree_id'),
                    (opts.depth_field + 1).label('depth'),
                    opts.path_field.label('parent_path'),
                    sqlalchemy.select(
                        [sqlalchemy.func.max(opts.path_field)],
                        opts.parent_id_field == self.parent_id
                    ).label('last_child_path'),
                ],
                opts.pk_field == self.parent_id
            )
        else:
            # a new instance will be a root node.
            # `tree_id` is next unused integer value,
            # `depth` for root nodes is equal to zero,
            # `path` should be `ALPHABET[0] * opts.steplen`.
            query = sqlalchemy.select(
                [
                    (sqlalchemy.func.coalesce(
                        sqlalchemy.func.max(opts.tree_id_field), 0
                     ) + 1).label('tree_id'),
                    sqlalchemy.sql.literal(0).label('depth'),
                    sqlalchemy.sql.literal('').label('parent_path'),
                    sqlalchemy.sql.literal(None).label('last_child_path')
                ]
            )
        result = self.session.execute(query).fetchone()
        # `tree_id` and `depth` values can be used
        # directly from the query we made:
        self._query_result = dict(
            tree_id=result['tree_id'], depth=result['depth']
        )

        parent_path = result['parent_path']
        last_child_path = result['last_child_path']
        steplen = self._mp_opts.steplen
        if not last_child_path:
            # node is root or first child.
            path = parent_path + ALPHABET[0] * steplen
        else:
            try:
                path = inc_path(last_child_path, steplen)
            except PathOverflowError:
                # transform exception `PathOverflowError`, raised by
                # `inc_path()` to more convinient `TooManyChildrenError`.
                raise TooManyChildrenError()

        if len(path) > PATH_FIELD_LENGTH:
            raise PathTooDeepError()
        self._query_result['path'] = path

    @property
    def query_result(self):
        """
        Get query result dict, calling `self._perform_query()`
        for the first time.
        """
        if self._query_result is None:
            self._perform_query()
        return self._query_result


class TreeIdField(sqlalchemy.types.TypeDecorator):
    "Integer field representing node's tree identifier."
    impl = sqlalchemy.Integer
    def process_bind_param(self, value, dialect):
        if not isinstance(value, _InsertionsParamsSelector):
            return value
        return value.query_result['tree_id']

class DepthField(sqlalchemy.types.TypeDecorator):
    "Integer field representing node's depth level."
    impl = sqlalchemy.Integer
    def process_bind_param(self, value, dialect):
        if not isinstance(value, _InsertionsParamsSelector):
            return value
        return value.query_result['depth']

class PathField(sqlalchemy.types.TypeDecorator):
    "Varchar field representing node's path."
    impl = sqlalchemy.String
    def process_bind_param(self, value, dialect):
        if not isinstance(value, _InsertionsParamsSelector):
            return value
        return value.query_result['path']
    def adapt_operator(self, op):
        # required for concatenation to work right
        return self.impl.adapt_operator(op)


class MPMapperExtension(sqlalchemy.orm.interfaces.MapperExtension):
    """
    An extension to node class' mapper.

    :param opts: instance of :class:`MPOptions`
    """
    def __init__(self, opts):
        super(MPMapperExtension, self).__init__()
        self._mp_opts = opts

    def before_insert(self, mapper, connection, instance):
        """
        Creates an :class:`_InsertionsParamsSelector` instance and
        sets values of tree_id, depth and path fields to it.
        """
        opts = self._mp_opts
        parent = getattr(instance, opts.parent_id_field.name)
        tree_id = depth = path = _InsertionsParamsSelector(
            opts, sqlalchemy.orm.session.object_session(instance), parent
        )
        setattr(instance, opts.tree_id_field.name, tree_id)
        setattr(instance, opts.path_field.name, path)
        setattr(instance, opts.depth_field.name, depth)

    def after_insert(self, mapper, connection, instance):
        """
        Replaces :class:`_InsertionsParamsSelector` instance (which
        is remains after flush) with actual values of tree_id, depth
        and path fields.
        """
        opts = self._mp_opts
        params_selector = getattr(instance, opts.path_field.name)
        assert isinstance(params_selector, _InsertionsParamsSelector)
        query_result = params_selector.query_result
        setattr(instance, opts.tree_id_field.name, query_result['tree_id'])
        setattr(instance, opts.path_field.name, query_result['path'])
        setattr(instance, opts.depth_field.name, query_result['depth'])


class MPClassManager(object):
    """
    Node class manager. No need to create it by hand: it created
    by :class:`MPManager`.

    :param opts: instance of :class:`MPOptions`
    """
    def __init__(self, opts):
        self._mp_opts = opts
        self.mapper_extension = MPMapperExtension(opts)

    @property
    def max_children(self):
        "The maximum number of children in each node, readonly."
        return self._mp_opts.max_children
    @property
    def max_depth(self):
        "The maximum level of nesting in this tree, readonly."
        return self._mp_opts.max_depth

    def __clause_element__(self):
        """
        Allows to use instances of `MPClassManager` directly
        as argument for `sqlalchemy.orm.Query.order_by()`.
        Sort query by `tree_id` and `path` fields. Can be
        used like this (assume that :class:`MPManager` is
        attached to class `Node` and named `'mp'`)::

            query = session.query(Node).filter(root.filter_children())
            query.order_by(Node.mp)

        .. note:: There is no need to sort queries returned by
            :class:`MPInstanceManager`'s `query_*()` methods this way
            as they returned already sorted.
        """
        return self._mp_opts.order_by_clause()

    def rebuild_subtree(self, root_node_id, order_by=None):
        """
        Reset paths for all nodes in subtree defined by `root_node_id`
        on the basis of adjacency relations.

        :param root_node_id:
            the value of subtree root's primary key.
        :param order_by:
            an "order by clause" for sorting children nodes
            in each subtree.
        """
        opts = self._mp_opts
        path, depth, tree_id = sqlalchemy.select(
            [opts.path_field, opts.depth_field, opts.tree_id_field],
            opts.pk_field == root_node_id
        ).execute().fetchone()
        self._do_rebuild_subtree(
            root_node_id, path, depth, tree_id, order_by or opts.pk_field
        )

    def _do_rebuild_subtree(self, root_node_id, root_path, root_depth, \
                            tree_id, order_by):
        """
        The main recursive function for rebuilding trees.

        :param root_node_id:
            subtree's root node primary key value.
        :param root_path:
            the pre-calculated path of root node.
        :param root_depth:
            the pre-calculated root node's depth.
        :param tree_id:
            the pre-calculated identifier for this tree.
        :param order_by:
            the children sort order.
        """
        opts = self._mp_opts
        path = root_path + ALPHABET[0] * opts.steplen
        depth = root_depth + 1
        children = sqlalchemy.select(
            [opts.pk_field],
            opts.parent_id_field == root_node_id
        ).order_by(order_by)
        query = opts.table.update()
        for child in children.execute().fetchall():
            [child] = child
            query.where(opts.pk_field == child) \
                 .values({opts.path_field: path, \
                          opts.depth_field: depth, \
                          opts.tree_id_field: tree_id}).execute()
            self._do_rebuild_subtree(child, path, depth, tree_id, order_by)
            path = inc_path(path, opts.steplen)

    def rebuild_all_trees(self, order_by=None):
        """
        Perform a complete rebuild of all trees on the basis
        of adjacency relations.

        Drops indexes before processing and recreates it after.

        :param order_by:
            an "order by clause" for sorting root nodes and a
            children nodes in each subtree.
        """
        opts = self._mp_opts
        order_by = order_by or opts.pk_field
        for index in opts.indices:
            index.drop()
        roots = sqlalchemy.select(
            [opts.pk_field], opts.parent_id_field == None
        ).order_by(order_by)
        for root_node in roots.execute().fetchall():
            [node_id] = root_node
            self.rebuild_subtree(node_id, order_by)
        for index in opts.indices:
            index.create()


class MPInstanceManager(object):
    """
    A node instance manager, unique for each node. First created
    on access to :class:`MPManager` descriptor from instance.
    Implements API to query nodes related somehow to particular
    node: descendants, ancestors, etc.

    :param opts: instance of `MPOptions`
    :param obj: particular node instance
    """
    __slots__ = ('_mp_opts', '_obj_ref')

    def __init__(self, opts, obj):
        self._mp_opts = opts
        self._obj_ref = weakref.ref(obj)

    def _get_obj(self):
        "Dereference weakref and return node instance."
        return self._obj_ref()

    def _get_query(self, obj, session):
        """
        Get a query for the node's class.

        If :attr:`session` is `None` tries to use :attr:`obj`'s session,
        if it is available.

        :param session: a sqlalchemy `Session` object or `None`.
        :return: an object `sqlalchemy.orm.Query`.
        :raises AssertionError:
            if :attr:`session` is `None` and node is not bound
            to a session.
        """
        obj_session = self._get_session_and_assert_flushed(obj)
        if session is None:
            # use node's session only if particular session
            # was not specified
            session = obj_session
        return sqlalchemy.orm.Query(type(obj), session=session)

    def _get_session_and_assert_flushed(self, obj):
        """
        Ensure that node has "real" values in its `path`, `tree_id`
        and `depth` fields and return node's session.

        Determines object session, flushs it if instance is in "pending"
        state and session has `autoflush == True`. Flushing is needed
        for instance's `path`, `tree_id` and `depth` fields hold real
        values applicable for queries. If the node is not bound to a
        session tries to check that it was "persistent" once upon a time.

        :return: session object or `None` if node is in "detached" state.
        :raises AssertionError:
            if instance is in "pending" state and session has `autoflush`
            disabled.
        :raises AssertionError:
            if instance is in "transient" state (has no "persistent" copy
            and is not bound to a session).
        """
        session = sqlalchemy.orm.session.object_session(obj)
        if session is not None:
            if obj in session.new:
                assert session.autoflush, \
                        "instance %r is in 'pending' state and attached " \
                        "to non-autoflush session. call `session.flush()` " \
                        "to be able to get filters and perform queries." % obj
                session.flush()
        else:
            assert all(getattr(obj, field.name) is not None \
                       for field in self._mp_opts.fields), \
                    "instance %r seems to be in 'transient' state. " \
                    "put it in the session to be able to get filters " \
                    "and perform queries." % obj
        return session

    def filter_descendants(self, and_self=False):
        """
        Get a filter condition for node's descendants.

        Requires that node has `path`, `tree_id` and `depth` values
        available (that means it has "persistent version" even if the
        node itself is in "detached" state or it is in "pending" state
        in `autoflush`-enabled session).

        Usage example::

            session.query(Node).filter(root.mp.filter_descendants()) \\
                               .order_by(Node.mp)

        This example is silly and only shows an approach of using
        `filter_descendants`, dont use it for such purpose as there is a
        better way for such simple queries: :meth:`query_descendants`.

        :param and_self:
            `bool`, if set to `True` self node will be selected by filter.
        :return:
            a filter clause applicable as argument for
            `sqlalchemy.orm.Query.filter()` and others.
        """
        opts = self._mp_opts
        obj = self._get_obj()
        self._get_session_and_assert_flushed(obj)
        path = getattr(obj, opts.path_field.name)
        # we are not use queries like `WHERE path LIKE '0.1.%` instead
        # they looks like `WHERE path > '0.1' AND path < '0.2'`
        try:
            next_sibling_path = inc_path(path, opts.steplen)
        except PathOverflowError:
            # this node is theoretically last, will not check
            # for `path < next_sibling_path`
            next_sibling_path = None
        tree_id = getattr(obj, opts.tree_id_field.name)
        # always filter by `tree_id`:
        filter_ = opts.tree_id_field == tree_id
        if and_self:
            # non-strict inequality if this node should satisfy filter
            filter_ &= opts.path_field >= path
        else:
            filter_ &= opts.path_field > path
        if next_sibling_path is not None:
            filter_ &= opts.path_field < next_sibling_path
        return filter_

    def query_descendants(self, session=None, and_self=False):
        """
        Get a query for node's descendants.

        Requires that node is in "persistent" state or in "pending"
        state in `autoflush`-enabled session.

        :param session:
            session object for query. If not provided, node's session is
            used. If node is in "detached" state and :attr:`session` is
            not provided, query will be detached too (will require setting
            `session` attribute to execute).
        :param and_self:
            `bool`, if set to `True` self node will be selected by query.
        :return:
            a `sqlalchemy.orm.Query` object which contains only node's
            descendants and is ordered by `path`.
        """
        query = self._get_query(self._get_obj(), session) \
                    .filter(self.filter_descendants(and_self=and_self)) \
                    .order_by(self._mp_opts.order_by_clause())
        return query

    def filter_children(self):
        """
        The same as :meth:`filter_descendants` but filters children nodes
        and does not accepts :attr:`and_self` parameter.
        """
        opts = self._mp_opts
        obj = self._get_obj()
        self._get_session_and_assert_flushed(obj)
        depth = getattr(obj, opts.depth_field.name) + 1
        # Oh yeah, using adjacency relation may be more efficient here. But
        # one can access AL-based children collection without `sqlamp` at all.
        # And in that case we can be sure that at least `(tree_id, path)`
        # index is used. `parent_id` field may not have index set up so
        # condition `pk == parent_id` in SQL query may be even less efficient.
        return self.filter_descendants() & (opts.depth_field == depth)

    def query_children(self, session=None):
        """
        The same as :meth:`query_descendants` but queries children nodes and
        does not accepts :attr:`and_self` parameter.
        """
        query = self._get_query(self._get_obj(), session) \
                    .filter(self.filter_children()) \
                    .order_by(self._mp_opts.order_by_clause())
        return query

    def filter_ancestors(self, and_self=False):
        "The same as :meth:`filter_descendants` but filters ancestor nodes."
        opts = self._mp_opts
        obj = self._get_obj()
        self._get_session_and_assert_flushed(obj)
        tree_id = getattr(obj, opts.tree_id_field.name)
        depth = getattr(obj, opts.depth_field.name)
        path = getattr(obj, opts.path_field.name)
        # WHERE tree_id = <node.tree_id> AND <node.path> LIKE path || '%'
        filter_ = (opts.tree_id_field == tree_id) \
                  & sqlalchemy.sql.expression.literal(
                        path, sqlalchemy.String
                    ).like(opts.path_field + '%')
        if and_self:
            filter_ &= opts.depth_field  <= depth
        else:
            filter_ &= opts.depth_field < depth
        return filter_

    def query_ancestors(self, session=None, and_self=False):
        "The same as :meth:`query_descendants` but queries node's ancestors."
        query = self._get_query(self._get_obj(), session) \
                    .filter(self.filter_ancestors(and_self=and_self)) \
                    .order_by(self._mp_opts.depth_field)
        return query

    def filter_parent(self):
        "Get a filter condition for a node's parent."
        opts = self._mp_opts
        obj = self._get_obj()
        self._get_session_and_assert_flushed(obj)
        parent_id = getattr(obj, opts.parent_id_field.name)
        if parent_id is None:
            return sqlalchemy.sql.literal(False)
        filter_ = opts.pk_field == parent_id
        return filter_


class MPManager(object):
    """
    Descriptor for access class-level and instance-level API.

    Usage is simple::

        class Node(object):
            mp = sqlamp.MPManager(...)

    Now there are an ability to get instance manager or class manager
    via property `'mp'` depending on way to access it. `Node.mp` will
    return class manager :class:`MPClassManager` for class `Node` and
    `instance_node.mp` will return instance_node's
    :class:`MPInstanceManager`. See that classes for more details about
    its public API.

    :param table:
        instance of `sqlalchemy.Table`. A table that will be mapped to
        node class and will hold tree nodes in its rows.
    :param pk_field:
        the `table`'s primary key column, may be an instance
        of `sqlalchemy.Column` or field name as string.
    :param parent_id_field:
        a foreign key field that is reference to parent node's
        primary key.
    :param path_field_name='mp_path':
        name for the path field.
    :param depth_field_name='mp_depth':
        name for the depth field.
    :param tree_id_field_name='mp_tree_id':
        name for the tree_id field.
    :param steplen=3:
        integer, the number of characters in each part of the path.
        This value allows to fine-tune the limits for max tree depth
        (equal to `255 / steplen`) and max children in each node
        (`36 ** steplen`). Default `3` value sets the following limits:
        max depth is `85` and max children number is `46656`.
    :param instance_manager_key='_mp_instance_manager':
        name for node instance's attribute to cache node's instance
        manager.

    .. warning::
        Do not change the values of `MPManager` constructor's attributes
        after saving a first tree node. Doing this will corrupt the tree.
    """
    def __init__(self, *args, **kwargs):
        self.instance_manager_key = kwargs.pop('instance_manager_key', \
                                               '_mp_instance_manager')
        opts = MPOptions(*args, **kwargs)
        self._mp_opts = opts
        self.class_manager = MPClassManager(opts)

    def __get__(self, obj, objtype):
        """
        Get :class:`MPInstanceManager` if was accessed via instance
        or :class:`MPClassManager` if via class.
        """
        if obj is None:
            return self.class_manager
        else:
            instance_manager = obj.__dict__.get(self.instance_manager_key)
            if instance_manager is None:
                instance_manager = MPInstanceManager(self._mp_opts, obj)
                obj.__dict__[self.instance_manager_key] = instance_manager
            return instance_manager

