from newick.frontend.very_basic import tree_parse_basic, BlacklistTokenStrat
import os
import pytest


def test_basic0():
    txt = """
    a0,b0,c0,d0;
    a1,b0,c1,d0;
    a0,b1,c2;
    a0,b0,c4,d1;
    """
    t = tree_parse_basic(txt, "r")
    print("---")
    print(t.to_string())
    print("---")
    assert t.to_string() == "((((d0:1)c0:1,(d1:1)c4:1)b0:1,(c2:1)b1:1)a0:1,(((d0:1)c1:1)b0:1)a1:1)r;"
    
def test_basic0_nodist():
    txt = """
    a0,b0,c0,d0;
    a1,b0,c1,d0;
    a0,b1,c2;
    a0,b0,c4,d1;
    """
    t = tree_parse_basic(txt, "r")
    print("---")
    print(t.to_string(with_distances=False))
    print("---")
    assert t.to_string(with_distances=False) == "((((d0)c0,(d1)c4)b0,(c2)b1)a0,(((d0)c1)b0)a1)r;"
    
def test_basic0_nodist_blacklist_dropafterfirst():
    txt = """
    a0,b0,c0,d0;
    a1,b0,c1,d0;
    a0,b1,c2;
    a0,b0,c4,d1;
    a0,n.a.,n.a.;
    """
    t = tree_parse_basic(txt, "r", blacklist_token_strat=BlacklistTokenStrat.DROP_AFTER_FIRST)
    print("---")
    print(t.to_string(with_distances=False))
    print("---")
    assert t.to_string(with_distances=False) == "((((d0)c0,(d1)c4)b0,(c2)b1,n.a.)a0,(((d0)c1)b0)a1)r;"
    
def test_basic0_nodist_blacklist_ignore():
    txt = """
    a0,b0,c0,d0;
    a1,b0,c1,d0;
    a0,b1,c2;
    a0,b0,c4,d1;
    a0,n.a.,n.a.;
    """
    t = tree_parse_basic(txt, "r", blacklist_token_strat=BlacklistTokenStrat.IGNORE_BLACKLIST)
    print("---")
    print(t.to_string(with_distances=False))
    print("---")
    assert t.to_string(with_distances=False) == "((((d0)c0,(d1)c4)b0,(c2)b1,(n.a.)n.a.)a0,(((d0)c1)b0)a1)r;"
    
def test_basic0_nodist_blacklist_drop():
    txt = """
    a0,b0,c0,d0;
    a1,b0,c1,d0;
    a0,b1,c2;
    a0,b0,c4,d1;
    a0,n.a.,n.a.;
    """
    t = tree_parse_basic(txt, "r", blacklist_token_strat=BlacklistTokenStrat.DROP_TOKEN)
    print("---")
    print(t.to_string(with_distances=False))
    print("---")
    assert t.to_string(with_distances=False) == "((((d0)c0,(d1)c4)b0,(c2)b1)a0,(((d0)c1)b0)a1)r;"
        
def test_basic0_nodist_blacklist_dropline():
    txt = """
    a0,b0,c0,d0;
    a1,b0,c1,d0;
    a0,b1,c2;
    a0,b0,c4,d1;
    a0,n.a.,n.a.;
    """
    t = tree_parse_basic(txt, "r", blacklist_token_strat=BlacklistTokenStrat.DROP_ENTIRE_LINE)
    print("---")
    print(t.to_string(with_distances=False))
    print("---")
    assert t.to_string(with_distances=False) == "((((d0)c0,(d1)c4)b0,(c2)b1)a0,(((d0)c1)b0)a1)r;"
    
#@pytest.mark.xfail()
def test_file0():
    #import pdb; pdb.set_trace()
    with open('./test_file0.txt', 'r') as file:
        txt = file.read()
        t = tree_parse_basic(txt, "r")
        with open("./test_file0_out.tree", "w") as out:
            out_str = t.to_string()
            out.write(out_str)