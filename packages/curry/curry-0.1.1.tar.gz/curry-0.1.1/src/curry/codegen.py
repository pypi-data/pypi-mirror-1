import ast
import copy
import inspect
import textwrap
import astutils
import types
import cPickle as pickle

UNDEFINED = object()

class Break(Exception):
    def __init__(self, node):
        self.node = node

class Continue(Exception):
    def __init__(self, node):
        self.node = node

class Defined(ast.expr):
    """Nodes that represents symbols that are evaluated during partial
    applications should inherit from this mixin-class."""

    get = None

class Global(Defined):
    """Global (built-in) symbol."""

    id = None
    ctx = ast.Load()

    def __init__(self, id, _globals):
        self.id = id
        self._globals = _globals

    def get(self):
        return self._globals[self.id]

class Closure(ast.FunctionDef):
    """Function closure.

    This is essentially an unnamed function definition.
    """

    _fields = 'args', 'body', 'decorator_list'

    decorator_list = []
    
    def __init__(self, node, call_args, transformer, name=None):
        self.args = node.args
        self.call_args = call_args
        self.body = node.body
        self._transformer = transformer
        self._name = name
        transformer._register(self)

    @property
    def name(self):
        if self._name is None:
            self._name = self._transformer._get_id(self)
        return self._name

class Resolved(ast.Name, Defined):
    """Resolved name.

    Represents a symbol in the AST for which the value is known. The
    symbol name (``id``) is generated on-demand by the transformer.

    Note that we omit the ``id`` field to avoid generation on clone.
    """

    _id = None
    _fields = "ctx",

    def __new__(cls, value, transformer, ctx=None):
        if ctx is None or isinstance(ctx, ast.Load):
            if isinstance(value, (int, float, long, bool)):
                return Num(value)
            if isinstance(value, basestring):
                return Str(value)
        return ast.AST.__new__(cls)

    def __init__(self, value, transformer, ctx=ast.Load()):
        self._value = value
        self._transformer = transformer
        self.ctx = ctx
        transformer._register(self)

    def __len__(self):
        return len(self.id)

    def __str__(self):
        return self.id

    def __radd__(self, other):
        return other + self.id

    @property
    def id(self):
        if isinstance(self._value, ast.Name):
            return self._value.id
        if isinstance(self._value, Closure):
            return self._value.name
        if self._id is None:
            self._id = self._transformer._get_id(self)
        return self._id

    def get(self):
        if isinstance(self._value, Resolved):
            return self._value.get()
        return self._value

class Num(ast.Num, Defined):
    def get(self):
        return self.n

class Str(ast.Str, Defined):
    def get(self):
        return self.s

class Statements(ast.stmt):
    """Inline list of statements."""

    _fields = "body",

    def __init__(self, body):
        self.body = body

