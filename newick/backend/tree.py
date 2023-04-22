from collections.abc import Mapping
from typing import Callable, Iterable
from os import linesep
from .node import Node, HybridNode, RootNode
from .path import Path

class Tree:
    """
    Wraps around the root node of the tree in order to 
    represent the entire tree. Also provides some additional
    functionality.
    """
    
    
    # class fields
    #_root
    #_hybrids  # dict[(str, int), HybridNode] # TODO:
    #_hybrid_ignore_set
    #_default_dist
    #_dist_adjust_strat
  
  
    def _DIST_ADJUST_STRAT_NEW_fn(old_node:Node, new_dist:float) -> float:
        return new_dist
    _DIST_ADJUST_STRAT_NEW=_DIST_ADJUST_STRAT_NEW_fn
    
    def _DIST_ADJUST_STRAT_OLD_fn(old_node:Node, new_dist:float) -> float:
        return new_dist
    _DIST_ADJUST_STRAT_OLD = _DIST_ADJUST_STRAT_OLD_fn
    
    def _DIST_ADJUST_STRAT_ROLL2_fn(old_node:Node, new_dist:float) -> float:
        return (old_node.get_distance() + new_dist) / 2
        
    def _DIST_ADJUST_STRAT_AVERAGE_fn(old_node:Node, new_dist:float) -> float:
        weighted_old_dist = (old_node.get_distance() * (old_node.get_duplication_count()+1))
        return (weighted_old_dist + new_dist) / (old_node.get_duplication_count()+2)
    _DIST_ADJUST_STRAT_AVERAGE=_DIST_ADJUST_STRAT_AVERAGE_fn
    
    
    def __init__(self,
                 root_node:RootNode,
                 default_dist:float=1.0,
                 dist_adjust_strategy:Callable[[Node,float],float]=_DIST_ADJUST_STRAT_AVERAGE):
        """Creates a new node with the given information.

        Args:
            root_node (RootNode): 
                Root node of the tree. 
                Use the `RootNode()` constructor to create one.
            default_dist (float, optional):
                The default distance of a node from its parent in this tree,
                which is used when a path does not contain distance information.
                Defaults to 1.
            dist_adjust_strategy (Callable[[Node,float],float], optional):
                A function that takes the pre-existing `Node` in the tree and 
                the distance (`float`) of the supposed new node that is to be inserted, 
                and calculates the new distance that will be written into said
                pre-existing `Node` in the tree. 
                This is supposed to allow the user to control which changes are made on 
                the distance of a node when contradicting information are encountered
                during a new node's insertion. 
                You can define your own function or use one of the 
                `Tree._DIST_ADJUST_STRAT_...`s.
        """
        
        # validation
        if not isinstance(root_node, RootNode):
            if isinstance(root_node, Node):
                root_node = RootNode.from_node(root_node)
            else:
                msg = \
                """
                The `root_node` has to be a RootNode.
                Use the `RootNode()` constructor to create it.
                """
                raise ValueError(root_node, msg)
        #TODO: validate other args
        
        # write class fields 
        self._root = root_node
        self._default_dist = default_dist
        self._hybrids = dict()
        self._hybrid_ignore_set = set()
        self.set_dist_adjust_strat(dist_adjust_strategy)

    
    def node_dist_or_def(self, 
                         dist:float):
        if dist == float("-inf"):
            return self._default_dist
        else:
            return dist
        
    def dist_adjust_strat_or_def(self, 
                                 dist:float):
        """
        Returns the distance adjustment function only if the given 
        distance is not default (`float("-inf")`).
        This is to prevent distance adjustments after first definition
        if no explicit distances are given. 
        """
        if dist == float("-inf"):
            return None
        else:
            return self._dist_adjust_strat
    
    
    RootNode = RootNode
    
    
    def reg_hybrid_id(self,
                      label:str,
                      hybrid_id:int,
                      distance:float,
                      additional_info:dict) -> HybridNode:
        """For internal use only.

        Returns:
            HybridNode: 
                The HybridNode instance with the given label and id
                that is already present in the tree, or a newly created
                one if it is not registered yet.
        """
        if (label, hybrid_id) in self._hybrids.keys:
            return self._hybrids[(label, hybrid_id)]
        else:
            wchild = HybridNode(label,
                                hybrid_id,
                                distance, 
                                additional_info)
            self._hybrids[(label, hybrid_id)] = wchild
            return wchild
     
    
    def add_new_node(self, path:Path, additional_info:dict=dict()) -> bool:
        """
        Adds a new node to the tree if it does not exist yet in the 
        location determined by the `path`.
        Also attaches the given additional info.
        If the node is already present, by default
         * duplication is counted
         * distance is adjusted by the tree's strategy, if a distance
           is given
         * additional info is being copied over (lists and sets are merged)

        Args:
            path (Path): 
                Path where to place the node.
            additional_info (dict, optional): 
                Additional info dict to attach

        Raises:
            ValueError: When the given path is too short or the root does 
            not match.

        Returns:
            bool: 
                True iff the node has been created, False if it had to be 
                merged.
        """
        cparent = self._root
        cret = False
        # check root
        if (len(path) <= 1):
            msg = \
                "Cannot insert a node with a path shorter than 2 waypoints."
            raise ValueError(path, msg)
        if (self._root.get_label(), self._root.get_distance()) != path[0]:
            msg = \
                "The start waypoint of the path differs from the tree's root."
            raise ValueError(path, msg)
        # insert rest
        cpath = path[1:]
        while len(cpath) > 0:
            is_end_of_path = (len(cpath) == 1)
            wlabel, wdist = cpath[0]
            w_dist_adjust_strat = self.dist_adjust_strat_or_def(wdist)
            wdist = self.node_dist_or_def(wdist)    
            waddinfo = additional_info if is_end_of_path else dict()
            wchild = Node(wlabel, 
                          distance=wdist, 
                          additional_info=waddinfo)
            cret, achild = cparent.add_child(wchild, 
                                     w_dist_adjust_strat,
                                     count_duplicate=is_end_of_path)
            cpath = cpath[1:]
            cparent = achild
        return cret
    
    def add_new_hybrid_node(self, paths:Iterable[str], hybrid_id=-1, additional_info:dict=dict()) -> bool:
        """
        Adds a new hybrid node to the tree if it does not exist yet in the 
        locations determined by the `path`.
        Also attaches the given additional info.
        If the node is already present, by default
         * duplication is counted
         * distance is adjusted by the tree's strategy, if a distance
           is given
         * additional info is being copied over (lists and sets are merged)

        Args:
            path (Iterable[Path]): 
                Collection of paths where to place the node.
            additional_info (dict, optional): 
                Additional info dict to attach

        Raises:
            ValueError: When the given path is too short or the root does 
            not match.

        Returns:
            bool: 
                True iff the node was inserted in at least one location, 
                otherwise False.
        """
        ret = False
        is_first_path = True
        for path in paths:
            cparent = self._root
            cret = False
            # check root
            if (len(path) <= 1):
                msg = \
                    "Cannot insert a node with a path shorter than 2 waypoints."
                raise ValueError(path, msg)
            if (self._root.get_label(), self._root.get_distance()) != path[0]:
                msg = \
                    "The start waypoint of the path differs from the tree's root."
                raise ValueError(path, msg)
            # insert rest
            cpath = path[1:]
            while len(cpath) > 0:
                is_end_of_path = (len(cpath) == 1)
                wlabel, wdist = cpath[0]
                w_dist_adjust_strat = self.dist_adjust_strat_or_def(wdist)
                wdist = self.node_dist_or_def(wdist)    
                if is_end_of_path and is_first_path:
                    waddinfo = additional_info
                else:
                    waddinfo = dict()
                wchild = self.reg_hybrid_id(wlabel, 
                                            hybrid_id,
                                            distance=wdist, 
                                            additional_info=waddinfo)
                cret, achild = cparent.add_child(wchild, 
                                         w_dist_adjust_strat,
                                         count_duplicate=is_end_of_path)
                cpath = cpath[1:]
                cparent = achild
            ret |= cret
            is_first_path = False
        return ret
    
    
    def set_dist_adjust_strat(self, dist_adjust_strat:Callable[[Node,float],float]):
        """Sets the distance adjustment function of this tree. 

        Args:
            dist_adjust_strat (Callable[[Node,float],float])
        """
        if dist_adjust_strat:
            self._dist_adjust_strat = dist_adjust_strat
        else:
            pass  # maybe throw error?
    
    
    def to_string(self,
                  with_labels:bool=True,
                  with_distances:bool=True,
                  with_additional_info_nhx:bool=False,
                  append_newline:bool=False,
                  outputlabel_mapper:Mapping[Node,str]=None) -> str:
        """
        Generates a string representation of this tree in newick 
        format.

        Args:
            with_labels (bool, optional): 
                Whether or not to output labels (see also 
                `outputlabel_mapper`). Defaults to True.
            with_distances (bool, optional): 
                Whether or not to output distances to parent node. 
                Defaults to True.
            with_additional_info_nhx (bool, optional): 
                Whether to output the additional info attached 
                to this node (in NHX format) or to leave it out. 
                Defaults to False.
                To ensure that the output can be used by third party
                implementations, make sure the string representation
                of each element (key or value) in the dictionary is 
                free from special symbols and control characters
                such as newline, '=' and ':'. 
                Best practice: Only use alphanumerics and pre-convert
                values (and keys) to strings. All other characters 
                will be escaped, hoping for compliance with your 
                other tool's definitions of the syntax of NHX.
                Defaults to False.
            default_distance (int, optional):
                The default distance between a node and its parent
                Defaults to 1.
            append_newline (bool, optional): 
                Whether or not to append a newline character after
                the tree's string representation. 
                Defaults to False.
            outputlabel_mapper (Mapping[Node,str], optional): 
                A mapping function (`Node` to `str`) that maps a node
                to the label string that is to be written for it in 
                the output. 
                Defaults to `lambda n: n.get_label()` for regular 
                nodes (might differ for other kinds), so that a 
                `Node` is mapped to its `Node._label`, which is the 
                identification `label` (unique in its parent). 
                Please note that your custom implementation would 
                have to take the differences between the different 
                kinds of nodes into account.

        Returns:
            str: A string representation of this tree.
        """
        ret = []
        ret.append( \
            self._root.to_string(with_labels=with_labels,
                                 with_distances=with_distances,
                                 with_additional_info_nhx=with_additional_info_nhx,
                                 outputlabel_mapper=outputlabel_mapper))
        ret.append(';')
        if append_newline:
            ret.append(linesep)
        return ''.join(ret)
    