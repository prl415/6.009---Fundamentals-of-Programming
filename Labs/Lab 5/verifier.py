import traceback

def check_turn_type(a,b,c):
    if (not isinstance(a[0],int) or not isinstance(a[1],int) or 
        not isinstance(b[0],int) or not isinstance(b[1],int) or 
        not isinstance(c[0],int) or not isinstance(c[1],int)):
        raise TypeError
    v1=(b[0]-a[0],b[1]-a[1])
    v2=(c[0]-b[0],c[1]-b[1])
    cross=v1[0]*v2[1]-v1[1]*v2[0]
    dot = v1[0]*v2[0]+v1[1]*v2[1]
    if cross==0 and dot<0: return 'U'		# U turn
    if cross==0: return 'S'				# straight turn
    if cross<0: return 'L'				# left turn, notice different x-y plane orientation
    return 'R'						# right turn

def check_is_valid(path, edges, source, destination, numTurns, func):
    if path[0]["start"] != source:
        return False, "path does not start at the source!"
    if path[-1]["end"] != destination:
        return False, "path does not end at the destination!"

    if len(path) == 1:
        return path[0] in edges
    else:
        countTurns = 0
        start1 = path[0]['start']
        end1 = path[0]['end']
        
        if path[0] not in edges:
            return False, "{} is not a valid edge".format(path[0])

        for i in range(len(path)-1):
            start2 = path[i+1]['start']
            end2 = path[i+1]['end']
            if end1 != start2:
                return False, "{} does not start at the end coordinate of {}".format(path[i + 1], path[i])
            if path[i+1] not in edges:
                return False, "{} is not a valid edge".format(path[0])
        
            ch = check_turn_type(start1, end1, end2)
            if ch=='U':
                return False, "you took a U-turn!"
            if ch=='L':
                countTurns+=1
            
            start1 = start2
            end1 = end2
        if func == "shortest_path_no_lefts" and countTurns != 0:
            return False, "you took a left!"
        if func == "shortest_path_k_lefts" and countTurns > numTurns:
            return False, "you took {} lefts, when it should be <= {}".format(countTurns, numTurns)
        return True, "all good"

