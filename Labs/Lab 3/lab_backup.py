"""6.009 Lab 3 -- Circuit Solver."""

# NO IMPORTS ALLOWED!

# Uncomment below and comment/rename the solveLinear defined in this file to
# use the sample solveLinear function.
# Remember to comment it out before submitting!

#from solve_linear_sample import solveLinear

def substituteEquation(equation, substitutedVariable, substitutionEquation):
    """
        Note that implementing this function is optional. You might want to
        consider implementing it to break up your code into more managable
        chunks.
        
        Given:
            equation: An equation represented by a dictionary that maps the
                      variables or 1 to its coefficient in the equation.
                      E.g. {1: 2, 'x': 2, 'y': 3} represents 2 + 2x + 3y = 0.
            substitutedVariable: The variable to be substituted out of the
                                 equation.
            substitutionEquation: The substitution equation represented as a
                                  dictionary.
        Return:
            finalEquation: A dictionary representing the resulting equation
                           after the substitution is performed. 
    """
    
    #Now substitute the new_eq (i.e. our substituted variable) into the equation 
    coeff_of_subs_var = equation.pop(substitutedVariable)
    resulting_eq = {var: coeff_of_subs_var * coeff for var, coeff in substitutionEquation.items()}
    for var, coeff in equation.items():
        if var in resulting_eq:
            new_coeff = resulting_eq[var] + coeff
            #Check that whether we have zero coeffient if we have, remove the
            #variable from resulting eqn.
            if new_coeff == 0.0:
                del resulting_eq[var]
                continue
        else:
            new_coeff = coeff
        resulting_eq[var] = new_coeff
    
    return resulting_eq

def substituteValues(equation, num_value_dict):
    '''
    Given:
        equation: An equation represented by a dictionary that maps the
                  variables or 1 to its coefficient in the equation.
                  E.g. {1: 2, 'x': 2, 'y': 3} represents 2 + 2x + 3y = 0.
        variable: A string representing the variable whose numerical value 
                 will be found
        num_value_dict = A dictionary that maps the variables to their numerical
                        values
    Return:
        result: A float number which is numerical value of the variable
    '''
    #If there is a constant number in equation add it to result else set the
    #result 0
    if 1 in equation:
        result = equation.pop(1)
    else:
        result = 0
    
    #substitute the values of variables in the eqn and add them to the result    
    for var, coeff in equation.items():
        num_value = num_value_dict[var]
        result += coeff * num_value
            
    return result

def solveLinear(variables, equations):
    """
        Given:
            variables: A set of strings or tuples representing the independent
                       variables. E.g. {'x', 'y', 'z'}
            equations: A list of linear equations where each equation is
                       represented as a dictionary. Each dictionary maps the
                       variables or 1 to its coefficient in the equation.
                       E.g. {1: 2, 'x': 2, 'y': 3} represents 2 + 2x + 3y = 0.
                       Note that all variables may not appear in all of the
                       equations. Moreover, you may assume that the equations
                       are independent.
        Return:
            result: A dictionary mapping each variable to the numerical value
            that solves the system of equations. Assume that there is exactly
            one solution. Some inaccuracy as typical from floating point
            computations will be acceptable.
    """
    error_message = 'number of equations should be equal to number of variables'
    assert len(equations) == len(variables), error_message
    #To improve the performance of the function, we will make some manipulation
    #Remove the elements with zero coefficient from each equation
    for equation in equations:
        keys_to_be_removed = []
        for var, coeff in equation.items():
            if coeff == 0:
                keys_to_be_removed.append(var)
        for rem_key in keys_to_be_removed:
            del equation[rem_key]
    
    return solveLinearRecursively(variables, equations)
    
