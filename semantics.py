# TODO: split in multiple files

class Node(object):
    def __init__(self, node_type):
        self.type = node_type
        self.parent = None
        self._children = []

    def add_child(self, child):
        self._children.append(child)
        if isinstance(child, Node): # TODO: remove check when finished
            child.parent = self

    def add_children(self, children):
        for child in children:
            self.add_child(child)

    # TODO: incapsulate scopes traversal
    def getvar(self, name):
        parent = self.parent
        while parent is not None:
            if isinstance(parent, ScopeNode) and name in parent.scope:
                value = self._getvar(parent.scope, name)
                return value
            parent = parent.parent
        raise UndeclaredVariableError(name)

    def iterchildren(self):
        for child in self._children:
            yield child

    def __repr__(self):
        return self.type

    def _getvar(self, scope, name):
        value = scope[name]
        if value is not None:
            return value
        return UndefinedValue()


# Control flow nodes


class LanguageItemNode(Node):
    TYPES = ['boolean', 'number', 'string', 'any']

    def ensure_func_types(self, func):
        self.ensure_type(func.return_type)
        for param in func.params:
            self.ensure_type(param.type)

    def ensure_type(self, type_name):
        if type_name in self.TYPES:
            return
        var = self.getvar(type_name)
        if not isinstance(var.value, ClassValue):
            # TODO: use separate error for types
            raise UndeclaredVariableError(type_name)

    def run(self):
        raise NotImplementedError()

    def setvar(self, name, value):
        node = self
        while node is not None:
            if isinstance(node, ScopeNode):
                self._setvar(scope, name, value)
                return
            node = node.parent
        raise Exception('Cannot find a parent scope')

    def _setvar(self, scope, name, value):
        typecheck(value, var.type)
        var.value = value


class ScopeNode(LanguageItemNode):
    def __init__(self, statements):
        super(ScopeNode, self).__init__('block')
        self.scope = {}
        for statement in statements:
            self.add_child(statement)

    def run(self):
        for child in self._children:
            child.run()

    def update_scope(self, scope):
        self.scope.update(scope)


class VariableAssignmentNode(LanguageItemNode):
    def __init__(self, name, expression):
        super(VariableAssignmentNode, self).__init__('variable assignment')
        self._name = name
        self.add_child(expression)

    def run(self):
        value = self._children[0].calculate()
        var = self.getvar(self._name)
        typecheck(value, var.type)
        var.value = value


class DeclaredVariableAssignmentNode(VariableAssignmentNode):
    def __init__(self, var_decl, expression):
        name = var_decl.var.name
        super(DeclaredVariableAssignmentNode, self).__init__(name, expression)
        self.add_child(var_decl)

    def run(self):
        self._children[1].run()
        super(DeclaredVariableAssignmentNode, self).run()


class MemberAssignmentNode(LanguageItemNode):
    def __init__(self, member_node, expression):
        super(MemberAssignmentNode, self).__init__('member assignment')
        self.add_child(member_node)
        self.add_child(expression)

    def run(self):
        member_node = self._children[0]
        member_node_child = next(iter(member_node.iterchildren()))
        obj = member_node_child.calculate().obj()
        obj[member_node.name] = self._children[1].calculate()


class FunctionDeclarationNode(LanguageItemNode):
    def __init__(self, func):
        super(FunctionDeclarationNode, self).__init__('function declaration')
        self.func = func

    def run(self):
        name = self.func.name
        func_type = self.func.gettype()
        var = Variable(name, func_type, self.func)
        self.setvar(name, var)


class ReturnNode(LanguageItemNode):
    def __init__(self, expression):
        super(ReturnNode, self).__init__('return statement')
        self.add_child(expression)

    def run(self):
        # TODO: check if in function
        result = self._children[0].calculate()
        raise _Return(result)


class ClassDeclarationNode(LanguageItemNode):
    def __init__(self, name, members):
        super(ClassDeclarationNode, self).__init__('class declaration')
        self.cls = ClassValue(name, members)
        self._name = name

    def run(self):
        class_type = self.cls.gettype()
        var = Variable(self._name, class_type, self.cls)
        self.setvar(self.name, var)


class PrintNode(LanguageItemNode):
    def __init__(self, expression):
        super(PrintNode, self).__init__('print statement')
        self.add_child(expression)

    def run(self):
        print self._children[0].calculate().str()


