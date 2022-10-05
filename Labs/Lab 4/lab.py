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
    #Create a set of variables
    variables = set()
    variable_values = {}
    for clause in formula:
        for literal in clause:
            variables.add(literal[0])
            variable_values[literal[0]] = literal[1]

    def helper(formula, truth_table):
        #Base Cases
        # 1 - We found a solution. Return the result
        if len(formula) == 0:
            return truth_table
        
        # 2 - We use all of the variables but there is still unsatisfied formula
        # No solution exists in that case
        if len(variables) == 0:
            return None
        
        #Recursive step
        else:
            #Check unit clauses
            for clause in formula:
                #We found a unit clause such as [('x', b)]. Set it x = b and 
                #recurse to find out whether a solution exists
                if len(clause) == 1:
                    var = clause[0][0]
                    value_of_var = clause[0][1]
                    # Check conflicts. Conflict means no solution exists
                    if check_conflict(formula, var, value_of_var):
                        return None
                    #By using x = b, update result table and formula
                    if var in variables:
                        variables.remove(var)
                    truth_table[var] = value_of_var
                    updated_formula = update_formula(formula, var, value_of_var)
                    #A result is found. Return the resulting table
                    if helper(updated_formula, truth_table) is not None:
                        return truth_table
                    #No solution exists. Undo all changes and return None
                    variables.add(var)
                    truth_table.pop(var)
                    return None
            
            #No unit clauses. Choose a variable and try to find a solution 
            #for var = True and var = False. If a solution exists for one of the
            #boolean values, then return the result. Otherwise no soln. exists.
            var = variables.pop()
            for bool_val in [True, False]:
                truth_table[var] = bool_val
                # Check conflicts
                if check_conflict(formula, var, bool_val):
                    return None
                #By using var = bool_val, update formula and check whether a 
                #solution exists
                updated_formula = update_formula(formula, var, bool_val)
                if helper(updated_formula, truth_table) is not None:
                    return truth_table
            
            #No soln. exists. Return None
            return None
                
    def update_formula(formula, variable, val_of_var):
        '''
        According to truth value of variable, updates the given formula and
        returns updated formula 
        '''
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
        #If unit-clause [(variable, val_of_var)] and [(variable, not val_of_var)]
        #exists at the same time, this will be a conflict 
        if [(variable, val_of_var)] in formula or [[variable, val_of_var]] in formula:
            if [(variable, not val_of_var)] in formula or [[variable, not val_of_var]] in formula:
                return True
        return False
    
    return helper(formula, {})

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
    def get_combinations(variables, n):
        '''
        Returns a list which is all of the combinations created by the elements
        of given variables list. There are n elements in each combination
        '''
        error_message = 'Number of elements has to be equal or bigger than n'
        assert len(variables) >= n, error_message
        
        #Base Cases: There are 2 base cases
        #1 -> n = 1: There k = len(variables) 1-element combinations
        if n == 1:
            return [[e] for e in variables]
        
        #2 -> n = len(variables): There are 1 n-element combination
        elif len(variables) == n:
            return [variables]
        
        #Recursive Step
        else:
            combinations = []
            for i in range(len(variables)-n+1):
                for el in get_combinations(variables[i+1:], n-1):
                    comb = [variables[i]] + el
                    combinations.append(comb)
                    
            return combinations
        
    
    def students_in_desired_rooms(preferences):
        '''
        Returns a cnf formula according to students' preferences
        '''
        formula = []
        for student, prefs_of_stu in preferences.items():
            clause1 = []
            #Here one of the variables being True represents that student is
            #assigned to one of their preferences
            for pref in prefs_of_stu:
                clause1.append((str(student) + '_' + str(pref), True))
            formula.append(clause1)
            
        return formula
    
    def students_in_one_session(students, sessions):
        '''
        Returns a cnf formula according to rule that each student must attend
        to only one session
        '''
        formula = []
        
        for student in students:
            student_and_rooms = []
            for session in sessions:
                student_and_rooms.append(str(student) + '_' + str(session))
            
            #Here we actually enforce that a student can't assigned two different
            #session at the same time
            combinations = get_combinations(student_and_rooms, 2)
            for comb in combinations:
                clause = [(comb[0], False), (comb[1], False)]
                formula.append(clause)
        
        return formula
    
    def no_overcrowded_rooms(students, session_capacities):
        '''
        Returns a cnf formula according to rule that there has to be no 
        overcrowded session
        '''
        formula = []
        
        for session, capacity in session_capacities.items():
            #There are enough capacity for everyone in this session.
            #So, no constraint is required for that session
            if capacity >= len(students):
                continue
            
            #There is not enough capacity so we have to make sure that given
            #session won't be overcrowded
            else:
                students_in_that_room = [str(student) + '_' + str(session) for student in students]
                group_combinations = get_combinations(students_in_that_room, capacity + 1)
                for group in group_combinations:
                    formula.append([(person, False) for person in group])
                        
        return formula
    
    rule1 = students_in_desired_rooms(student_preferences)
    rule2 = students_in_one_session(list(student_preferences.keys()), list(session_capacities.keys()))
    rule3 = no_overcrowded_rooms(list(student_preferences.keys()), session_capacities)
    
    return rule1 + rule2 + rule3

if __name__ == '__main__':
    import doctest
    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    doctest.testmod(optionflags=_doctest_flags)