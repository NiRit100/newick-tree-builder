from newick.backend.tree import Tree
from newick.backend.node import RootNode
from newick.backend.path import Path
from newick.backend.util_funcs import format_int


def tree_parse_basic(text:str, 
                     root_label:str=None, 
                     line_delim:str=";", 
                     waypoint_sep:str=",",
                     label_dist_sep:str=":", 
                     trim_sym:list[str]=['\r', '\n', ' ']) -> Tree:
    index = 0
    lines = text.split(line_delim)
    outtree = Tree(RootNode(root_label))
    for line in lines:
        waypoints = line.split(waypoint_sep)
        outpath = Path(root_label=root_label)
        for waypoint in waypoints:
            for sym in trim_sym:
                waypoint.removeprefix(sym)
                waypoint.removesuffix(sym)
            waypoint_split = waypoint.split(label_dist_sep)
            if len(waypoint_split) == 1:
                ndist = float("-inf")
            else:
                ndist = float(waypoint_split[1])
            nlabel = waypoint_split[0]
            outpath.add(nlabel, ndist)
        myaddinfo = {"_parse_index": { format_int(index) }}
        outtree.add_new_node(outpath, 
                             additional_info=myaddinfo)
        index += 1
    return outtree