class IfNode(LanguageItemNode):
    def __init__(self, condition, block):
        super(IfNode, self).__init__('if statement')
        self.add_child(condition)
        self.add_child(block)

    def add_else(self, block):
        if len(self._children) == 2:
            self.add_child(block)
        else:
            raise Exception("Trying to add 'else' block when it already exists")

    def run(self):
        if self._children[0].calculate().bool():
            self._children[1].run()
        else:
            if len(self._children) == 3:
                self._children[2].run()


class WhileLoopNode(LanguageItemNode):
    def __init__(self, condition, block):
        super(WhileLoopNode, self).__init__('while loop')
        self.add_child(condition)
        self.add_child(block)

    def run():
        while self._children[0].calculate().bool():
            self._children[1].run()


class VariableDeclarationNode(LanguageItemNode):
    def __init__(self, var):
        super(VariableDeclarationNode, self).__init__('variable declaration')
        self.var = var

    def run(self):
        self.ensure_type(var.type)
        var.value = None
        self.setvar(var.name, var)


# Expression nodes


class ExpressionNode(Node):
    def calculate(self):
        raise NotImplementedError()


class PrimitiveValueExpression(ExpressionNode):
    def __init__(self, value):
        super(PrimitiveValueExpression, self).__init__('primitive value')
        self._value = value

    def calculate(self):
        return self._value


class VariableExpression(ExpressionNode):
    def __init__(self, name):
        super(VariableExpression, self).__init__('variable')
        self._name = name

    def calculate(self):
        return self.getvar(name).value


class NegateExpression(ExpressionNode):
    def __init__(self, expression):
        super(NegateExpression, self).__init__('boolean negation')
        self.add_child(expression)

    def calculate(self):
        value = self._children[0].calculate()
        bool_result = not value.bool()
        return BooleanValue(bool_result)


class NegativeExpression(ExpressionNode):
    def __init__(self, expression):
        super(NegateExpression, self).__init__('negation')
        self.add_child(expression)

    def calculate(self):
        value = self._children[0].calculate()
        num_result = -value.num()
        return NumberValue(num_result)


class MemberAccessessExpression(ExpressionNode):
    def __init__(self, operand, name):
        super(MemberAccessessExpression, self).__init__('member access')
        self.add_child(operand)
        self.name = name

    def calculate(self):
        value = self._children[0].calculate()
        obj = value.obj()
        return obj[self.name]


class FunctionCallExpression(ExpressionNode):
    def __init__(self, name, params):
        super(FunctionCallExpression, self).__init__('function call')
        self.name = name
        self.add_children(params)

    def calculate(self):
        values = [child.calculate() for child in self._children]
        func = self.getvar(self._name).value
        if not isinstance(func, FunctionValue):
            raise NotAFunctionError(self._name)
        return func.call(values)


class NewInstanceExpression(ExpressionNode):
    # TODO: extract common parts with FunctionCallExpression
    def __init__(self, func_call):
        super(NewInstanceExpression, self).__init__('new instance')
        self._name = func_call.name
        self.add_children(func_call.iterchildren())

    def calculate(self):
        cls = self.getvar(self._name).value
        if not isinstance(cls, ClassValue):
            # TODO: different error for classes?
            raise NotAFunctionError(self._name)
        params = [child.calculate() for child in self._children]
        return cls.instantiate(params)


class ThisExpression(ExpressionNode):
    def __init__(self):
        super(ThisExpression, self).__init__('this')

    def calculate(self):
        # TODO: find current this
        pass


# Values


class LanguageValue(object):
    def bool(self):
        raise NotImplementedError()

    def num(self):
        raise NotImplementedError()

    def obj(self):
        # TODO: add wrappers for primitives
        raise NotImplementedError()

    def str(self):
        raise NotImplementedError()

    def __repr__(self):
        return self.str()


class LanguageContainerValue(LanguageValue):
    def __init__(self, value):
        self.value = value

    def bool(self):
        return bool(self.value)

    def str(self):
        return str(self.value)


class BooleanValue(LanguageContainerValue):
    def bool(self):
        return self.value

    def num(self):
        if self.value:
            return 1
        return 0

    def str(self):
        if self.value:
            return 'true'
        return 'false'


class NumberValue(LanguageContainerValue):
    def num(self):
        return self.value


class StringValue(LanguageContainerValue):
    def num(self):
        try:
            return float(self.value)
        except ValueError:
            return 0

    def str(self):
        return self.value


