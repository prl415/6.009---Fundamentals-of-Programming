"""6.009 Lab 8: Graphs, Paths, Matrices."""

from abc import ABC, abstractmethod
# NO ADDITIONAL IMPORTS ALLOWED!


class Graph(ABC):
    """Interface for a mutable directed, weighted graph."""

    @abstractmethod
    def add_node(self, node):
        """Add a node to the graph.

        Arguments:
            node (str): the node to add

        Raises:
            ValueError: if the node already exists.

        """

    @abstractmethod
    def add_edge(self, start, end, weight):
        """Add a directed edge to the graph.

        If the edge already exists, then set its weight to `weight`.

        Arguments:
            start (str): the node where the edge starts
            end (str): the node where the edge ends
            weight (int or float): the weight of the edge, assumed to be a nonnegative number

        Raises:
            LookupError: if either of these nodes doesn't exist

        """

    @abstractmethod
    def nodes(self):
        """Return the nodes in the graph.

        Returns:
            set: all of the nodes in the graph

        """

    @abstractmethod
    def neighbors(self, node):
        """Return the neighbors of a node.

        Arguments:
            node (str): a node name

        Returns:
            set: all tuples (`neighbor`, `weight`) for which `node` has an
                 edge to `neighbor` with weight `weight`

        Raises:
            LookupError: if `node` is not in the graph

        """

#    @abstractmethod
    def get_path_length(self, start, end):
        """Return the length of the shortest path from `start` to `end`.

        Arguments:
            start (str): a node name
            end (str): a node name

        Returns:
            float or int: the length (sum of edge weights) of the path or
                          `None` if there is no such path.

        Raises:
            LookupError: if either `start` or `end` is not in the graph

        """

#    @abstractmethod
    def get_path(self, start, end):
        """Return the shortest path from `start` to `end`.

        Arguments:
            start (str): a node name
            end (str): a node name

        Returns:
            list: nodes, starting with `start` and, ending with `end`, which
                  comprise the shortest path from `start` to `end` or `None`
                  if there is no such path

        Raises:
            LookupError: if either `start` or `end` is not in the graph

        """

#    @abstractmethod
    def get_all_path_lengths(self):
        """Return lengths of shortest paths between all pairs of nodes.

        Returns:
            dict: map from tuples `(u, v)` to the length of the shortest path
                  from `u` to `v`

        """

#    @abstractmethod
    def get_all_paths(self):
        """Return shortest paths between all pairs of nodes.

        Returns:
            dict: map from tuples `(u, v)` to a list of nodes (starting with
                  `u` and ending with `v`) which is a shortest path from `u`
                  to `v`

        """


class AdjacencyDictGraph(Graph):
    """A graph represented by an adjacency dictionary."""

    def __init__(self):
        """Create an empty graph."""
        self.graph = dict()
        self.dist = dict()
        self.pred = dict()
    
    def add_node(self, node):
        
        if node in self.graph: #Node already exists
            raise ValueError
            
        else:
            self.graph[node] = set()
            self.dist[(node, node)] = 0 #0-length path from node to itself
        
    def add_edge(self, start, end, weight):
        
        if start not in self.graph or end not in self.graph:
            raise LookupError
        
        else: #Start node exists
            pair = ()
            for neighbor, wght in self.neighbors(start):
                if neighbor == end:
                    pair = (neighbor, wght)
                    continue
            
            if pair != ():
                self.graph[start].remove(pair)
                
            self.graph[start].add((end, weight))
    
    def nodes(self):
        return set(self.graph)
    
    def neighbors(self, node):
        return self.graph[node]

    def relax(self, u, x, v, weight):
        '''
        Helper Method
        Check if dist(u, x) + weight = dist(x, v) < dist(u, v)
        If that is the case, update dist and pred dict
        Otherwise don't do nothing
        '''
        if self.dist[(u, x)] + weight < self.dist[(u, v)]:
            self.dist[(u, v)] = self.dist[(u, x)] + weight
            self.pred[(u, v)] = x
    
    def create_edges(self):
        '''
        Helper method for shortest_dist
        Update dist dictionary to reflect the assumption that distance between
        distinct nodes is infinite before calculating shortest paths
        '''
        for start in self.nodes():
            for end in self.nodes():
                if start != end and (start, end) not in self.dist:
                    self.dist[(start, end)] = float('inf')
                    
    def create_path(self, start, end):
        '''
        Helper method for get_path
        By using self.pred dict, creates the path between start and end
        if it exists otherwise returns None
        '''
        try:
            path = [end]
            prev = self.pred[(start, end)]
            while prev != start:
                path.append(prev)
                prev = self.pred[(start, prev)]
            path.append(start)
            path.reverse()
            return path
        
        except:
            return None
          
    def shortest_dist(self):
        '''
        Calculates the shortest distance between every (u, v) distinc pair
        of nodes
        '''
        self.create_edges()
        for n in range(len(self.nodes()) - 1):
            for u in self.nodes():
                for x in self.nodes():
                    for v, weight in self.neighbors(x):
                        self.relax(u, x, v, weight)
    
    def get_path_length(self, start, end):
        
        if start not in self.nodes() or end not in self.nodes():
            raise LookupError
            
        self.shortest_dist()
        
        try:
            if self.dist[(start, end)] == float('inf'):
                return None
            
            return self.dist[(start, end)]
        
        except:
            return None
    
    def get_path(self, start, end):
        if start not in self.nodes() or end not in self.nodes():
            raise LookupError
            
        self.shortest_dist()
        
        return self.create_path(start, end)
        
    def get_all_path_lengths(self):
        dist_map = {}
        self.shortest_dist()
        for pair, dist in self.dist.items():
            if dist != float('inf'):
                dist_map[pair] = dist
        return dist_map
    
    def get_all_paths(self):
        all_paths = dict()
        
