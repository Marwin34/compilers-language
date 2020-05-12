from abc import ABC, abstractmethod
from collections import namedtuple
import math
import copy

from scopes import Scopes
from utils import determine_type, convert_to, valid_type

functions = {}

function_scopes = {}

nodes_count = 0

scopes = Scopes()


def node_id():
    global nodes_count
    id = f"Node{nodes_count}"
    nodes_count += 1
    return id


class Node(ABC):
    @abstractmethod
    def serve(self):
        pass

    @abstractmethod
    def optimize(self):
        pass

    @abstractmethod
    def draw(self):
        pass

    def __str__(self):
        return node_id()


class Program(Node):
    def __init__(self, block):
        super().__init__()

        self.block = block
        self.id = str(self)

    def serve(self):
        return self.block.serve()

    def optimize(self):
        self.block = self.block.optimize()
        return self

    def draw(self, graph):
        graph.node(self.id, "Program")
        self.block.draw(graph, self.id)


class Block(Node):
    def __init__(self, statements):
        super().__init__()

        self.statements = statements
        self.id = str(self)

    def serve(self):
        value = None

        for statement in self.statements:
            value = statement.serve()

        return value

    def optimize(self):
        new_statements = []
        for statement in self.statements:
            new_statements.append(statement.optimize())

        self.statements = new_statements
        return self

    def draw(self, graph, parent_id):
        graph.node(self.id, "Block")
        graph.edge(parent_id, self.id)

        for statement in self.statements:
            statement.draw(graph, self.id)

    def get_statements(self):
        return self.statements


class UMinus(Node):
    def __init__(self, statement):
        super().__init__()

        self.statement = statement
        self.id = str(self)

    def serve(self):
        return -self.statement.serve()

    def optimize(self):
        self.statement = self.statement.optimize()
        return self

    def draw(self, graph, parent_id):
        graph.node(self.id, "UnaryMinus")
        graph.edge(parent_id, self.id)

        self.statement.draw(graph, self.id)


class Condition(Node):
    def __init__(self, condition, action):
        super().__init__()

        self.condition = condition
        self.action = action
        self.id = str(self)

    def serve(self):
        condition_value = self.condition.serve()
        if type(condition_value) is not bool:
            print(f"Invalid syntax: condition is not a bool type.")
            return None

        if condition_value:
            return self.action.serve()
        else:
            return None

    def optimize(self):
        return self

    def draw(self, graph, parent_id):
        graph.node(self.id, "Condition")
        graph.edge(parent_id, self.id)

        self.condition.draw(graph, parent_id)
        self.action.draw(graph, parent_id)


class While(Node):
    def __init__(self, condition, block):
        super().__init__()

        self.condition = condition
        self.block = block
        self.id = str(self)

    def serve(self):
        value = None

        condition_value = self.condition.serve()
        if type(condition_value) is not bool:
            print(f"Invalid syntax: condition is not a bool type.")
            return value

        while condition_value:
            value = self.block.serve()

            condition_value = self.condition.serve()

        return value

    def optimize(self):
        self.block = self.block.optimize()

        return self

    def draw(self, graph, parent_id):
        graph.node(self.id, "While")
        graph.edge(parent_id, self.id)

        self.condition.draw(graph, self.id)
        self.block.draw(graph, self.id)


class For(Node):
    def __init__(self, init, condition, step, block):
        super().__init__()

        self.init = init
        self.condition = condition
        self.step = step
        self.block = block
        self.id = str(self)

    def serve(self):
        value = None

        self.init.serve()

        condition_value = self.condition.serve()
        if type(condition_value) is not bool:
            print(f"Invalid syntax: condition is not a bool type.")
            return value

        while condition_value:
            self.step.serve()
            value = self.block.serve()

            condition_value = self.condition.serve()

        return value

    def optimize(self):
        self.block = self.block.optimize()
        return self

    def draw(self, graph, parent_id):
        graph.node(self.id, "For")
        graph.edge(parent_id, self.id)

        self.init.draw(graph, self.id)
        self.condition.draw(graph, self.id)
        self.block.draw(graph, self.id)


