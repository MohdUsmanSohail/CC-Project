from src.icg.ir import *

class ConstantFolder:
    def __init__(self,instructions):
        self.instructions = instructions

    def fold(self):
        for instr in self.instructions:
            self._fold_instr(instr)
        return self.instructions
    
    def _fold_instr(self, instr):
        if isinstance(instr,Assign):
            instr.arg1, instr.arg2 = self._fold_expr(instr.op,instr.arg1,instr.arg2)
        elif isinstance(instr,FunctionFragment):
            instr.body = ConstantFolder(instr.body).fold()

    def _fold_expr(self,op,arg1,arg2):
        # fold binary_expr if both args are numeric
        if arg2 is not None:
            if isinstance(arg1,(int,float)) and isinstance(arg2,(int,float)):
                try:
                    if op == '+': return arg1 + arg2, None
                    if op == '-': return arg1 - arg2, None
                    if op == '*': return arg1 * arg2, None
                    if op == '/': return arg1 / arg2, None
                    if op == '>': return arg1 > arg2, None
                    if op == '<': return arg1 < arg2, None
                    if op == ">=": return arg1 >= arg2, None
                    if op == "<=": return arg1 <= arg2, None
                    if op == "==": return arg1 == arg2, None
                    if op == "!=": return arg1 != arg2, None
                except Exception:
                    pass
        elif isinstance(arg1,(int,float)):
            if op == '-': return -arg1, None
        
        #no folding possible
        return arg1, arg2