#        self.shortest_dist()
        
        #Paths between distinct nodes
        for start, end in self.get_all_path_lengths():
            if start == end: #Path from node to itself
                all_paths[(start, end)] = [start]
            else: #Path between two distinct nodes
                all_paths[(start, end)] = self.create_path(start, end)
         
        return all_paths
    
class AdjacencyMatrixGraph(Graph):
    """A graph represented by an adjacency matrix."""

    def __init__(self):
        """Create an empty graph."""
        self.graph = []
        self.dist = []
        self.pred = []
        self.node_to_id = dict()
        self.id_to_node = dict()
        self.index = 0
    
    def add_node(self, node):
        
        if node in self.node_to_id: #Node already exists
            raise ValueError
        
        else:
            self.graph.append([float('inf') for i in range(len(self.node_to_id) + 1)]) #Each new row represents new node
            self.graph[self.index][self.index] = 0
            self.node_to_id[node] = self.index
            self.id_to_node[self.index] = node
            #Update each row
            for i in range(len(self.node_to_id)-1):
                self.graph[i].append(float('inf'))
            self.index += 1
    
    def add_edge(self, start, end, weight):
        if start not in self.node_to_id or end not in self.node_to_id:
            raise LookupError
        
        else:
            start_id = self.node_to_id[start]
            end_id = self.node_to_id[end]
            n = len(self.node_to_id) #Number of nodes
            if self.graph[start_id] == []:
#                self.graph[start_id].extend([float('inf') for i in range(end_id)] + [weight] + [float('inf') for i in range(end_id + 1, n)])
                self.graph[start_id][start_id] = 0
            else:
                self.graph[start_id][end_id] = weight
    
    def nodes(self):
        return set(self.node_to_id)
    
    def neighbors(self, node):
        
        n = len(self.node_to_id) #Number of nodes
        node_id = self.node_to_id[node] #ID of the given node
        
        #List of (neighbor_id, weight) pairs
        neighbor_ids = [(i, self.graph[node_id][i]) for i in range(n) if self.graph[node_id][i] != float('inf')]
        
        neighbors = [(self.id_to_node[neighbor_id], weight) for neighbor_id, weight in neighbor_ids if node_id != neighbor_id]
#        neighbors = []
        #By using neighbor_ids. list, create set of (neighbor, weight) pairs