class Relation(Node):
    def __init__(self, operator, left, right):
        super().__init__()

        self.operator = operator
        self.left = left
        self.right = right
        self.id = str(self)

    def serve(self):
        left = self.left.serve()
        right = self.right.serve()

        if type(left) != type(right):
            print(f"Relation values types missmatch.")
            return None

        if self.operator == ">":
            return left > right
        elif self.operator == "<":
            return left < right
        elif self.operator == ">=":
            return left >= right
        elif self.operator == "<=":
            return left <= right
        elif self.operator == "==":
            return left == right
        elif self.operator == "!=":
            return left != right
        else:
            return False

    def optimize(self):
        self.left = self.left.optimize()
        self.right = self.right.optimize()
        return self

    def draw(self, graph, parent_id):
        graph.node(self.id, "Relation")
        graph.edge(parent_id, self.id)

        self.left.draw(graph, self.id)
        graph.node(self.id + self.operator, self.operator)
        graph.edge(self.id, self.id + self.operator)
        self.right.draw(graph, self.id)


class Operator(Node):
    def __init__(self, operator, left_part, right_part):
        super().__init__()

        self.operator = operator
        self.left_part = left_part
        self.right_part = right_part
        self.optimized = None
        self.id = str(self)

    def serve(self):
        left_part = self.left_part.serve()
        right_part = self.right_part.serve()

        if type(left_part) != type(right_part):
            print(
                f"Operator values types missmatch {type(left_part)}, {type(right_part)}."
            )
            return None

        both_type = determine_type(left_part)

        if self.operator == "+":
            return left_part + right_part

        if both_type == "str":
            print(f"{self.operator} is not available for {both_type}")
            return None

        if self.operator == "-":
            return left_part - right_part
        elif self.operator == "*":
            return left_part * right_part
        elif self.operator == "/":
            return left_part / right_part
        elif self.operator == "^":
            return convert_to(math.pow(left_part, right_part), both_type)
        else:
            print(f"Unsupported operator {self.operator}.")
            return None

    def optimize(self):
        self.left_part = self.left_part.optimize()
        self.right_part = self.right_part.optimize()

        # left_part = self.left_part.serve()
        # right_part = self.right_part.serve()

        # if type(left_part) != type(right_part):
        # return self

        if (
            type(self.left_part) == IntVal or type(self.left_part) == FloatVal
        ) and type(self.right_part) == KeyVal:
            left_part = self.left_part.serve()

            if self.operator == "+":
                if left_part == 0:
                    return self.right_part

            if self.operator == "*":
                if left_part == 0:
                    return self.left_part
                elif left_part == 1:
                    return self.right_part
                elif left_part == 2:
                    return Operator("+", self.right_part, self.right_part)

            if self.operator == "^":
                if left_part == 0 or left_part == 1:
                    return self.left_part

        if type(self.left_part) == KeyVal and (
            type(self.right_part) == IntVal or type(self.right_part) == FloatVal
        ):
            right_part = self.right_part.serve()

            if self.operator == "+":
                if right_part == 0:
                    return self.right_part

            if self.operator == "-":
                if right_part == 0:
                    return self.left_part

            if self.operator == "*":
                if right_part == 0:
                    return self.right_part
                elif right_part == 1:
                    return self.left_part
                elif right_part == 2:
                    return Operator("+", self.left_part, self.left_part)

            if self.operator == "/":
                if right_part == 1:
                    return self.left_part
                elif right_part == 2:
                    return Operator("*", self.left_part, 0.5)

            if self.operator == "^":
                if right_part == 0:
                    return self.IntVal(1)
                elif right_part == 1:
                    return self.left_part
                elif right_part == 2:
                    return Operator("*", self.left_part, self.left_part)

        if type(self.left_part) == IntVal and type(self.right_part) == IntVal:
            left_part = self.left_part.serve()
            right_part = self.right_part.serve()

            if self.operator == "+":
                return IntVal(left_part + right_part)

            if self.operator == "-":
                return IntVal(left_part - right_part)

            if self.operator == "*":
                return IntVal(left_part * right_part)

        if type(self.left_part) == FloatVal and type(self.right_part) == FloatVal:
            left_part = self.left_part.serve()
            right_part = self.right_part.serve()

            if self.operator == "+":
                return FloatVal(left_part + right_part)

            if self.operator == "-":
                return FloatVal(left_part - right_part)

            if self.operator == "*":
                return FloatVal(left_part * right_part)

            if self.operator == "/":
                return FloatVal(left_part / right_part)

        return self

    def draw(self, graph, parent_id):
        graph.node(self.id, "Operator")
        graph.edge(parent_id, self.id)

        if self.optimized is not None:
            self.optimized.draw(graph, self.id)
        else:
            self.left_part.draw(graph, self.id)
            graph.node(self.id + self.operator, self.operator)
            graph.edge(self.id, self.id + self.operator)
            self.right_part.draw(graph, self.id)


