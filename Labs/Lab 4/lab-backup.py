# -*- coding: utf-8 -*-
"""
Created on Sun May 31 04:53:44 2020

@author: Mustafa
"""

"""6.009 Lab 4 -- Boolean satisfiability solving"""

import sys
sys.setrecursionlimit(10000)
# NO ADDITIONAL IMPORTS


def satisfying_assignment(formula):
    """
    Find a satisfying assignment for a given CNF formula.
    Returns that assignment if one exists, or None otherwise.

    >>> satisfying_assignment([])
    {}
    >>> x = satisfying_assignment([[('a', True), ('b', False), ('c', True)]])
    >>> x.get('a', None) is True or x.get('b', None) is False or x.get('c', None) is True
    True
    >>> satisfying_assignment([[('a', True)], [('a', False)]])
    """
    if len(formula) == 0:
        return {}
    
    #Create a set of variables
    variables = set()
    variable_values = {}
    for clause in formula:
        for literal in clause:
            variables.add(literal[0])
            variable_values[literal[0]] = literal[1]

    def helper(formula, truth_table):
        #Base Cases
        # 1 - We use all of the variables but there is still unsatisfied formula
        # No solution exists in that case
        if len(formula) == 0:
            return truth_table
        
        if len(variables) == 0:
            return None
        
        #Recursive step
        else:
            #Check unit clauses
            for clause in formula:
                if len(clause) == 1:
                    var = clause[0][0]
                    value_of_var = clause[0][1]
#                    print('There is a unit clause:', var)
#                    print('With value: ', value_of_var)
#                    print('Formula is: ', formula)
#                    print()
                    if check_conflict(formula, var, value_of_var):
#                        print('There is a conflict return None: ', var)
                        return None
                    if var in variables:
                        variables.remove(var)
                    truth_table[var] = value_of_var
                    updated_formula = update_formula(formula, var, value_of_var)
                    if helper(updated_formula, truth_table) is not None:
                        return truth_table
                    variables.add(var)
                    truth_table.pop(var)
                    return None
                    
            var = variables.pop()
#            print('Chosen variable is: ', var)
#            print('With value: ', True)
#            print('Truth table is: ', truth_table)
#            print('Variables: ', variables)
            truth_table[var] = True
            if check_conflict(formula, var, True):
                return None
            updated_formula = update_formula(formula, var, True)
#            print('Updated formula is: ', updated_formula)
#            print()
            if helper(updated_formula, truth_table) is not None:
                return truth_table
            
            truth_table[var] = False
            if check_conflict(formula, var, False):
                return None
            updated_formula = update_formula(formula, var, False)
            if helper(updated_formula, truth_table) is not None:
                return truth_table
            
            return None
                
    def update_formula(formula, variable, val_of_var):
        new_formula = []
        for clause in formula:
            if (variable, val_of_var) in clause or [variable, val_of_var] in clause:
                continue
            elif (variable, not val_of_var) in clause or [variable, not val_of_var] in clause:
                new_clause = [literal for literal in clause if tuple(literal) != (variable, not val_of_var)]
                new_formula.append(new_clause)
            else:
                new_formula.append(clause)
                
        return new_formula
    
    def check_conflict(formula, variable, val_of_var):
        '''
        Returns true if there is a conflict otherwise False
        '''
        if [(variable, val_of_var)] in formula or [[variable, val_of_var]] in formula:
            if [(variable, not val_of_var)] in formula or [[variable, not val_of_var]] in formula:
#                print('There is a conflict: ', variable)
                return True
        return False
    
    soln = helper(formula, {})
    if soln is None:
        return None
    
    for v in variables:
        if v not in soln:
            soln[v] = variable_values[v]
            
    return soln

def boolify_scheduling_problem(student_preferences, session_capacities):
    """
    Convert a quiz-room-scheduling problem into a Boolean formula.

    student_preferences: a dictionary mapping a student name (string) to a set
                         of session names (strings) that work for that student
    session_capacities: a dictionary mapping each session name to a positive
                        integer for how many students can fit in that session

    Returns: a CNF formula encoding the scheduling problem, as per the
             lab write-up
    We assume no student or session names contain underscores.
    """
    raise NotImplementedError


if __name__ == '__main__':
    import doctest
    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    doctest.testmod(optionflags=_doctest_flags)