class ObjectValue(LanguageContainerValue):
    def __init__(self, cls, params):
        super(ObjectValue, self).__init__({})
        # TOOD: set members as variables similar to scope
        # TODO: handle None cls as a dev solution
        self.cls = cls
        self._params = params

    def bool(self):
        return True

    def getttype(self):
        return 'object'

    def num(self):
        return 0

    def obj(self):
        return self

    def str(self):
        return str(self.value)

    def __getitem__(self, name):
        if name in self.value:
            return self.value[name]
        return UndefinedValue()

    def __setitem__(self, name, value):
        # TODO: check if such var exists, typecheck
        self.value[name] = value


class FunctionValue(ObjectValue):
    def __init__(self, name, params, return_type, block):
        super(FunctionValue, self).__init__(None, [])
        # TODO: support for checking return types
        if not isinstance(block, ScopeNode):
            raise Exception('You must pass a block to a function value')
        self.name = name
        self.params = params
        self.return_type = return_type
        self.block = block

    def call(self, values):
        self._check_values(values)
        try:
            self._run(values)
        except _Return as r:
            return r.value
        return UndefinedValue()

    def gettype(self):
        # TODO: also specify params and return type
        return 'function'

    def str(self):
        return self.gettype()

    def _check_values(self, values):
        if len(values) != len(self.params):
            raise ParameterError('Invalid number of parameters passed')
        try:
            for value, param in zip(values, self.params):
                typecheck(value, param.type)
        except TypeMismatchError:
            raise ParameterError('Invalid parameter type')

    def _run(self, values):
        scope = {}
        for value, param in zip(values, self.params):
            scope[param.name] = value
        self.block.update_scope(scope)
        self.block.run()


class ClassValue(ObjectValue):
    def __init__(self, name, members):
        super(ClassValue, self).__init__(None, [])
        self.name = name
        self.members = members
        self._fields = [m for m in members if isinstance(m, Variable)]
        self._methods = [m for m in members if isinstance(m, FunctionValue)]
        self._register_constructor()

    def instantiate(self, values):
        result = self._instantiate()
        if self._constructor is not None:
            # TODO: call constructor
            pass
        return result

    def _instantiate(self):
        params = self._fields[:]
        for method in self._methods:
            var = Variable(method.name, method.gettype(), method)
            params.append(var)
        obj = ObjectValue(self, params)
        return obj

    def _register_constructor(self):
        # TODO: avoid using the keyword directly
        constructors = [m for m in self.methods if m.name == 'constructor']
        num = len(constructors)
        if num > 2:
            raise SemanticError('Multiple constructors in one class')
        constructor = None
        if num == 1:
            constructor = constructors[0]
        self._constructor = constructor


class NullValue(LanguageValue):
    def bool(self):
        return False

    def num(self):
        return 0

    def obj(self, name):
        raise AttributeError('Null reference exception')

    def str(self):
        return 'null'


class UndefinedValue(LanguageValue):
    def bool(self):
        return False

    def num(self):
        return float('nan')

    def obj(self, name):
        raise AttributeError('Reference to undefined')

    def str(self):
        return 'undefined'


# Auxiliary objects


_VALUE_TYPE_MAP = {
    'number': NumberValue,
    'string': StringValue,
    'boolean': BooleanValue,
}


def typecheck(value, var_type):
    if isinstance(value, NullValue) or isinstance(value, UndefinedValue):
        return
    if var_type in _VALUE_TYPE_MAP:
        necessary_type = _VALUE_TYPE_MAP[var_type]
        if isinstance(value, necessary_type):
            return
    else:
        cls_name = value.cls.name
        if cls_name == var_type:
            return
    raise TypeMismatchError(value, var_type)


class _Return(Exception):
    def __init__(self, value):
        self.value = value


class Variable(object):
    def __init__(self, name, var_type, value=None):
        self.name = name
        self.type = var_type
        self.value = value


# Errors


class SemanticError(Exception):
    pass


class NotAFunctionError(SemanticError):
    def __init__(self, name):
        msg = '{} is not a function'.format(name)
        super(NotAFunctionError, self).__init__(msg)


class UndeclaredVariableError(SemanticError):
    def __init__(self, name):
        msg = 'Operation with undeclared variable "{}"'.format(name)
        super(UndeclaredVariableError, self).__init__(msg)


class TypeMismatchError(SemanticError):
    def __init__(self, value, var_type):
        msg = 'Value {} must be of type {}'.format(value, var_type)
        super(TypeMismatchError, self).__init__(msg)


class ParameterError(SemanticError):
    pass
