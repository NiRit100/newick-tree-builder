def generate_nhx(dict:dict, ext_head='&&NHX') -> str:
    if dict == None or len(dict) == 0:
        return ""
    else:
        ret_elements = []
        for key in dict.keys():
            str_key = nhx_filter_str(str(key))
            str_val = nhx_filter_str(str(dict[key]))
            str_el = str_key + '=' + str_val
            ret_elements.append(str_el)
        str_elements = ':'.join(ret_elements)
        return "[" + ext_head + ':' + str_elements + "]"
    
def nhx_filter_str(string:str):
    global _NHX_FILTER_NO_ESCAPE
    if '_NHX_FILTER_NO_ESCAPE' in globals():
        sym_no_escape = _NHX_FILTER_NO_ESCAPE
    else:
        sym_no_escape =  {'_', '-', '.', '+', '?', '!', '#', '~', 
                        '\'', '%', '§', '$', '€', '&', '/', '@', 
                        '*', ' '}
    skipset = set()
    mod_string = string
    for c in set(string):
        if          not c.isalnum() \
                and not c in sym_no_escape \
                and not c in skipset:
            mod_string = mod_string.replace(c, '\\'+c)
            skipset.add(c)
    return mod_string
