from typing import Any, Optional, Sequence, Dict

class IRInstruction:
    """Base class for all IR instructions"""
    pass

class LoadTable(IRInstruction):
    def __init__(self,target: str,filename: str):
        self.target = target
        self.source = filename

    def __repr__(self):
        return f"LoadTable(target = {self.target!r}, filename = {self.source!r})"
    
class Filter(IRInstruction):
    def __init__(self,input_table: str, predicate_label: str, output_table: str,predicate_temp: str):
        self.input = input_table
        self.predicate_label = predicate_label
        self.output = output_table
        self.predicate_temp = predicate_temp

    def __repr__(self):
        return f"Filter(input={self.input!r}, pred={self.predicate_label!r}, output={self.output!r}, pred_temp={self.predicate_temp!r})"
    
class Map(IRInstruction):
    def __init__(self,input_table: str,map_label: str,output_table: str):
        self.input = input_table
        self.map_label = map_label
        self.output = output_table

    def __repr__(self):
        return f"Map(input={self.input!r}, map_fn={self.map_label!r}, output={self.output!r})"
    
class Aggregate(IRInstruction):
    def __init__(self,input_table: str,agg_label: str,output_table: str):
        self.input = input_table
        self.agg_label = agg_label
        self.output = output_table

    def __repr__(self):
        return f"Aggregate(input={self.input!r}, agg_fn={self.agg_label!r}, output={self.output!r})"
    
class ForBegin(IRInstruction):
    def __init__(self,table: str,iter_var: str):
        self.table = table
        self.iter_var = iter_var

    def __repr(self):
        return f"ForBegin(table={self.table!r}, iter_var={self.iter_var!r})"
    
class ForEnd(IRInstruction):
    def __repr__(self):
        return "ForEnd()"
    
class Print(IRInstruction):
    def __init__(self, value: Any):
        self.value = value

    def __repr__(self):
        return f"Print({self.value!r})"
    
class Assign(IRInstruction):
    """Three-address code assignments, example:
        t1 = t2 + t3 (target = t1, op = +, arg1 = t2, arg2 = t3)"""
    def __init__(self,target: str,op: str,arg1: Optional[Any] = None,arg2: Optional[Any] = None):
        self.target = target
        self.op = op
        self.arg1 = arg1
        self.arg2 = arg2

    def __repr__(self):
        return f"Assign(target={self.target!r}, op={self.op!r}, arg1={self.arg1!r}, arg2={self.arg2!r})"

class Label(IRInstruction):
    def __init__(self,name: str):
        self.name = name

    def __repr__(self):
        return f"Label({self.name!r})"
    
class Return(IRInstruction):
    def __init__(self,value: Any):
        self.value = value

    def __repr__(self):
        return f"Return({self.value!r})"
    
class FunctionFragment(IRInstruction):
    """Optional wrapper to group related IR instructions"""
    def __init__(self,name: str,body: Optional[Sequence[IRInstruction]] = None):
        self.name = name
        self.body = list(body) if body else []

    def __repr__(self):
        return f"FunctionalFragment(name={self.name!r}, body_len={len(self.body)})"
    
__all__= [
    "IRInstruction",
    "LoadTable","Filter","Map","Aggregate",
    "ForBegin","ForEnd","Print",
    "Assign","Label","Return","FunctionFragment",
]