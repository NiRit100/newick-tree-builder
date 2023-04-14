from collections.abc import Mapping
from .nhx_util import generate_nhx
from .util_funcs import format_float, format_int


class Node:
    """
    Represents a single node in the tree.
    """
    
    
    _DEFAULT_OUTPUTLABEL_MAPPER:Mapping['Node',str] = \
        lambda n: n.get_label()
    
    
    # class fields
    #_label
    #_distance          = 1.0
    #_children          = []
    #_dupcount          = 0
    #_additional_info   = None
    #_children_by_label = dict()
    
    
    def __init__(self, 
                 label:str, 
                 distance:float         = 1.0, 
                 duplicates_count:int   = 0, 
                 additional_info:dict   = dict(),
                 children:list          = []):
        """Creates a new node with the given information.

        Args:
            label (str): 
                identifier within parent (usually the visible label) 
                of the node. 
                Has to be unique in its parent (see also 
                `to_string()`)! 
            distance (float, optional): 
                distance from the parent node. Defaults to 1.0.
            duplicates_count (int, optional): 
                duplicate counter -- counts how many other nodes 
                there exist with the same label. Defaults to 0.
            additional_info (dict, optional): 
                dictionary with all additional data you want to attach
                to the node (see also `to_string()`). Defaults to 
                dict().
            children (list, optional): 
                list of children nodes. Defaults to [].
                Please avoid using this if possible.
        """
        
        # argument validation
        if label == None:
            label = ""
        elif not isinstance(label, str):
                label = str(label)
        if not isinstance(distance, float):
            distance = float(distance)
        if distance < 0:
            msg = \
                """
                Distance from parent node must be positive.
                """ 
            raise ValueError(distance, msg)
        if not isinstance(additional_info, dict):
            msg = \
                """
                The `additional_info` must be a dictionary to allow 
                NHX serialization for the output. If you want to attach 
                a different kind of object, do so by wrapping it in a 
                dictionary under a static key. 
                """
            raise ValueError(additional_info, msg) 
        
        # write to class members
        self._distance          = distance
        self._label             = label
        self._dupcount          = duplicates_count
        self._additional_info   = additional_info
        # handle children
        self._children          = []
        self._children_by_label = dict() # maps label to index of _children
        for c in children:
            self.add_child(c)
        
    
    def contains_child_with_label(self, label:str) -> bool:
        """Determines wether `self` has a child with the `label`.

        Args:
            label (str): label (identifier within parent) to look for.

        Returns:
            bool: 
                `True` iff a child with that `label` does exist here.
        """
        return label in self._children_by_label.keys()
    
    def count_children(self) -> int:
        """Counts `self`'s children.

        Returns:
            int: The number of children `self` has.
        """
        return len(self._children_by_label)
    
    def is_leaf(self) -> bool:
        """Determines whether this node is a leaf or not.

        Returns:
            bool: Return True iff `self` has no children.
        """ 
        return self.count_children() == 0
    
    def is_root(self) -> bool:
        """
        Determines whether this node is a root node.
        This kind of node is not a root node by definition, so that 
        this function always returns a constant `False`.

        Returns:
            bool: Constant False.
        """
        return False
    
    def get_child_by_label(self, label:str) -> 'Node':
        """Gets the child node with the given label.

        Args:
            label (str): label (identifier within parent) to look for.

        Returns:
            Node: 
                The child node withe the given `label` iff it exists 
                in `self`, otherwise `None`.
        """
        if self.contains_child_with_label(label):
            return self._children[self._children_by_label[label]]
        else:
            return None
    
    def add_child(self, 
                  child:'Node', 
                  dist_adjust_strategy=None,
                  count_duplicate:bool=True) -> tuple[bool,'Node']:
        """
        Adds the `child` node to `self`'s children. 
        
        Duplicate labels are forbidden -- duplicates are handled 
        using the `handle_duplicate()` method.
        Override `handle_duplicate()` for custom behaviour. 

        Args:
            child (Node): 
                node to be added.
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
        if not self.contains_child_with_label(child.get_label()):
            self._children_by_label[child.get_label()] = len(self._children)
            self._children.append(child)
            return (True, child)
        else:
            ochild = self.get_child_by_label(child.get_label())
            if dist_adjust_strategy:
                adjusted_dist = dist_adjust_strategy(ochild, 
                                                    child.get_distance())
                ochild.set_distance(adjusted_dist)
            ochild.handle_duplicate(child, count=count_duplicate)
            return (False, ochild)
    
    
    def handle_duplicate(self, other:'Node', count=True):
        """
        Handles the case when a second node with the same `label` as 
        `self`'s was to be added to the parent, which is forbidden. 
        By default this function counts duplicates, copies the 
        additional information and otherwise ignores the  `other` 
        child, which could not be added. That's true sisterly affection. 
        During copying of additional info, whenever a key is already
        present within the dictionary, the new value will be ignored,
        unless both are lists or sets, then they will be merged.
        Override this method for custom behaviour. 
        NOTE: Taking away this functionality may break some 
        `Tree._DIST_ADJUST_STRAT_...`s! It is therefore recommended 
        to still call this function, even when overridden by a 
        subclass.

        Args:
            other (Node): 
                Node that was to be added but was declined because it 
                has the same `label` as self.
            count (bool, optional):
                Whether or not to count this duplication.
        """
        # count duplicates
        if count:
            self._dupcount += 1
        # copy additional information
        s_ao = self.get_additional_info()
        o_ao = other.get_additional_info()
        for k in o_ao.keys():
            v = o_ao[k]
            if k in s_ao.keys():
                if s_ao[k] != v:
                    if isinstance(v, set) and isinstance(s_ao[k], set):
                        s_ao[k] = s_ao[k].union(v)
                    elif isinstance(v, list) and isinstance(s_ao[k], list):
                        s_ao[k].extend(v)
                    else:
                        # This key is already present with a different value. 
                        # TODO: What to do here?
                        pass 
            else:
                # add the key and value.
                s_ao[k] = v
        
        
    def get_label(self) -> str:
        """Retrieves the label (identifier) string of `self`.

        Returns:
            str: label (identifier within its parent) of `self`
        """
        return self._label
    
    def get_distance(self) -> float:
        """Retrieves the distance of `self` from its parent.

        Returns:
            float: distance of `self` from its parent
        """
        return self._distance
    
    def set_distance(self, distance):
        """
        Sets the distanec of `self` to the given `val`.
        """
        if not isinstance(distance, float):
            distance = float(distance)
        if distance < 0:
            msg = \
                """
                Distance from parent node must be positive.
                """ 
            raise ValueError(distance, msg)
        self._distance = distance

    def get_duplication_count(self) -> int:
        """Retrieves the duplicate counter's value.

        Returns:
            int: 
                number of duplicates counted by default 
                `handle_duplicate()`
        """
        return self._dupcount
        
    def get_additional_info(self) -> dict:
        """
        Retrieves the additional info dictionary attached to 
        `self`. 

        Returns:
            dict: additional info dictionary attached to `self`
        """
        return self._additional_info
    
    
    def gen_children_strings(self,
                             with_labels:bool, 
                             with_distances:bool, 
                             with_additional_info_nhx:bool, 
                             outputlabel_mapper:Mapping['Node',str]) -> list:
        """generate the strings for all the children.

        Args:
            with_labels (bool): see `to_string()`.
            with_distances (bool): see `to_string()`.
            with_additional_info_nhx (bool): see `to_string()`.
            outputlabel_mapper (bool): see `to_string()`.

        Returns:
            list: of all the children's string representations.
        """
        ret_ch = []
        for child in self._children:
            ret_ch.append(
                child.to_string(with_labels, 
                                with_distances, 
                                with_additional_info_nhx, 
                                outputlabel_mapper))
        return ret_ch
    
    def to_string(self,
                  with_labels:bool=True,
                  with_distances:bool=True,
                  with_additional_info_nhx:bool=False,
                  outputlabel_mapper:Mapping['Node',str]=None) -> str:
        """
        Generates a string representation of `self` and its 
        children in newick format.

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
            outputlabel_mapper (Mapping[Node,str], optional): 
                A mapping function (`Node` to `str`) that maps a node
                to the label string that is to be written for it in 
                the output. 
                Defaults to `lambda n: n.get_label()`, so that a 
                `Node` is mapped to its `Node._label`, which is the 
                identification `label` (unique in its parent). 

        Returns:
            str: A string representation of `self` and its subtree.
        """
        ret = []
        # append children info
        ret_ch = self.gen_children_strings(with_labels, 
                                           with_distances, 
                                           with_additional_info_nhx, 
                                           outputlabel_mapper)
        if len(ret_ch) > 0:
            ret.append('(' + ','.join(ret_ch) + ')')
        # append own info
        if with_labels:
            if outputlabel_mapper:
                ret.append(outputlabel_mapper(self))
            else:
                ret.append(self._DEFAULT_OUTPUTLABEL_MAPPER())
        if with_additional_info_nhx:
            ret.append(generate_nhx(self.get_additional_info()))
        if with_distances:
            ret.append(':' + format_float(self.get_distance()))
        # convert to string and return
        return ''.join(ret)
    
    
    def __repr__(self) -> str:
        """`to_string()` with default settings.

        Returns:
            str: 
                A string representation of `self` and its subtree with
                default settings.
        """
        return self.to_string()
    
    
class HybridNode(Node):
    """
    Represents a single hybrid node in the tree 
    (see Extended Newick format).
    """
    
    
    # class fields:
    #_hybrid_ignore_pool
    #_hybrid_id
    
    
    _DEFAULT_OUTPUTLABEL_MAPPER:Mapping['Node',str] = \
        lambda n: (n.get_label() + n.gen_hybrid_id_string())
        
    
    def __init__(self, 
                 label:str, 
                 hybrid_id:int,
                 hybrid_ignore_pool:set,
                 distance:float         = 1.0, 
                 duplicates_count:int   = 0, 
                 additional_info:dict   = dict(),
                 children:list          = []):
        """Creates a new node with the given information.

        Args:
            label (str): 
                identifier within parent (usually the visible label) 
                of the node. 
                Has to be unique in its parent (see also 
                `to_string()`)! 
            distance (float, optional): 
                distance from the parent node. Defaults to 1.0.
            hybrid_id (int):
                the identifier number of this hybrid.
            hybrid_ignore_pool (set):
                This mechanism is supposed to prevent duplicate 
                declarations on hybrids. 
                If the hybrid node finds a representation of itself in
                this pool, it will not append its children and 
                additional info to its label during `to_string`.
                This is supposed to be a reference to a set inside the 
                managing `Tree`, which is being flushed by said `Tree` 
                every time a new `to_string` process is being started. 
                When this hybrid node's `to_string` is called, it adds 
                itself to the pool automatically. If you want to 
                prevent that, pass `None` for this arg or override the 
                `handle_to_string()` function.   
            duplicates_count (int, optional): 
                duplicate counter -- counts how many other nodes 
                there exist with the same label. Defaults to 0.
            additional_info (dict, optional): 
                dictionary with all additional data you want to attach
                to the node (see also `to_string()`). Defaults to 
                dict().
            children (list, optional): 
                list of children nodes. Defaults to [].
                Please avoid using this if possible.
        """
        
        # instantiate via super constructor
        super(HybridNode, self).__init__( \
                         label=label, 
                         distance=distance, 
                         duplicates_count=duplicates_count,
                         additional_info=additional_info,
                         children=children)
        
        # argument validation
        if not isinstance(hybrid_id, int):
            msg = \
                """
                Please pass a valid integer for the `hybrid_id`.
                If you don't wish to instantiate a hybrid, use
                the `Node` 
                """
        if not (isinstance(hybrid_ignore_pool, set) 
                or hybrid_ignore_pool == None):
            msg = \
                """
                The `hybrid_ignore_pool` has to be a `set` or `None`.
                """
            raise ValueError(hybrid_ignore_pool, msg)
        
        # write to class fields
        self._hybrid_id = hybrid_id
        self._hybrid_ignore_pool = hybrid_ignore_pool
    
    def gen_hybrid_id_string(self) -> str:
        """
        Generates the portion of the id that contains `self`'s 
        `hybrid_id`.
        
        Returns:
            str: the portion of the id that contains `self`'s 
            `hybrid_id`
        """
        return "#" + format_int(self._hybrid_id)
    
    def gen_children_strings(self,
                             with_labels, 
                             with_distances, 
                             with_additional_info_nhx, 
                             outputlabel_mapper) -> list:
        """
        Generate the strings for all the children.
        Modified so that it returns an empty list if this hybrid is in 
        the `_hybrid_ignore_pool`.

        Args:
            with_labels (bool): see `to_string()`.
            with_distances (bool): see `to_string()`.
            with_additional_info_nhx (bool): see `to_string()`.
            outputlabel_mapper (bool): see `to_string()`.

        Returns:
            list: of all the children's string representations.
        """
        hid_str = self.gen_hybrid_id_string()
        if hid_str in self._hybrid_ignore_pool:
            return [] # on empty list, children will not be included 
                      # in the output string
        else:
            return super(HybridNode, self) \
                .gen_children_strings(with_labels,
                                      with_distances,
                                      with_additional_info_nhx,
                                      outputlabel_mapper)
                
    
    def to_string(self,
                  with_labels:bool=True,
                  with_distances:bool=True,
                  with_additional_info_nhx:bool=False,
                  outputlabel_mapper:Mapping['Node',str]=None) -> str:
        # only print distance when first appearance
        hid_str = self.gen_hybrid_id_string()
        m_with_distances = with_distances and \
                hid_str in self._hybrid_ignore_pool
        return super(HybridNode, self) \
                    .to_string(with_labels,
                               m_with_distances,
                               with_additional_info_nhx,
                               outputlabel_mapper)


class RootNode(Node):
    """
    Represents the root node of the tree.
    """
    
    
    def __init__(self, 
                 label:str, 
                 additional_info:dict   = dict(),
                 children:list          = []):
        """Creates a new node with the given information.

        Args:
            label (str): 
                identifier within parent (usually the visible label) 
                of the node. 
                Has to be unique in its parent (see also 
                `to_string()`)!
            additional_info (dict, optional): 
                dictionary with all additional data you want to attach
                to the node (see also `to_string()`). Defaults to 
                dict().
            children (list, optional): 
                list of children nodes. Defaults to [].
                Please avoid using this if possible.
        """
        super(RootNode, self).__init__(label=label, 
                                       distance=0,
                                       duplicates_count=0,
                                       additional_info=additional_info,
                                       children=children)
        
        
    def from_node(node:Node) -> 'RootNode':
        """
        Create a `RootNode` from the given `node`.
        Note that not all information will be copied from the `node`.
        The following data is guaranteed to be retained:
         * label id string
         * additional info dictionary
         * children nodes
        Other data in `node` may be lost.

        Args:
            node (Node): original node

        Returns:
            RootNode: a clone of `node` as a `RootNode` 
        """
        ret = RootNode(label=node._label,
                       additional_info=node._additional_info)
        ret._children = node._children
        ret._children_by_label = node._children_by_label
        return ret


    def is_root(self) -> bool:
        """
        Determines whether this node is a root node.
        Nodes of type `RootNode`, like this one, are roots by 
        definition.

        Returns:
            bool: Constant True.
        """
        return True
    

    def to_string(self,
                  with_labels:bool=True,
                  with_distances:bool=True,
                  with_additional_info_nhx:bool=False,
                  outputlabel_mapper:Mapping['Node',str]=None) -> str:
        """
        Generates a string representation of `self` and its 
        children in newick format.

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
            outputlabel_mapper (_type_, optional): 
                A mapping function (`Node` to `str`) that maps a node
                to the label string that is to be written for it in 
                the output. 
                Defaults to `lambda n: n.get_label()`, so that a 
                `Node` is mapped to its `Node._label`, which is the 
                identification `label` (unique in its parent). 

        Returns:
            str: A string representation of `self` and its subtree.
        """
        
        ret = []
        # append children info
        ret_ch = self.gen_children_strings(with_labels, 
                                           with_distances, 
                                           with_additional_info_nhx, 
                                           outputlabel_mapper)
        if len(ret_ch) > 0:
            ret.append('(' + ','.join(ret_ch) + ')')
        # append own info
        if with_labels:
            if outputlabel_mapper:
                ret.append(outputlabel_mapper(self))
            else:
                ret.append(self._DEFAULT_OUTPUTLABEL_MAPPER())
        if with_additional_info_nhx:
            ret.append(generate_nhx(self.get_additional_info()))
        # convert to string and return
        return ''.join(ret)
    