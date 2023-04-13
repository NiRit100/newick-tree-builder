from newick.backend.path import Path

def test_basic():
    a = Path("R", [("A", 1.0)])
    b = Path("R", [("B", 2.0)])
    c = Path("Root")
    assert len(a) == 2
    assert str(a) == "R:0 -> A:1"
    assert len(b) == 2
    assert str(b) == "R:0 -> B:2"
    assert len(c) == 1
    assert str(c) == "Root:0"
