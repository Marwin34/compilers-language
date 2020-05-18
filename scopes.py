from utils import determine_type, valid_type, not_keyword_or_type, Variable


class Error(Exception):
    pass


class KeyError(Error):
    def __init__(self, message):
        self.message = message


class VariableTypeError(Error):
    def __init__(self, message):
        self.message = message


class AlreadyExist(Error):
    def __init__(self, message):
        self.message = message


class KeywordName(Error):
    def __init__(self, message=""):
        self.message = message


class Scope:
    def __init__(self):
        super().__init__()

        self.names = {}

    def declare(self, v_name, v_type):
        if not not_keyword_or_type(v_name):
            raise KeywordName()

        if v_name in self.names:
            raise AlreadyExist(f"{v_name} already exists.")

        if not valid_type(v_type):
            raise VariableTypeError(f"{v_type} is not valid type.")

        self.names[v_name] = Variable(v_type, None)

    def define(self, v_name, v_value):
        v_type = determine_type(v_value)

        if not not_keyword_or_type(v_name):
            raise KeywordName()

        if v_name in self.names:
            raise AlreadyExist(f"{v_name} already exists.")

        if not valid_type(v_type):
            raise VariableTypeError(f"{v_type} is not valid type.")

        self.names[v_name] = Variable(v_type, v_value)

    def assign(self, v_name, v_value):
        if v_name not in self.names:
            return False

        if self.names[v_name].type != determine_type(v_value):
            raise VariableTypeError(
                f"value {v_value} and type {self.names[v_name][0]} missmatch"
            )

        self.names[v_name] = Variable(self.names[v_name].type, v_value)

        return True

    def get(self, v_name):
        return self.names.get(v_name, None)


class Scopes:
    def __init__(self):
        super().__init__()

        self.scopes_list = []
        self.add_scope() # global scope

    def add_scope(self):
        self.scopes_list.append(Scope())

    def remove_scope(self):
        self.scopes_list.pop()

    def declare(self, v_name, v_type):
        top = len(self.scopes_list) - 1
        try:
            res = self.scopes_list[top].declare(v_name, v_type)
        except (AlreadyExist, VariableTypeError) as e:
            print(e.message)
        except KeywordName:
            pass

        return None

    def define(self, v_name, v_value):
        top = len(self.scopes_list) - 1
        try:
            res = self.scopes_list[top].define(v_name, v_value)
        except (AlreadyExist, VariableTypeError) as e:
            print(e.message)
        except KeywordName:
            pass

        return None

    def assign(self, v_name, v_value):
        top = self.scopes_list[-1]
        bottom = self.scopes_list[0]
        try:
            if top.assign(v_name, v_value):
                return None
        except VariableTypeError as e:
            print(e.message)

        try:
            if bottom.assign(v_name, v_value):
                return None
        except VariableTypeError as e:
            print(e.message)

        print(f"{v_name} not decleared.")

        return None

    def get(self, v_name):
        for scope in reversed(self.scopes_list):
            res = scope.get(v_name)
            if res is not None:
                return res.value

        print(f"{v_name} not decleared.")

        return None

    def available_name(self, name):
        for scope in self.scopes_list:
            if name in scope.names:
                return False

        return not_keyword_or_type(name)
