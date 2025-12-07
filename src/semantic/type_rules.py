ARITH_TYPES = {"int","float"}

def is_numeric(type_):
    return type_ in ARITH_TYPES

def numeric_compatible(type1,type2):
    return is_numeric(type1) and is_numeric(type2)

def check_binary_expr(left_type,op,right_type):
    if op in ("+","-","*","/","%"):
        if left_type not in ARITH_TYPES or right_type not in ARITH_TYPES:
            raise Exception(f"Type error: '{op}' not supported for {left_type},{right_type}")
        return "float" if "float" in (left_type,right_type) else "int"
    elif op in ("==","!=","<",">","<=",">="):
        if (left_type != right_type) and not numeric_compatible(left_type,right_type):
            raise Exception(f"Type error: '{op} not supported for {left_type},{right_type}")
        return "bool"
    elif op in ("and","or"):
        if left_type != "bool" or right_type != "bool":
            raise Exception(f"Type error: '{op}' requires bool operands")
        return "bool"
    else:
        raise Exception(f"Unknown operator '{op}'")
    
def check_unary_expr(op,operand_type):
    if op == "-" and operand_type in ARITH_TYPES:
        return operand_type
    raise Exception(f"Type error: unary '{op}' not supported for {operand_type}")

def check_aggregrate_function(func_name,arg_type):
    if func_name in ("sum","avg"):
        if arg_type not in ARITH_TYPES:
            raise Exception(f"'{func_name}' requires numeric argument, got '{arg_type}'")
        return "float"
    if func_name == "count":
        return "int"
    raise Exception(f"Unknown function '{func_name}'")