def solveLinearRecursively(variables, equations):
    """
        Given:
            variables: A set of strings or tuples representing the independent
                       variables. E.g. {'x', 'y', 'z'}
            equations: A list of linear equations where each equation is
                       represented as a dictionary. Each dictionary maps the
                       variables or 1 to its coefficient in the equation.
                       E.g. {1: 2, 'x': 2, 'y': 3} represents 2 + 2x + 3y = 0.
                       Note that all variables may not appear in all of the
                       equations. Moreover, you may assume that the equations
                       are independent and equations are sorted according to 
                       their length in descending order.
            num_results_dict: A dictionary mapping variables to their numerical
                              value
        Return:
            result: A dictionary mapping each variable to the numerical value
            that solves the system of equations. Assume that there is exactly
            one solution. Some inaccuracy as typical from floating point
            computations will be acceptable.
    """
    #Base Case
    if len(equations) == 1:
        equation = equations.pop()
        variable = variables.pop()
        if 1 not in equation:
            return {variable: 0}
        return {variable: -equation[1]/equation[variable]}
    
    #Recursive step
    else:
        #Choose the equation with the fewest elements
        index = equations.index(min(equations, key=len))
        substitutionEquation = equations.pop(index)
        #Choose the variable with the largest absolute coefficient
        substitutedVariable = max([[abs(v), k] for k, v in substitutionEquation.items() if k != 1], key = lambda i: i[0])[-1]
        variables.remove(substitutedVariable)
        #Rearrange the substitution eqn such that substitution variable is 
        #represented in terms of other variables in the substitution equation
        coeff_of_subs_var = substitutionEquation.pop(substitutedVariable)
        for var, coeff in substitutionEquation.items():
            substitutionEquation[var] = -coeff/coeff_of_subs_var
        #Substitute the variable into the every equation which contains subs var
        for i in range(len(equations)):
            if substitutedVariable in equations[i]:
                equations[i] = substituteEquation(equations[i], substitutedVariable, substitutionEquation)
        #Find the values of the variables after substitution and use them 
        #to find the value of subs var
        num_results_dict = solveLinearRecursively(variables, equations)
        value_of_subs_var = substituteValues(substitutionEquation, num_results_dict)
        num_results_dict[substitutedVariable] = value_of_subs_var
        return num_results_dict

def solveCircuit(junctions, wires, resistances, voltages):
    """
        Given:
            junctions:  A set of junctions. Each junction is labeled by a string
                        or a tuple.
            wires:      A dictionary mapping a unique wire ID (a string or tuple)
                        to a tuple of two elements representing the starting and
                        ending junctions of the wire, respectively. The set of
                        wire IDs is disjoint from the set of junction labels.
                        Note that although electricity can flow in either
                        directions, each wire between a pair of junctions will
                        appear exactly once in the list. Moreover, the starting
                        and ending junctions are distinct.
            resistances:A dictionary mapping each unique wire ID to a numeric
                        value representing the magnitude of the resistance of
                        the wire in Ohms. This dictionary has the same set of
                        keys as the wires dictionary.
            voltages:   A dictionary mapping each unique wire ID to a numeric
                        value representing the voltage (EMF or potential
                        difference) of the battery connected along the wire in 
                        Volts. The positive terminal of the battery is next to
                        the ending junction (as defined in the wires dictionary)
                        if the voltage is positive whereas it is next to the 
                        starting junction otherwise. This dictionary also has
                        the same set of keys as the wires dictionary.
        Return:
            result: A dictionary mapping the label of each wire to the current
                    it carries. The labels must be the keys in the wires
                    dictionary and the current should be considered positive if
                    it is flowing from the starting junction to the ending
                    junction as specified in the wires dictionary.
    """
    #Obtain Kcl and Ohm equations
    equations = getKclEquations(junctions, wires) + getOhmEquations(wires, resistances, voltages)
    
    #Set one of the juctions Vjunc = 0 and add this eqn. also into equations list
    #So we have sufficient number of independent equations to solve the circuit
    ground_junc = junctions.pop()
    junctions.add(ground_junc)
    equations.append({'V' + str(ground_junc): 1})
    
    #Solve the equation system by using solveLinear function
    variables = set(['V' + str(junc) for junc in junctions] + list(wires.keys()))
    result = solveLinear(variables, equations)
    voltages = list(result.keys())
    for var in voltages:
        if var[0] == 'V':
            del result[var]
    
    return result

def getKclEquations(junctions, wires):
    """
        Given:
            junctions:  A set of junctions. Each junction is labeled by a string
                        or a tuple.
            wires:      A dictionary mapping a unique wire ID (a string or tuple)
                        to a tuple of two elements representing the starting and
                        ending junctions of the wire, respectively. The set of
                        wire IDs is disjoint from the set of junction labels.
                        Note that although electricity can flow in either
                        directions, each wire between a pair of junctions will
                        appear exactly once in the list. Moreover, the starting
                        and ending junctions are distinct.
        Return:
            result: A list of equations which are created by using KCL
    """
    #Get the junction graph
    junction_graph = createJunctionGraph(junctions, wires)
    
    #Now, by using junction_graph we can write kcl equations in the form of
    #input_wires - output wires = 0
    kcl_equations = []
    for junc, junc_wires in junction_graph.items():
        input_wires = junc_wires[0]
        output_wires = junc_wires[1]
        kcl_eqn = {}
        for wire in input_wires:
            kcl_eqn[wire] = 1
        for wire in output_wires:
            kcl_eqn[wire] = -1
        kcl_equations.append(kcl_eqn)
    
    #we have j = len(junctions) equations but we need j-1, so remove one eqn.
    kcl_equations.pop() 
    return kcl_equations
    
