from src.lexer import Token
from src.ast import *

class Parser:
    def __init__(self,tokens):
        self.tokens = tokens
        self.pos = 0

    def current(self):
        if self.pos >= len(self.tokens):
            return Token("EOF","",-1,-1)
        return self.tokens[self.pos]
    
    def advance(self):
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
        return self.current()

    def match(self,*types):
        tok = self.current()

        if tok.type in types:
            self.pos += 1
            return tok
        return None
    
    def expect(self,*types):
        tok = self.match(*types)
        if not tok:
            raise Exception(f"Expected {' or '.join(types)} at line {self.current().line}")
        return tok
    
    def consume(self,type):
        tok = self.expect(type)
        return tok.value
    
    #Entry point
    def parse(self):
        stmts = []
        while self.current().type != 'EOF':
            stmts.append(self.statement())
        return Program(stmts)
    
    #Statements
    def statement(self):
        tok = self.current()

        if tok.type == "LOAD":
            return self.parse_load()
        elif tok.type == "FILTER":
            return self.parse_filter()
        elif tok.type == "MAP":
            return self.parse_map()
        elif tok.type == "AGGREGATE":
            return self.parse_aggregate()
        elif tok.type == "PRINT":
            return self.parse_print()
        elif tok.type == "FOR":
            return self.parse_for()
        else:
            raise Exception(f"Unexpected statement at line {tok.line}: {tok.type}")
    
    def parse_load(self):
        self.expect("LOAD")
        name = self.expect("IDENTIFIER").value
        self.expect("FROM")
        filename = self.expect("STRING_LITERAL").value
        return LoadStmt(name,filename)
    
    def parse_filter(self):
        self.expect("FILTER")
        target = self.expect("IDENTIFIER").value
        self.expect("LBRACE")
        self.match("WHERE")
        pred = self.expression()
        self.expect("RBRACE")
        return FilterStmt(target,source=None,predicate=pred)
    
    def parse_map(self):
        self.expect("MAP")
        target = self.expect("IDENTIFIER").value
        self.expect("ON")
        source = self.expect("IDENTIFIER").value
        self.expect("LBRACE")

        assigns = []
        while not self.match("RBRACE"):
            name = self.expect("IDENTIFIER").value
            self.expect("EQUAL")
            expr = self.expression()
            assigns.append(MapAssign(name,expr))
            self.match("COMMA")

        return MapStmt(target,source,assigns)
    
    def parse_aggregate(self):
        self.expect("AGGREGATE")
        target = self.expect("IDENTIFIER").value
        self.expect("ON")
        source = self.expect("IDENTIFIER").value
        self.expect("LBRACE")

        assigns = []
        while not self.match("RBRACE"):
            name = self.expect("IDENTIFIER").value
            self.expect("EQUAL")
            func = self.expect("IDENTIFIER").value
            self.expect("LPAREN")
            expr = self.expression()
            self.expect("RPAREN")
            assigns.append(AggAssign(name,func,expr))
            self.match("COMMA")

        return AggregateStmt(target,source,assigns)
    
    def parse_print(self):
        self.expect("PRINT")
        expr_list = [self.expression()]
        while self.match("COMMA"):
            expr_list.append(self.expression())
        return PrintStmt(expr_list)
    
    def parse_for(self):
        self.expect("FOR")
        iter_var = self.expect("IDENTIFIER").value
        self.expect("IN")
        source = self.expect("IDENTIFIER").value
        self.expect("LBRACE")
        body = []
        while not self.match("RBRACE"):
            body.append(self.statement())
        return ForStmt(iter_var,source,body)
    
    #expressions
    def expression(self):
        return self.parse_logic()
    
    def parse_logic(self):
        expr = self.parse_rel()
        while self.current().type in ("AND", "OR"):
            op = self.current().value
            self.advance()
            right = self.parse_rel()
            expr = BinaryExpr(expr,op,right)
        return expr
    
    def parse_rel(self):
        expr = self.parse_add()
        while self.current().type in ("EQ","NEQ","GT","LT","GTE","LTE"):
            op = self.current().value
            self.advance()
            right = self.parse_add()
            expr = BinaryExpr(expr,op,right)
        return expr
    
    def parse_add(self):
        expr = self.parse_mul()
        while self.current().type in ("PLUS","MINUS"):
            op = self.current().value
            self.advance()
            right = self.parse_mul()
            expr = BinaryExpr(expr,op,right)
        return expr
    
    def parse_mul(self):
        expr = self.parse_unary()
        while self.current().type in ("STAR","SLASH"):
            op = self.current().value
            self.advance()
            right = self.parse_unary()
            expr = BinaryExpr(expr,op,right)
        return expr
    
    def parse_unary(self):
        if self.current().type == "MINUS":
            op = self.current().value
            self.advance()
            operand = self.parse_primary()
            return UnaryExpr(op,operand)
        return self.parse_primary()
    
    def parse_primary(self):
        tok = self.current()

        if tok.type == "IDENTIFIER":
            self.advance()
            node = Identifier(tok.value)

            if self.current().type == "LPAREN":
                self.expect("LPAREN")
                args = []
                if self.current().type != "RPAREN":
                    args.append(self.expression())
                    while self.match("COMMA"):
                        args.append(self.expression())
                self.expect("RPAREN")
                return FunctionCall(node.name,args)

            if self.match("DOT"):
                field = self.expect("IDENTIFIER").value
                return DotAccess(node,field)
            
            return node
        elif tok.type == "NUMBER":
            self.advance()
            return NumberLiteral(float(tok.value))
        elif tok.type == "STRING_LITERAL":
            self.advance()
            return StringLiteral(tok.value)
        elif self.match("LPAREN"):
            expr = self.expression()
            self.expect("RPAREN")
            return expr
        
        raise Exception(f"Unexpected token {tok.type} at line {tok.line}")