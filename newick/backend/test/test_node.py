from newick.backend.node import Node


def test_simple_instantiation_and_parenting():
    # label only
    node0 = Node("testa")
    assert node0.get_label() == "testa"
    # label and distance
    node1 = Node("testb", distance=2.25)
    assert node1.get_label() == "testb"
    assert node1.get_distance() == 2.25
    # now some parenting
    node0.add_child(node1)
    assert node0.count_children() == 1
    print(node1._children_by_label)
    assert node1.count_children() == 0
    assert node0.get_child_by_label("testa") is node1
    assert node0.get_child_by_label("xyz") == None
    
#def test_