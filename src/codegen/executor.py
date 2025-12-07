import pandas as pd
from typing import Any, Dict, List
from src.icg.ir import *

class Executor:
    def __init__(self,instructions: List[IRInstruction],verbose: bool = False):
        self.instructions = instructions
        self.verbose = verbose

        self.tables: Dict[str, pd.DataFrame] = {}
        self.env: Dict[str,Any] = {}
        self.loop_stack: List[Dict[str,Any]] = []

    def _is_block_assign(self,instr:IRInstruction) -> bool:
        if not isinstance(instr,Assign):
            return False
        
        idx = self.instructions.index(instr)
        if idx == 0:
            return False
        
        prev = self.instructions[idx - 1]
        return isinstance(prev,(Filter,Map,Aggregate))
    
    def _is_inside_for_body(self, instr: IRInstruction) -> bool:
        idx = self.instructions.index(instr)
        depth = 0
        for j in range(idx - 1, -1, -1):
            prev = self.instructions[j]
            if isinstance(prev, ForEnd):
                depth += 1
            elif isinstance(prev, ForBegin):
                if depth == 0:
                    return True
                else:
                    depth -= 1
        return False

    def run(self):
        skip_for_body = False

        for instr in self.instructions:
            if isinstance(instr, Assign) and self._is_block_assign(instr):
                continue

            if isinstance(instr, ForBegin):
                skip_for_body = True
                if self.verbose:
                    print(f"[EXEC] {instr}")
                self.exec_for_begin(instr)
                continue

            if isinstance(instr, ForEnd):
                skip_for_body = False
                continue

            if skip_for_body:
                continue

            if self.verbose:
                print(f"[EXEC] {instr}")
            self.execute_instruction(instr)


    '''def run(self):
        for instr in self.instructions:
            if isinstance(instr,Assign) and self._is_block_assign(instr):
                continue

            if self._is_inside_for_body(instr) and not isinstance(instr,ForBegin):
                continue

            if self.verbose:
                print(f"[EXEC] {instr}")
            self.execute_instruction(instr)'''

    def execute_instruction(self,instr:IRInstruction):
        if isinstance(instr,LoadTable):
            self.exec_load_table(instr)
        elif isinstance(instr,Filter):
            self.exec_filter(instr)
        elif isinstance(instr,Map):
            self.exec_map(instr)
        elif isinstance(instr,Aggregate):
            self.exec_aggregate(instr)
        elif isinstance(instr,ForBegin):
            self.exec_for_begin(instr)
        elif isinstance(instr,Print):
            self.exec_print(instr)
        elif isinstance(instr,Assign):
            self.exec_assign(instr)
        elif isinstance(instr,(ForEnd,Label,Return,FunctionFragment)):
            return
        else:
            raise Exception(f"Unknown IR instruction {instr}")

    def _collect_assigns(self,start_instr):
        idx = self.instructions.index(start_instr)
        assigns = []
        j = idx + 1
        while j < len(self.instructions):
            instr = self.instructions[j]
            if not isinstance(instr,Assign):
                break
            assigns.append(instr)
            j += 1

        return assigns

    def exec_load_table(self,instr: LoadTable):
        df = pd.read_csv(instr.source)
        self.tables[instr.target] = df

    def exec_filter(self,instr: Filter):
        input_df = self.tables.get(instr.input)
        if input_df is None:
            raise Exception(f"Filter: unknown input table '{instr.input}'")
        
        assigns = self._collect_assigns(instr)
        predicate_temp = instr.predicate_temp

        output_rows = []

        for _,row in input_df.iterrows():
            saved_env = dict(self.env)

            self.env["row"] = row
            for col in input_df.columns:
                self.env[col] = self._resolve_value(row[col])

            for a in assigns:
                self.exec_assign(a)

            if bool(self.env.get(predicate_temp,False)):
                output_rows.append(row)

            self.env = saved_env

        self.tables[instr.output] = (
            pd.DataFrame(output_rows) if output_rows else input_df.iloc[0:0].copy()
        )

    def exec_map(self,instr: Map):
        input_df = self.tables.get(instr.input)
        if input_df is None:
            raise Exception(f"Map: unknown input table '{instr.input}'")
        
        assigns = self._collect_assigns(instr)

        new_rows = []

        for _,row in input_df.iterrows():
            saved_env = dict(self.env)

            self.env["row"] = row
            for col in input_df.columns:
                self.env[col] = self._resolve_value(row[col])

            new_row = dict(row)

            for a in assigns:
                self.exec_assign(a)

            for name,value in self.env.items():
                if not self._is_temp(name) and name not in input_df.columns:
                    new_row[name] = value

            new_rows.append(new_row)
            self.env = saved_env

        self.tables[instr.output] = pd.DataFrame(new_rows)

    def exec_aggregate(self,instr: Aggregate):
        input_df = self.tables.get(instr.input)
        if input_df is None:
            raise Exception(f"Aggregate: unknown input table '{instr.input}'")
        assigns = self._collect_assigns(instr)
        
        result = {}

        for a in assigns:
            func = a.op
            arg = a.arg1

            if isinstance(arg,str) and arg in input_df.columns:
                series = input_df[arg]
                if func == "sum":
                    result[a.target] = series.sum()
                elif func == "avg":
                    result[a.target] = series.mean()
                elif func == "count":
                    result[a.target] = len(series)
            else:
                val = self._resolve_value(arg)
                if func == "count":
                    result[a.target] = len(input_df)
                elif func in ("sum","avg"):
                    result[a.target] = float(val)
        
        self.tables[instr.output] = pd.DataFrame([result])

    def exec_for_begin(self,instr:ForBegin):
        table = self.tables.get(instr.table)
        if table is None:
            raise Exception(f"For: unknown input table '{instr.table}'")

        idx = self.instructions.index(instr)
        body = []
        depth = 0

        for j in range(idx + 1,len(self.instructions)):
            i2 = self.instructions[j]
            if isinstance(i2, ForBegin):
                depth += 1
            elif isinstance(i2,ForEnd):
                if depth == 0:
                    break
                else:
                    depth -= 1
            body.append(i2)

        for _,row in table.iterrows():
            saved_env = dict(self.env)
            self.env[instr.iter_var] = row
            self.env["row"] = row

            for bi in body:
                if not isinstance(bi,ForEnd):
                    self.execute_instruction(bi)
            
            self.env = saved_env

    def exec_print(self,instr:Print):
        val = instr.value

        if isinstance(val, str) and val in self.tables:
            print(self.tables[val])
            return

        print(self._resolve_value(val))

    def exec_assign(self,instr:Assign):
        op = instr.op
        a1 = instr.arg1
        a2 = instr.arg2

        if isinstance(op,str) and op.startswith("call "):
            fn = op[len("call "):]
            args = a1 if isinstance(a1,list) else [a1]
            args = [self._resolve_value(x) for x in args]
            self.env[instr.target] = self._call_function(fn,args)
            return
        
        if op == ".":
            base = self._resolve_value(a1)
            key = a2
            self.env[instr.target] = self._resolve_value(base[key])
            return
        
        if a2 is not None:
            left = self._resolve_value(a1)
            right = self._resolve_value(a2)
            self.env[instr.target] = self._apply_binary_op(op,left,right)
            return
        
        if op == "-":
            self.env[instr.target] = -self._resolve_value(a1)
            return
        
        self.env[instr.target] = self._resolve_value(a1)

    def _resolve_value(self, v):
        if isinstance(v, str) and v in self.env:
            return self.env[v]

    
        if isinstance(v, str):
            try:
                if "." in v:
                    return float(v)
                return int(v)
            except:
                return v

        return v

    def _apply_binary_op(self,op,l,r):
        l = self._resolve_value(l)
        r = self._resolve_value(r)

        if op == "+": return l + r
        if op == "-": return l - r
        if op == "*": return l * r
        if op == "/": return l / r
        if op == "==": return l == r
        if op == "!=": return l != r
        if op == ">": return l > r
        if op == "<": return l < r
        if op == ">=": return l >= r
        if op == "<=": return l <= r
        raise Exception(f"Unknown operator '{op}'")
    
    def _call_function(self,fn,args):
        if fn == "sum": return sum(args)
        if fn == "avg": return sum(args) / len(args) if args else 0
        if fn == "count": return len(args)
        raise Exception(f"Unknown function '{fn}'")
    
    def _is_temp(self,name):
        return isinstance(name,str) and name.startswith("t")