class Symbol:
    def __init__ (self,name,category,type_,node=None):
        self.name = name
        self.category = category    # e.g. table,column,function
        self.type = type_           # e.g. string,number,table<row>
        self.node = node            # AST node

class SymbolTable:
    def __init__(self,parent=None):
        self.symbols = {}
        self.parent = parent

    def define(self,name,category,type_,node=None):
        if name in self.symbols:
            raise Exception(f"'{name}' already defined in current scope")
        self.symbols[name] = Symbol(name,category,type_,node)

    def assign(self,name,type_):
        sym = self.lookup(name)
        if not sym:
            raise Exception(f"'{name}' not defined")
        sym.type = type_

    def lookup(self,name):
        table = self
        while table:
            if name in table.symbols:
                return table.symbols[name]
            table = table.parent
        return None
    
    def push_scope(self):
        return SymbolTable(parent=self)
    
    def pop_scope(self):
        return self.parent