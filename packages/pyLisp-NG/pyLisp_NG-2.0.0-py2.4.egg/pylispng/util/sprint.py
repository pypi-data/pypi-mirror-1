from pylispng import lisp

def getTree(sexp, padding='', initial=False):
    """
    An s-expression printer.
    """
    out = ''
    indent = ' ' * 4
    for node in sexp:
        if isinstance(node, lisp.ListObject):
            out += getTree(node, padding + indent)
        else:
            type = lisp.get_type(node)
            if type == lisp.SymbolObject:
                out += padding + indent + '|--[' + str(node) + ']\n'
            else:
                prefix = '+--'
                if initial:
                    prefix = '   '
                out += padding + prefix + '[' + str(node) + ']\n'
    return out

def sprint(sexp):
    print '\n', getTree(sexp, initial=True)
