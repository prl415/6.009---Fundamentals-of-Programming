"""6.009 Lab 5 -- Don't Turn Left!"""

# NO ADDITIONAL IMPORTS

#Helper Functions
#----------------------
def BFS(graph, start, end, k = 0):
    '''
    Breadth First Search
    By using given graph, finds the shortest path between start and end
    
    Args:
        graph: a list of dictionaries, where each dictionary has two items. 
            These items have keys `"start"` and `"end"` and values that are 
            dictionaries (two keys named 'previous' and 'current'),
            to specify the transition from 'start' edge to 'end' edge.
        start: a tuple representing our initial location.
        end: a tuple representing the target location.
        k: a int to specify left turns allowed (which is needed in 
        shortest_path_k_lefts). It's default value is zero

    Returns:
        A list containing the edges taken in the resulting path if one exists, 
            None if there is no path
    '''
    #By using transition graph create a new_graph to use in BFS. This graph 
    #maps the edges to their neighbours.
    new_graph = {}
    for transition in graph:
        start_edge = transition['start']
        next_edge = transition['end']
        #Shortest_path or Shortest_path_no_lefts problem. Keys is the 2 element
        #tuple which represents the edge and the value is the neighbour edges
        if k == 0:
            node = (start_edge['previous'], start_edge['current'])
            child = (next_edge['previous'], next_edge['current'])
        #Shortest_path_k_lefts problem. Keys are the 3 element tuple which 
        #represents the edge and the left turns remaining and the value is
        #the neighbour edges and their left turns remaining
        else:
            node = (start_edge['previous'], start_edge['current'], start_edge['left_turns_remaining'])
            child = (next_edge['previous'], next_edge['current'], next_edge['left_turns_remaining'])
        new_graph.setdefault(node, set()).add(child)
    
    #Some manipulation is needed: There may be more than one edge from start
    #node so we have to explore all of them to find shortest path
    start_edges = set()
    for edge in new_graph:
        if start == edge[0]:
            if k == 0:
                start_edges.add(edge)
            elif k == edge[2]:
                start_edges.add(edge)
   
    #Breadth First Search             
    shortest_path = None
    for start in start_edges:        
        level = {start: 0}
        parent = {start: None}
        i = 1
        frontier = [start]
        is_found = False
        while frontier and not is_found:
            next_level = []
            for u in frontier:
                #Make sure that u has at least one child
                if u in new_graph:
                    for v in new_graph[u]:
                        if v not in level:
                            level[v] = i
                            parent[v] = u
                            next_level.append(v)
                            #If target node is found we are done, exit from loop
                            if v[1] == end:
                                is_found = True
                                end_edge = v
                                break
                #There is no need to explore other cells if we reach target node            
                if is_found:
                    break
            
            frontier = next_level
            i += 1
            
        if is_found:
            #A valid path exists, by starting from end node trace the path to reach
            #start node. Then, by using that path create list of edges that create
            #the path and return the result
            path = [end_edge]
            while parent[path[-1]] != None:
                path.append(parent[path[-1]])
            path.reverse()
            edge_path = []
            if k == 0:
                for u, v in path:
                    edge_path.append({'start': u, 'end': v})
            #Shortest_path_k_lefts problem. There are 3 elements to unpack
            #for each edge
            else:
                for u, v, _ in path:
                    edge_path.append({'start': u, 'end': v})
        
            if shortest_path == None:
                shortest_path = edge_path
            
            elif shortest_path != None and len(shortest_path) > len(edge_path):
                shortest_path = edge_path
    
    return shortest_path

def create_mapping(edges):
    '''Creates a mapping of nodes which maps nodes to 2-element tuples. Each tuple
    consists of a neighbour and an edge which connects node to that neighbour
    Useful to know the neigbours of each edge.
    Returns the resulting mapping'''
    mapping = {}
    for edge in edges:
        start_node = edge['start']
        end_node = edge['end']
        mapping.setdefault(start_node, set()).add(end_node)
    return mapping

