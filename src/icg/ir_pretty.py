from .ir import *

class IRPretty:
    def __init__(self,instructions):
        self.instructions = instructions

    def pretty(self):
        for instr in self.instructions:
            print(self.format(instr))

    def format(self,instr):
        if isinstance(instr,LoadTable):
            return f"LOAD {instr.target} from {instr.source}"
        elif isinstance(instr,Filter):
            return f"FILTER {instr.input} -> {instr.output} [LABEL {instr.predicate_label}]"
        elif isinstance(instr,Map):
            return f"MAP {instr.input} -> {instr.output} [LABEL {instr.map_label}]"
        elif isinstance(instr,Aggregate):
            return f"AGGREGATE {instr.input} -> {instr.output} [LABEL {instr.agg_label}]"
        elif isinstance(instr,Assign):
            if instr.arg2 is not None:
                return f"{instr.target} = {instr.arg1} {instr.op} {instr.arg2}"
            elif isinstance(instr.arg1,list):
                args = ", ".join(map(str, instr.arg1))
                return f"{instr.target} = {instr.op}({args})"
            else:
                return f"{instr.target} = {instr.op} {instr.arg1}"
        elif isinstance(instr,Print):
            return f"PRINT {instr.value}"
        elif isinstance(instr,ForBegin):
            return f"FOR {instr.iter_var} IN {instr.table}"
        elif isinstance(instr,ForEnd):
            return "END FOR"
        else:
            return f"UNKNOWN INSTRUCTION {instr}"