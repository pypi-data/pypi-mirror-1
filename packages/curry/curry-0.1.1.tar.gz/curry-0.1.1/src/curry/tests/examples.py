import re

class Index(object):
    """An inefficient search index."""

    separator = ' '

    def __init__(self, body):
        self.body = body

    def search(self, query):
        body = self.body.replace('. ', self.separator)
        words = body.rstrip('.').split(self.separator)
        occurances = words.count(query)
        return float(occurances)/len(words)

class Interpreter(object):
    """Python interpreter.

    Will execute any source-code you pass in.
    """

    def __init__(self, source):
        self.source = source

    def execute(self):
        for line in self.source.split('\n'):
            exec line

class Template(object):
    """A simple implementation of the Genshi text-mode template
    language, where expressions on the form `${expr}` are evaluated at
    render-time.

    The typical implementation relies on an AST-transform which looks
    up symbols from a dictionary (e.g. double-star keyword
    arguments). In this simple example we will instead require a
    ``context`` parameter, which will be the only known symbol in the
    template variable scope.
    """

    re_expression = re.compile(r'\${([^}]+)}')

    class expression(unicode):
        pass

    def __init__(self, body):
        self.parts = []
        while body:
            m = self.re_expression.search(body)
            if m is not None:
                if m.start() > 0:
                    self.parts.append(body[:m.start()])
                    self.parts.append(self.expression(m.groups()[0]))
                    body = body[m.end():]
            else:
                self.parts.append(body)
                break

    def render(self, context):
        out = []
        for part in self.parts:
            if isinstance(part, self.expression):
                part = eval(part)
            out.append(part)
        return u"".join(out)