def make_transform(mapping, k = 0):
    '''
    By using mapping of nodes, creates the list of each transition which can be 
    took place.
    Returns the resulting list
    '''
    transform = []
    for i in range(k+1):
        for node, children in mapping.items():
            for child in children:
                if child in mapping:
                    for grandchild in mapping[child]:
                        if k == 0:
                            transition = {'start': {'previous': node, 'current': child}, 'end': {'previous': child, 'current': grandchild}}
                        #Shortest_path_k_lefts problem. We need to know also how many left turns remaining for each edge
                        else:
                            transition = {'start': {'previous': node, 'current': child, 'left_turns_remaining': i}, 'end': {'previous': child, 'current': grandchild, 'left_turns_remaining': i}}
                        transform.append(transition)
    return transform

def check_left_turns(transition_graph, k = 0):
    '''
    According to dot product and cross product removes the left turns and 
    u_turns from the transition_graph. Removes the updated transition graph
    '''
    new_graph = []
    for edges in transition_graph:
        v1, v2 = create_vectors(edges)
        cross_product = v1[0]*v2[1] - v1[1]*v2[0]
        dot_product = v1[0]*v2[0] + v1[1]*v2[1]
        
        #A left turn
        if cross_product < 0:
            if k == 0:
                continue
            #Shortest_path_k_lefts problem. So we should also consider whether
            #we can make a left turn
            elif (edges['start'])['left_turns_remaining'] > 0:
                (edges['end'])['left_turns_remaining'] -= 1
                new_graph.append(edges)
                
        #Right turn
        elif cross_product > 0:
            new_graph.append(edges)
            
        elif cross_product == 0:
            #Straight direction
            if not dot_product < 0:
                new_graph.append(edges)
                
    return new_graph
            
def create_vectors(edges):
    '''
    By using given edges, creates vectors for 'start' and 'end' edge.
    Each vector is represented by 2 element tuple.
    Returns two vectors (tuples).
    '''
    edge1 = edges['start']
    edge2 = edges['end']
    v1 = (edge1['current'][0] - edge1['previous'][0], edge1['current'][1] - edge1['previous'][1])
    v2 = (edge2['current'][0] - edge2['previous'][0], edge2['current'][1] - edge2['previous'][1])
    return v1, v2
#End of the helper functions
#--------------------------------
    
def shortest_path(edges, start, end):
    """
    Finds a shortest path from start to end using the provided edges

    Args:
        edges: a list of dictionaries, where each dictionary has two items. 
            These items have keys `"start"` and `"end"` and values that are 
            tuples (two integers), to specify grid locations.
        start: a tuple representing our initial location.
        end: a tuple representing the target location.

    Returns:
        A list containing the edges taken in the resulting path if one exists, 
            None if there is no path

        formatted as:
            [{"start":(x1,y1), "end":(x2,y2)}, {"start":(x2,y2), "end":(x3,y3)}]
    """
    #Create a mapping of nodes which maps nodes to 2-element tuples. Each tuple
    #consists of a neighbour and an edge which connects node to that neighbour
    mapping = create_mapping(edges)
    transformed_graph = make_transform(mapping)
    
    return BFS(transformed_graph, start, end)

def shortest_path_no_lefts(edges, start, end):
    """
    Finds a shortest path without any left turns that goes
        from start to end using the provided edges. 
        (reversing turns are also not allowed)

    Args:
        edges: a list of dictionaries, where each dictionary has two items. 
            These items have keys `"start"` and `"end"` and values that are 
            tuples (two integers), to specify grid locations.
        start: a tuple representing our initial location.
        end: a tuple representing the target location.

    Returns:
        A list containing the edges taken in the resulting path if one exists, 
            None if there is no path

        formatted as:
            [{"start":(x1,y1), "end":(x2,y2)}, {"start":(x2,y2), "end":(x3,y3)}]
    """
    #By using edges, create a mapping of nodes. This mapping will be used
    #to create a transformed graph
    mapping = create_mapping(edges)
    transformed_graph = make_transform(mapping)
    #Remove the left turns from the transformed graph
    updated_graph = check_left_turns(transformed_graph)
    
    return BFS(updated_graph, start, end)

