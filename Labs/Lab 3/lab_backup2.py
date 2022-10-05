# -*- coding: utf-8 -*-
"""
Created on Sun Apr 26 15:23:53 2020

@author: Mustafa
"""

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
    resulting_eq = {var: equation[substitutedVariable] * coeff for var, coeff in substitutionEquation.items()}
    for var, coeff in equation.items():
        if var != substitutedVariable:
            if var in resulting_eq:
                new_coeff = resulting_eq[var] + equation[var]
                #Check that whether we have zero coeffient if we have, remove the
                #variable from resulting eqn.
                if new_coeff == 0.0:
                    del resulting_eq[var]
            else:
                new_coeff = equation[var]
            resulting_eq[var] = new_coeff
    
    return resulting_eq

def substituteValues(equation, variable, num_value_dict):
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
    result = 0
    for var, coeff in equation.items():
        if var != variable:
            if var == 1:
                result += coeff
            else:
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
    #To improve the performance of the function, we will make some manipulation
    #Remove the elements with zero coefficient from each equation
    for equation in equations:
        keys_to_be_removed = []
        for var, coeff in equation.items():
            if coeff == 0:
                keys_to_be_removed.append(var)
        for rem_key in keys_to_be_removed:
            equation.pop(rem_key)
    
    #Create a set of 2-element-tuples. In each tuple first element represents length of the
    #equation and second element represents the index of that equation in eqiation list
    len_to_index_set = set()
    for i in range(len(equations)):
        len_to_index_set.add((len(equations[i]), i))
        
    return solveLinearRecursively(variables, equations, len_to_index_set)
    
def solveLinearRecursively(variables, equations, len_to_index_set):
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
    if len(len_to_index_set) == 1:
        index = (len_to_index_set.pop())[1]
        equation = equations[index]
        variable = variables.pop()
        if 1 not in equation:
            return {variable: 0}
        return {variable: -equation[1]/equation[variable]}
    
    #Recursive step
    else:
        #Choose the equation with the fewest elements
        len_and_index = min(len_to_index_set, key = lambda i: i[0])
        substitutionEquation = equations[len_and_index[1]]
        len_to_index_set.remove(len_and_index)
        #Choose the variable with the largest absolute coefficient
        substitutedVariable = max([[abs(v), k] for k, v in substitutionEquation.items() if k != 1], key = lambda i: i[0])[-1]
        variables.remove(substitutedVariable)
        #Create a new equation which is representation of substitution variable  
        #in terms of other variables in substitution equation
        new_eq = {}
        coeff_of_subs_var = substitutionEquation[substitutedVariable]
        for var, coeff in substitutionEquation.items():
            if var != substitutedVariable:
                new_eq[var] = -coeff/coeff_of_subs_var
        substitutionEquation = new_eq
        #Substitute the variable into the every equation
        for _, i in len_to_index_set:
            if substitutedVariable in equations[i]:
                equations[i] = substituteEquation(equations[i], substitutedVariable, substitutionEquation)
        num_results_dict = solveLinearRecursively(variables, equations, len_to_index_set)
        value_of_subs_var = substituteValues(substitutionEquation, substitutedVariable ,num_results_dict)
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
    raise NotImplementedError

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
    raise NotImplementedError

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
    raise NotImplementedError

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
    
#    c = 0
#    result = solveLinear(variables, equations)
#    for k in soln:
#        if abs(result[k]-soln[k]) > 10**(-6):
#            c += 1
#            print('This value is differs from the original result: ', k)
#            print('That much: ', abs(result[k]-soln[k]))