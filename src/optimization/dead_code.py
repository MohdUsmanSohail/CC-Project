from typing import Iterable, Set, List, Any
from src.icg.ir import *

def _collect_names_from_value(val: Any) -> Set[str]:
    names: Set[str] = set()

    if val is None:
        return names

    # Only treat temp variables as "names" DCE cares about.
    # Column names ("salary", "bonus", "name") must NOT be treated as variable dependencies.
    if isinstance(val, str):
        if val.startswith("t"):  # temp name like t1, t2, ...
            names.add(val)
        return names

    if isinstance(val, (list, tuple, set)):
        for e in val:
            names.update(_collect_names_from_value(e))
        return names

    if isinstance(val, dict):
        for k, v in val.items():
            names.update(_collect_names_from_value(k))
            names.update(_collect_names_from_value(v))
        return names

    return names



class DeadCodeEliminator:
    def __init__(self,instructions: List[IRInstruction]):
        self.insructions = list(instructions)
    
    def _is_block_assign(self, idx: int) -> bool:
        if idx == 0:
            return False

        prev = self.insructions[idx - 1]

        if isinstance(prev, Assign) and self._is_block_assign(idx - 1):
            return True

        return isinstance(prev, (Filter, Map, Aggregate))

    """def _is_block_assign(self, idx: int) -> bool:
        if idx == 0:
            return False
        prev = self.insructions[idx - 1]
        return isinstance(prev, (Filter, Map, Aggregate))"""

    def eliminate(self) -> List[IRInstruction]:
        used = self._find_used()
        new_instructions = []

        for idx,instr in enumerate(self.insructions):
            if isinstance(instr,Assign) and self._is_block_assign(idx):
                new_instructions.append(instr)
                continue
            
            if isinstance(instr,Assign):
                if instr.target in used:
                    new_instructions.append(instr)
                    continue

                if isinstance(instr.op,str) and instr.op.startswith("call "):
                    call_name = instr.op[len("call "):]
                    if call_name in used:
                        new_instructions.append(instr)
                        continue
            else:
                new_instructions.append(instr)
        
        return new_instructions
    
    def _find_used(self) -> Set[str]:
        used: Set[str] = set()

        fragment_names: Set[str] = set()
        produced_tables: Set[str] = set()

        for instr in self.insructions:
            if isinstance(instr, FunctionFragment):
                fragment_names.add(instr.name)

            if isinstance(instr, LoadTable):
                produced_tables.add(getattr(instr, "target", None))

            if isinstance(instr, Map):
                produced_tables.add(getattr(instr, "output", None))
                lbl = getattr(instr, "map_label", None)
                if isinstance(lbl, str):
                    used.add(lbl)

            if isinstance(instr, Filter):
                produced_tables.add(getattr(instr, "output", None))
                lbl = getattr(instr, "predicate_label", None)
                if isinstance(lbl, str):
                    used.add(lbl)
                temp = getattr(instr, "predicate_temp", None)
                if isinstance(temp, str):
                    used.add(temp)

            if isinstance(instr, Aggregate):
                produced_tables.add(getattr(instr, "output", None))
                lbl = getattr(instr, "agg_label", None)
                if isinstance(lbl, str):
                    used.add(lbl)


        used.update([t for t in produced_tables if isinstance(t, str)])

        for instr in self.insructions:
            if isinstance(instr, Assign):
                used.update(_collect_names_from_value(instr.arg1))
                used.update(_collect_names_from_value(instr.arg2))
                if isinstance(instr.op, str) and instr.op.startswith("call "):
                    fname = instr.op[len("call "):]
                    used.add(fname)

            elif isinstance(instr, Print):
                used.update(_collect_names_from_value(instr.value))

            elif isinstance(instr, ForBegin):
                if getattr(instr, "table", None):
                    used.update(_collect_names_from_value(instr.table))
                if getattr(instr, "iter_var", None):
                    used.add(instr.iter_var)

            elif isinstance(instr, FunctionFragment):
                frag_used = DeadCodeEliminator(instr.body)._find_used()
                used.update(frag_used)

            elif isinstance(instr, (Filter, Map, Aggregate)):
                for field in ("input", "output", "predicate_label", "map_label", "agg_label"):
                    if hasattr(instr, field):
                        used.update(_collect_names_from_value(getattr(instr, field)))

            else:
                for attr in ("arg1", "arg2", "value", "target", "input", "output"):
                    if hasattr(instr, attr):
                        used.update(_collect_names_from_value(getattr(instr, attr)))

        for fname in fragment_names:
            if fname in used:
                used.add(fname)

        return used
