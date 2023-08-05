import inspect
import compiler

from dap.lib import escape


class ASTVisitor(object):
    def __init__(self, sequence):
        self._sequence = sequence
        self.filters = []

    def visitCompare(self, node):
        a, op, b = node.getChildren()
        ops = {'>': '>', '<': '<', '==': '=', '!=': '!=', '<=': '<=', '>=': '>='}
        if op in ops:
            id = self.visit(a)
            b = self.visit(b)
            if op == '==': b = escape(b)
            filter_ = '%s%s%s' % (id, ops[op], b)
            self.filters.append(filter_)

    def visitSubscript(self, node):
        subs = self.visit(node.subs[0])
        id = self._sequence[subs].id
        return id

    def visitName(self, node):
        return node.name

    def visitConst(self, node):
        return node.value

    def visitOr(self, node):
        raise Exception, 'OR not supported by the DAP spec!'

    def visitCallFunc(self, node):
        function = self.visit(node.node)
        if function in ['re.match', 'match']:
            b, a = node.args
            b = self.visit(b)
            id = self.visit(a)
            filter_ = '%s=~%s' % (id, b)
            self.filters.append(filter_)

        elif function == 'str':
            return self.visit(node.args[0])

    def visitGetattr(self, node):
        return '%s.%s' % (self.visit(node.expr), node.attrname)

    
def get_filters(sequence):
    frame = inspect.currentframe()
    try:
        try: outer = inspect.getouterframes(frame)
        except: outer = []
    finally:
        del frame

    # Parse code.
    filters = []
    for record in outer:
        context = record[4]
        if context:
            # Grab the source.
            src = context[0].strip()
            visitor = ASTVisitor(sequence)
            try:
                ast = compiler.parse(src)
                compiler.walk(ast, visitor)
            except:  # ignore exceptions, returning no filters.
                pass
            filters.extend(visitor.filters)

    return filters
