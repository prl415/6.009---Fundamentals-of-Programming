# -*- coding: utf-8 -*-
"""
Created on Sat Dec  7 18:38:51 2019

@author: Mustafa
"""

# NO IMPORTS ALLOWED!

import json

filename = 'resources/names.json'
with open(filename, 'r') as f:
    id_to_names = json.load(f)

BACON = 4724
   
def load_movie_database(file_name):
    '''
    Create and returns the database with the given file_name
    '''
    with open(file_name, 'r') as f:
        movie_database = json.load(f)
    return movie_database
    
def get_actor(names, actor_id):
    '''
    Returns actor's name which has actor id = actor_id.
    If actor_id is not in the names database, raises Exception 
    '''
    for k in names:
        if names[k] == actor_id:
            return k
    raise Exception('Actor is not in the database')

def did_x_and_y_act_together(data, actor_id_1, actor_id_2):
    '''
    Returns True, if actor_id_1 and actor_id_2 is in the same list (are they
    act together in a movie) according to the given database called data
    Otherwise, Returns False
    '''
    for e in data:
        if set(e[:2]) == set([actor_id_1, actor_id_2]):
            return True
    return False

def get_actors_with_bacon_number(data, n):
    '''
    Returns set of actors which has bacon number n
    '''
    
    if n == 0:
        return set([BACON])
    
    else:
        parents = set()
        current_level = set([BACON])
        actor_map = create_actor_map(data)
        
        for i in range(n):
            current_level, parents = get_next_level(actor_map, current_level, parents)
        return current_level
    
#Helper code for get_actors_with_bacon_number and get_bacon_path
def create_actor_map(data):
    '''
    Map each actor to actors which he/she acts together
    '''
    #Represent all graph as a dictionary
    actor_map = {}
    for e in data:
        if len(set(e)) == 3:
            actor_map.setdefault(e[0], set()).add(e[1])
            actor_map.setdefault(e[1], set()).add(e[0])
    return actor_map

def get_next_level(actor_map, level, parents):
    new_level = set()
    
    for actor in level:
        new_level.update(actor_map[actor])
        
    new_level.difference_update(level)
    new_level.difference_update(parents)
    parents = level.copy()
    
    return new_level, parents

#End of the helper code

def get_bacon_path(data, actor_id):
    '''
    Returns the shortest path between Kevin Bacon and given actor which has actor_id
    If such a path doesn't exist, returns None
    
    arguments:
        data: List, Movie and actor database
        actor_id: integer, id of the actor 
    '''
    
    if actor_id == BACON:
        return None
    
    else:
        parents = set()
        level_map = {}
        level_map[0] = set([BACON])
        actor_map = create_actor_map(data)
        current_level = set([BACON])
        is_actor_exist = False
        i = 1
        while len(current_level) != 0:
           current_level, parents = get_next_level(actor_map, current_level, parents)
           
           if len(current_level) != 0:
               level_map[i] = current_level
           
           if actor_id in current_level:
               is_actor_exist = True
               break
           
           i += 1
        if is_actor_exist:
            path = [actor_id]
            path_var = actor_id
            while i > 0:
                path_var = ((level_map[i-1].intersection(actor_map[path_var])).copy()).pop()
                path.append(path_var)
                i -= 1
            path.reverse()
            return path
        else:
            return None

def get_path(data, actor_id_1, actor_id_2):
    '''
    Returns the shortest path between given actors which have actor_id_1 and actor_id_2
    If such a path doesn't exist, returns None
    
    arguments:
        data: List, Movie and actor database
        actor_id_1: integer, id of the actor 1
        actor_id_2: integer, id of the actor 1
    '''
    if did_x_and_y_act_together(data, actor_id_1, actor_id_2):
        return [actor_id_1, actor_id_2]
    
    else:
        parents = set()
        level_map = {}
        level_map[0] = set([actor_id_1])
        actor_map = create_actor_map(data)
        current_level = set([actor_id_1])
        is_actor_exist = False
        i = 1
        while len(current_level) != 0:
           current_level, parents = get_next_level(actor_map, current_level, parents)
           
           if len(current_level) != 0:
               level_map[i] = current_level
           
           if actor_id_2 in current_level:
               is_actor_exist = True
               break
           
           i += 1
        if is_actor_exist:
            path = [actor_id_2]
            path_var = actor_id_2
            while i > 0:
                path_var = ((level_map[i-1].intersection(actor_map[path_var])).copy()).pop()
                if path_var == BACON:
                    path_var = ((level_map[i-1].intersection(actor_map[path_var])).copy()).pop()
                path.append(path_var)
                i -= 1
            path.reverse()
            return path
        else:
            return None
#        
if __name__ == '__main__':
    with open('resources/small.json') as f:
        smalldb = json.load(f)

    # additional code here will be run only when lab.py is invoked directly
    # (not when imported from test.py), so this is a good place to put code
    # used, for example, to generate the results for the online questions.
        # Get bacon path server test 1
    import time
    db = load_movie_database('resources/large.json')
    n = 6
    start = time.time()
    result = get_actors_with_bacon_number(db, n)
    end = time.time()
    print('Actors with bacon number ' + str(n) + ' are: ', result)
    print('Test took: ', end-start)
    
