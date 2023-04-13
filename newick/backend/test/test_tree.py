from newick.backend.tree import Tree
from newick.backend.path import Path

def test_basic():
    r = Tree.RootNode("R")
    t = Tree(r)
    t.add_new_node(Path("R", [("A", 1.0)]))
    t.add_new_node(Path("R", [("B", 2.0)]))
    assert t.to_string() == "(A:1,B:2)R;"
