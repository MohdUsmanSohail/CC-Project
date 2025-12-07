# Token types

KEYWORDS = {
    "load",
    "from",
    "filter",
    "where",
    "map",
    "on",
    "aggregate",
    "print",
    "for",
    "in",
    "and",
    "or"
}

SINGLE_CHARS = {
    '(' : "LPAREN",
    ')' : "RPAREN",
    '{' : "LBRACE",
    '}' : "RBRACE",
    '.' : "DOT",
    ',' : "COMMA",
    '=' : "EQUAL"
}

OPERATORS = {
    ">=" : "GTE",
    "<=" : "LTE",
    "==" : "EQ",
    "!=" : "NEQ",
    '>' : "GT",
    '<' : "LT",
    '+' : "PLUS",
    '-' : "MINUS",
    '*' : "STAR",
    '/' : "SLASH"
}

class Token:
    def __init__(self,type,value,line,column):
        self.type = type
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f"Token({self.type},{self.value},{self.line},{self.column})"
