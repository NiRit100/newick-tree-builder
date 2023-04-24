from newick.backend.tree import Tree
from newick.backend.node import RootNode, Node
from newick.backend.path import Path
from newick.backend.util_funcs import format_int
from typing import Callable
from enum import Enum


class BlacklistTokenStrat(Enum):
    """
    Defines constants representing the paticular strategies of 
    handling blacklisted waypoint name tokens.
    
    IGNORE_BLACKLIST: 
        Ignore the blacklist (handle blacklisted tokens like non-
        blacklisted tokens) and therefore do not drop anything.
    DROP_TOKEN:
        Drop (i.e. do not process) blacklisted tokens and the tokens of
        the rest of the path (children).
    DROP_AFTER_FIRST:
        Drop (i.e. do not process) *not* the blacklisted token itself,
        but their children.
        This is useful for typical classification tables, where
        blacklisted tokens semantically represent a "not classified"
        value, and all their children will logically also be 
        "not classified".
    DROP_ENTIRE_LINE:
        Drop (i.e. do not process) the entire path (line) when it 
        contains a blacklisted token. 
    """
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
    """
    A very ugly, very basic parser that produces a newick tree out 
    of a given set of tree paths.
     
    Input text format (example):
    
      A:da,B:db,C:dc,E:de;
      A,B,F:df,G;
    
    where A, B, C, E, F and G are the waypoints 
    and da, db, dc, de and df their respective distances from their
    prior waypoint. The tree represented by this input would look
    something like this (distances ignored in this illustration): 
    
                     +- C --- E
      r --- A --- B -+
                     +- F --- G
                     
    The corresponding newick notation (with default settings) would be
    
      ((((E:de)C:dc),((G:default_dist)F:df)B:db)A:da)r;
    
    This algorithm creates a new root node with a given label -- in
    the illustration above, this would be "r". Each path given will be
    mounted as a child of this root. 
    
    Note: 
      * Duplicates are generally allowed. 
      * Distances can be omitted. 
      * No hybridisation or NH-X support.
      * Each end-point of a path will contain attached NHX data with a 
        list of the indices of the path in the input text (i.e. a line 
        number), under the key '_parse_index'. Check it out!

    Args:
        text (str): Input text to be parsed.
        root_label (str, optional): 
            Label of the tree's newly created root. 
            Defaults to None.
        line_delim (str, optional): 
            Line (path) end symbols. 
            Defaults to ";".
        waypoint_sep (str, optional): 
            Delimiter between each pair of adjecent waypoints. 
            Defaults to ",".
        label_dist_sep (str, optional): 
            Delimiter between each waypoint and its respective 
            distance.
            Defaults to ":".
        trim_sym (str, optional): Symbold to be trimmed away from each
            line, as a string. 
            Defaults to '\\r\\n ' (CR, LF, Space).
        blacklist (list[str], optional): 
            List of waypoint names that are to be handled as 
            blacklisted.
            See also `blacklist_token_strat`. 
            Defaults to ["n.a.", "O", "Unclassified"].
        blacklist_token_strat (BlacklistTokenStrat, optional): 
            Determines the strategy of handling blacklisted waypoint 
            name tokens. Your options are:
            IGNORE_BLACKLIST: 
                Ignore the blacklist (handle blacklisted tokens like 
                non-blacklisted tokens) and therefore do not drop 
                anything.
            DROP_TOKEN:
                Drop (i.e. do not process) blacklisted tokens and the
                tokens of the rest of the path (children).
            DROP_AFTER_FIRST:
                Drop (i.e. do not process) *not* the blacklisted token
                itself, but their children.
                This is useful for typical classification tables, where
                blacklisted tokens semantically represent a "not 
                classified" value, and all their children will
                logically also be "not classified".
            DROP_ENTIRE_LINE:
                Drop (i.e. do not process) the entire path (line) when 
                it contains a blacklisted token. . 
            Defaults to BlacklistTokenStrat.DROP_AFTER_FIRST.
        default_dist (float, optional): 
            Distance to assign to a Node when no distance is given in
            the input.  
            Defaults to 1.0.
        dist_adjust_strategy (Callable[[Node,float],float], optional): 
            Function of 
              (old_node, new_nodes_dist) -> old_nodes_new_dist
            to calculate the new distance to assign to the old (already
            present) node, with respect to the distance of the supposed
            new node, in case of duplication.
            Defaults to None, which internally represents calculating
            the average over all the distances given for that node.
            You can define your own function or use the pre-defined 
            ones from the `newick.backend.Tree` class: 
              * _DIST_ADJUST_STRAT_NEW:
                Always overwrite (keep the `new_node_dist` value).
              * _DIST_ADJUST_STRAT_OLD: 
                Never overwrite (keep the `old_node._distance`).
              * _DIST_ADJUST_STRAT_ROLL2:
                Rolling average with (1/log2)^n weight for the n-th 
                oldest distance.
              * _DIST_ADJUST_STRAT_AVERAGE:
                Average over all the distances given for that node.
                This is the default.

    Returns:
        Tree: An object representing a newick tree from the given 
        input. It can be converted into a newick string using the
        `to_string` method, which has a lot of options. Check it out!
    """
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
                        or waypoint_split[0] in blacklist):
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
            if outpath and len(outpath) > 1:
                myaddinfo = {"_parse_index": { format_int(index) }}
                outtree.add_new_node(outpath, 
                                    additional_info=myaddinfo)
        index += 1
    return outtree

def clean_token(token, trim_sym):
    return token.strip(trim_sym)