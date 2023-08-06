#!/usr/bin/env python
"""
`sqlamp` functional tests.
"""
import unittest

import sqlalchemy
import sqlamp

import tests._testlib as _testlib
_testlib.setup()
from tests._testlib import Cls, make_session, tbl


class FunctionalTestCase(_testlib._BaseTestCase):
    name_pattern = [
        ("root1", [
            ("child11", []),
            ("child12", []),
            ("child13", []),
        ]),
        ("root2", [
            ("child21", [
                ("child211", []),
                ("child212", [
                    ("child2121", []),
                    ("child2122", [
                        ("child21221", []),
                        ("child21222", []),
                    ]),
                ]),
            ]),
            ("child22", []),
            ("child23", []),
        ]),
        ("root3", []),
    ]

    def test_insert_roots(self):
        o, o2, o3 = Cls(), Cls(), Cls()
        self.sess.add_all([o, o2, o3])
        self.sess.commit()
        self.assertTrue(o2 in self.sess)
        self.assertFalse(o2 in self.sess.dirty)

        o1, o2, o3 = self.sess.query(Cls).order_by('id').all()
        self.assertEqual(o1.mp_tree_id, 1)
        self.assertEqual(o2.mp_tree_id, 2)
        self.assertEqual(o3.mp_tree_id, 3)

        for o in [o1, o2, o3]:
            self.assertEqual(o.mp_path, '')
            self.assertEqual(o.mp_depth, 0)

    def test_insert_children(self):
        parent = Cls()
        self.sess.add(parent)
        self.sess.flush()

        children = Cls(), Cls(), Cls()
        for child in children:
            child.parent = parent
        self.sess.add_all(children)
        self.sess.commit()
        self.sess.expunge_all()

        parent, c1, c2, c3 = self.sess.query(Cls).order_by('id').all()
        for child in [c1, c2, c3]:
            self.assertEqual(child.mp_tree_id, parent.mp_tree_id)
            self.assertEqual(child.mp_depth, 1)
        self.assertEqual(c1.mp_path, '00')
        self.assertEqual(c2.mp_path, '01')
        self.assertEqual(c3.mp_path, '02')

        children = Cls(), Cls(), Cls()
        for child in children:
            child.parent = c1
        self.sess.add_all(children)
        self.sess.commit()

        for child in children:
            self.assertEqual(child.mp_tree_id, parent.mp_tree_id)
            self.assertEqual(child.mp_depth, 2)
        self.assertEqual(children[0].mp_path, c1.mp_path + '00')
        self.assertEqual(children[1].mp_path, c1.mp_path + '01')
        self.assertEqual(children[2].mp_path, c1.mp_path + '02')

    def _fill_tree(self):
        def _create_node(name, parent=None):
            node = Cls(name=name, parent=parent)
            self.sess.add(node)
            self.sess.flush()
            return node

        def _process_node(node, parent=None):
            name, children = node
            node = _create_node(name, parent)
            for child in children:
                _process_node(child, node)

        for node in self.name_pattern:
            _process_node(node)
        self.sess.commit()

    def test_rebuild_all_trees(self):
        self._fill_tree()
        query = sqlalchemy.select([tbl]).order_by(tbl.c.id)
        data_before = query.execute().fetchall()
        Cls.mp.rebuild_all_trees()
        data_after = query.execute().fetchall()
        self.assertEqual(data_before, data_after)

    def test_fixing_path_in_root_nodes(self):
        self._fill_tree()
        root1 = self.sess.query(Cls).filter_by(name='root1').one()
        root1.mp_path = '#'
        self.sess.flush()
        Cls.mp.rebuild_all_trees()
        self.sess.expire(root1)
        self.assertNotEqual(root1.mp_path, '#')

    def test_descendants(self):
        self._fill_tree()
        child212 = self.sess.query(Cls).filter_by(name='child212').one()
        descendants = self.sess.query(Cls).filter(
            child212.mp.filter_descendants(and_self=False)
        ).order_by(Cls.mp).all()
        self.assertEqual(descendants, child212.mp.query_descendants().all())
        should_be = self.sess.query(Cls).filter(
            tbl.c.name.in_(
                ("child2121", "child2122", "child21221", "child21222")
            )
        ).order_by(Cls.mp).all()
        self.assertEqual(descendants, should_be)
        descendants_and_self = self.sess.query(Cls).filter(
            child212.mp.filter_descendants(and_self=True)
        ).order_by(Cls.mp).all()
        self.assertEqual(
            descendants_and_self,
            child212.mp.query_descendants(and_self=True).all()
        )
        self.assertEqual(descendants_and_self, [child212] + should_be)

    def test_children(self):
        self._fill_tree()
        root2 = self.sess.query(Cls).filter_by(name='root2').one()
        children = self.sess.query(Cls).filter(
            root2.mp.filter_children()
        ).order_by(Cls.mp).all()
        should_be = self.sess.query(Cls).filter(
            tbl.c.name.in_(("child21", "child22", "child23"))
        ).order_by(Cls.mp).all()
        self.assertEqual(children, should_be)
        self.assertEqual(children, root2.mp.query_children().all())

    def test_filter_parent(self):
        self._fill_tree()
        root1 = self.sess.query(Cls).filter_by(name='root1').one()
        self.assertEqual(
            self.sess.query(Cls).filter(root1.mp.filter_parent()).count(), 0
        )
        for child in root1.mp.query_children():
            self.assertEqual(
                self.sess.query(Cls).filter(child.mp.filter_parent()).one(),
                root1
            )

    def test_ancestors(self):
        self._fill_tree()
        child2122 = self.sess.query(Cls).filter_by(name='child2122').one()
        ancestors = self.sess.query(Cls).filter(
            child2122.mp.filter_ancestors()
        ).order_by(Cls.mp).all()
        should_be = self.sess.query(Cls).filter(
            tbl.c.name.in_(("child212", "child21", "child2", "root2"))
        ).order_by(Cls.mp).all()
        self.assertEqual(ancestors, should_be)
        self.assertEqual(ancestors, child2122.mp.query_ancestors().all())
        ancestors_and_self = self.sess.query(Cls).filter(
            child2122.mp.filter_ancestors(and_self=True)
        ).order_by(Cls.mp).all()
        self.assertEqual(ancestors_and_self, should_be + [child2122])
        self.assertEqual(
            ancestors_and_self,
            child2122.mp.query_ancestors(and_self=True).all()
        )

    def test_too_many_children_and_last_child_descendants(self):
        self.assertEqual(Cls.mp.max_children, 1296) # 36 ** 2
        root = Cls()
        self.sess.add(root)
        self.sess.commit()
        for x in xrange(1296):
            self.sess.add(Cls(parent=root, name=str(x)))
        self.sess.commit()
        self.sess.add(Cls(parent=root))
        self.assertRaises(sqlamp.TooManyChildrenError, self.sess.flush)
        self.sess.rollback()
        last_child = self.sess.query(Cls).filter_by(name='1295').one()
        last_childs_child = Cls(parent=last_child, name='1295.1')
        self.sess.add(last_childs_child)
        self.sess.flush()
        self.assertEqual(
            last_child.mp.query_descendants().all(), [last_childs_child]
        )

    def test_path_too_deep(self):
        self.assertEqual(Cls.mp.max_depth, 128) # int(255 / 2) + 1
        node = None
        for x in xrange(128):
            new_node = Cls(parent=node)
            self.sess.add(new_node)
            self.sess.flush()
            node = new_node
        self.sess.add(Cls(parent=node))
        self.assertRaises(sqlamp.PathTooDeepError, self.sess.flush)

    def test_query_all_trees(self):
        self._fill_tree()
        all_trees = Cls.mp.query_all_trees(self.sess)
        self.assertEqual(
            [node.name for node in all_trees],
            ["root1", "child11", "child12", "child13", "root2", "child21",
             "child211", "child212", "child2121", "child2122",
             "child21221", "child21222", "child22", "child23", "root3"]
        )

    def test_tree_recursive_iterator(self):
        self._fill_tree()
        all_trees = Cls.mp.query_all_trees(self.sess)
        all_trees = sqlamp.tree_recursive_iterator(all_trees, Cls.mp)
        def listify(recursive_iterator):
            return [(node.name, listify(children))
                    for node, children in recursive_iterator]
        self.assertEqual(self.name_pattern, listify(all_trees))


def get_suite():
    return unittest.TestLoader().loadTestsFromTestCase(FunctionalTestCase)


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(get_suite())