def createJunctionGraph(junctions, wires):
    """
        Given:
            junctions:  A set of junctions. Each junction is labeled by a string
                        or a tuple.
            wires:      A dictionary mapping a unique wire ID (a string or tuple)
                        to a tuple of two elements representing the starting and
                        ending junctions of the wire, respectively. The set of
                        wire IDs is disjoint from the set of junction labels.
                        Note that although electricity can flow in either
                        directions, each wire between a pair of junctions will
                        appear exactly once in the list. Moreover, the starting
                        and ending junctions are distinct.
        Return:
            result: A mapping of junctions to their input and output wires. 
            Mapping is a dictionary, where a key is ID of a junction and
            value is list of 2-lists where first list represents wires that is
            going in to that junction and second list representes wires that is
            going out from that junction
    """
    junction_graph = {junc: [[],[]] for junc in junctions}
    
    #Loop over the wires to find input and output wires of junctions 
    for wire, junctions in wires.items():
        start_point = junctions[0]
        end_point = junctions[1]
        #If a junc. is a start pt., wire is one of the output wires of the junction
        (junction_graph[start_point])[1].append(wire)
        #if a junc. is a end pt., wire is one of the input wires of the junction
        (junction_graph[end_point])[0].append(wire)  
    
    return junction_graph

def getOhmEquations(wires, resistances, voltages):
    """
        Given:
            wires:      A dictionary mapping a unique wire ID (a string or tuple)
                        to a tuple of two elements representing the starting and
                        ending junctions of the wire, respectively. The set of
                        wire IDs is disjoint from the set of junction labels.
                        Note that although electricity can flow in either
                        directions, each wire between a pair of junctions will
                        appear exactly once in the list. Moreover, the starting
                        and ending junctions are distinct.
            resistances:A dictionary mapping each unique wire ID to a numeric
                        value representing the magnitude of the resistance of
                        the wire in Ohms. This dictionary has the same set of
                        keys as the wires dictionary.
            voltages:   A dictionary mapping each unique wire ID to a numeric
                        value representing the voltage (EMF or potential
                        difference) of the battery connected along the wire in 
                        Volts. The positive terminal of the battery is next to
                        the ending junction (as defined in the wires dictionary)
                        if the voltage is positive whereas it is next to the 
                        starting junction otherwise. This dictionary also has
                        the same set of keys as the wires dictionary.
        Return:
            result: A list of equations which are created by using Ohm's Law
    """
    ohm_equations = []
    for wire, junc in wires.items():
        end_junc_volt = 'V' + str(junc[1])
        start_junc_volt = 'V' + str(junc[0])
        ohm_eq = {end_junc_volt: 1, start_junc_volt: -1, wire: resistances[wire], 1: -voltages[wire]}
        ohm_equations.append(ohm_eq)
    
    return ohm_equations

