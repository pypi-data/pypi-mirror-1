r"""
>>> from mptt.tests.models import Category, Genre, Node

>>> def print_tree_details(nodes):
...     m = nodes[0]._tree_manager
...     print '\n'.join(['%s %s %s %s %s %s' % \
...                      (n.pk, getattr(n, '%s_id' % m.parent_attr) or '-',
...                       getattr(n, m.tree_id_attr), getattr(n, m.level_attr),
...                       getattr(n, m.left_attr), getattr(n, m.right_attr)) \
...                      for n in nodes])

# Creation ####################################################################
>>> action = Genre.objects.create(name='Action')
>>> platformer = Genre.objects.create(name='Platformer', parent=action)
>>> platformer_2d = Genre.objects.create(name='2D Platformer', parent=platformer)
>>> platformer_3d = Genre.objects.create(name='3D Platformer', parent=platformer)
>>> platformer_4d = Genre.objects.create(name='4D Platformer', parent=platformer)
>>> rpg = Genre.objects.create(name='Role-playing Game')
>>> arpg = Genre.objects.create(name='Action RPG', parent=rpg)
>>> trpg = Genre.objects.create(name='Tactical RPG', parent=rpg)
>>> print_tree_details(Genre.tree.all())
1 - 1 0 1 10
2 1 1 1 2 9
3 2 1 2 3 4
4 2 1 2 5 6
5 2 1 2 7 8
6 - 2 0 1 6
7 6 2 1 2 3
8 6 2 1 4 5

# Model Instance Methods ######################################################
>>> action = Genre.objects.get(pk=action.pk)
>>> [g.name for g in action.get_ancestors()]
[]
>>> [g.name for g in action.get_ancestors(ascending=True)]
[]
>>> [g.name for g in action.get_descendants()]
[u'Platformer', u'2D Platformer', u'3D Platformer', u'4D Platformer']
>>> [g.name for g in action.get_descendants(include_self=True)]
[u'Action', u'Platformer', u'2D Platformer', u'3D Platformer', u'4D Platformer']
>>> action.get_descendant_count()
4
>>> [g.name for g in action.get_siblings()]
[u'Role-playing Game']
>>> [g.name for g in action.get_siblings(include_self=True)]
[u'Action', u'Role-playing Game']

>>> platformer = Genre.objects.get(pk=platformer.pk)
>>> [g.name for g in platformer.get_ancestors()]
[u'Action']
>>> [g.name for g in platformer.get_ancestors(ascending=True)]
[u'Action']
>>> [g.name for g in platformer.get_descendants()]
[u'2D Platformer', u'3D Platformer', u'4D Platformer']
>>> [g.name for g in platformer.get_descendants(include_self=True)]
[u'Platformer', u'2D Platformer', u'3D Platformer', u'4D Platformer']
>>> platformer.get_descendant_count()
3
>>> [g.name for g in platformer.get_siblings()]
[]
>>> [g.name for g in platformer.get_siblings(include_self=True)]
[u'Platformer']

>>> platformer_3d = Genre.objects.get(pk=platformer_3d.pk)
>>> [g.name for g in platformer_3d.get_ancestors()]
[u'Action', u'Platformer']
>>> [g.name for g in platformer_3d.get_ancestors(ascending=True)]
[u'Platformer', u'Action']
>>> [g.name for g in platformer_3d.get_descendants()]
[]
>>> [g.name for g in platformer_3d.get_descendants(include_self=True)]
[u'3D Platformer']
>>> platformer_3d.get_descendant_count()
0
>>> [g.name for g in platformer_3d.get_siblings()]
[u'2D Platformer', u'4D Platformer']
>>> [g.name for g in platformer_3d.get_siblings(include_self=True)]
[u'2D Platformer', u'3D Platformer', u'4D Platformer']

# The move_to method will be used in a few places in the tests which
# follow to verify that it calls the TreeManger correctly.

# Automatic Reparenting #######################################################

Test that trees are in the appropriate state and that reparented items have the
correct tree attributes defined, should they be required for use after a save.

# Extract new root node from a subtree
>>> platformer = Genre.objects.get(pk=platformer.pk)
>>> platformer.parent = None
>>> platformer.save()
>>> print_tree_details([platformer])
2 - 3 0 1 8
>>> print_tree_details(Genre.tree.all())
1 - 1 0 1 2
6 - 2 0 1 6
7 6 2 1 2 3
8 6 2 1 4 5
2 - 3 0 1 8
3 2 3 1 2 3
4 2 3 1 4 5
5 2 3 1 6 7

# Extract new root node from a leaf node which has siblings
>>> platformer_3d = Genre.objects.get(pk=platformer_3d.pk)
>>> platformer_3d.parent = None
>>> platformer_3d.save()
>>> print_tree_details([platformer_3d])
4 - 4 0 1 2
>>> print_tree_details(Genre.tree.all())
1 - 1 0 1 2
6 - 2 0 1 6
7 6 2 1 2 3
8 6 2 1 4 5
2 - 3 0 1 6
3 2 3 1 2 3
5 2 3 1 4 5
4 - 4 0 1 2

# Check that exceptions are raised appropriately when giving
# a root node a parent.
>>> rpg = Genre.objects.get(pk=rpg.pk)
>>> rpg.parent = rpg
>>> rpg.save()
Traceback (most recent call last):
    ...
InvalidTarget: The target node must be in a different tree.
>>> arpg = Genre.objects.get(pk=arpg.pk)
>>> rpg.parent = arpg
>>> rpg.save()
Traceback (most recent call last):
    ...
InvalidTarget: The target node must be in a different tree.

# Make a tree a subtree of another tree
>>> rpg = Genre.objects.get(pk=rpg.pk)
>>> platformer = Genre.objects.get(pk=platformer.pk)
>>> rpg.parent = platformer
>>> rpg.save()
>>> print_tree_details([rpg])
6 2 3 1 6 11
>>> print_tree_details(Genre.tree.all())
1 - 1 0 1 2
2 - 3 0 1 12
3 2 3 1 2 3
5 2 3 1 4 5
6 2 3 1 6 11
7 6 3 2 7 8
8 6 3 2 9 10
4 - 4 0 1 2

# Move a leaf node to another tree
>>> arpg = Genre.objects.get(pk=arpg.pk)
>>> platformer_3d = Genre.objects.get(pk=platformer_3d.pk)
>>> arpg.parent = platformer_3d
>>> arpg.save()
>>> print_tree_details([arpg])
7 4 4 1 2 3
>>> print_tree_details(Genre.tree.all())
1 - 1 0 1 2
2 - 3 0 1 10
3 2 3 1 2 3
5 2 3 1 4 5
6 2 3 1 6 9
8 6 3 2 7 8
4 - 4 0 1 4
7 4 4 1 2 3

# Move a subtree to another tree
>>> rpg = Genre.objects.get(pk=rpg.pk)
>>> platformer_3d = Genre.objects.get(pk=platformer_3d.pk)
>>> rpg.parent = platformer_3d
>>> rpg.save()
>>> print_tree_details([rpg])
6 4 4 1 4 7
>>> print_tree_details(Genre.tree.all())
1 - 1 0 1 2
2 - 3 0 1 6
3 2 3 1 2 3
5 2 3 1 4 5
4 - 4 0 1 8
7 4 4 1 2 3
6 4 4 1 4 7
8 6 4 2 5 6

# Check that exceptions are raised appropriately when moving
# a subtree within its tree.
>>> rpg = Genre.objects.get(pk=rpg.pk)
>>> rpg.parent = rpg
>>> rpg.save()
Traceback (most recent call last):
    ...
InvalidMove: A node may not be made a child of itself or any of its descendants.
>>> trpg = Genre.objects.get(pk=trpg.pk)
>>> rpg.parent = trpg
>>> rpg.save()
Traceback (most recent call last):
    ...
InvalidMove: A node may not be made a child of itself or any of its descendants.

# Move a subtree up a level (position stays the same)
>>> trpg = Genre.objects.get(pk=trpg.pk)
>>> platformer_3d = Genre.objects.get(pk=platformer_3d.pk)
>>> trpg.parent = platformer_3d
>>> trpg.save()
>>> print_tree_details([trpg])
8 4 4 1 6 7
>>> print_tree_details(Genre.tree.all())
1 - 1 0 1 2
2 - 3 0 1 6
3 2 3 1 2 3
5 2 3 1 4 5
4 - 4 0 1 8
7 4 4 1 2 3
6 4 4 1 4 5
8 4 4 1 6 7

# Move a subtree down a level
>>> arpg = Genre.objects.get(pk=arpg.pk)
>>> rpg = Genre.objects.get(pk=rpg.pk)
>>> arpg.parent = rpg
>>> arpg.save()
>>> print_tree_details([arpg])
7 6 4 2 3 4
>>> print_tree_details(Genre.tree.all())
1 - 1 0 1 2
2 - 3 0 1 6
3 2 3 1 2 3
5 2 3 1 4 5
4 - 4 0 1 8
6 4 4 1 2 5
7 6 4 2 3 4
8 4 4 1 6 7

# Move a subtree with descendants down a level
>>> rpg = Genre.objects.get(pk=rpg.pk)
>>> trpg = Genre.objects.get(pk=trpg.pk)
>>> rpg.parent = trpg
>>> rpg.save()
>>> print_tree_details([rpg])
6 8 4 2 3 6
>>> print_tree_details(Genre.tree.all())
1 - 1 0 1 2
2 - 3 0 1 6
3 2 3 1 2 3
5 2 3 1 4 5
4 - 4 0 1 8
8 4 4 1 2 7
6 8 4 2 3 6
7 6 4 3 4 5

# Move a subtree with descendants up a level
>>> rpg = Genre.objects.get(pk=rpg.pk)
>>> platformer_3d = Genre.objects.get(pk=platformer_3d.pk)
>>> rpg.parent = platformer_3d
>>> rpg.save()
>>> print_tree_details([rpg])
6 4 4 1 4 7
>>> print_tree_details(Genre.tree.all())
1 - 1 0 1 2
2 - 3 0 1 6
3 2 3 1 2 3
5 2 3 1 4 5
4 - 4 0 1 8
8 4 4 1 2 3
6 4 4 1 4 7
7 6 4 2 5 6

# Deletion ####################################################################

# Delete a node which has siblings
>>> platformer_2d = Genre.objects.get(pk=platformer_2d.pk)
>>> platformer_2d.delete()
>>> print_tree_details(Genre.tree.all())
1 - 1 0 1 2
2 - 3 0 1 4
5 2 3 1 2 3
4 - 4 0 1 8
8 4 4 1 2 3
6 4 4 1 4 7
7 6 4 2 5 6

# Delete a node which has descendants
>>> rpg = Genre.objects.get(pk=rpg.pk)
>>> rpg.delete()
>>> print_tree_details(Genre.tree.all())
1 - 1 0 1 2
2 - 3 0 1 4
5 2 3 1 2 3
4 - 4 0 1 4
8 4 4 1 2 3

# Delete a root node
>>> platformer = Genre.objects.get(pk=platformer.pk)
>>> platformer.delete()
>>> print_tree_details(Genre.tree.all())
1 - 1 0 1 2
4 - 4 0 1 4
8 4 4 1 2 3

# Moving Nodes Manually #######################################################
>>> games = Category.objects.create(name='PC & Video Games')
>>> wii = Category.objects.create(name='Nintendo Wii', parent=games)
>>> wii_games = Category.objects.create(name='Games', parent=wii)
>>> wii_hardware = Category.objects.create(name='Hardware & Accessories', parent=wii)
>>> xbox360 = Category.objects.create(name='Xbox 360', parent=games)
>>> xbox360_games = Category.objects.create(name='Games', parent=xbox360)
>>> xbox360_hardware = Category.objects.create(name='Hardware & Accessories', parent=xbox360)
>>> ps3 = Category.objects.create(name='PlayStation 3', parent=games)
>>> ps3_games = Category.objects.create(name='Games', parent=ps3)
>>> ps3_hardware = Category.objects.create(name='Hardware & Accessories', parent=ps3)
>>> print_tree_details(Category.tree.all())
1 - 1 0 1 20
2 1 1 1 2 7
3 2 1 2 3 4
4 2 1 2 5 6
5 1 1 1 8 13
6 5 1 2 9 10
7 5 1 2 11 12
8 1 1 1 14 19
9 8 1 2 15 16
10 8 1 2 17 18

>>> wii = Category.objects.get(pk=wii.pk)
>>> wii.move_to(None)
>>> print_tree_details([wii])
2 - 2 0 1 6
>>> print_tree_details(Category.tree.all())
1 - 1 0 1 14
5 1 1 1 2 7
6 5 1 2 3 4
7 5 1 2 5 6
8 1 1 1 8 13
9 8 1 2 9 10
10 8 1 2 11 12
2 - 2 0 1 6
3 2 2 1 2 3
4 2 2 1 4 5

>>> games = Category.objects.get(pk=games.pk)
>>> Category.tree.make_child_node(wii, games)
>>> print_tree_details([wii])
2 1 1 1 14 19
>>> print_tree_details(Category.tree.all())
1 - 1 0 1 20
5 1 1 1 2 7
6 5 1 2 3 4
7 5 1 2 5 6
8 1 1 1 8 13
9 8 1 2 9 10
10 8 1 2 11 12
2 1 1 1 14 19
3 2 1 2 15 16
4 2 1 2 17 18

>>> ps3 = Category.objects.get(pk=ps3.pk)
>>> Category.tree.move_within_tree(wii, ps3)
>>> print_tree_details([wii])
2 8 1 2 13 18
>>> print_tree_details(Category.tree.all())
1 - 1 0 1 20
5 1 1 1 2 7
6 5 1 2 3 4
7 5 1 2 5 6
8 1 1 1 8 19
9 8 1 2 9 10
10 8 1 2 11 12
2 8 1 2 13 18
3 2 1 3 14 15
4 2 1 3 16 17

>>> ps3 = Category.objects.get(pk=ps3.pk)
>>> Category.tree.make_root_node(ps3)
>>> print_tree_details([ps3])
8 - 2 0 1 12
>>> print_tree_details(Category.tree.all())
1 - 1 0 1 8
5 1 1 1 2 7
6 5 1 2 3 4
7 5 1 2 5 6
8 - 2 0 1 12
9 8 2 1 2 3
10 8 2 1 4 5
2 8 2 1 6 11
3 2 2 2 7 8
4 2 2 2 9 10

>>> wii = Category.objects.get(pk=wii.pk)
>>> games = Category.objects.get(pk=games.pk)
>>> Category.tree.move_to_new_tree(wii, games)
>>> print_tree_details([wii])
2 1 1 1 8 13
>>> print_tree_details(Category.tree.all())
1 - 1 0 1 14
5 1 1 1 2 7
6 5 1 2 3 4
7 5 1 2 5 6
2 1 1 1 8 13
3 2 1 2 9 10
4 2 1 2 11 12
8 - 2 0 1 6
9 8 2 1 2 3
10 8 2 1 4 5

# Regression test for no level change being required
>>> xbox360_games = Category.objects.get(pk=xbox360_games.pk)
>>> Category.tree.move_within_tree(xbox360_games, wii)
>>> print_tree_details([xbox360_games])
6 2 1 2 11 12
>>> print_tree_details(Category.tree.all())
1 - 1 0 1 14
5 1 1 1 2 5
7 5 1 2 3 4
2 1 1 1 6 13
3 2 1 2 7 8
4 2 1 2 9 10
6 2 1 2 11 12
8 - 2 0 1 6
9 8 2 1 2 3
10 8 2 1 4 5

#######################
# Intra-Tree Movement #
#######################

>>> root = Node.objects.create()
>>> c_1 = Node.objects.create(parent=root)
>>> c_1_1 = Node.objects.create(parent=c_1)
>>> c_1_2 = Node.objects.create(parent=c_1)
>>> c_2 = Node.objects.create(parent=root)
>>> c_2_1 = Node.objects.create(parent=c_2)
>>> c_2_2 = Node.objects.create(parent=c_2)
>>> print_tree_details(Node.tree.all())
1 - 1 0 1 14
2 1 1 1 2 7
3 2 1 2 3 4
4 2 1 2 5 6
5 1 1 1 8 13
6 5 1 2 9 10
7 5 1 2 11 12

# Validate exceptions are raised appropriately
>>> Node.tree.move_within_tree(root, root, position='first-child')
Traceback (most recent call last):
    ...
InvalidMove: A node may not be made a child of itself or any of its descendants.
>>> Node.tree.move_within_tree(c_1, c_1_1, position='last-child')
Traceback (most recent call last):
    ...
InvalidMove: A node may not be made a child of itself or any of its descendants.
>>> Node.tree.move_within_tree(root, root, position='right')
Traceback (most recent call last):
    ...
InvalidMove: A node may not be made a sibling of itself or any of its descendants.
>>> Node.tree.move_within_tree(c_1, c_1_1, position='left')
Traceback (most recent call last):
    ...
InvalidMove: A node may not be made a sibling of itself or any of its descendants.
>>> Node.tree.move_within_tree(c_1_2, root, position='right')
Traceback (most recent call last):
    ...
InvalidMove: A node may not be made a sibling of its root node.
>>> Node.tree.move_within_tree(c_1, c_2, position='cheese')
Traceback (most recent call last):
    ...
ValueError: An invalid position was given: cheese.

# Move up the tree using first-child
>>> c_2_2 = Node.objects.get(pk=c_2_2.pk)
>>> c_1 = Node.objects.get(pk=c_1.pk)
>>> Node.tree.move_within_tree(c_2_2, c_1, 'first-child')
>>> print_tree_details([c_2_2])
7 2 1 2 3 4
>>> print_tree_details(Node.tree.all())
1 - 1 0 1 14
2 1 1 1 2 9
7 2 1 2 3 4
3 2 1 2 5 6
4 2 1 2 7 8
5 1 1 1 10 13
6 5 1 2 11 12

# Undo the move using right
>>> c_2_1 = Node.objects.get(pk=c_2_1.pk)
>>> c_2_2.move_to(c_2_1, 'right')
>>> print_tree_details([c_2_2])
7 5 1 2 11 12
>>> print_tree_details(Node.tree.all())
1 - 1 0 1 14
2 1 1 1 2 7
3 2 1 2 3 4
4 2 1 2 5 6
5 1 1 1 8 13
6 5 1 2 9 10
7 5 1 2 11 12

# Move up the tree with descendants using first-child
>>> c_2 = Node.objects.get(pk=c_2.pk)
>>> c_1 = Node.objects.get(pk=c_1.pk)
>>> Node.tree.move_within_tree(c_2, c_1, 'first-child')
>>> print_tree_details([c_2])
5 2 1 2 3 8
>>> print_tree_details(Node.tree.all())
1 - 1 0 1 14
2 1 1 1 2 13
5 2 1 2 3 8
6 5 1 3 4 5
7 5 1 3 6 7
3 2 1 2 9 10
4 2 1 2 11 12

# Undo the move using right
>>> c_1 = Node.objects.get(pk=c_1.pk)
>>> Node.tree.move_within_tree(c_2, c_1, 'right')
>>> print_tree_details([c_2])
5 1 1 1 8 13
>>> print_tree_details(Node.tree.all())
1 - 1 0 1 14
2 1 1 1 2 7
3 2 1 2 3 4
4 2 1 2 5 6
5 1 1 1 8 13
6 5 1 2 9 10
7 5 1 2 11 12

COVERAGE    | U1 | U> | D1 | D>
------------+----+----+----+----
first-child | Y  | Y  |    |
last-child  |    |    |    |
left        |    |    |    |
right       |    |    | Y  | Y

# Move down the tree using first-child
>>> c_1_2 = Node.objects.get(pk=c_1_2.pk)
>>> c_2 = Node.objects.get(pk=c_2.pk)
>>> Node.tree.move_within_tree(c_1_2, c_2, 'first-child')
>>> print_tree_details([c_1_2])
4 5 1 2 7 8
>>> print_tree_details(Node.tree.all())
1 - 1 0 1 14
2 1 1 1 2 5
3 2 1 2 3 4
5 1 1 1 6 13
4 5 1 2 7 8
6 5 1 2 9 10
7 5 1 2 11 12

# Undo the move using last-child
>>> c_1 = Node.objects.get(pk=c_1.pk)
>>> Node.tree.move_within_tree(c_1_2, c_1, 'last-child')
>>> print_tree_details([c_1_2])
4 2 1 2 5 6
>>> print_tree_details(Node.tree.all())
1 - 1 0 1 14
2 1 1 1 2 7
3 2 1 2 3 4
4 2 1 2 5 6
5 1 1 1 8 13
6 5 1 2 9 10
7 5 1 2 11 12

# Move down the tree with descendants using first-child
>>> c_1 = Node.objects.get(pk=c_1.pk)
>>> c_2 = Node.objects.get(pk=c_2.pk)
>>> Node.tree.move_within_tree(c_1, c_2, 'first-child')
>>> print_tree_details([c_1])
2 5 1 2 3 8
>>> print_tree_details(Node.tree.all())
1 - 1 0 1 14
5 1 1 1 2 13
2 5 1 2 3 8
3 2 1 3 4 5
4 2 1 3 6 7
6 5 1 2 9 10
7 5 1 2 11 12

# Undo the move using left
>>> c_2 = Node.objects.get(pk=c_2.pk)
>>> Node.tree.move_within_tree(c_1, c_2, 'left')
>>> print_tree_details([c_1])
2 1 1 1 2 7
>>> print_tree_details(Node.tree.all())
1 - 1 0 1 14
2 1 1 1 2 7
3 2 1 2 3 4
4 2 1 2 5 6
5 1 1 1 8 13
6 5 1 2 9 10
7 5 1 2 11 12

COVERAGE    | U1 | U> | D1 | D>
------------+----+----+----+----
first-child | Y  | Y  | Y  | Y
last-child  | Y  |    |    |
left        |    | Y  |    |
right       |    |    | Y  | Y

# Move up the tree using right
>>> c_2_2 = Node.objects.get(pk=c_2_2.pk)
>>> c_1_1 = Node.objects.get(pk=c_1_1.pk)
>>> Node.tree.move_within_tree(c_2_2, c_1_1, 'right')
>>> print_tree_details([c_2_2])
7 2 1 2 5 6
>>> print_tree_details(Node.tree.all())
1 - 1 0 1 14
2 1 1 1 2 9
3 2 1 2 3 4
7 2 1 2 5 6
4 2 1 2 7 8
5 1 1 1 10 13
6 5 1 2 11 12

# Undo the move using last-child
>>> c_2 = Node.objects.get(pk=c_2.pk)
>>> Node.tree.move_within_tree(c_2_2, c_2, 'last-child')
>>> print_tree_details([c_2_2])
7 5 1 2 11 12
>>> print_tree_details(Node.tree.all())
1 - 1 0 1 14
2 1 1 1 2 7
3 2 1 2 3 4
4 2 1 2 5 6
5 1 1 1 8 13
6 5 1 2 9 10
7 5 1 2 11 12

# Move up the tree with descendants using right
>>> c_2 = Node.objects.get(pk=c_2.pk)
>>> c_1_1 = Node.objects.get(pk=c_1_1.pk)
>>> Node.tree.move_within_tree(c_2, c_1_1, 'right')
>>> print_tree_details([c_2])
5 2 1 2 5 10
>>> print_tree_details(Node.tree.all())
1 - 1 0 1 14
2 1 1 1 2 13
3 2 1 2 3 4
5 2 1 2 5 10
6 5 1 3 6 7
7 5 1 3 8 9
4 2 1 2 11 12

# Undo the move using last-child
>>> root = Node.objects.get(pk=root.pk)
>>> Node.tree.move_within_tree(c_2, root, 'last-child')
>>> print_tree_details([c_2])
5 1 1 1 8 13
>>> print_tree_details(Node.tree.all())
1 - 1 0 1 14
2 1 1 1 2 7
3 2 1 2 3 4
4 2 1 2 5 6
5 1 1 1 8 13
6 5 1 2 9 10
7 5 1 2 11 12

COVERAGE    | U1 | U> | D1 | D>
------------+----+----+----+----
first-child | Y  | Y  | Y  | Y
last-child  | Y  |    | Y  | Y
left        |    | Y  |    |
right       | Y  | Y  | Y  | Y

# Move down the tree with descendants using left
>>> c_1 = Node.objects.get(pk=c_1.pk)
>>> c_2_2 = Node.objects.get(pk=c_2_2.pk)
>>> Node.tree.move_within_tree(c_1, c_2_2, 'left')
>>> print_tree_details([c_1])
2 5 1 2 5 10
>>> print_tree_details(Node.tree.all())
1 - 1 0 1 14
5 1 1 1 2 13
6 5 1 2 3 4
2 5 1 2 5 10
3 2 1 3 6 7
4 2 1 3 8 9
7 5 1 2 11 12

# Undo the move using first-child
>>> root = Node.objects.get(pk=root.pk)
>>> Node.tree.move_within_tree(c_1, root, 'first-child')
>>> print_tree_details([c_1])
2 1 1 1 2 7
>>> print_tree_details(Node.tree.all())
1 - 1 0 1 14
2 1 1 1 2 7
3 2 1 2 3 4
4 2 1 2 5 6
5 1 1 1 8 13
6 5 1 2 9 10
7 5 1 2 11 12

# Move down the tree using left
>>> c_1_1 = Node.objects.get(pk=c_1_1.pk)
>>> c_2_2 = Node.objects.get(pk=c_2_2.pk)
>>> Node.tree.move_within_tree(c_1_1, c_2_2, 'left')
>>> print_tree_details([c_1_1])
3 5 1 2 9 10
>>> print_tree_details(Node.tree.all())
1 - 1 0 1 14
2 1 1 1 2 5
4 2 1 2 3 4
5 1 1 1 6 13
6 5 1 2 7 8
3 5 1 2 9 10
7 5 1 2 11 12

# Undo the move using left
>>> c_1_2 = Node.objects.get(pk=c_1_2.pk)
>>> Node.tree.move_within_tree(c_1_1,  c_1_2, 'left')
>>> print_tree_details([c_1_1])
3 2 1 2 3 4
>>> print_tree_details(Node.tree.all())
1 - 1 0 1 14
2 1 1 1 2 7
3 2 1 2 3 4
4 2 1 2 5 6
5 1 1 1 8 13
6 5 1 2 9 10
7 5 1 2 11 12

COVERAGE    | U1 | U> | D1 | D>
------------+----+----+----+----
first-child | Y  | Y  | Y  | Y
last-child  | Y  | Y  | Y  | Y
left        | Y  | Y  | Y  | Y
right       | Y  | Y  | Y  | Y

I guess we're covered :)

#######################
# Inter-Tree Movement #
#######################

>>> new_root = Node.objects.create()
>>> print_tree_details(Node.tree.all())
1 - 1 0 1 14
2 1 1 1 2 7
3 2 1 2 3 4
4 2 1 2 5 6
5 1 1 1 8 13
6 5 1 2 9 10
7 5 1 2 11 12
8 - 2 0 1 2

# Moving child nodes between trees ############################################

# Validate exceptions are raised appropriately
>>> Node.tree.move_to_new_tree(c_1, c_1, position='first-child')
Traceback (most recent call last):
    ...
InvalidTarget: The target node must be in a different tree.
>>> Node.tree.move_to_new_tree(c_1, new_root, position='left')
Traceback (most recent call last):
    ...
InvalidMove: A node may not be made a sibling of a root node.
>>> Node.tree.move_to_new_tree(c_1, new_root, position='right')
Traceback (most recent call last):
    ...
InvalidMove: A node may not be made a sibling of a root node.
>>> Node.tree.move_to_new_tree(c_1, new_root, position='cheese')
Traceback (most recent call last):
    ...
ValueError: An invalid position was given: cheese.

# Move using default (last-child)
>>> c_2 = Node.objects.get(pk=c_2.pk)
>>> c_2.move_to(new_root)
>>> print_tree_details([c_2])
5 8 2 1 2 7
>>> print_tree_details(Node.tree.all())
1 - 1 0 1 8
2 1 1 1 2 7
3 2 1 2 3 4
4 2 1 2 5 6
8 - 2 0 1 8
5 8 2 1 2 7
6 5 2 2 3 4
7 5 2 2 5 6

# Move using left
>>> c_1_1 = Node.objects.get(pk=c_1_1.pk)
>>> c_2 = Node.objects.get(pk=c_2.pk)
>>> Node.tree.move_to_new_tree(c_1_1, c_2, position='left')
>>> print_tree_details([c_1_1])
3 8 2 1 2 3
>>> print_tree_details(Node.tree.all())
1 - 1 0 1 6
2 1 1 1 2 5
4 2 1 2 3 4
8 - 2 0 1 10
3 8 2 1 2 3
5 8 2 1 4 9
6 5 2 2 5 6
7 5 2 2 7 8

# Move using first-child
>>> c_1_2 = Node.objects.get(pk=c_1_2.pk)
>>> c_2 = Node.objects.get(pk=c_2.pk)
>>> Node.tree.move_to_new_tree(c_1_2, c_2, position='first-child')
>>> print_tree_details([c_1_2])
4 5 2 2 5 6
>>> print_tree_details(Node.tree.all())
1 - 1 0 1 4
2 1 1 1 2 3
8 - 2 0 1 12
3 8 2 1 2 3
5 8 2 1 4 11
4 5 2 2 5 6
6 5 2 2 7 8
7 5 2 2 9 10

# Move using right
>>> c_2 = Node.objects.get(pk=c_2.pk)
>>> c_1 = Node.objects.get(pk=c_1.pk)
>>> Node.tree.move_to_new_tree(c_2, c_1, position='right')
>>> print_tree_details([c_2])
5 1 1 1 4 11
>>> print_tree_details(Node.tree.all())
1 - 1 0 1 12
2 1 1 1 2 3
5 1 1 1 4 11
4 5 1 2 5 6
6 5 1 2 7 8
7 5 1 2 9 10
8 - 2 0 1 4
3 8 2 1 2 3

# Move using last-child
>>> c_1_1 = Node.objects.get(pk=c_1_1.pk)
>>> Node.tree.move_to_new_tree(c_1_1, c_2, position='last-child')
>>> print_tree_details([c_1_1])
3 5 1 2 11 12
>>> print_tree_details(Node.tree.all())
1 - 1 0 1 14
2 1 1 1 2 3
5 1 1 1 4 13
4 5 1 2 5 6
6 5 1 2 7 8
7 5 1 2 9 10
3 5 1 2 11 12
8 - 2 0 1 2

# Moving a root node into another tree as a child node ########################

# Validate exceptions are raised appropriately
>>> Node.tree.make_child_node(c_1, new_root, position='first-child')
Traceback (most recent call last):
    ...
ValueError: A root node must be given.
>>> Node.tree.make_child_node(root, c_1, position='first-child')
Traceback (most recent call last):
    ...
InvalidTarget: The target node must be in a different tree.
>>> Node.tree.make_child_node(new_root, root, position='left')
Traceback (most recent call last):
    ...
InvalidMove: A node may not be made a sibling of a root node.
>>> Node.tree.make_child_node(new_root, root, position='right')
Traceback (most recent call last):
    ...
InvalidMove: A node may not be made a sibling of a root node.
>>> Node.tree.make_child_node(new_root, c_1, position='cheese')
Traceback (most recent call last):
    ...
ValueError: An invalid position was given: cheese.

>>> new_root = Node.objects.get(pk=new_root.pk)
>>> c_2 = Node.objects.get(pk=c_2.pk)
>>> new_root.move_to(c_2, position='first-child')
>>> print_tree_details([new_root])
8 5 1 2 5 6
>>> print_tree_details(Node.tree.all())
1 - 1 0 1 16
2 1 1 1 2 3
5 1 1 1 4 15
8 5 1 2 5 6
4 5 1 2 7 8
6 5 1 2 9 10
7 5 1 2 11 12
3 5 1 2 13 14

>>> new_root = Node.objects.create()
>>> root = Node.objects.get(pk=root.pk)
>>> Node.tree.make_child_node(new_root, root, position='last-child')
>>> print_tree_details([new_root])
9 1 1 1 16 17
>>> print_tree_details(Node.tree.all())
1 - 1 0 1 18
2 1 1 1 2 3
5 1 1 1 4 15
8 5 1 2 5 6
4 5 1 2 7 8
6 5 1 2 9 10
7 5 1 2 11 12
3 5 1 2 13 14
9 1 1 1 16 17

>>> new_root = Node.objects.create()
>>> c_2_1 = Node.objects.get(pk=c_2_1.pk)
>>> Node.tree.make_child_node(new_root, c_2_1, position='left')
>>> print_tree_details([new_root])
10 5 1 2 9 10
>>> print_tree_details(Node.tree.all())
1 - 1 0 1 20
2 1 1 1 2 3
5 1 1 1 4 17
8 5 1 2 5 6
4 5 1 2 7 8
10 5 1 2 9 10
6 5 1 2 11 12
7 5 1 2 13 14
3 5 1 2 15 16
9 1 1 1 18 19

>>> new_root = Node.objects.create()
>>> c_1 = Node.objects.get(pk=c_1.pk)
>>> Node.tree.make_child_node(new_root, c_1, position='right')
>>> print_tree_details([new_root])
11 1 1 1 4 5
>>> print_tree_details(Node.tree.all())
1 - 1 0 1 22
2 1 1 1 2 3
11 1 1 1 4 5
5 1 1 1 6 19
8 5 1 2 7 8
4 5 1 2 9 10
10 5 1 2 11 12
6 5 1 2 13 14
7 5 1 2 15 16
3 5 1 2 17 18
9 1 1 1 20 21
"""

# TODO Fixtures won't work with Django MPTT unless the pre_save signal
#      is given the ``save()`` method's ``raw`` argument, so we know not
#      to attempt any tree processing.
#
#      http://code.djangoproject.com/ticket/5422 has a patch for this.
#
#      Once this change is available, we can think about using the more
#      appropriate ``django.tests.TestCase`` with fixtures for testing
#      specific features without having a knock-on effect on other
#      tests.
