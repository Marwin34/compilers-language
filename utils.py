from collections import namedtuple


Variable = namedtuple("Variable", ["type", "value"])

TYPES = ["int", "float", "string", "bool"]
KEYWORDS = ["while", "if", "for", "print", "static_cast"]


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