class Print(Node):
    def __init__(self, statement):
        super().__init__()

        self.statement = statement
        self.id = str(self)

    def serve(self):
        value = self.statement.serve()
        print(value)
        return None

    def optimize(self):
        self.statement = self.statement.optimize()
        return self

    def draw(self, graph, parent_id):
        graph.node(self.id, "Print")
        graph.edge(parent_id, self.id)

        self.statement.draw(graph, self.id)


class Assign(Node):
    def __init__(self, name, value):
        super().__init__()

        self.name = name
        self.value = value
        self.id = str(self)

    def serve(self):
        value = self.value.serve()
        name = self.name.serve()

        scopes.assign(name, value)

        return None

    def optimize(self):
        self.value = self.value.optimize()
        return self

    def draw(self, graph, parent_id):
        graph.node(self.id, "Assign")
        graph.edge(parent_id, self.id)

        self.name.draw(graph, self.id)
        self.value.draw(graph, self.id)


class TypeDeclare(Node):
    def __init__(self, name, type_name):
        super().__init__()

        self.name = name
        self.type_name = type_name
        self.id = str(self)

    def serve(self):
        name = self.name.serve()
        type_name = self.type_name.serve()

        scopes.declare(name, type_name)

        return None

    def optimize(self):
        return self

    def draw(self, graph, parent_id):
        graph.node(self.id, "TypeDeclare")
        graph.edge(parent_id, self.id)

        self.name.draw(graph, self.id)
        self.type_name.draw(graph, self.id)


class AssignWithType(Node):
    def __init__(self, name, value):
        super().__init__()

        self.name = name
        self.value = value
        self.id = str(self)

    def serve(self):
        name = self.name.serve()
        value = self.value.serve()

        scopes.define(name, value)

        return None

    def optimize(self):
        self.value = self.value.optimize()
        return self

    def draw(self, graph, parent_id):
        graph.node(self.id, "AssignmentWithType")
        graph.edge(parent_id, self.id)

        self.name.draw(graph, self.id)
        self.value.draw(graph, self.id)


class Cast(Node):
    def __init__(self, value, type_name):
        super().__init__()

        self.value = value
        self.type_name = type_name
        self.id = str(self)

    def serve(self):
        type_name = self.type_name.serve()
        if type_name is None:
            return None

        value = self.value.serve()

        new_val = convert_to(value, type_name)

        return new_val

    def optimize(self):
        return self

    def draw(self, graph, parent_id):
        graph.node(self.id, "Cast")
        graph.edge(parent_id, self.id)

        self.value.draw(graph, self.id)
        self.type_name.draw(graph, self.id)


class Args(Node):
    def __init__(self, arguments):
        super().__init__()

        self.arguments = arguments
        self.id = str(self)

    def serve(self):
        parsed_arguments = []
        for argument in self.arguments:
            argument_name = argument[0].serve()
            argument_type = argument[1].serve()

            if argument_name is None or argument_type is None:
                print(f"Bad argument declaration.")
                return None

            parsed_arguments.append((argument_name, argument_type))

        return parsed_arguments

    def optimize(self):
        return self

    def draw(self, graph, parent_id):
        graph.node(self.id, "Arguments")
        graph.edge(parent_id, self.id)

        for i, argument in enumerate(self.arguments, 1):
            graph.node(self.id + f"arg_{i}", f"Arg {i}")
            graph.edge(self.id, self.id + f"arg_{i}")

            argument[0].draw(graph, self.id + f"arg_{i}")
            argument[1].draw(graph, self.id + f"arg_{i}")

    def get_arguments(self):
        return self.arguments


class ArgsVal(Node):
    def __init__(self, arguments):
        super().__init__()

        self.arguments = arguments
        self.id = str(self)

    def serve(self):
        values = []

        for argument in self.arguments:
            values.append(argument.serve())

        return values

    def optimize(self):
        new_arguments = []

        for argument in self.arguments:
            new_arguments.append(argument.optimize())

        self.arguments = new_arguments
        return self

    def draw(self, graph, parent_id):
        graph.node(self.id, "ArgsValues")
        graph.edge(parent_id, self.id)

        for argument in self.arguments:
            argument.draw(graph, self.id)

    def get_arguments(self):
        return self.arguments


