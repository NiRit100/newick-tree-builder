from newick.backend.node import Node


# BASIC TESTS


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
    assert node1.count_children() == 0
    assert node0.get_child_by_label("testb") is node1
    assert node0.get_child_by_label("xyz") == None
    assert node1.get_child_by_label("testa") == None
    
def test_repr_default_single():
    node0 = Node("testa")
    assert str(node0) == "testa:1"
    
def test_repr_default_two():
    node0 = Node("A")
    node1 = Node("B", distance=2)
    node0.add_child(node1)
    assert str(node0) == "(B:2)A:1"
    
def test_repr_default_afew():
    node0 = Node("A")
    node1 = Node("B", distance=2)
    node2 = Node("C", distance=1.2)
    node3 = Node("D", distance=5)
    node4 = Node("E")
    node5 = Node("F", distance=4.2)
    node2.add_child(node3)
    node2.add_child(node4)
    node1.add_child(node2)
    node0.add_child(node5)
    node0.add_child(node1)
    assert str(node0) == "(F:4.2,((D:5,E:1)C:1.2)B:2)A:1"
    
def test_repr_nodist_single():
    node0 = Node("testa")
    assert node0.to_string(with_distances=False) == "testa"
    
def test_repr_nodist_two():
    node0 = Node("A")
    node1 = Node("B", distance=2)
    node0.add_child(node1)
    assert node0.to_string(with_distances=False) == "(B)A"
    
def test_repr_nodist_afew():
    node0 = Node("A")
    node1 = Node("B", distance=2)
    node2 = Node("C", distance=1.2)
    node3 = Node("D", distance=5)
    node4 = Node("E")
    node5 = Node("F", distance=4.2)
    node2.add_child(node3)
    node2.add_child(node4)
    node1.add_child(node2)
    node0.add_child(node5)
    node0.add_child(node1)
    assert node0.to_string(with_distances=False) == "(F,((D,E)C)B)A"
    
def test_repr_default_single():
    node0 = Node("testa")
    assert node0.to_string(with_labels=False) == ":1"
    
def test_repr_default_two():
    node0 = Node("A")
    node1 = Node("B", distance=2)
    node0.add_child(node1)
    assert node0.to_string(with_labels=False) == "(:2):1"
    
def test_repr_default_afew():
    node0 = Node("A")
    node1 = Node("B", distance=2)
    node2 = Node("C", distance=1.2)
    node3 = Node("D", distance=5)
    node4 = Node("E")
    node5 = Node("F", distance=4.2)
    node2.add_child(node3)
    node2.add_child(node4)
    node1.add_child(node2)
    node0.add_child(node5)
    node0.add_child(node1)
    assert node0.to_string(with_labels=False) == "(:4.2,((:5,:1):1.2):2):1"
    
def test_repr_labels_only_on_leaves_afew():
    node0 = Node("A")
    node1 = Node("B", distance=2)
    node2 = Node("C", distance=1.2)
    node3 = Node("A", distance=5)
    node4 = Node("E")
    node5 = Node("F", distance=4.2)
    node2.add_child(node3)
    node2.add_child(node4)
    node1.add_child(node2)
    node0.add_child(node5)
    node0.add_child(node1)
    only_leaves_name_mapper = lambda n:  n.get_label() if n.is_leaf() else ""
    assert node0.to_string(outputlabel_mapper=only_leaves_name_mapper) == "(F:4.2,((A:5,E:1):1.2):2):1"
    
def test_duplicates():
    node0 = Node("A")
    node1 = Node("B", distance=2)
    node2 = Node("B")
    assert node0.add_child(node1)[0]
    assert not node0.add_child(node2)[0]
    assert str(node0) == "(B:2)A:1"
    assert node1.get_duplication_count() == 1
    
    
# TODO: HYBRID NODE TESTS

