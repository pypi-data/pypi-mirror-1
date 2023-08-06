import ast
import codegen
import types

def cook(method):
    """Cook bound method.

    Takes any bound method and returns a cooked, unbound method.
    """

    if not isinstance(method, types.MethodType):
        raise TypeError("Not a bound method: %s." % repr(method))

    transformer = codegen.Transformer()
    module = transformer(method)
    function = module.body[-1]
    assert isinstance(function, ast.FunctionDef), \
           "Expected function definition as last statement in module."

    # wrap module body in a wrapper method to define module-level
    # symbols in function closure
    module.body = [ast.FunctionDef(
        "bind", (), module.body + [
            ast.Return(ast.Name(method.__name__, ast.Load()))], ())]

    # generate source-code and compile into code object
    generator = codegen.ASTCodeGenerator(module)
    print ""
    print generator.code
    try:
        code = compile(generator.code, '<string>', 'exec')
    except SyntaxError, e:
        # raise a more informative exception
        raise SyntaxError(
            "%s\n\n%s" % (str(e), generator.code))
    _locals = {}
    exec code in __builtins__, _locals
    bind = _locals.pop("bind")
    return bind()
