import doctest

# NO ADDITIONAL IMPORTS ALLOWED!
# You are welcome to modify the classes below, as well as to implement new
# classes and helper functions as necessary.

def create_bin_op(e1, e2, op):
    op_table = {'+': e1 + e2, '-': e1 - e2, '*': e1 * e2, '/': e1 / e2}
    return op_table[op]

def tokenize(exp):
    '''
    Helper function for sym
    Converts given expression exp into meaningful Symbol tokens and returns
    them as a list
    '''
    def helper(str_list):
        '''
        Separates the parantheses from the given str_list to separate parens 
        from the meaningful tokens
        '''
        new_str_list = []
        for e in str_list:
            #Recursive cases: parens are combined with tokens. separate them
            if e[0] == '(':
                new_str_list.extend([e[0]] + helper([e[1:]]))
            elif e[-1] == ')':
                new_str_list.extend(helper([e[:-1]]) + [e[-1]])
            #This is a meaningful token. add it to our result list
            else:
                new_str_list.append(e)
        return new_str_list
    
    return helper(exp.split(sep = ' '))

def parse(tokens):
    '''
    Helper function for sym
    By using meaningful tokens, creates a symbolic expression
    '''
    def parse_expression(index):
        token = tokens[index]
        #Token is an integer. so it will be a Num object
        if token[-1].isdigit():
            return Num(int(token)), index + 1
        
        #Token is a letter, so it will be a Var object
        elif len(token) == 1 and token.isalpha():
            return Var(token), index + 1
        
        #The expression is in the form of (E1 op E2) --> Recursively parse 
        #E1 and E2 then return the corresponding BinOp with the index of next
        #rightmost paren
        else:
            #Token is '(', create e1
            if token == '(':
                e1, index = parse_expression(index + 1)
                token = tokens[index]
            
            #Token is an operator, create e2
            if token in '+-*/':
                op = token
                e2, index = parse_expression(index + 1)
                
            return create_bin_op(e1, e2, op), index + 1
    
    parsed_expression, next_index = parse_expression(0)
    return parsed_expression

def sym(exp):
    '''
    Converts the given string expression into a symbolic expression
    '''
    tokens = tokenize(exp)
    sym_exp = parse(tokens)
    return sym_exp
            
            
class Symbol:
    def __add__(e1, e2):
        return Add(e1, e2)
    
    def __sub__(e1, e2):
        return Sub(e1, e2)
    
    def __mul__(e1, e2):
        return Mul(e1, e2)
    
    def __truediv__(e1, e2):
        return Div(e1, e2)
    
    def __radd__(e1, e2):
        return Add(e1, e2)
    
    def __rsub__(e1, e2):
        return Sub(e2, e1)
    
    def __rmul__(e1, e2):
        return Mul(e1, e2)
    
    def __rtruediv__(e1, e2):
        return Div(e2, e1)
    
    def simplify(self):
        return self
    
    def is_zero(self):
        return self.get_type() == Num and self.get_val() == 0

class Var(Symbol):
    def __init__(self, n):
        """
        Initializer.  Store an instance variable called `name`, containing the
        value passed in to the initializer.
        """
        self.name = n

    def __str__(self):
        return self.name

    def __repr__(self):
        return 'Var(' + repr(self.name) + ')'
    
    def get_type(self):
        return 'var'
    
    def get_val(self):
        return self.name
    
    def deriv(self, var):
        if self.name == var:
            return Num(1)
        
        return Num(0)
    
    def eval(self, mapping):
        return mapping[self.get_val()]

class Num(Symbol):
    def __init__(self, n):
        """
        Initializer.  Store an instance variable called `n`, containing the
        value passed in to the initializer.
        """
        self.n = n

    def __str__(self):
        return str(self.n)

    def __repr__(self):
        return 'Num(' + repr(self.n) + ')'
    
    def get_type(self):
        return 'num'
    
    def get_val(self):
        return self.n
    
    def deriv(self, var):
        return Num(0)
    
    def eval(self, mapping):
        return self.get_val()

class BinOp(Symbol):
    def __init__(self, left, right):
        if self.type_check(left) is not None:
            left = self.type_check(left)
        
        elif self.type_check(right) is not None:
            right = self.type_check(right)
            
        self.left = left
        self.right = right
        self.type = self.get_type()
        self.op = self.get_op()
        self.precedence = self.get_precedence()
        
    def type_check(self, val):
        if isinstance(val, str):
            return Var(val)
            
        elif isinstance(val, int):
            return Num(val)
        
        return None
        
    def __repr__(self):
        return self.type + '(' + repr(self.left) + ', ' + repr(self.right) + ')'
    
    def __str__(self):
        left_string = self.get_string(self.left)
        right_string = self.get_string(self.right, True)
            
        return left_string + ' ' + str(self.op) + ' ' + right_string
    
    def get_precedence(self):
        if self.op in '+-':
            return 1
        
        else:
            return 2
        
    def get_string(self, exp, is_right = False):
        #Num or Var, no need to parenthesization
        if exp.get_type() == 'var' or exp.get_type() == 'num':
            return str(exp)
        
        #Special case: where B is / or - and right exp. has same 
        #precedence with B
        elif is_right and (self.op in '/-') and (self.precedence == exp.precedence):
            return '(' + str(exp) + ')'
        
        #Precedence of B is bigger than exp
        elif self.precedence > exp.precedence:
            return '(' + str(exp) + ')'
        
        return str(exp)
    
