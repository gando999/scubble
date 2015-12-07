from core import (
    Scope, MemorySpace, ASTNode, StructInstance,
    FunctionSpace, ReturnValue
)


global_space = MemorySpace('global')
current_space = global_space

stack = []


class Interpreter(object):

    def __init__(self, parser_scope):
        self.global_scope = parser_scope

    def _get_space_with_symbol(self, iid):
        if stack and iid in stack[0].members.keys():
            return stack[0]
        global global_space
        if iid in global_space.members:
            return global_space
        return None

    def _load(self, node):
        memspace = self._get_space_with_symbol(node.leaf)
        if memspace:
            return memspace.members[node.leaf]
        raise RuntimeError('No such variable {}'.format(node.leaf))

    def _handle_assign(self, node):
        lhs = node.children[0] # ID or QID
        expr = node.children[1]
        value = self.eval(expr)
        if isinstance(lhs, ASTNode) and lhs.type == 'QID':
            base, member = lhs.leaf.split('.')
            # TODO: parser / tree should do this
            baseobj = self._load(ASTNode('ID', leaf=base)) 
            resolved_member = baseobj.ss.resolve_member(member)
            if not resolved_member:
                raise RuntimeError('{} has no field {}'.format(base, member))
            baseobj.members[member] = value
        memspace = self._get_space_with_symbol(lhs.leaf)
        if not memspace: # new definition - use current space
            global current_space
            current_space.members[lhs.leaf] = value

    def _handle_call(self, node):
        funcname = node.children[0]
        symbol = node.scope.resolve(funcname)
        if not symbol:
            raise RuntimeError('No such function {}'.format(funcname))
        fspace = FunctionSpace(symbol)
        global current_space
        savespace = current_space
        current_space = fspace
        args_passed = node.children[1]
        argcount = len(args_passed)
        if argcount != len(symbol.formal_args):
            raise RuntimeError('{} arglist mismatch'.format(funcname))
        for i, argsym in enumerate(symbol.formal_args.values()): 
            ith_arg = args_passed[i]
            arg_value = self.eval(ith_arg)
            fspace.members[argsym.name] = arg_value
        result = None
        stack.insert(0, fspace)
        try:
            for s in symbol.ast_block:
                self.eval(s)
        except ReturnValue as rv:
            result = rv.value
        stack.pop()
        current_space = savespace
        return result

    def eval(self, node):
        if not node:
            return
        if node.type == 'ASSIGN':
            return self._handle_assign(node)
        if node.type == 'INSTANCE':
            name = node.leaf
            struct_symbol = node.scope.resolve(name)
            return StructInstance(struct_symbol)
        if node.type == 'CALL':
            return self._handle_call(node)
        if node.type == 'ID' or node.type == 'QID':
            return self._load(node)
        if node.type == 'PRINT':
            print self.eval(node.leaf)
        if node.type == 'STRING':
            return str(node.leaf)
        if node.type == 'INT':
            return int(node.leaf)
        if node.type == 'RET':
            ReturnValue.value = self.eval(node.leaf)
            raise ReturnValue

    def run(self, program):
        results = []
        if isinstance(program, list):
            for e in program:
                results.append(self.eval(e))
        else:
            results.append(self.eval(program))
        return results
