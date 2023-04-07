def generate_nhx(dict:dict, ext_head='&&NHX') -> str:
    if dict == None or len(dict) == 0:
        return "[" + ext_head + "]"
    else:
        ret_elements = []
        for key in dict.keys:
            str_key = nhx_filter_str(str(key))
            str_val = nhx_filter_str(dict[key])
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
    last_c = ''
    for c in string:
        if          not c.isalnum() \
                and not c in sym_no_escape \
                and not last_c == '\\':
            string.replace(c, '\\'+c)
        last_c = c
    return string
