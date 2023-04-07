from collections.abc import Mapping
from .nhx_util import generate_nhx

class Node:
    """
    Represents a single node in the tree.
    """
    
    _DEFAULT_OUTPUTLABEL_MAPPER:Mapping['Node',str] = lambda n: n.get_label()
    
    
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
            distance (float, optional): 
                distance from the parent node. Defaults to 1.0.
            label (str, optional): 
                identifier within parent (usually the visible label) of 
                the node. 
                Has to be unique in its parent (see also `to_string()`)! 
            duplicates_count (int, optional): 
                duplicate counter -- counts how many other nodes 
                there exist with the same label. Defaults to 0.
            additional_info (dict, optional): 
                dictionary with all additional data you want to attach
                to the node (see also `to_string()`). Defaults to dict().
            children (list, optional): 
                list of children nodes. Defaults to [].
                Please avoid using this if possible.
        """
        
        # argument validation
        if not isinstance(label, str):
            label = str(label)
        if len(label) < 1: 
            msg = \
                """
                The `label` is not allowed to be the empty string.
                If you want empty labels in the output, override the 
                `outputlabel_mapper` argument in the `to_string()` 
                function with somthing like `lambda n: ""`. 
                """
            raise ValueError(label, msg)
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
                The `additional_info` must be a dictionary to allow NHX 
                serialization for the output. If you want to attach a
                different kind of object, do so by wrapping it in a 
                dictionary under a static key. 
                """
        
        # write to class members
        self._distance          = distance
        self._label             = label
        self._children          = children
        self._dupcount          = duplicates_count
        self._additional_info   = additional_info
        self._children_by_label = dict() # maps label to index in list
        
    
    def contains_child_with_label(self, label:str) -> bool:
        """Determines wether `self` has a child with the `label`.

        Args:
            label (str): label (identifier within parent) to look for.

        Returns:
            bool: `True` iff a child with that `label` does exist here.
        """
        return label in self._children_by_label.keys
    
    def get_child_by_label(self, label:str) -> 'Node':
        """Gets the child node with the given label.

        Args:
            label (str): label (identifier within parent) to look for.

        Returns:
            Node: 
                The child node withe the given `label` iff it exists in 
                `self`, otherwise `None`.
        """
        if self.contains_child_with_label(label):
            return self._children[self._children_by_label[label]]
        else:
            return None
    
    def add_child(self, child:'Node') -> bool:
        """
        Adds the `child` node to `self`'s children. 
        
        Duplicate labels are forbidden -- duplicates are handled using 
        the `handle_duplicate()` method.
        Override `handle_duplicate()` for custom behaviour. 

        Args:
            child (Node): node to be added.
        """
        if not self.contains_child_with_label(child.get_label()):
            self._children_by_label[child.get_label()] = len(self._children)
            self._children.append(child)
            return True
        else:
            self.get_child_by_label(child.get_label()).handle_duplicate(child)
            return False
    
    
    
    def handle_duplicate(self, other:'Node'):
        """
        Handles the case when a second node with the same `label` as 
        `self`'s was to be added to the parent, which is forbidden. 
        By default this function counts duplicates and ignores the 
        `other` child, which could not be added. Override this method 
        for custom behaviour. 
        That's true sisterly affection.

        Args:
            other (Node): 
                Node that was to be added but was declined because it 
                has the same `label` as self.
        """
        self._dupcount += 1
        
        
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
    
    
    def to_string(self,
                  with_labels:bool=True,
                  with_distances:bool=True,
                  with_additional_info_nhx:bool=False,
                  outputlabel_mapper:Mapping['Node',str]=_DEFAULT_OUTPUTLABEL_MAPPER) -> str:
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
        if len(self._children) > 0:
            ret_ch = []
            for child in self._children:
                ret_ch.append(
                    child.to_string(with_labels, 
                                    with_distances, 
                                    with_additional_info_nhx, 
                                    outputlabel_mapper))
            ret.append('(' + ','.join(ret_ch) + ')')
        # append own info
        if with_labels:
            ret.append(outputlabel_mapper(self))
        if with_additional_info_nhx:
            ret.append(generate_nhx(self.get_additional_info()))
        if with_distances:
            ret.append(':' + format(self.get_distance(), 'f'))
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
    