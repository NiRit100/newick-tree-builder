from .util_funcs import format_float


class Path:
    
    # class fields
    #_waypoints:list = list()
    #_distances:list = list()
    
    
    def __init__(self, 
                 root_label=None,
                 points:list[tuple[str,float]]=[]):
        self._waypoints = list()
        self._distances = list()
        if root_label:
            self._waypoints.append(root_label)
            self._distances.append(0.0)
        else:
            self._waypoints.append("")
            self._distances.append(0.0)
        for w, d in points:
            self.add(w, d)
    
    
    def __len__(self):
        return len(self._waypoints)
    
    def __getitem__(self, key):
        return [(self._waypoints[i], self._distances[i]) for i in range(len(self))][key]
    
    def __contains__(self, item):
        if      isinstance(item, str):
            return item in self._waypoints
        elif    isinstance(item, int) \
             or isinstance(item, float):
            return item in self._waypoints
        elif    isinstance(item, tuple[str,int]) \
             or isinstance(item, tuple[str,float]):
            return item in zip(self._waypoints, self._distances)
        else:
            raise TypeError(item, "unexpected item type")
    
    def __iter__(self):
        yield from [(self._waypoints[i], self._distances[i]) for i in range(len(self))]
        
        
    def __repr__(self):
        ret_strs = []
        for w,d in self:
            ret_strs.append(w + ":" + format_float(d))
        return type(self).__name__ + "(" + " -> ".join(ret_strs) + ")"
    
    
    def add(self,
            waypoint:str,
            distance:float=float('-inf')):
        """Adds a waypoint to the path.

        Args:
            waypoint (str): 
                label of the waypoint.
            distance (float, optional): 
                distance of this waypoint from the prior.
                Pass `float('-inf')`, which will be replaced by the
                `Tree`'s `default_distance`. 
                Defaults to `float('-inf')`.
        """
        self._waypoints.append(str(waypoint))
        self._distances.append(float(distance))
    
    