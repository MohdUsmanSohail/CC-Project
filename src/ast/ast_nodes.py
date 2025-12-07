# Base classes

class ASTNode:
    """Base class for all AST Nodes"""
    pass

class Statement(ASTNode):
    """Base class for <stmt> related productions."""
    pass

class Expression(ASTNode):
    """Base class for <expr> related productions."""
    pass


# <program> ::= <statement>
class Program(ASTNode):
    def __init__(self,statements):
        self.statements = statements


# <load_stmt> ::= "load" name "from" filename
class LoadStmt(Statement):
    def __init__(self,name,filename):
        self.name = name
        self.filename = filename

# <filter_stmt> ::= "filter" target { predicate } 
# source is the input file
class FilterStmt(Statement):
    def __init__(self,target,source,predicate):
        self.target = target
        self.source = source
        self.predicate = predicate

# <map_stmt> ::= "map" target "on" source { assignments (from MapAssign class ) }
class MapAssign(ASTNode):
    def __init__(self,name,expr):
        self.name = name
        self.expr = expr

class MapStmt(Statement):
    def __init__(self,target,source,assignments):
        self.target = target
        self.source = source
        self.assignments = assignments

# <aggregate_stmt> ::= "aggregate" target "on" source { assignments (from AggAssign class) }
class AggAssign(ASTNode):
    def __init__(self,name,func,expr):
        self.name = name
        self.func = func
        self.expr = expr

class AggregateStmt(Statement):
    def __init__(self,target,source,assignments):
        self.target = target
        self.source = source
        self.assignments = assignments

# <print_stmt> ::= "print" <expr_list>
class PrintStmt(Statement):
    def __init__(self,expressions):
        self.expressions = expressions

# <for_stmt> ::= "for" iter_var "in" source { body }
class ForStmt(Statement):
    def __init__(self,iter_var,source,body):
        self.iter_var = iter_var
        self.source = source
        self.body = body

# <primary> ::= IDENTIFIER | NUMBER | STRING_LITERAL
class Identifier(Expression):
    def __init__(self,name):
        self.name = name

class NumberLiteral(Expression):
    def __init__(self,value):
        self.value = value

class StringLiteral(Expression):
    def __init__(self,value):
        self.value = value

# <primary> ::= obj "." field
class DotAccess(Expression):
    def __init__(self,obj,field):
        self.obj = obj
        self.field = field

#<function_call> ::= "(" [<expr_list] ")"
class FunctionCall(Expression):
    def __init__(self,name,args):
        self.name = name
        self.args = args

# for <logic_expr>, <rel_expr>, <add_expr> and <mul_expr>
class BinaryExpr(Expression):
    def __init__(self,left,op,right):
        self.left = left
        self.op = op
        self.right = right

# <unary_expr> ::= [ "-" ] <primary>
class UnaryExpr(Expression):
    def __init__(self,op,operand):
        self.op = op
        self.operand = operand