class Function(Node):
    def __init__(self, name, args, block):
        super().__init__()

        self.name = name
        self.args = args
        self.block = block
        self.id = str(self)

    def serve(self):
        name = self.name.serve()

        if not scopes.available_name(name):
            print(f"{name} already exist.")
        else:
            args = self.args.serve()

            if args is None:
                print(f"Error in function definition {name}.")
                return None

            functions[name] = {"args": args, "block": self.block}
            return None

    def optimize(self):
        self.block = self.block.optimize()
        return self

    def draw(self, graph, parent_id):
        graph.node(self.id, "FunctionDefinition")
        graph.edge(parent_id, self.id)

        self.name.draw(graph, self.id)
        self.args.draw(graph, self.id)
        self.block.draw(graph, self.id)


class Call(Node):
    def __init__(self, name, args):
        super().__init__()

        self.name = name
        self.args = args
        self.id = str(self)

    def serve(self):
        name = self.name.serve()
        if name not in functions:
            print(f"Function {name} not defined!")
            return None
        else:
            function = functions[name]

            args_val = self.args.serve()
            if len(args_val) != len(function["args"]):
                print(f"Arguments count missmatch in function {name}.")
                return None
            else:
                scopes.add_scope()
                valid_args = True
                res = None

                for i in range(len(args_val)):
                    arg_name = function["args"][i][0]
                    arg_type = function["args"][i][1]
                    arg_value = args_val[i]
                    given_arg_type = determine_type(arg_value)

                    arg_value = convert_to(arg_value, arg_type)

                    scopes.define(arg_name, arg_value)

                if valid_args:
                    res = function["block"].serve()

                scopes.remove_scope()

                return res

    def optimize(self):
        return self

    def draw(self, graph, parent_id):
        graph.node(self.id, "Call")
        graph.edge(parent_id, self.id)

        self.name.draw(graph, self.id)
        self.args.draw(graph, self.id)


class FloatVal(Node):
    def __init__(self, value):
        super().__init__()

        self.value = value
        self.id = str(self)

    def serve(self):
        return float(self.value)

    def optimize(self):
        return self

    def draw(self, graph, parent_id):
        graph.node(self.id, "Float")
        graph.node(self.id + "val", str(self.value))
        graph.edge(parent_id, self.id)
        graph.edge(self.id, self.id + "val")


class IntVal(Node):
    def __init__(self, value):
        super().__init__()

        self.value = value
        self.id = str(self)

    def serve(self):
        return int(self.value)

    def optimize(self):
        return self

    def draw(self, graph, parent_id):
        graph.node(self.id, "Int")
        graph.node(self.id + "val", str(self.value))
        graph.edge(parent_id, self.id)
        graph.edge(self.id, self.id + "val")


class StringVal(Node):
    def __init__(self, value):
        super().__init__()

        self.value = value[1:-1]
        self.id = str(self)

    def serve(self):
        return self.value

    def optimize(self):
        return self

    def draw(self, graph, parent_id):
        graph.node(self.id, "String")
        graph.node(self.id + "val", self.value)
        graph.edge(parent_id, self.id)
        graph.edge(self.id, self.id + "val")


class NameVal(Node):
    def __init__(self, name):
        super().__init__()

        self.name = name
        self.id = str(self)

    def serve(self):
        return self.name

    def optimize(self):
        return self

    def draw(self, graph, parent_id):
        graph.node(self.id, "Name")
        graph.node(self.id + "val", self.name)
        graph.edge(parent_id, self.id)
        graph.edge(self.id, self.id + "val")


class KeyVal(Node):
    def __init__(self, key):
        super().__init__()

        self.key = key
        self.id = str(self)

    def serve(self):
        return scopes.get(self.key)

    def optimize(self):
        return self

    def draw(self, graph, parent_id):
        graph.node(self.id, "Variable")
        graph.node(self.id + "val", self.key)
        graph.edge(parent_id, self.id)
        graph.edge(self.id, self.id + "val")


class TypeVal(Node):
    def __init__(self, type_name):
        super().__init__()

        self.type_name = type_name
        self.id = str(self)

    def serve(self):
        if valid_type(self.type_name):
            return self.type_name
        else:
            print(f"{self.type_name} is not valid type!")

        return None

    def optimize(self):
        return self

    def draw(self, graph, parent_id):
        graph.node(self.id, "Type")
        graph.node(self.id + "type", self.type_name)

        graph.edge(parent_id, self.id)
        graph.edge(self.id, self.id + "type")


class BoolVal(Node):
    def __init__(self, value):
        super().__init__()

        self.value = True if value == "true" else False
        self.id = str(self)

    def serve(self):
        return self.value

    def optimize(self):
        return self

    def draw(self, graph, parent_id):
        graph.node(self.id, "Bool")
        graph.node(self.id + "bool", str(self.value))

        graph.edge(parent_id, self.id)
        graph.edge(self.id, self.id + "bool")