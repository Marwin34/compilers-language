import math
from collections import namedtuple


Variable = namedtuple("Variable", ["type", "value"])

TYPES = ["int", "float", "string", "bool"]
KEYWORDS = [
    "while",
    "if",
    "for",
    "print",
    "static_cast",
    "sin",
    "cos",
    "exp",
    "sqrt",
    "log",
    "PI",
]

math_functions = {
    "sin": math.sin,
    "cos": math.cos,
    "exp": math.exp,
    "sqrt": math.sqrt,
    "log": math.log,
}

pi = math.pi


def valid_type(type_name):
    return type_name in TYPES


def determine_type(value):
    if type(value) is int:
        return TYPES[0]
    elif type(value) is float:
        return TYPES[1]
    elif type(value) is str:
        return TYPES[2]
    elif type(value) is bool:
        return TYPES[3]
    else:
        return None


def not_keyword_or_type(name):
    if name.lower() in KEYWORDS:
        print(f"{name} is a keyword.")
        return False

    if name.lower() in TYPES:
        print(f"{name} is a type.")
        return False

    return True


def convert_to(value, type_name):
    if type_name == TYPES[0]:
        return int(value)
    elif type_name == TYPES[1]:
        return float(value)
    elif type_name == TYPES[2]:
        return str(value)
    elif type_name == TYPES[3]:
        return bool(value)
    else:
        return None


def evaluate(name, value):
    return math_functions[name](value)


def type_to_string(var):
    type_of_var = type(var).__name__
    if type_of_var == int.__name__:
        return "IntVal"
    elif type_of_var == float.__name__:
        return "FloatVal"
    elif type_of_var == str.__name__:
        return "StringVal"
    elif type_of_var == bool.__name__:
        return "BoolVal"
    else:
        return "Unknown type"
