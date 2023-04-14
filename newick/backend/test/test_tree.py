from newick.backend.tree import Tree
from newick.backend.path import Path


def test_basic():
    r = Tree.RootNode("R")
    t = Tree(r)
    t.add_new_node(Path("R", [("A", 1.0)]))
    t.add_new_node(Path("R", [("B", 2.0)]))
    assert t.to_string() == "(A:1,B:2)R;"

def test_partial_duplicate():
    r = Tree.RootNode("R")
    t = Tree(r)
    t.add_new_node(Path("R", [("A", 1.0)]))
    t.add_new_node(Path("R", [("B", 4.0)]))
    t.add_new_node(Path("R", [("B", 2.0), ("C-c", 2.2)]))
    assert t.to_string() == "(A:1,(C-c:2.2)B:3)R;"
    assert t._root.get_child_by_label("B").get_duplication_count() == 0
    t.add_new_node(Path("R", [("B", 4.0)]))
    assert t.to_string() == "(A:1,(C-c:2.2)B:3.5)R;"
    assert t._root.get_child_by_label("B").get_duplication_count() == 1
    
def test_exact_duplicate():
    r = Tree.RootNode("R")
    t = Tree(r)
    t.add_new_node(Path("R", [("A", 1.0)]))
    t.add_new_node(Path("R", [("B", 2.0), ("C-c", 2.2)]))
    t.add_new_node(Path("R", [("B", 4.0), ("C-c", 2.2)]))
    assert t.to_string() == "(A:1,(C-c:2.2)B:3)R;"
    assert t._root.get_child_by_label("B").get_duplication_count() == 0
    assert t._root.get_child_by_label("B").get_child_by_label("C-c").get_duplication_count() == 1