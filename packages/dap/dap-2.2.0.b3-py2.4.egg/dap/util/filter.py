import inspect
import compiler
from urllib import quote

from dap.lib import encode_atom


class ASTVisitor(object):
    def __init__(self, sequence):
        self._sequence = sequence
        self.filters = []

    def visitCompare(self, node):
        a, op, b = node.getChildren()
        ops = {'>': '>', '<': '<', '==': '=', '!=': '!=', '<=': '<=', '>=': '>='}
        if op in ops:
            id = self.visit(a).id

            b = self.visit(b)
            b = encode_atom(b)
            b = quote(b)

            filter_ = '%s%s%s' % (id, ops[op], b)
            self.filters.append(filter_)

    def visitSubscript(self, node):
        subs = self.visit(node.subs[0])
        child = self._sequence.get(subs, None)
        if hasattr(child, 'id'): return child

    def visitName(self, node):
        return node.name

    def visitConst(self, node):
        return node.value

    def visitUnarySub(self, node):
        return -1 * self.visit(node.getChildren()[0])

    def visitOr(self, node):
        raise Exception, 'OR not supported by the DAP spec!'

    def visitCallFunc(self, node):
        function = self.visit(node.node)
        if function in ['re.match', 'match']:
            b, a = node.args
            b = self.visit(b)
            id = self.visit(a).id
            filter_ = '%s=~%s' % (id, b)
            self.filters.append(filter_)

        elif function == 'str':
            return self.visit(node.args[0])

    def visitGetattr(self, node):
        parent, child = node.getChildren()
        child = getattr(self._sequence, child, None)
        if hasattr(child, 'id'): return child

    
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
