from newick.backend.node import Node


def test_simple_instantiation():
    node0 = Node("testa")
    assert node0.get_label() == "testa"
