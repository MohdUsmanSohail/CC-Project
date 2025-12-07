from typing import List, Any
from src.ast import *
from .ir import *

class IRGenerator:
    def __init__(self):
        self.temp_counter = 0
        self.label_counter = 0
        self.instructions: List[IRInstruction] = []

    def new_temp(self) -> str:
        self.temp_counter += 1
        return f"t{self.temp_counter}"
    
    def new_label(self) -> str:
        self.label_counter += 1
        return f"L{self.label_counter}"
    
    def generate(self,node: ASTNode) -> List[IRInstruction]:
        self.gen_node(node)
        return self.instructions
    
    def gen_node(self,node: ASTNode) -> Any:
        method_name = f'gen_{type(node).__name__}'
        visitor = getattr(self, method_name, self.generic_gen)
        return visitor(node)
    
    def generic_gen(self,node: ASTNode):
        raise Exception(f" No 'gen_{type(node).__name__}' method defined")
    
    def gen_Program(self,node: Program):
        for stmt in node.statements:
            self.gen_node(stmt)

    def gen_LoadStmt(self,node: LoadStmt):
        self.instructions.append(LoadTable(node.name,node.filename))

    def gen_FilterStmt(self,node: FilterStmt):
        pred_label = self.new_label()
        filter_instr = Filter(node.source, pred_label, node.target, None)
        self.instructions.append(filter_instr)
        pred_temp = self.gen_node(node.predicate)
        filter_instr.predicate_temp = pred_temp

    def gen_MapStmt(self,node: MapStmt):
        map_label = self.new_label()
        self.instructions.append(Map(node.source,map_label,node.target))
        for assign in node.assignments:
            self.gen_node(assign)

    def gen_MapAssign(self,node: MapAssign):
        value = self.gen_node(node.expr)
        self.instructions.append(Assign(target=node.name, op="=", arg1=value, arg2=None))

    def gen_AggregateStmt(self,node: AggregateStmt):
        agg_label = self.new_label()
        self.instructions.append(Aggregate(node.source,agg_label,node.target))
        for assign in node.assignments:
            self.gen_node(assign)

    def gen_AggAssign(self,node: AggAssign):
        value = self.gen_node(node.expr)
        self.instructions.append(Assign(node.name,node.func,value))

    def gen_PrintStmt(self,node: PrintStmt):
        for expr in node.expressions:
            value = self.gen_node(expr)
            self.instructions.append(Print(value))

    def gen_ForStmt(self,node: ForStmt):
        self.instructions.append(ForBegin(node.source,node.iter_var))
        for stmt in node.body:
            self.gen_node(stmt)
        self.instructions.append(ForEnd())

    def gen_Identifier(self,node: Identifier):
        return node.name
    
    def gen_NumberLiteral(self,node: NumberLiteral):
        return node.value
    
    def gen_StringLiteral(self,node: StringLiteral):
        return node.value
    
    def gen_DotAccess(self,node: DotAccess):
        base = self.gen_node(node.obj)
        temp = self.new_temp()
        self.instructions.append(Assign(temp,".",base,node.field))
        return temp
    
    def gen_FunctionCall(self,node: FunctionCall):
        args = [self.gen_node(arg) for arg in node.args]
        temp = self.new_temp()
        self.instructions.append(Assign(temp,f"call {node.name}",args))
        return temp
    
    def gen_BinaryExpr(self,node: BinaryExpr):
        left = self.gen_node(node.left)
        right = self.gen_node(node.right)
        temp = self.new_temp()
        self.instructions.append(Assign(temp,node.op,left,right))
        return temp
    
    def gen_UnaryExpr(self,node: UnaryExpr):
        operand = self.gen_node(node.operand)
        temp = self.new_temp()
        self.instructions.append(Assign(temp,node.op,operand))
        return temp