from newick.backend.nhx_util import *

def test_generate_nhx_null():
    assert generate_nhx(None) == ""
    
def test_generate_nhx_empty():
    assert generate_nhx(dict()) == ""
    
def test_generate_nhx_alphanum():
    dct = {"A":1, "Bonn": None, 52: True}
    assert generate_nhx(dct) == "[&&NHX:A=1:Bonn=None:52=True]"

def test_generate_nhx_othersym():
    dct = {"A=C":1, "B:nn": "B(er)lin", "new\n-line": "s p a c e"}
    assert generate_nhx(dct) == "[&&NHX:A\\=C=1:B\\:nn=B\\(er\\)lin:new\\\n-line=s p a c e]"
    
def test_nhx_filter_str_0():
    assert nhx_filter_str("A=C") == "A\\=C"
    