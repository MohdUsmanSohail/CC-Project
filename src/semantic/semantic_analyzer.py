import pandas as pd
from .symbol_table import SymbolTable
from .type_rules import check_binary_expr,check_unary_expr,check_aggregrate_function
from src.ast import *

def schema_from_csv(filename):
    try:
        df = pd.read_csv(filename,nrows=10)
    except Exception as e:
        raise Exception(f"Failed to load CSV '{filename}: {e}")
    
    schema = {}
    for col in df.columns:
        dtype = df[col].dtype
        if pd.api.types.is_integer_dtype(dtype):
            schema[col] = "int"
        elif pd.api.types.is_float_dtype(dtype):
            schema[col] = "float"
        else:
            schema[col] = "string"
    return schema

class SemanticAnalyzer:
    def __init__(self):
        self.global_table = SymbolTable()
        self.current_table = self.global_table

        for f in ("avg","sum"):
            self.global_table.define(f,"function",f"{f}(number) -> number")
        self.global_table.define("count","function","count(any) -> number")

        self.table_schemas = {}

    def analyze(self,node,in_aggregate=False):
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self,method_name,self.generic_visit)
        return visitor(node,in_aggregate)
    
    def generic_visit(self,node,in_aggregate=False):
        raise Exception(f"No 'visit_{type(node).__name__}' method defined")
    
    def visit_Program(self,node: Program,in_aggregate=False):
        for stmt in node.statements:
            self.analyze(stmt, in_aggregate)
    
    def visit_LoadStmt(self,node: LoadStmt,in_aggregate=False):
        table_schema = schema_from_csv(node.filename)
        self.table_schemas[node.name] = table_schema
        self.current_table.define(node.name,"table",table_schema)

    def visit_FilterStmt(self,node: FilterStmt,in_aggregate=False):
        if not self.table_schemas:
            raise Exception("No tables loaded before filter")
        last_table = list(self.table_schemas.keys())[-1]
        node.source = last_table
        src_schema = self.table_schemas[node.source]

        block_scope = self.current_table.push_scope()
        self.current_table = block_scope

        self.current_table.define("row","iterator",src_schema)
        for col_name,col_type in src_schema.items():
            self.current_table.define(col_name,"column",col_type)

        self.analyze(node.predicate)

        self.current_table = self.current_table.pop_scope()

        self.table_schemas[node.target] = src_schema.copy()
        self.current_table.define(node.target,"table",self.table_schemas[node.target])

    def visit_MapStmt(self,node: MapStmt,in_aggregate=False):
        src_schema = self.table_schemas.get(node.source)
        if not src_schema:
            raise Exception(f"Undefined source '{node.source}' in map")
        
        block_scope = self.current_table.push_scope()
        self.current_table = block_scope

        self.current_table.define("row","iterator",src_schema)
        for col_name,col_type in src_schema.items():
            self.current_table.define(col_name,"column",col_type)

        map_schema = src_schema.copy()
        for assign in node.assignments:
            expr_type = self.analyze(assign.expr)
            self.current_table.define(assign.name,"column",expr_type)
            map_schema[assign.name] = expr_type

        self.current_table = self.current_table.pop_scope()

        self.table_schemas[node.target] = map_schema
        self.current_table.define(node.target,"table",map_schema)

    def visit_AggregateStmt(self,node: AggregateStmt,in_aggregate=False):
        src_schema = self.table_schemas.get(node.source)
        if not src_schema:
            raise Exception(f"Undefined source '{node.source}' in aggregate")
        
        block_scope = self.current_table.push_scope()
        self.current_table = block_scope

        self.current_table.define("row","iterator",src_schema)
        for col_name,col_type in src_schema.items():
            self.current_table.define(col_name,"column",col_type)

        agg_schema = {}
        for assign in node.assignments:
            expr_type = self.analyze(assign.expr,in_aggregate=True)
            col_type = check_aggregrate_function(assign.func,expr_type)
            self.current_table.define(assign.name,"column",col_type)
            agg_schema[assign.name] = col_type

        self.current_table = self.current_table.pop_scope()

        self.table_schemas[node.target] = agg_schema
        self.current_table.define(node.target,"table",agg_schema)

    def visit_PrintStmt(self,node: PrintStmt,in_aggregate=False):
        for expr in node.expressions:
            self.analyze(expr,in_aggregate)

    def visit_ForStmt(self,node: ForStmt,in_aggregate=False):
        src_schema = self.table_schemas.get(node.source)
        if not src_schema:
            raise Exception(f"Undefined source '{node.source}' in for loop")
        
        block_scope = self.current_table.push_scope()
        self.current_table = block_scope

        self.current_table.define("row","iterator",src_schema)
        for col_name,col_type in src_schema.items():
            self.current_table.define(col_name,"column",col_type)

        for stmt in node.body:
            self.analyze(stmt,in_aggregate)

        self.current_table = self.current_table.pop_scope()

    def visit_BinaryExpr(self,node: BinaryExpr,in_aggregate=False):
        left_type = self.analyze(node.left,in_aggregate)
        right_type = self.analyze(node.right,in_aggregate)
        return check_binary_expr(left_type,node.op,right_type)
    
    def visit_UnaryExpr(self,node: UnaryExpr,in_aggregate=False):
        operand_type = self.analyze(node.operand,in_aggregate)
        return check_unary_expr(node.op,operand_type)
    
    def visit_Identifier(self,node: Identifier,in_aggregate=False):
        sym = self.current_table.lookup(node.name)
        if not sym:
            raise Exception(f"Undefined variable '{node.name}'")
        return sym.type

    def visit_NumberLiteral(self,node: NumberLiteral,in_aggregate=False):
        if isinstance(node.value,int):
            return "int"
        return "float"
    
    def visit_StringLiteral(self,node: StringLiteral,in_aggregate=False):
        return "string"
    
    def visit_DotAccess(self,node: DotAccess,in_aggregate=False):
        obj_type = self.analyze(node.obj,in_aggregate)
        if not isinstance(obj_type,dict):
            raise Exception(f"Cannot access field '{node.field}' of non-row type")
        field_sym = self.current_table.lookup(node.field)
        if not field_sym:
            raise Exception(f"Field '{node.field}' not found in row")
        return field_sym.type

    def visit_FunctionCall(self,node: FunctionCall,in_aggregate=False):
        if not in_aggregate and node.name in ("sum","avg","count"):
            raise Exception(f"Aggregate function '{node.name}' cannot be used outside aggregate block")
        arg_types = [self.analyze(arg,in_aggregate) for arg in node.args]
        return check_aggregrate_function(node.name,arg_types[0] if arg_types else None)