class Transformer(astutils.ASTTransformer):
    """Partial application transformer."""

    immutable = (int, float, long, basestring, tuple)
    defined = (Resolved, ast.Num, ast.Str)
    static_builtin_methods = (unicode.join,)

    bin_ops = {
        ast.Add: "__add__",
        ast.Sub: "__sub__",
        ast.Mult: "__mul__",
        ast.Div: "__div__",
        ast.Mod: "__mod__",
        ast.Pow: "__pow__",
        ast.LShift: "__lshift__",
        ast.RShift: "__rshift__",
        ast.BitOr: "__or__",
        ast.BitXor: "__xor__",
        ast.BitAnd: "__and__",
        ast.FloorDiv: "__floordiv__",
        }

    unary_ops = {
        ast.Invert: lambda op: ~op,
        ast.Not: lambda op: not op,
        ast.UAdd: lambda op: +op,
        ast.USub: lambda op: -op,
    }

    globals = __builtins__.copy()
    globals.update({
        # as a special case, the ``eval`` method should return an
        # AST-expression rather than evaluate the expression
        'eval': lambda expression: astutils.parse(expression, 'eval').body,
        })

    def __init__(self):
        self.locals = [{}]
        self.resolved = []
        self.closures = []

    def __call__(self, bound_method):
        """Visits bound method and returns an AST-object that contains
        a module with a single, unbound method (carrying the same
        name).

        Note that the unbound method will take one argument less
        (namely the class instance argument).

        This is a low-level API function.
        """

        assert len(self.resolved) == 0 and len(self.closures) == 0, \
               "Single invokation only."

        source = inspect.getsource(bound_method)
        source = textwrap.dedent(source)
        module = ast.parse(source)

        # node is a module with a single statement, a function
        # definition
        assert isinstance(module, ast.Module)
        assert isinstance(module.body[0], ast.FunctionDef)

        # pop function definition and define as closure
        function_def = module.body.pop(0)
        args = list(function_def.args.args)
        args[0] = Resolved(bound_method.im_self, self)
        closure = Closure(function_def, args, self, name=function_def.name)
        function_node = self.visit(closure)

        # insert closures
        for closure in self.closures:
            module.body.insert(0, closure)

        # fall back to Python pickle for state restore (slow!)
        loads = Resolved(pickle.loads, self)

        imports = []
        global_seen = set()

        # process module-level function definitions
        for stmt in module.body:
            if not isinstance(stmt, ast.FunctionDef):
                continue

            # get list of names
            names = set()
            for child in ast.walk(stmt):
                if type(child) is ast.Name and isinstance(child.ctx, ast.Load):
                    names.add(child.id)

            # removed unused targets (names) from assignments
            for child in ast.walk(stmt):
                if isinstance(child, ast.Assign):
                    for target in tuple(child.targets):
                        if isinstance(target, ast.Name) and target.id not in names:
                            child.targets.remove(target)
                    if not child.targets and isinstance(child.value, Defined):
                        child.value = None

            # get list of resolved names
            seen = set()
            for child in ast.walk(stmt):
                if isinstance(child, Resolved):
                    seen.add(child)

            inverse_mapping = {}
            assigned = set()

            def assign_resolved(resolved, assignments, imports):
                if resolved in assigned:
                    return

                value = resolved.get()
                inverse_mapping[id(value)] = resolved

                if resolved not in seen:
                    return

                node = None

                def _import(value):
                    as_name = Resolved(value, self, ctx=ast.Load())
                    seen.add(as_name)
                    node = ast.ImportFrom(
                        value.__module__, [
                            ast.alias(value.__name__, as_name)],
                        None)
                    imports.append(node)
                    return as_name

                def _convert_to_ast(value):
                    if value is None:
                        return ast.Name("None", ast.Load())

                    kls = value.__class__
                    if kls is list:
                        return ast.List(map(_convert_to_ast, value), ast.Load())
                    if kls is tuple:
                        return ast.Tuple(map(_convert_to_ast, value), ast.Load())
                    if kls in (str, unicode):
                        return Str(value)
                    if kls in (int, float, long, bool):
                        return Num(value)
                    if kls is dict:
                        keys = []
                        values = []
                        for k, v in value.items():
                            keys.append(_convert_to_ast(k))
                            values.append(_convert_to_ast(v))
                        return ast.Dict(keys, values)

                    if kls is types.BuiltinMethodType:
                        return ast.Attribute(
                            _convert_to_ast(value.__self__),
                            value.__name__, ast.Load())
                    if kls is types.BuiltinFunctionType:
                        return Global(value.__name__)

                    if isinstance(value, types.BuiltinMethodType):
                        if value.__self__ is not None:
                            if self._is_global(value.__self__.__class__):
                                return ast.Attribute(
                                    Global(value.__name__),
                                    value.__name__, ast.Load())

                    raise NotImplementedError(
                        "Unable to convert value: %s." % repr(value))
                    
                if isinstance(value, Closure):
                    return
                elif isinstance(value, ast.AST):
                    raise RuntimeError("Node not expected: %s." % repr(value))
                elif isinstance(value, types.BuiltinMethodType):
                    if value.__self__ is None:
                        node = _import(value)
                    else:
                        try:
                            ref = inverse_mapping.get(id(value.__self__))
                        except TypeError:
                            ref = Resolved(value.__self__, self)
                        if ref is not None:
                            required = []
                            seen.add(ref)
                            assign_resolved(ref, required, imports)
                            assignments.extend(required)
                            node = ast.Attribute(ref, value.__name__, ast.Load())

                if node is None:
                    node = _convert_to_ast(value)

                    if node is None:
                        required = []
                        seen.add(loads)
                        assign_resolved(loads, required, imports)
                        assignments[:0] = required
                        value = pickle.dumps(value)
                        node = ast.Call(loads, [ast.Str(value)], (), None, None)

                target = Resolved(resolved, self, ctx=ast.Store())
                assignments.append(ast.Assign([target], node))
                assigned.add(resolved)

            # assign state to resolved values
            nodes = []
            for resolved in tuple(self.resolved):
                assign_resolved(resolved, nodes, imports)
            stmt.body[:0] = nodes

            # maintain global set of resolved values that have been set
            global_seen.update(seen)

        # filter out resolved nodes that are unused; though not
        # strictly required, this prevents inflation in the numbering
        # of generated symbols
        self.resolved[:] = filter(global_seen.__contains__, self.resolved)

        # prepend imports; to-do: filter duplicates
        module.body[:0] = imports

        return module

    def _get_id(self, node):
        method = getattr(self, "_get_id_for_%s" % node.__class__.__name__.lower())
        return method(node)

    def _get_id_for_resolved(self, node):
        return "_resolved%d" % self.resolved.index(node)

    def _get_id_for_closure(self, node):
        return "_closure%d" % self.closures.index(node)

    def _is_global(self, value):
        if value in self.globals.values():
            for name, obj in self.globals.items():
                if obj is value:
                    return True
        return False

    def _register(self, node):
        method = getattr(self, "_register_%s" % node.__class__.__name__.lower())
        method(node)

    def _register_resolved(self, node):
        self.resolved.append(node)

    def _register_closure(self, node):
        self.closures.append(node)

    def _invalidate_target(self, target):
        scope = self.locals[-1]
        if isinstance(target, ast.Name):
            scope[target.id] = UNDEFINED
        else:
            raise NotImplementedError(
                "Don't know how to invalidate target: %s." % repr(target))
                
    def _possibly_invalidate_local(self, value):
        scope = self.locals[-1]
        if isinstance(value, types.MethodType):
            value = value.__self__
        elif isinstance(value, types.BuiltinMethodType):
            value = value.__self__

        if value is not None:
            for name, obj in scope.items():
                if isinstance(obj, Defined):
                    obj = obj.get()
                if obj is value:
                    scope[name] = UNDEFINED

    def visit_NotImplemented(self, node):
        raise NotImplementedError(
            "Nodes of type `%s` unsupported." % type(node).__name__)

    visit_Module = visit_NotImplemented
    visit_Interactive = visit_NotImplemented
    visit_Expression = visit_NotImplemented
    visit_Suite = visit_NotImplemented

    visit_FunctionDef = visit_NotImplemented
    visit_ClassDef = visit_NotImplemented
    # visit_Return = visit_NotImplemented
    visit_Delete = visit_NotImplemented
    visit_Assign = visit_NotImplemented
    visit_AugAssign = visit_NotImplemented
    # visit_Print = visit_NotImplemented
    visit_For = visit_NotImplemented
    visit_While = visit_NotImplemented
    visit_If = visit_NotImplemented
    visit_With = visit_NotImplemented
    visit_Raise = visit_NotImplemented
    visit_TryExcept = visit_NotImplemented
    visit_TryFinally = visit_NotImplemented
    visit_Assert = visit_NotImplemented

    visit_Import = visit_NotImplemented
    visit_ImportFrom = visit_NotImplemented
    visit_Exec = visit_NotImplemented
    visit_Global = visit_NotImplemented
    # visit_Expr = visit_NotImplemented

    visit_BoolOp = visit_NotImplemented
    visit_BinOp = visit_NotImplemented
    visit_UnaryOp = visit_NotImplemented
    visit_Lambda = visit_NotImplemented
    visit_IfExp = visit_NotImplemented
    visit_Dict = visit_NotImplemented
    visit_ListComp = visit_NotImplemented
    visit_GeneratorExp = visit_NotImplemented
    visit_Yield = visit_NotImplemented
    visit_Compare = visit_NotImplemented
    visit_Call = visit_NotImplemented
    visit_Repr = visit_NotImplemented

    visit_Attribute = visit_NotImplemented
    visit_Subscript = visit_NotImplemented
    visit_Name = visit_NotImplemented
    visit_List = visit_NotImplemented
    visit_Tuple = visit_NotImplemented

    visit_comprehension = visit_NotImplemented
    visit_excepthandler = visit_NotImplemented
    visit_arguments = visit_NotImplemented
    visit_keyword = visit_NotImplemented
    visit_alias = visit_NotImplemented

    #visit_Slice = visit_NotImplemented
    visit_ExtSlice = visit_NotImplemented
    # visit_Index = visit_NotImplemented

    visit_Break = visit_NotImplemented
    visit_Continue = visit_NotImplemented

    def visit_Assign(self, node):
        node = super(Transformer, self).visit_Assign(node)
        scope = self.locals[-1]
        for target in node.targets:
            if isinstance(node.value, Defined):
                value = node.value
            else:
                value = UNDEFINED
            scope[target.id] = value
        return node

    def visit_Attribute(self, node):
        node = super(Transformer, self).visit_Attribute(node)

        if isinstance(node.value, Defined):
            value = getattr(node.value.get(), node.attr)
            return Resolved(value, self)

        return node

    def visit_AugAssign(self, node):
        node = super(Transformer, self).visit_AugAssign(node)
        assign = ast.Assign(
            [node.target], ast.BinOp(
                node.target, node.op, node.value))
        return self.visit(assign)

    def visit_BinOp(self, node):
        orig = node
        node = super(Transformer, self).visit_BinOp(node)

        # binary operators act from left to right
        if isinstance(node.left, Defined):
            left = node.left.get()
            attribute = self.bin_ops[type(node.op)]

            if isinstance(node.right, Defined):
                right = node.right.get()

                # this is necessary when dealing with incompatible
                # number types
                if isinstance(left, int) and isinstance(right, complex):
                    left = complex(left)
                if isinstance(left, int) and isinstance(right, float):
                    left = float(left)
                if isinstance(left, int) and isinstance(right, long):
                    left = long(left)

                method = getattr(left, attribute)
                return Resolved(method(right), self)
            else:
                method = getattr(left, attribute)
                if isinstance(method, (types.MethodType, types.FunctionType)):
                    return self.visit(ast.Call(
                        Resolved(method, self), [node.right], (), None, None))

        return node

    def visit_Break(self, node):
        raise Break(node)

    def visit_Continue(self, node):
        raise Continue(node)
        
    def visit_Call(self, node):
        orig = node
        node = super(Transformer, self).visit_Call(node)

        if isinstance(node.func, Defined):
            func = node.func.get()
            for arg in node.args:
                if not isinstance(arg, Defined):
                    self._possibly_invalidate_local(func)
                    break
            else:
                args = [arg.get() for arg in node.args]
                value = func(*args)
                if isinstance(value, ast.expr):
                    return value
                return Resolved(value, self)

            if isinstance(func,
                (types.BuiltinMethodType, types.BuiltinFunctionType)):
                return node

            if self._is_global(func):
                return node

            # make sure we got everything right :-)
            assert isinstance(func, (types.MethodType, types.FunctionType))

            # some or all arguments are undefined; inline function as
            # closure and return modified call-node
            source = inspect.getsource(func)
            source = textwrap.dedent(source)
            module = ast.parse(source)
            function_node = module.body[0]
            assert isinstance(function_node, ast.FunctionDef)

            # for methods, we prepend the bound argument
            if isinstance(func, types.MethodType):
                im_self = Resolved(func.im_self, self)
                node.args.insert(0, im_self)

            # the closure will have any defined arguments
            # incorporated as locals, and we should omit them from
            # the call-node
            defined_args = filter(
                lambda arg: isinstance(arg, Defined), node.args)
            undefined_args = filter(
                lambda arg: not isinstance(arg, Defined), node.args)
            
            # define closure and link to resolved node
            closure = Closure(function_node, node.args, self)
            resolved = Resolved(self.visit(closure), self)

            return ast.Call(
                resolved, undefined_args, (), None, None)

        return node

    def visit_Closure(self, node):
        """Visit function closure.

        The arguments that are defined should be added to the local
        function scope, then stripped from the closure arguments list.
        """

        scope = dict((arg.id, self.globals.get(arg.id, UNDEFINED))
                     for arg in node.args.args)

        zipped = zip(node.args.args, node.call_args)
        del node.args.args[:]
        del node.call_args[:]

        for arg, call_arg in zipped:
            assert isinstance(arg, ast.Name)
            if isinstance(call_arg, Defined):
                scope[arg.id] = call_arg
            else:
                node.args.args.append(arg)
                node.call_args.append(call_arg)

        self.locals.append(scope)
        node.body = [self.visit(x) for x in node.body]
        self.locals.pop()
        return node

    def visit_Compare(self, node):
        node = super(Transformer, self).visit_Compare(node)
        left = node.left

        # we compare left to right
        ops = []
        comparators = []
        for op, comparator in zip(node.ops, node.comparators):
            if isinstance(left, Defined) and isinstance(comparator, Defined):
                vleft = left.get()
                vright = comparator.get()

                if isinstance(op, ast.Eq):
                    result = vleft == vright
                elif isinstance(op, ast.NotEq):
                    result = vleft != vright
                elif isinstance(op, ast.Lt):
                    result = vleft < vright
                elif isinstance(op, ast.LtE):
                    result = vleft <= vright
                elif isinstance(op, ast.Gt):
                    result = vleft > vright
                elif isinstance(op, ast.GtE):
                    result = vleft >= vright
                elif isinstance(op, ast.Is):
                    result = vleft is vright
                elif isinstance(op, ast.IsNot):
                    result = vleft is not vright
                elif isinstance(op, ast.In):
                    result = vleft in vright
                elif isinstance(op, ast.NotIn):
                    result = vleft not in vright
                else:
                    raise RuntimeError(
                        "Unknown operator: %s." % repr(op))
                left = Resolved(result, self)
            else:
                ops.append(op)
                comparators.append(comparator)
                left = None
                
        node.ops[:] = ops
        node.comparators[:] = comparators

        if isinstance(left, Defined):
            return left
        
        return node
    
    def visit_Exec(self, node):
        node = super(Transformer, self).visit_Exec(node)
        
        if node.locals:
            raise NotImplementedError(
                "Dynamic execution only allowed using local scope.")

        if node.globals:
            raise NotImplementedError(
                "Dynamic execution must use default globals.")
        
        if not isinstance(node.body, Defined):
            raise NotImplementedError(
                "Dynamic execution must happen during partial application.")

        body = astutils.parse(node.body.get(), 'exec').body
        return Statements(body)

    def visit_Expr(self, node):
        node = super(Transformer, self).visit_Expr(node)
        if isinstance(node.value, ast.Name):
            return None
        return node

    def visit_For(self, node):
        body = node.body
        node.iter = super(Transformer, self).visit(node.iter)

        if isinstance(node.iter, Defined):
            scope = self.locals[-1]

            if not isinstance(node.target, ast.Name):
                raise NotImplemented(
                    "Iterator target must be a name.")

            iterator = node.iter.get()
            nodes = []
            name = node.target.id

            for value in iterator:
                # assign value to node target
                resolved = Resolved(value, self)
                assign = ast.Assign(
                    [ast.Name(name, ast.Store())], resolved)
                nodes.append(self.visit(assign))

                try:
                    # loop through node body, flattening the loop
                    for child in body:
                        child = copy.deepcopy(child)
                        nodes.append(
                            super(Transformer, self).visit(child))
                except Break:
                    break
                except Continue:
                    continue
            else:
                nodes.extend(
                    [self.visit(stmt) for stmt in node.orelse])

            return Statements(nodes)
        else:
            node.body = super(Transformer, self).visit(node.body)

        return node

    def visit_FunctionDef(self, node):
        """Visit function definition.

        This initializes a new local variable scope registry which is
        used to record variable assignment.

        The 'known' variables are then the local variable scope plus
        the module globals. All other names are unresolvable at CT.
        """

        scope = dict((arg.id, self.globals.get(arg.id, UNDEFINED))
                     for arg in node.args.args)
        scope.update(self.locals[-1])
        self.locals.append(scope)
        node.body = [self.visit(x) for x in node.body]
        self.locals.pop()
        return node

    def visit_If(self, node):
        node.test = super(Transformer, self).visit(node.test)

        # if the test can't be resolved, we don't touch neither the
        # body or the or-else conditions
        if isinstance(node.test, Defined):
            value = node.test.get()
            if value:
                nodes = node.body
            else:
                nodes = node.orelse
            return self.visit(Statements(nodes))
        return node

    def visit_List(self, node):
        node = super(Transformer, self).visit_List(node)

        if isinstance(node.ctx, ast.Load):
            for elt in node.elts:
                if not isinstance(elt, Defined):
                    break
            else:
                value = [resolved.get() for resolved in node.elts]
                return Resolved(value, self)
        return node

    def visit_Name(self, node):
        node = super(Transformer, self).visit_Name(node)
        if isinstance(node.ctx, ast.Store):
            return node

        scope = self.locals[-1]
        value = scope.get(node.id)
        if isinstance(value, Defined):
            return value

        if node.id in self.globals:
            return Global(node.id, self.globals)

        return node

    def visit_Global(self, node):
        return node

    def visit_Num(self, node):
        return Num(node.n)

    def visit_Resolved(self, node):
        return node

    def visit_Statements(self, node):
        return Statements([self.visit(x) for x in node.body])

    def visit_Str(self, node):
        return Str(node.s)

    def visit_Subscript(self, node):
        node = super(Transformer, self).visit_Subscript(node)

        if not isinstance(node.value, Defined):
            return node

        value = node.value.get()

        if isinstance(node.slice, ast.Index):
            if isinstance(node.slice.value, Defined):
                return Resolved(value[node.slice.value.get()], self)

            method = value.__getitem__
            if isinstance(method, (types.MethodType, types.FunctionType)):
                return self.visit(ast.Call(
                    Resolved(method, self), [node.slice.value], (), None, None))
            return node

        if isinstance(node.slice, ast.Slice):
            upper = node.slice.upper
            lower = node.slice.lower
            step = node.slice.step

            if isinstance(upper, Defined):
                upper = upper.get()

            if isinstance(lower, Defined):
                lower = lower.get()

            if isinstance(step, Defined):
                step = step.get()

            if (isinstance(upper, ast.AST) or \
                isinstance(lower, ast.AST) or \
                isinstance(step, ast.AST)):
                if step is not None:
                    raise NotImplemented("Step parameter not supported.")
                method = value.__getslice__
                if isinstance(method, (types.MethodType, types.FunctionType)):
                    return self.visit(ast.Call(
                        Resolved(method, self), [node.lower, node.upper],
                        (), None, None))
                return node
            
            return Resolved(value[lower:upper:step], self)

        return node

    def visit_Tuple(self, node):
        node = super(Transformer, self).visit_Tuple(node)
        for elt in node.elts:
            if not isinstance(elt, Defined):
                break
        else:
            value = tuple(resolved.get() for resolved in node.elts)
            return Resolved(value, self)
        return node
    
    def visit_UnaryOp(self, node):
        node = super(Transformer, self).visit_UnaryOp(node)

        # binary operators act from left to right
        if isinstance(node.operand, Defined):
            operand = node.operand.get()
            value = self.unary_ops[type(node.op)](operand)
            return Resolved(value, self)

        return node

    def visit_While(self, node):
        count = 0
        body = []
        condition = True
        
        while condition:
            count += 1
            test = super(Transformer, self).visit(
                copy.deepcopy(node.test))

            # we should only get an undefined test once
            if not isinstance(test, Defined):
                node.test = test
                assert count == 1

                # invalidate assignment targets
                for child in ast.walk(node):
                    if isinstance(child, ast.Assign):
                        for target in child.targets:
                            self._invalidate_target(target)

                return node

            condition = test.get()
            if not condition:
                continue

            try:
                # loop through node body, flattening the loop
                for child in node.body:
                    child = copy.deepcopy(child)
                    body.append(
                        super(Transformer, self).visit(child))
            except Break:
                break
            except Continue:
                continue
        else:
            body.extend(
                [self.visit(node) for node in node.orelse])

        return Statements(body)
    
class ASTCodeGenerator(astutils.ASTCodeGenerator):
    def visit_Resolved(self, node):
        if isinstance(node.ctx, ast.Load):
            value = node.get()
            if isinstance(value, (int, float, long)):
                self.visit(ast.Num(value))
            if isinstance(value, basestring):
                self.visit(ast.Str(value))

        self.visit_Name(node)

    def visit_Statements(self, node):
        for child in node.body:
            self.visit(child)

    def visit_Assign(self, node):
        if node.value is not None:
            super(ASTCodeGenerator, self).visit_Assign(node)

    def visit_Closure(self, node):
        return self.visit_FunctionDef(node)

    visit_Global = visit_Resolved