def findMaximumDeviationJunction(junctions, wires, resistances, voltages, currents):
    """
        Note that this part is completely optional and would not contribute to your grade.
        
        Given:
            junctions:  A set of junctions. Each junction is labeled by a
                        string or a tuple.
            wires:      A dictionary mapping a unique wire ID (a string or tuple)
                        to a tuple of two elements representing the starting and
                        ending junctions of the wire respectively. The set of
                        wire IDs is disjoint from the set of junction labels.
                        Note that although electricity can flow in either
                        direction, each wire between a pair of junctions will
                        appear exactly once in the list. Moreover, the starting
                        and ending junctions are distinct.
            resistances:A dictionary mapping each unique wire ID to a numeric
                        value representing the magnitude of the resistance of
                        the wire in Ohms. This dictionary has the same set of
                        keys as the wires dictionary.
            voltages:   A dictionary mapping each unique wire ID to a numeric
                        value representing the voltage (EMF or potential
                        difference) of the battery connected along the wire in
                        Volts. The positive terminal of the battery is next to
                        the ending junction (as defined in the wires dictionary)
                        if the voltage is positive whereas it is next to the
                        starting junction otherwise. This dictionary also has 
                        the same set of keys as the wires dictionary.
            currents:   A dictionary mapping each unique wire ID to a numeric
                        value representing the indicated current flowing along
                        the wire. The format is identical to that of the output 
                        of the previous function. Note that the values will not
                        necessarily be correct.
        Return:
            result: A junction with the maximum deviation from current
                    conservation. Note that any junction with maximal deviation
                    will be accepted.
    """
    #Get the junction graph
    junction_graph = createJunctionGraph(junctions, wires)
    
    #Find the junction with maximum deviation by checking abs difference between
    #current values of input and output wires of each junction. 
    max_deviation_junction = ''
    max_deviation = 0
    for junction, junction_wires in junction_graph.items():
        input_wires = junction_wires[0]
        input_wires_total = sum([currents[wire] for wire in input_wires])
        output_wires = junction_wires[1]
        output_wires_total = sum([currents[wire] for wire in output_wires])
        if abs(input_wires_total-output_wires_total) >= max_deviation:
            max_deviation = abs(input_wires_total-output_wires_total)
            max_deviation_junction = junction
    
    return max_deviation_junction

def findMaximumDeviationLoop(junctions, wires, resistances, voltages, currents):
    """
        Note that this part is completely optional and would not contribute to your grade.
        
        Given:
            junctions:  A set of junctions. Each junction is labeled by a string
                        or a tuple.
            wires:      A dictionary mapping a unique wire ID (a string or tuple)
                        to a tuple of two elements representing the starting and
                        ending junctions of the wire respectively. The set of
                        wire IDs is disjoint from the set of junction labels.
                        Note that although electricity can flow in either
                        directions, each wire between a pair of junctions will
                        appear exactly once in the list. Moreover, the starting
                        and ending junctions are distinct.
            resistances:A dictionary mapping each unique wire ID to a numeric
                        value representing the magnitude of the resistance of 
                        the wire in Ohms. This dictionary has the same set of
                        keys as the wires dictionary.
            voltages:   A dictionary mapping each unique wire ID to a numeric
                        value representing the voltage (EMF or potential
                        difference) of the battery connected along the wire in
                        Volts. The positive terminal of the battery is next to
                        the ending junction (as defined in the wires dictionary)
                        if the voltage is positive whereas it is next to the 
                        starting junction otherwise. This dictionary also has
                        the same set of keys as the wires dictionary.
            currents:   A dictionary mapping each unique wire ID to a numeric
                        value representing the indicated current flowing along
                        the wire. The format is identical to that of the output
                        of the previous function. Note that the values will not
                        necessarily be correct.
        Return:
            result: A list of wires IDs representing the edges along a loop with
                    maximal (additive) deviation from Kirchoff's loop law.
                    The wires should be in order along the cycle but the
                    starting node and the direction may be arbitrary.
    """
    #Calculate the potential difference on each wire
    pot_diff = {}
    for wire in wires:
        pot_diff[wire] = voltages[wire] - resistances[wire] * currents[wire]
    
    #To find all of the loops, we have to make some manipulation
    #if current on a wire is negative switch the junctions 
    for wire, junction_points in wires.items():
        if currents[wire] < 0:
            wires[wire] = (junction_points[1], junction_points[0])

    loopsInCircuit = getAllCycles(junctions, wires)
    deviations = {}
    for loop in loopsInCircuit:
        deviations[abs(sum([pot_diff[wire] for wire in loop]))] = loop
    
    maxDevLoop = deviations[max(deviations)]
    maxDev = max(deviations)
    print('Len: ', len(maxDevLoop))
    print('Loop: ', maxDevLoop)
    for wire in maxDevLoop:
        print('Deviation on wire' + str(wire) + ' is: ', pot_diff[wire])
    print('Maximum Deviation: ', maxDev)
    print(deviations.keys())
    
    return maxDevLoop

