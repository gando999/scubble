class ReturnValue(Exception):
    """
    Return value for function calls

    """
    value = None


class ASTNode(object):
    """
    Node to represent an operation in the AST

    """
    def __init__(self, ntype, children=None, leaf=None):
        self.type = ntype
        self.children = children if children else []
        self.leaf = leaf
        self.scope = None
        self.tree = None

    def __str__(self):
        return ' Type [{}], Scope {}, leaf={} children=[{}] '.format(
            self.type, self.scope,
            self.leaf, ''.join([str(x) for x in self.children])
        )


class ScopedSymbol(object):
    """
    Base class for symbols

    """

    def __init__(self, name, enclosing_scope):
        self.name = name
        self.scope = None
        self.enclosing_scope = enclosing_scope

    def define(self, symbol):
        self.get_members()[symbol.name] = symbol
        symbol.scope = self

    def resolve(self, name):
        symbol = self.get_members()[name]
        if symbol is not None:
            return symbol
        if self.get_parent_scope():
            return self.get_parent_scope().resolve(name)
        return None

    def get_members(self):
        raise NotImplementedError()

    def resolve_member(self, name):
        return self.fields[name]

    def get_parent_scope(self):
        return self.enclosing_scope


class StructSymbol(ScopedSymbol):
    """
    Represents context for defining a structure

    """
    
    def __init__(self, name, parent_scope):
        super(StructSymbol, self).__init__(name, parent_scope)
        self.fields = {}

    def resolve_member(self, name):
        try:
            return self.fields[name]
        except KeyError:
            return None

    def get_members(self):
        return self.fields

    def __str__(self):
        return '{}, {}'.format(self.name, self.fields)


class FunctionSymbol(ScopedSymbol):
    """
    Represents context for defining a function

    """

    def __init__(self, name, parent_scope):
        super(FunctionSymbol, self).__init__(name, parent_scope)
        self.ast_block = None
        self.formal_args = {}

    def get_members(self):
        return self.formal_args

    def __str__(self):
        return '{} {}'.format(self.name, self.formal_args)


class VariableSymbol(object):
    """
    Represents context for defining a variable

    """

    def __init__(self, name):
        self.name = name
        self.scope = None

    def __str__(self):
        return '{} {}'.format(self.name, self.scope)


class Scope(object):
    """
    A scope holds symbols

    """

    def __init__(self, parent_scope=None):
        self.enclosing_scope = parent_scope
        self.symbols = {}

    def resolve(self, name):
        s = self.symbols[name]
        if s:
            return s
        if self.get_parent_scope():
            return self.get_parent_scope.resolve(name)
        return None

    def define(self, symbol):
        self.symbols[symbol.name] = symbol
        symbol.scope = self

    def get_parent_scope(self):
        return self.enclosing_scope
        
    def __str__(self):
        return str(self.symbols.keys())


class LocalScope(Scope):
    """
    A local scope has a parent

    """

    def __init__(self, parent_scope=None):
        super(LocalScope, self).__init__(parent_scope)


class MemorySpace(object):
    """
    A context for defining specific values for execution.
    Every executing program has a global space
    
    """

    def __init__(self, name):
        self.name = name
        self.members = {}


class FunctionSpace(MemorySpace):
    """
    A context where data for specific function evaluation
    is held.
    
    """

    def __init__(self, func_symbol):
        super(FunctionSpace, self).__init__(func_symbol.name)
        self.symbol = func_symbol # the function we are executing
        

# Should this really inherit from a space?
class StructInstance(MemorySpace):
    """
    Underlying implementation of a struct

    """

    def __init__(self, struct_symbol):
        super(StructInstance, self).__init__(struct_symbol.name)
        self.ss = struct_symbol

    def __str__(self):
        return '<struct>{} fields {} values {}'.format(
            self.name, self.ss.get_members().keys(),
            self.members
        )
