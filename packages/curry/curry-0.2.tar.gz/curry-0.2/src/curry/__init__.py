import ast
import codegen
import types
import marshal

GLOBALS = globals()

def cook(method, prebind=True):
    """Cook bound method.

    Takes any bound method (or closure) and returns an unbound method.
    """

    if not isinstance(method, types.MethodType):
        raise TypeError("Not a bound method: %s." % repr(method))

    transformer = codegen.Transformer()
    module = transformer(method)
    function = module.body[-1]
    assert isinstance(function, ast.FunctionDef), \
           "Expected function definition as last statement in module."

    if prebind:
        # wrap module body in a wrapper method to define module-level
        # symbols in function closure
        module.body = [ast.FunctionDef(
            "bind", (), module.body + [
                ast.Return(ast.Name(method.__name__, ast.Load()))], ())]
    else:
        # define module-level symbols inside function body
        function.body[:0] = module.body[:-1]
        module.body[:] = [function]

    # generate source-code and compile into code object
    generator = codegen.ASTCodeGenerator(module)
    try:
        code = compile(generator.code, '<string>', 'exec')
    except SyntaxError, e:
        # raise a more informative exception
        raise SyntaxError(
            "%s\n\n%s" % (str(e), generator.code))
    _locals = {}
    exec code in __builtins__, _locals

    if prebind:
        bind = _locals.pop("bind")
        return bind()

    return _locals.pop(method.__name__)

class factory:
    def __init__(self, obj):
        self.obj = obj

    def __call__(self):
        return self.obj

def dumps(obj):
    bind = cook(factory(obj).__call__, prebind=False)
    return marshal.dumps(bind.func_code)

def loads(data):
    func_code = marshal.loads(data)
    curried = types.FunctionType(func_code, GLOBALS)
    return curried()