class Add(BinOp):
    def get_type(self):
        return 'Add'
    
    def get_op(self):
        return '+'
    
    def deriv(self, var):
        return self.left.deriv(var) + self.right.deriv(var)
    
    def simplify_helper(self):
        left = self.left.simplify()
        right = self.right.simplify()
        result = (left + right).simplify()
        return result
    
    def simplify(self):
        if type(self.left) != Num:
            self.left = self.left.simplify()
            
        if type(self.right) != Num:
            self.right = self.right.simplify()
            
        #Addition with zero
        if type(self.left) == Num and self.left.get_val() == 0:
            return self.right.simplify()
        
        elif type(self.right) == Num and self.right.get_val() == 0:
            return self.left.simplify()
        
        #Both sides are numbers
        elif type(self.left) == Num and type(self.right) == Num:
            return Num(self.left.get_val() + self.right.get_val())
        
        #Addition of Var with Var or Var with Num which isn't zero
        return self.left + self.right
    
    def eval(self, mapping):
        return self.left.eval(mapping) + self.right.eval(mapping)
        
class Sub(BinOp):
    def get_type(self):
        return 'Sub'
    
    def get_op(self):
        return '-'
    
    def deriv(self, var):
        return self.left.deriv(var) - self.right.deriv(var)
    
    def simplify(self):
        if type(self.left) != Num:
            self.left = self.left.simplify()
            
        if type(self.right) != Num:
            self.right = self.right.simplify()
            
        #Subtraction of zero
        if type(self.right) == Num and self.right.get_val() == 0:
            return self.left.simplify()
        
        #Both sides are numbers
        elif type(self.left) == Num and type(self.right) == Num:
            return Num(self.left.get_val() - self.right.get_val())
        
        #Subtraction of Var with Var or Var with Num which isn't zero
        return self.left - self.right
    
    def eval(self, mapping):
        return self.left.eval(mapping) - self.right.eval(mapping)
    
class Mul(BinOp):
    def get_type(self):
        return 'Mul'
    
    def get_op(self):
        return '*'
    
    def deriv(self, var):
        left = self.left.deriv(var) * self.right
        right = self.left * self.right.deriv(var)
        return left + right
    
    def simplify(self):
        if type(self.left) != Num:
            self.left = self.left.simplify()
            
        if type(self.right) != Num:
            self.right = self.right.simplify()
            
        #Multiplication with 0
        if type(self.left) == Num and self.left.get_val() == 0:
            return Num(0)
        
        if type(self.right) == Num and self.right.get_val() == 0:
            return Num(0)
        
        #Multiplication with 1
        if type(self.left) == Num and self.left.get_val() == 1:
            return self.right.simplify()
        
        elif type(self.right) == Num and self.right.get_val() == 1:
            return self.left.simplify()
        
        #Both sides are numbers
        elif type(self.left) == Num and type(self.right) == Num:
            return Num(self.left.get_val() * self.right.get_val())
        
        #Multiplication of Var with Var or Var with Num which isn't zero
        return self.left * self.right
    
    def eval(self, mapping):
        return self.left.eval(mapping) * self.right.eval(mapping)
    
class Div(BinOp):
    def get_type(self):
        return 'Div'
    
    def get_op(self):
        return '/' 
    
    def deriv(self, var):
        num = self.left.deriv(var) * self.right - self.left * self.right.deriv(var)
        denum = self.right * self.right
        return num / denum
    
    def simplify(self):
        if type(self.left) != Num:
            self.left = self.left.simplify()
            
        if type(self.right) != Num:
            self.right = self.right.simplify()
            
        #Dividing by one
        if type(self.right) == Num and self.right.get_val() == 1:
            return self.left.simplify()
        
        #Division of zero with another number
        elif type(self.left) == Num and self.left.get_val() == 0:
            return Num(0)
        
        #Both sides are numbers
        elif type(self.left) == Num and type(self.right) == Num:
            return Num(self.left.get_val() / self.right.get_val())
        
        #Division of Var with Var or Var with Num which isn't zero
        return self.left / self.right
    
    def eval(self, mapping):
        return self.left.eval(mapping) / self.right.eval(mapping)
    
if __name__ == '__main__':
    doctest.testmod()
    
    #REPL Code
    #----------------
    exp = input('in> ')
    while str(exp) != 'QUIT':
        try:
            tokens = tokenize(str(exp))
            sym_exp = parse(tokens)
            print('  out>',repr(sym_exp))
        except:
            print()
            print('You should type expression in the form of single expression or (e1 op e2)')
            print('To exit type QUIT')
            print()
        exp = input('in> ')