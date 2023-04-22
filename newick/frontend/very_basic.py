from newick.backend.tree import Tree
from newick.backend.node import RootNode, Node
from newick.backend.path import Path
from newick.backend.util_funcs import format_int
from typing import Callable
from enum import Enum


class BlacklistTokenStrat(Enum):
    IGNORE_BLACKLIST = 0
    DROP_TOKEN = 1
    DROP_AFTER_FIRST = 2
    DROP_ENTIRE_LINE = 3
    

def tree_parse_basic(text:str, 
                     root_label:str=None, 
                     line_delim:str=";", 
                     waypoint_sep:str=",",
                     label_dist_sep:str=":", 
                     trim_sym:str='\r\n ',
                     blacklist:list[str]=["n.a.", "O", "Unclassified"],
                     blacklist_token_strat:BlacklistTokenStrat=BlacklistTokenStrat.DROP_AFTER_FIRST,
                     default_dist:float=1.0,
                     dist_adjust_strategy:Callable[[Node,float],float]=None) -> Tree:
    index = 0
    lines = text.split(line_delim)
    outtree = Tree(RootNode(root_label), 
                   default_dist=default_dist)
    outtree.set_dist_adjust_strat(dist_adjust_strategy)
    for line in lines:
        line = clean_token(line, trim_sym)
        if line != "":
            waypoints = line.split(waypoint_sep)
            outpath = Path(root_label=root_label)
            for waypoint in waypoints:
                flag_drop_after_token = False
                waypoint = clean_token(waypoint, trim_sym)
                waypoint_split = waypoint.split(label_dist_sep)
                if (waypoint in blacklist \
                        or waypoint_split in blacklist):
                    match blacklist_token_strat:
                        case BlacklistTokenStrat.DROP_ENTIRE_LINE:
                            outpath = None
                            break
                        case BlacklistTokenStrat.DROP_TOKEN:
                            break
                        case BlacklistTokenStrat.DROP_AFTER_FIRST:
                            flag_drop_after_token = True
                if len(waypoint_split) == 1:
                    ndist = float("-inf")
                else:
                    ndist = float(waypoint_split[1])
                nlabel = waypoint_split[0]
                outpath.add(nlabel, ndist)
                if flag_drop_after_token:
                    break
            if outpath:
                myaddinfo = {"_parse_index": { format_int(index) }}
                outtree.add_new_node(outpath, 
                                    additional_info=myaddinfo)
        index += 1
    return outtree

def clean_token(token, trim_sym):
    return token.strip(trim_sym)