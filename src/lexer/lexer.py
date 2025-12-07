from .tokens import KEYWORDS, SINGLE_CHARS, OPERATORS, Token

class Lexer:
    def __init__(self,text:str):
        self.text = text
        self.pos = 0
        self.line = 1
        self.column = 1

    def current(self):
        if self.pos >= len(self.text):
            return None
        return self.text[self.pos]
    
    def advance(self):
        c = self.current()
        self.pos += 1
        if c == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return c
    
    # matching for multi-character operators
    def match_operator(self):
        for op in sorted(OPERATORS, key=lambda x: -len(x)):
            if self.text.startswith(op,self.pos):
                line, col = self.line, self.column
                self.pos += len(op)
                self.column += len(op)
                return Token(OPERATORS[op], op, line, col)
        
        return None
    
    def tokenize(self):
        tokens = []

        while True:
            c = self.current()
            if c is None:
                break

            if c.isspace():
                self.advance()
                continue

            # for IDENTIFIER or KEYWORD
            if c.isalpha() or c == "_":
                start_line,start_col = self.line, self.column
                lex = self.consume_identifier()
                if lex in KEYWORDS:
                    tokens.append(Token(lex.upper(), lex, start_line, start_col))
                else:
                    tokens.append(Token("IDENTIFIER", lex, start_line, start_col))
                continue

            # for Number literals
            if c.isdigit():
                start_line,start_col = self.line, self.column
                lex = self.consume_number()
                tokens.append(Token("NUMBER", lex, start_line, start_col))
                continue

            # for String literals
            if c == '"':
                start_line,start_col = self.line,self.column
                lex = self.consume_string()
                tokens.append(Token("STRING_LITERAL", lex, start_line, start_col))
                continue

            # for operators
            op_token = self.match_operator()
            if op_token:
                tokens.append(op_token)
                continue

            # for SINGLE_CHARS
            if c in SINGLE_CHARS:
                start_line,start_col = self.line,self.column
                self.advance()
                tokens.append(Token(SINGLE_CHARS[c], c, start_line, start_col))
                continue

            raise Exception(f"Unexpected character '{c}' at line {self.line}, column {self.column}")
        
        tokens.append(Token("EOF","",self.line,self.column))
        return tokens
    
    # consumer functions
    def consume_identifier(self):
        start = self.pos

        while True:
            c = self.current()
            if c is None or not (c.isalnum() or c == "_"):
                break
            self.advance()
        return self.text[start:self.pos]
    
    def consume_number(self):
        start = self.pos
        has_dot = False

        while True:
            c = self.current()
            if c is None:
                break
            if c.isdigit():
                self.advance()
            elif c == "." and not has_dot:
                next_c = self.text[self.pos + 1] if self.pos + 1 < len(self.text) else None
                if next_c is not None and next_c.isdigit():
                    has_dot = True
                    self.advance()
                else:
                    break
            else:
                break

        lexeme = self.text[start:self.pos]
        if lexeme.startswith(".") or lexeme.endswith("."):
            raise Exception(f"Invalid number format '{lexeme}' at line {self.line}, column {self.column}")
        return lexeme
    
    def consume_string(self):
        self.advance() # skip opening quote
        start = self.pos
        while True:
            c = self.current()
            if c is None:
                raise Exception(f"Unterminated string at line {self.line} column {self.column}")
            if c == '"':
                lexeme = self.text[start:self.pos]
                self.advance()
                return lexeme
            self.advance()