#        for neighbor_id, weight in neighbor_ids:
#            for vertex in self.node_to_id:
#                if neighbor_id == self.node_to_id[vertex]:
#                    neighbors.append((vertex, weight))
                    
        return set(neighbors)
    
    def double_max_edges(self, M):
        '''
        Helper method for the shortest distance algorithm
        '''
        #Create a copy of matrix M
        new_M = []
        for row in M:
            new_M.append(row)
        for i in self.node_to_id.values():
            for j in self.node_to_id.values():
                for k in self.node_to_id.values():
                    if new_M[i][j] > new_M[i][k] + new_M[k][j]:
                        new_M[i][j] = new_M[i][k] + new_M[k][j]
                        self.pred[i][j] = k
        return new_M
    
    def shortest_dist(self):
        # Update the pred and dist matrix
        n = len(self.node_to_id) #Number of nodes
        self.pred = [[None for i in range(n)] for i in range(n)] # nxn matrix
        dist = self.graph #It is the same as adjacency matrix at first
        
        # Repeat the algorithm for n-1 times (Since maximum number of edges 
        # between two distinct nodes can be at most n-1)
        for i in range(n-1):
            dist = self.double_max_edges(dist)
        
        self.dist = dist
        
    def create_path(self, i, j):
        #Base Case
        if self.pred[i][j] == None: 
            #Nodes are connected directly
            if self.dist[i][j] != float('inf'): 
                return [i, j]
            
            #There is no path between these nodes
            return None 
        
        else:
            try:
                k = self.pred[i][j]
                path = self.create_path(i, k)[:-1] + self.create_path(k, j)
                return path
            except:
                return None
                
    def get_path_length(self, start, end):
        """Return the length of the shortest path from `start` to `end`.

        Arguments:
            start (str): a node name
            end (str): a node name

        Returns:
            float or int: the length (sum of edge weights) of the path or
                          `None` if there is no such path.

        Raises:
            LookupError: if either `start` or `end` is not in the graph

        """
        if start not in self.node_to_id or end not in self.node_to_id:
            raise LookupError
        
        if self.dist == []:
            self.shortest_dist()
        
        start_id = self.node_to_id[start]
        end_id = self.node_to_id[end]
        
        if self.dist[start_id][end_id] == float('inf'):
            return None
            
        return self.dist[start_id][end_id]

    def get_path(self, start, end):
        """Return the shortest path from `start` to `end`.

        Arguments:
            start (str): a node name
            end (str): a node name

        Returns:
            list: nodes, starting with `start` and, ending with `end`, which
                  comprise the shortest path from `start` to `end` or `None`
                  if there is no such path

        Raises:
            LookupError: if either `start` or `end` is not in the graph

        """
        if start not in self.node_to_id or end not in self.node_to_id:
            raise LookupError
            
        if self.dist == []:
            self.shortest_dist()
        
        start_id = self.node_to_id[start]
        end_id = self.node_to_id[end]
        
        id_path = self.create_path(start_id, end_id)
        
        if id_path == None:
            return None
        
        path = []
        for node_id in id_path:
            path.append(self.id_to_node[node_id])
        
        return path
        

    def get_all_path_lengths(self):
        """Return lengths of shortest paths between all pairs of nodes.

        Returns:
            dict: map from tuples `(u, v)` to the length of the shortest path
                  from `u` to `v`

        """
        if self.dist == []:
            self.shortest_dist()
        n = len(self.node_to_id)
        path_lengths = dict()
        for i in range(n):
            for j in range(n):
                dist = self.dist[i][j]
                if dist != float('inf'):
                    start = self.id_to_node[i]
                    end = self.id_to_node[j]
                    path_lengths[(start, end)] = dist
        
        return path_lengths
                

    def get_all_paths(self):
        """Return shortest paths between all pairs of nodes.

        Returns:
            dict: map from tuples `(u, v)` to a list of nodes (starting with
                  `u` and ending with `v`) which is a shortest path from `u`
                  to `v`

        """
        all_paths = dict()
        
        
        #Paths between distinct nodes
        for start, end in self.get_all_path_lengths():
            if start == end: #Path from node to itself
                all_paths[(start, end)] = [start]
            else: #Path between two distinct nodes
                start_id = self.node_to_id[start]
                end_id = self.node_to_id[end]
                id_path = self.create_path(start_id, end_id)
                all_paths[(start, end)] = [self.id_to_node[node_id] for node_id in id_path]
         
        return all_paths
        
            
    
class GraphFactory:
    """Factory for creating instances of `Graph`."""

    def __init__(self, cutoff=0.5):
        """Create a new factory that creates instances of `Graph`.

        Arguments:
            cutoff (float): the maximum density (as defined in the lab handout)
                            for which the an `AdjacencyDictGraph` should be
                            instantiated instead of an `AdjacencyMatrixGraph`

        """
        raise NotImplementedError

    def from_edges_and_nodes(self, weighted_edges, nodes):
        """Create a new graph instance.

        Arguments:
            weighted_edges (list): the edges in the graph given as
                                   (start, end, weight) tuples
            nodes (list): nodes in the graph

        Returns:
            Graph: a graph containing the given edges

        """
        raise NotImplementedError


def get_most_central_node(graph):
    """Return the most central node in the graph.

    "Most central" is defined as having the shortest average round trip to any
    other node.

    Arguments:
        graph (Graph): a graph with at least one node from which round trips
                       to all other nodes are possible

    Returns:
        node (str): the most central node in the graph; round trips to all
                    other nodes must be possible from this node

    """
    raise NotImplementedError


if __name__ == "__main__":
    # You can place code (like custom test cases) here that will only be
    # executed when running this file from the terminal.
    pass