def shortest_path_k_lefts(edges, start, end, k):
    """
    Finds a shortest path with no more than k left turns that 
        goes from start to end using the provided edges.
        (reversing turns are also not allowed)

    Args:
        edges: a list of dictionaries, where each dictionary has two items. 
            These items have keys `"start"` and `"end"` and values that are 
            tuples (two integers), to specify grid locations.
        start: a tuple representing our initial location.
        end: a tuple representing the target location.
        k: the max number of allowed left turns.

    Returns:
        A list containing the edges taken in the resulting path if one exists, 
            None if there is no path

        formatted as:
            [{"start":(x1,y1), "end":(x2,y2)}, {"start":(x2,y2), "end":(x3,y3)}]
    """
    #No left turns allowed, so this is a no_left_turn problem
    if k == 0:
        return shortest_path_no_lefts(edges, start, end)
    
    #k > 0, some left turns allowed
    mapping = create_mapping(edges)
    transformed_graph = make_transform(mapping, k)
    updated_graph = check_left_turns(transformed_graph, k)
    
    return BFS(updated_graph, start, end, k)
    
if __name__ == "__main__":
    # additional code here will be run only when lab.py is invoked directly
    # (not when imported from test.py), so this is a good place to put code
    # used for testing.
    edges = [
            {"start":(0,1), "end":(1,0)},
            {"start":(1,2), "end":(0,1)},
            {"start":(1,2), "end":(2,1)},
            {"start":(2,1), "end":(1,0)},
          ]
    
    large = [
        {"start":(1,1), "end":(1,0)},
        {"start":(1,2), "end":(1,1)},
        {"start":(3,0), "end":(2,0)},
        {"start":(1,4), "end":(2,3)},
        {"start":(1,4), "end":(1,3)},
        {"start":(1,3), "end":(2,3)},
        {"start":(2,3), "end":(3,3)},
        {"start":(2,3), "end":(2,2)},
        {"start":(2,4), "end":(2,3)},
        {"start":(2,2), "end":(3,2)},
        {"start":(3,0), "end":(4,0)},
        {"start":(3,1), "end":(3,0)},
        {"start":(3,1), "end":(2,1)},
        {"start":(3,2), "end":(3,1)},
        {"start":(3,2), "end":(4,2)},
        {"start":(3,3), "end":(3,2)},
        {"start":(3,3), "end":(4,4)},
        {"start":(4,0), "end":(4,1)},
        {"start":(4,1), "end":(3,1)},
        {"start":(4,4), "end":(3,4)},
        {"start":(3,4), "end":(3,3)},
        {"start":(3,4), "end":(2,4)},
      ]
    
    result = shortest_path_k_lefts(
      [
        {"start":(1,1), "end":(1,0)},
        {"start":(1,2), "end":(1,1)},
        {"start":(3,0), "end":(2,0)},
        {"start":(1,4), "end":(2,3)},
        {"start":(1,4), "end":(1,3)},
        {"start":(1,3), "end":(2,3)},
        {"start":(2,3), "end":(3,3)},
        {"start":(2,3), "end":(2,2)},
        {"start":(2,4), "end":(2,3)},
        {"start":(2,2), "end":(3,2)},
        {"start":(3,0), "end":(4,0)},
        {"start":(3,1), "end":(3,0)},
        {"start":(3,1), "end":(2,1)},
        {"start":(3,2), "end":(3,1)},
        {"start":(3,2), "end":(4,2)},
        {"start":(3,3), "end":(3,2)},
        {"start":(3,3), "end":(4,4)},
        {"start":(4,0), "end":(4,1)},
        {"start":(4,1), "end":(3,1)},
        {"start":(4,4), "end":(3,4)},
        {"start":(3,4), "end":(3,3)},
        {"start":(3,4), "end":(2,4)},
      ],
      (1,4),
      (2,1),
      1,
    )