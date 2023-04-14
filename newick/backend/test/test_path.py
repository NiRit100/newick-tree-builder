from newick.backend.path import Path
import pytest

def test_basic0():
    a = Path("R", [("A", 1.0)])
    assert len(a) == 2
    assert str(a) == "Path(R:0 -> A:1)"
    
def test_basic1():
    b = Path("R", [("B", 2.0), ("C", 2.2)])
    assert len(b) == 3
    assert str(b) == "Path(R:0 -> B:2 -> C:2.2)"

def test_basic3():
    c = Path("Root")
    assert len(c) == 1
    assert str(c) == "Path(Root:0)"
    
def test_getitem():
    b = Path("R", [("B", 2.0), ("C", 2.2)])
    assert b[1] == ("B", 2.0)
    with pytest.raises(Exception) as e:
        c = b[6]
    
def test_iter():
    b = Path("R", [("B", 2), ("C", 2.2), ("meep", 0)])
    for c in b:
        assert isinstance(c, tuple)
        assert len(c) == 2
        assert isinstance(c[0], str)
        assert isinstance(c[1], float)
        