def getAllCycles(junctions, wires):
    '''
    returns list of all cycles in the given circuit
    '''
    juncs_to_wire = {}
    junction_graph = {}
    for w, juncs in wires.items():
        #Mapping of start and end junctions to wires between them
        juncs_to_wire[juncs] = w
        #Mapping of start junctions to end junctions. Like start nodes parents
        #end nodes children
        junction_graph.setdefault(juncs[0], []).append(juncs[1])
    
    #Get all the cycles in terms of nodes
    cycles = []
    for junc in junctions:
        for child in junction_graph[junc]:
            _, pathsFound = DFS(junction_graph, child, junc, [], None, [])
            for path in pathsFound:
                cycles.append([junc] + path)
    
    wire_graph = []
    #Convert the cycles into wire to wire graph
    for cycle in cycles:
        wire_graph.append([juncs_to_wire[tuple(cycle[i:i+2])] for i in range(len(cycle)-1)])
    
    return wire_graph
        
def DFS(graph, start, end, path, shortest, pathsFound):
    path = path + [start]
    
    if start == end:
        if path not in pathsFound:
            pathsFound.append(path)
        return path, pathsFound
    
    for node in graph[start]:
        if node not in path:
            newPath, pathsFound = DFS(graph, node, end, path, shortest, pathsFound)
            if newPath != None:
                shortest = newPath
    return shortest, pathsFound            

if __name__ == '__main__':
    # additional code here will be run only when lab.py is invoked directly
    # (not when imported from test.py), so this is a good place to put code
    # used for testing.
    
    #Test cases for substituteEquation
    #------------------------------------
    substitutedVariable = 'x'
    substitutionEquation = {'x': 2, 'y': 1}
    
    #Test1 
    equation = {'x': 1, 'y': 2, 'z': 4, 1: -1}
    expected = {'y': 1.5, 'z': 4, 1: -1} 
    result = substituteEquation(equation, substitutedVariable, substitutionEquation)
    print('The function passed the test 1: ', result == expected)
    print('And the resulting equation is: ', result)
    print()
    
    #Test2
    equation = {'x': 2, 'y': 3, 'z': 4, 1: 5}
    expected = {'y': 2, 'z': 4, 1: 5}
    result = substituteEquation(equation, substitutedVariable, substitutionEquation)
    print('The function passed the test 2: ', result == expected)
    print('And the resulting equation is: ', result)
    print()
    
    #Test for solveLinear
    equations = [{'x': 1, 'y': 2, 'z': 4, 1: -1}, {'x': 2, 'y': 1}, {'x': 2, 'y': 3, 'z': 4, 1: 5}]
    variables = set(['x', 'y', 'z'])
    print(solveLinear(variables, equations))
    print()
    
    variables = {'x', 'y', 'z', 'w'}
    equations = [{'w': 2, 'x': 3, 1: -5},
                 {'y': 4, 'z': 7, 1: -5},
                 {'w': 1, 'y': -1},
                 {'w': 4, 'z': 2, 1: -6}]
    soln = {'w': 1.6, 'x': 0.6, 'y': 1.6, 'z': -0.2}
    print('blablabla')
    print(solveLinear(variables, equations))
    print()
    print('Solution: ', soln)
    print()
    
    #Test for getKclEquations
    junctions = {'A', 'B', 'C'}
    wires = {'W0': ('C', 'A'), 'W1': ('A', 'B'), 'W2': ('B', 'C'), 'W3': ('B', 'C')}
    expected = [{'W0': 1, 'W1': -1}, {'W1': 1, 'W2': -1, 'W3': -1}, {'W2': 1, 'W3': 1, 'W0': -1}]
    result = getKclEquations(junctions, wires)
    print('The result is: \n', result)
    
    #Test for getOhmEquations
    wires = {'W0': ('C', 'A'), 'W1': ('A', 'B'), 'W2': ('B', 'C'), 'W3': ('B', 'C')}
    resistances = {'W0': 0, 'W1': 3, 'W2': 2, 'W3': 7}
    voltages = {'W0': 5, 'W1': 0, 'W2': 0, 'W3': -10}
    expected = [{'Va': 1, 'Vc': -1, 'Iw0': 0, 1: -5},
	            {'Vb': 1, 'Va': -1, 'Iw0': 3, 1: 0},
	            {'Vc': 1, 'Vb': -1, 'Iw0': 2, 1: 0},
	            {'Vc': 1, 'Vb': -1, 'Iw0': 7, 1: 10}]
    result = getOhmEquations(wires, resistances, voltages)
    print('The result is: \n', result)
    
    print()
    print(solveCircuit(junctions, wires, resistances, voltages))    