#-*- coding: utf-8 -*-
#
# Copyright (c) 2000 - 2002 William S. Annis.  All rights reserved.
# This is free software; you can redistribute it and/or modify it
# under the same terms as Perl (the Artistic Licence).  Developed at
# the Department of Biostatistics and Medical Informatics, University
# of Wisconsin, Madison.
#
# The S-expression parser (class Reader) probably came from someone
# else, but I am no longer sure where.  If you know, please tell me,
# though I have made many changes and its ancestry may no longer
# be apparent.
#
# Copyright (c) 2008 Duncan McGreggor
"""
A trivial Lisp implementation.
"""
import re
import sys
import types
import string

from pylispng.util import DynamicList

SYMCHARS = string.digits + string.uppercase + string.lowercase + '-+*/:&$?='
WS = string.whitespace
SPECIAL = "()`',@"
SYNTAX = WS + SPECIAL

# simple conversions that are almost always useful:
INT = re.compile(r'^[+-]?\d+$')
LONGINT = re.compile(r'^[+-]?\d+[lL]$')
FLOAT = re.compile(r'^[+-]?(\d+\.\d*$|\d*\.\d+$)')

_nummap = {
    INT: string.atoi,
    LONGINT: string.atol,
    FLOAT: string.atof
    }

class Error(Exception):
    pass

# The type system: every type knows how to evaluate itself but must
# be handed an Environment to work with, plus any arguments it might
# take.
class Evalable(object):
    """
    Evaluatable Lisp object interface.
    """
    def eval(self, environment, args=None):
        raise Error, "Unimplemented"

# property list
_PROPERTIES = {}

class SymbolObject(Evalable):
    """
    Everything in Lisp is a list of symbols.
    """
    def __init__(self, name):
        self.n = name
        if not _PROPERTIES.has_key(self.n):
            _PROPERTIES[self.n] = {}

    def __repr__(self):
        return self.n

    def __hash__(self):
        return hash(self.n)

    def eval(self, env, args=None):
        return env.get(self.n)

    def cons(self, item):
        return PairObject(item, self)

    def nullp(self):
        return FALSE

    # property lists (really a hash table here).
    def put(self, property, value):
        _PROPERTIES[self.n][property] = value

    def get(self, property):
        try:
            return _PROPERTIES[self.n][property]
        except:
            return FALSE


class StringObject(Evalable):
    def __init__(self, str):
        if isinstance(str, StringObject):
            str = str.string
        self.string = str

    def __repr__(self):
        return `self.string`

    def eval(self, env, args=None):
        return self.string

    def nullp(self):
        if self.string == "":
            return TRUE
        else:
            return FALSE

    def __getitem__(self, index):
        return self.string[index]


class NumberObject(Evalable):
    def __init__(self, value):
        if isinstance(value, NumberObject):
            value = value.v
        self.v = value

    def __repr__(self):
        return `self.v`

    def eval(self, env, args=None):
        return self

    def __cmp__(self, other):
        # if isinstance(other, NumberObject) or isinstance(other, LogicObject):
        if type(self) == type(other):
            if self.v == other.v:
                return 0
            elif self.v > other.v:
                return 1
            else:
                return -1
        else:
            if self.v == other:
                return 0
            elif self.v > other:
                return 1
            else:
                return -1

    def __add__(self, other):
        if type(self) == type(other):
            return NumberObject(self.v + other.v)
        else:
            return self.v + other
    __radd__ = __add__

    def __sub__(self, other):
        if type(self) == type(other):
            return NumberObject(self.v - other.v)
        else:
            return self.v - other
    __rsub__ = __sub__

    def __mul__(self, other):
        if type(self) == type(other):
            return NumberObject(self.v * other.v)
        else:
            return self.v * other
    __rmul__ = __mul__

    def __div__(self, other):
        if type(self) == type(other):
            return NumberObject(self.v / float(other.v))
        else:
            return self.v / float(other)
    __rdiv__ = __div__

    def __mod__(self, other):
        if type(self) == type(other):
            return NumberObject(self.v % other.v)
        else:
            return self.v % other
    __rmod__ = __mod__

    def nullp(self):
        if self.v == 0.0:
            return TRUE
        else:
            return FALSE

class LogicObject(Evalable):
    def __init__(self, value):
        if isinstance(value, NumberObject):
            self.v = value.v
        else:
            self.v = value

    def __repr__(self):
        if self.v == 1.0:
            return '*true*'
        elif self.v == 0.0:
            return '*false*'
        else:
            return "(logic %s)" % self.v

    def __cmp__(self, other):
        #if type(self) == type(other):
        if isinstance(other, LogicObject):
            if self.v == other.v:
                return 0
            elif self.v > other.v:
                return 1
            else:
                return -1
        else:
            if self.v == other:
                return 0
            elif self.v > other:
                return 1
            else:
                return -1

    def __neg__(self):
        return LogicObject(1.0 - self.v)

    def __and__(self, other):
        return LogicObject(min(self.v, other.v))

    def __or__(self, other):
        return LogicObject(max(self.v, other.v))

    def eval(self, env, args=None):
        return self

    def nullp(self):
        return -self

TRUE = LogicObject(1.0)
FALSE = LogicObject(0.0)

class PairObject(Evalable):
    """
    Not quite a list. In real Lisps, all lists are just piled up pairs.
    Not so in PyLisp. Pairs are special case, mostly for association
    lists and the sort.
    """
    def __init__(self, a, d):
        self.a, self.d = a, d

    def __repr__(self):
        if self.d == None:
            return "(%s)" % (self.a, self.d)
        else:
            return "(%s . %s)" % (self.a, self.d)

    def replaca(self, val):
        self.a = val
        return val

    def replacd(self, val):
        if isinstance(val, ListObject):
            return val.cons(self.a)
        else:
            self.d = val
            return val

    def first(self):
        return self.a

    def rest(self):
        return self.d

    def second(self):
        return self.d

    def nullp(self):
        return FALSE


class ListObject(Evalable):
    def __init__(self, lst=None):
        if lst is None:
            self.list = []
        else:
            self.list = lst

    def __repr__(self):
        if self.list == []:
            return "()"
        s = "(%s" % self.list[0]
        for e in self.list[1:]:
            s = s + " %s" % e
        return s + ")"

    def __len__(self):
        return len(self.list)

    def __getitem__(self, i):
        return self.list[i]

    def __and__(self, other):
        if isinstance(other, LogicObject):
            if self.nullp():
                return FALSE & other
            else:
                return TRUE & other

    def first(self):
        return self.list[0]

    def replaca(self, val):
        self.list[0] = val
        return val

    def second(self):
        try:
            return self.list[1]
        except:
            return ListObject([])

    def third(self):
        try:
            return self.list[2]
        except:
            return ListObject([])

    def rest(self):
        try:
            return ListObject(self.list[1:])
        except:
            return ListObject([])

    def replacd(self, val):
        self.list = [self.list[0]] + val.list
        return val

    def cons(self, item):
        n = ListObject(self.list[:])
        n.list.insert(0, item)
        return n

    def append(self, lst):
        if isinstance(lst, ListObject):
            #return ListObject(self.list + lst.list)
            self.list = self.list + lst.list
        else:
            #return ListObject(self.list + lst)
            self.list = self.list + lst

    def nconc(self, lst):
        self.append(lst)
        return self

    def eval(self, env, args=None):
        """
        Code and data look the same in lisp.
        """
        fn = self.list[0].eval(env)
        if isinstance(fn, LambdaObject) or \
           isinstance(fn, MacroObject) or \
           isinstance(fn, FunctionObject) or \
           isinstance(fn, SyntaxObject):
            return fn.eval(env, self.list[1:])
        else:
            raise Error, "%s is not applyable" % fn

    def nullp(self):
        if len(self.list) == 0:
            return TRUE
        else:
            return FALSE

    def iquote(self, env):
        """
        l.iquote(environment) - do the back-tick substitutions
        """
        answer = []
        length = len(self.list)
        i = 0
        while i < length:
            if isinstance(self.list[i], ListObject):
                answer.append(self.list[i].iquote(env))
            elif type(self.list[i]) == types.StringType:
                if self.list[i] == ',':
                    i = i + 1
                    if type(self.list[i]) == types.StringType:
                        if self.list[i] == '@':
                            # splice: `(a b ,@fred) -> (a b a b c)
                            i = i + 1
                            answer = answer + self.list[i].eval(env).list
                        else:
                            answer.append(self.list[i].eval(env))
                    else:
                        answer.append(self.list[i].eval(env))
            else:
                answer.append(self.list[i])
            i = i + 1
        return ListObject(answer)

    def assoc(self, item):
        for pair in self.list:
            if isinstance(pair, PairObject) or isinstance(pair, ListObject):
                key = pair.first()
                if isinstance(key, SymbolObject) and isinstance(item, SymbolObject):
                    if key.n == item.n:
                        return pair.second()
                else:
                    if key == item:
                        return pair.second()
            else:
                raise Error, "assoc: second argument must be list of lists/pairs"
        return FALSE

NIL = ListObject([])

class ObjectObject(Evalable):
    """
    A basic message-passing object orientation for PyLisp
    """
    def __init__(self, name, *attrs, **opts):
        self.name = name

    def __repr__(self):
        return "<object %s>" % id(self.name)

class FunctionObject(Evalable):
    """
    Internal (Python) functions
    """
    def __init__(self, fn):
        self.fn = fn

    def __repr__(self):
        return "<built-in function %s>" % id(self.fn)

    def eval(self, env, args):
        return self.fn(env, args)

    def nullp(self):
        return FALSE

class LambdaObject(Evalable):
    """
    Fuctions defined in PyLisp.
    """
    def __init__(self, bindings, code, env):
        self.bindings = bindings
        self.code = code
        # Remember the defining environment.
        self.env = env

    def eval(self, env, args):
        lisper = env.get('*self*')
        # If the lexical environment in which this was defined is different
        # than the one called from, push that saved environment's values
        # onto the new lambda's environment.
        if self.env:
            lisper.push_e(self.env.e)
        else:
            lisper.push_e()
        # Evaluate the arguments and bind to the correct names.
        i = 0
        n = len(self.bindings)
        while i < n:
            if self.bindings[i].n == "&rest":
                rest = []
                for arg in args[i:]:
                    rest.append(arg.eval(lisper.e))
                lisper.lexical_intern(self.bindings[i + 1].n, ListObject(rest))
                i = i + 1
            else:
                lisper.lexical_intern(self.bindings[i].n, args[i].eval(lisper.e))
            i = i + 1
        # Run the code.
        ans = FALSE
        for code in self.code:
            ans = code.eval(lisper.e)
        lisper.pop_e()
        return ans

    # Mostly transform things like the let into the lambda form, which
    # will speed things up a bit.
    def compile(self):
        pass

    def __repr__(self):
        if len(self.code) == 1:
            return "(lambda %s %s)" % (self.bindings, self.code[0])
        else:
            return "(lambda %s %s)" % (self.bindings, ListObject(['begin'] + self.code))

    def nullp(self):
        return FALSE


class MacroObject(Evalable):
    # (def incf (macro (x) `(+ ,x 1)))
    # ((macro (x) `(+ ,x 1)) swee)
    def __init__(self, bindings, code, env):
        self.bindings = bindings
        self.code = code
        self.env = env                  # defining environment

    def eval(self, env, args):
        lisper = env.get('*self*')
        # If the lexical environment in which this was defined is different
        # than the one called from, push that saved environment's values
        # onto the new macro's environment.
        if self.env:
            lisper.push_e(self.env.e)
        else:
            lisper.push_e()
        # Evaluate the arguments and bind to the correct names: UNEVALUATED.
        i = 0
        n = len(self.bindings)
        while i < n:
            if self.bindings[i].n == "&rest":
                lisper.lexical_intern(self.bindings[i + 1].n, ListObject(args[i:]))
                i = i + 1
            else:
                lisper.lexical_intern(self.bindings[i].n, args[i])
            i = i + 1
        # Run the code.  The first run to expand the macro.
        mcode = []
        for mc in self.code:
            mcode.append(mc.eval(lisper.e))
        # The macro bindings environment is finished.
        lisper.pop_e()
        # Now, run again, this time for real.
        ans = FALSE
        for code in mcode:
            ans = code.eval(lisper.e)
        return ans

    def expand(self, env, args):
        lisper = env.get('*self*')
        if self.env:
            lisper.push_e(self.env.e)
        else:
            lisper.push_e()
        # Evaluate the arguments and bind to the correct names: UNEVALUATED.
        i = 0
        n = len(self.bindings)
        while i < n:
            if self.bindings[i].n == "&rest":
                lisper.lexical_intern(self.bindings[i + 1].n, ListObject(args[i:]))
                i = i + 1
            else:
                lisper.lexical_intern(self.bindings[i].n, args[i])
            i = i + 1
        mcode = []
        for mc in self.code:
            mcode.append(mc.eval(lisper.e))
        lisper.pop_e()
        # The 'begin' turns the (Python) list of code into legally
        # parsable list of Pylisp code.
        return ListObject(mcode).cons('begin')

    def __repr__(self):
        if len(self.code) == 1:
            return "(macro %s %s)" % (self.bindings, self.code[0])
        else:
            # ???
            return "(macro %s %s)" % (self.bindings, ListObject(['begin'] + self.code))

    def nullp(self):
        return FALSE

class SyntaxObject(Evalable):
    """
    Same as the FunctionObject, but this object is expected to handle
    the evaluation of the arguments it is passed.
    """
    def __init__(self, fn):
        self.fn = fn

    def __repr__(self):
        return "<built-in syntax %s>" % id(self.fn)

    def eval(self, env, args):
        return self.fn(env, args)

    def nullp(self):
        return FALSE

# some syntactic sugar for the ' symbol.
QUOTE = SymbolObject('quote')
# and for `
IQUOTE = SymbolObject('i-quote')

class Reader(object):
    def __init__(self, str=None):
        self.str = str
        self.i = 0
        self.pounds = {}
        if str == None:
            self.len = 0
            self.sexpr = []
        else:
            self.len = len(str)
            self.sexpr = self.get_sexpr()

    def add_pound_helper(self, char, helper):
        self.pounds[char] = helper

    def get_token(self):
        if self.i >= self.len:
            return None
        # Munch leading whitespace.
        while self.i < self.len and self.str[self.i] in WS:
            self.i = self.i + 1
        if self.i == self.len:
            return None
        # Now, tokenize.
        if self.str[self.i] == '#':
            # Look ahead to get the second character of the pound escape
            # then sling on the next token for special treatment.
            self.i = self.i + 2
            return self.pounds[self.str[self.i - 1]](self.get_token())
        if self.str[self.i] in SPECIAL:
            self.i = self.i + 1
            return self.str[self.i - 1]
        elif self.str[self.i] == '"':
            # Parse a string.
            str = ""
            self.i = self.i + 1
            while self.str[self.i] != '"' and self.i < self.len:
                if self.str[self.i] == '\\':
                    self.i = self.i + 1
                    spchar = self.str[self.i]
                    if spchar == "n":
                        str = str + "\n"
                    elif spchar == "t":
                        str = str + "\t"
                else:
                    str = str + self.str[self.i]
                self.i = self.i + 1
            # Remove trailing quote
            self.i = self.i + 1
            return StringObject(str)
        else:
            tok = ""
            # First, build the token.
            while self.i < self.len - 1:
                if self.str[self.i] in SYNTAX:
                    break
                else:
                    tok = tok + self.str[self.i]
                    self.i = self.i + 1
            if not self.str[self.i] in SYNTAX:
                tok = tok + self.str[self.i]
                self.i = self.i + 1
            # If the thing is a number, convert it; if it's a string, make it a
            # symbol
            return self.get_simple_token(tok)

    def get_simple_token(tok):
        for number in INT, LONGINT, FLOAT:
            n = number.match(tok)
            if n:
                return NumberObject(_nummap[number](tok))
        return SymbolObject(tok)
    get_simple_token = staticmethod(get_simple_token)


    def get_sexpr(self, str=None):
        if str:
            self.i = 0
            self.str = str
            self.len = len(self.str)
        expr = None
        tok = self.get_token()
        if tok == ')':
            raise Error, "Unexpected ')'"
        elif tok == "(":
            expr = []
            tok = self.get_token()
            while tok != ")":
                if tok == '(':
                    # Start parsing again.
                    self.i = self.i - 1
                    expr.append(self.get_sexpr())
                elif tok == "'":
                    expr.append(ListObject([QUOTE, self.get_sexpr()]))
                elif tok == "`":
                    expr.append(ListObject([IQUOTE, self.get_sexpr()]))
                elif tok == None:
                    raise Error, "unexpected end of expression"
                else:
                    expr.append(tok)
                tok = self.get_token()
            return ListObject(expr)
        elif tok == "'":
            return ListObject([QUOTE, self.get_sexpr()])
        elif tok == "`":
            return ListObject([IQUOTE, self.get_sexpr()])
        else:
            return tok

class UnboundSymbolError(Error):
    pass

class Environment(object):
    def __init__(self, parent=None, bindings=None):
        if bindings:
            self.e = bindings
        else:
            self.e = {}
        # Parent environment.
        self.parent = parent
        if self.parent:
            self.level = self.parent.level + 1
        else:
            self.level = 0
        self.init()

    def init(self):
        """
        Subclass customization code here.
        """
        pass

    def set(self, sym, value):
        """
        Assign a binding in the environment.

        Keeps looking for the symbol in outer environment until found or
        until it gets to the top-level environment.
        """
        if self.e.has_key(sym):
            self.e[sym] = value
        elif self.parent:
            self.parent.set(sym, value)
        else:
            self.e[sym] = value

    def lexical_set(self, sym, value):
        """
        Set a binding in the immediate environment.
        """
        #print "LEXICAL_SET(%i):" % self.level, sym, value
        self.e[sym] = value

    def get(self, sym):
        if not self.e.has_key(sym):
            # Consult the parent environment if the symbol isn't here.
            if self.parent:
                return self.parent.get(sym)
            else:
                raise UnboundSymbolError, sym
        else:
            #print "GET(%i)" % self.level, sym, self.e[sym]
            return self.e[sym]

    def pop(self):
        """
        Throw myself away, returning the parent environment.
        """
        return self.parent

    def push(self, bindings=None):
        """
        Create a new environment.
        """
        return Environment(self, bindings=bindings)

    def __repr__(self):
        s = "\nLevel %s:\n" % self.level
        keys = self.e.keys()
        keys.sort()
        for key in keys:
            if key != "*env*":
                s = s + " %10s: %s\n" % (key, self.e[key])
        if self.parent:
            return s + `self.parent`# + s
        else:
            return s

    def nullp(self):
        return FALSE

class Lisper(object):
    """
    A small lisp environment.
    """
    envData = {
        # The default tiny lisp environment.
        '*self*': ['self'],
        '*env*': ['self.e'],
        '*true*': [TRUE],
        '*false*': [FALSE],
        '*true-enough*': [TRUE],
        '*gensym-string*': [SymbolObject, 'GENSYM@', 'no_self'],
        '*gensym-counter*': [NumberObject, 0, 'no_self'],
        'print': [FunctionObject, 'do_print'],
        'first': [FunctionObject, 'do_first'],
        'car': [FunctionObject, 'do_first'],
        'replaca': [FunctionObject, 'do_replaca'],
        'second': [FunctionObject, 'do_second'],
        'cadr': [FunctionObject, 'do_second'],
        'third': [FunctionObject, 'do_third'],
        'rest': [FunctionObject, 'do_rest'],
        'cdr': [FunctionObject, 'do_rest'],
        'replacd': [FunctionObject, 'do_replacd'],
        'cons': [FunctionObject, 'do_cons'],
        'append': [FunctionObject, 'do_append'],
        'null?': [FunctionObject, 'do_nullp'],
        'list': [FunctionObject, 'do_list'],
        'assoc': [FunctionObject, 'do_assoc'],
        '+': [FunctionObject, 'do_add'],
        '-': [FunctionObject, 'do_sub'],
        '/': [FunctionObject, 'do_div'],
        '%': [FunctionObject, 'do_mod'],
        '*': [FunctionObject, 'do_mul'],
        '>': [FunctionObject, 'do_gt'],
        '>=': [FunctionObject, 'do_ge'],
        '<': [FunctionObject, 'do_lt'],
        '<=': [FunctionObject, 'do_le'],
        '==': [FunctionObject, 'do_eql'],
        'eql': [FunctionObject, 'do_eql'],
        '!=': [FunctionObject, 'do_neq'],
        'not': [FunctionObject, 'do_not'],
        'and': [FunctionObject, 'do_and'],
        'or': [FunctionObject, 'do_or'],
        'logic': [FunctionObject, 'do_logic'],
        'load': [FunctionObject, 'do_read'],
        'gensym': [FunctionObject, 'do_gensym'],
        'eval': [FunctionObject, 'do_eval'],
        'list?': [FunctionObject, 'do_listp'],
        'pair?': [FunctionObject, 'do_pairp'],
        'symbol?': [FunctionObject, 'do_symbolp'],
        'string?': [FunctionObject, 'do_stringp'],
        'number?': [FunctionObject, 'do_numberp'],
        'logic?': [FunctionObject, 'do_logicp'],
        'symbol-name': [FunctionObject, 'do_symbol_name'],
        'top-level': [FunctionObject, 'do_top_level'],
        'the-environment': [FunctionObject, 'do_the_environment'],
        'get-environment': [FunctionObject, 'do_get_environment'],
        'env-get': [FunctionObject, 'do_env_get'],
        'env-set': [FunctionObject, 'do_env_set'],
        'get': [FunctionObject, 'do_get'],
        'put': [FunctionObject, 'do_put'],
        'elt': [FunctionObject, 'do_elt'],
        'apply': [FunctionObject, 'do_apply'],
        'send': [FunctionObject, 'do_send'],
        # Chat with Python.
        #'py-setattr': [FunctionObject, 'do_py_setattr'],
        #'py-getattr': [FunctionObject, 'do_py_getattr'],
        #'py-hash-make': [FunctionObject, 'do_py_hash_make'],
        #'py-hash-get': [FunctionObject, 'do_py_hash_get'],
        #'py-hash-set': [FunctionObject, 'do_py_hash_set'],
        #'py-send': [FunctionObject, 'do_py_send'],
        'py-format': [FunctionObject, 'do_py_format'],
        'py-type': [FunctionObject, 'do_py_type'],
        'py-eval': [FunctionObject, 'do_py_eval'],
        'py-exec': [FunctionObject, 'do_py_eval'],
        'keyword->pyhash': [FunctionObject, 'do_kw_to_pyhash'],
        # macros/syntax
        'begin': [SyntaxObject, 'do_m_begin'],
        'setq': [SyntaxObject, 'do_m_setq'],
        'def': [SyntaxObject, 'do_m_setq'],
        'let': [SyntaxObject, 'do_m_let'],
        'lambda': [SyntaxObject, 'do_m_lambda'],
        'macro': [SyntaxObject, 'do_m_macro'],
        'macro-expand': [SyntaxObject, 'do_m_macro_expand'],
        'quote': [SyntaxObject, 'do_m_quote'],
        'i-quote': [SyntaxObject, 'do_m_iquote'],
        'if': [SyntaxObject, 'do_m_if'],
        'cond': [SyntaxObject, 'do_m_cond'],
        'with-py-hash-env': [SyntaxObject, 'do_m_with_hash'],
        }

    def __init__(self, iostreams=(sys.stdin, sys.stdout, sys.stderr)):
        (self.stdin, self.stdout, self.stderr) = iostreams
        self.r = Reader()
        self.e = Environment()
        for symbol, args in self.envData.items():
            self.prepare_env(symbol, args)
        # Subclasses should override init() to add new functions
        # and syntax.
        self.init()

    def init(self):
        """
        Secondary initialization

        Subclasses should add new functionality to PyLisp in this method.
        """
        pass

    def add_pound_helper(self, char, helper):
        self.r.add_pound_helper(char, helper)

    def prepare_env(self, sym, args):
        if len(args) == 1:
            if args[0] == 'self':
                arg = self
            elif args[0] == 'self.e':
                arg = self.e
            else:
                arg = args[0]
        elif args[-1] == 'no_self':
            klass, param, dummy = args
            arg = klass(param)
        else:
            klass, attr = args
            arg = klass(getattr(self, attr))
        self.intern(sym, arg)

    def get_symbol_type(sym):
        """

        """
        if Lisper.envData.has_key(sym):
            type = Lisper.envData[sym][0]
        else:
            type = SymbolObject
        return type
    get_symbol_type = staticmethod(get_symbol_type)

    def intern(self, sym, val):
        """
        assign a symbol value in the environment
        """
        self.e.set(sym, val)

    def lexical_intern(self, sym, val):
        """
        assign a symbol value in the immediate environment
        """
        self.e.lexical_set(sym, val)

    def lookup(self, sym):
        return self.e.get(sym, UnboundSymbolError)

    def set(self, sym, propery, value):
        if not _PROPERTIES.has_key(sym):
            _PROPERTIES[sym] = {}
        _PROPERTIES[sym][property] = value

    def get(self, sym, property):
        try:
            return _PROPERTIES[sym][property]
        except:
            return None

    def eval(self, form):
        """
        Evaluate a lisp form, returning the value.
        """
        return form.eval(self.e)

    def evalstring(self, str):
        return self.eval(self.r.get_sexpr(str))

    def raw_input(self, prompt) :
        """
        raw_input with pseudo I/O streams.
        """
        if prompt :
            self.stdout.write("%s" % prompt)
            self.stdout.flush()
        line = self.stdin.readline()
        if line[-1] == "\n":
            line = line[:-1]
        return line

    # Code from Brian P Templeton <bpt@tunes.org>.  Now you can enter
    # multi-line sexps from the interactive interface.  *Much* nicer.
    def read_full_sexp(self, line="", parenlevel=0):
        """
        get a complete sexp
        """
        if line != "":
            line = line + " "
        if self.e.level != 0:
            prompt = "lisp %i%s " % (self.e.level, ">" * (parenlevel+1))
        else:
            prompt = "lisp%s " % (">" * (parenlevel+1))
            line = line  + self.raw_input(prompt)
            oparens = 0
            cparens = 0
            for c in line:
                if c == "(":
                    oparens = oparens + 1
                elif c == ")":
                    cparens = cparens + 1
            if oparens > cparens:
                return self.read_full_sexp(line, parenlevel+1)
            else:
                return line

    def read(self, file):
        """
        l.read(file) - read in and evaluate a file of PyLisp code
        """
        f = open(file, "r")
        code = f.readlines()
        f.close()
        code = re.sub(";.*(\n|$)", "", string.join(code))
        sexpr = self.r.get_sexpr(code)
        while sexpr:
            self.eval(sexpr)
            sexpr = self.r.get_sexpr()

    def repl(self):
        """
        Interactive lisp loop.

        A much friendlier version of the read-eval-print loop, care
        of Ole Martin Bjørndalen.
        """
        while 1:
            try:
                line = self.read_full_sexp()
            except EOFError:
                self.stdout.write("\n")
                break
            if not line:
                continue
            if line in ['(quit)', '(bye)']:
                break
            try:
                sexpr = self.r.get_sexpr(line)
                while sexpr:
                    self.stdout.write("\t%s\n" % self.eval(sexpr))
                    sexpr = self.r.get_sexpr()
            except UnboundSymbolError, e:
                self.stderr.write("ERROR: unbound symbol '%s'\n" % e.args[0])
            except:
                import traceback, sys
                traceback.print_exc(self.stderr)

    def repl_d(self):
        """
        l.repl_d() - debugging read-eval-print loop
        """
        # allows access to the Python debugger when something dies
        line = self.raw_input("lisp> ")
        while line and line not in ['(quit)', '(bye)']:
            sexpr = self.r.get_sexpr(line)
            while sexpr:
                self.stdout.write("\t %s\n" % self.eval(sexpr))
                sexpr = self.r.get_sexpr()
            line = self.raw_input("lisp> ")

    def push_e(self, env=None):
        if env:
            self.e = self.e.push(env)
        else:
            self.e = self.e.push()

    def pop_e(self):
        self.e = self.e.pop()

    def unwind_e(self):
        """
        Unroll to the top environment level.
        """
        while self.e.parent:
            self.e = self.e.parent

    def do_print(self, env, args):
        for a in args:
            result = a.eval(env)
            self.stdout.write("%s " % str(result))
        self.stdout.write("\n")
        return TRUE

    def do_first(self, env, args):
        return args[0].eval(env).first()

    def do_replaca(self, env, args):
        return args[0].eval(env).replaca(args[1].eval(env))

    def do_second(self, env, args):
        return args[0].eval(env).second()

    def do_third(self, env, args):
        return args[0].eval(env).third()

    def do_rest(self, env, args):
        return args[0].eval(env).rest()

    def do_replacd(self, env, args):
        return args[0].eval(env).replacd(args[1].eval(env))

    def do_cons(self, env, args):
        return args[1].eval(env).cons(args[0].eval(env))

    def do_append(self, env, args):
        lst = args[0].eval(env)
        for l in args[1:]:
            lst.append(l.eval(env))
        return lst

    def do_nullp(self, env, args):
        if len(args[0].eval(env)) == 0:
            return TRUE
        else:
            return FALSE

    def do_list(self, env, args):
        ans = []
        for n in args:
            ans.append(n.eval(env))
        return ListObject(ans)

    def do_assoc(self, env, args):
        return args[1].eval(env).assoc(args[0].eval(env))

    def do_add(self, env, args):
        ans = args[0].eval(env)
        for n in args[1:]:
            ans = ans + n.eval(env)
        return NumberObject(ans)

    def do_sub(self, env, args):
        ans = args[0].eval(env)
        if args[1:]:
            for n in args[1:]:
                ans = ans - n.eval(env)
        else:
            # (- 5) should negate
            ans = -ans.v
        return NumberObject(ans)

    def do_div(self, env, args):
        ans = args[0].eval(env)
        if args[1:]:
            for n in args[1:]:
                ans = ans / n.eval(env)
        else:
            # (/ 2) - give inverse
            ans = 1 / ans.v
        return NumberObject(ans)

    def do_mod(self, env, args):
        ans = args[0].eval(env)
        for n in args[1:]:
            ans = ans % n.eval(env)
        return NumberObject(ans)

    def do_mul(self, env, args):
        ans = args[0].eval(env)
        for n in args[1:]:
            ans = ans * n.eval(env)
        return NumberObject(ans)

    def do_gt(self, env, args):
        if args[0].eval(env) > args[1].eval(env):
            return TRUE
        else:
            return FALSE

    def do_ge(self, env, args):
        if args[0].eval(env) >= args[1].eval(env):
            return TRUE
        else:
            return FALSE


    def do_lt(self, env, args):
        if args[0].eval(env) < args[1].eval(env):
            return TRUE
        else:
            return FALSE

    def do_le(self, env, args):
        if args[0].eval(env) <= args[1].eval(env):
            return TRUE
        else:
            return FALSE

    def do_eql(self, env, args):
        a = args[0].eval(env)
        b = args[1].eval(env)
        if isinstance(a, SymbolObject) and isinstance(b, SymbolObject):
            if a.n == b.n:
                return TRUE
            else:
                return FALSE
        else:
            if a == b:
                return TRUE
            else:
                return FALSE

    def do_neq(self, env, args):
        if args[0].eval(env) != args[1].eval(env):
            return TRUE
        else:
            return FALSE

    def do_not(self, env, args):
        return -args[0].eval(env)

    def do_and(self, env, args):
        ans = args[0].eval(env)
        for arg in args[1:]:
            ans = ans & arg.eval(env)
            # Short circuit once falsity is known.
            if ans.v == 0.0:
            #if ans.nullp():
                break
        return ans

    def do_or(self, env, args):
        truth = env.get('*true-enough*')
        ans = args[0].eval(env)
        for arg in args[1:]:
            ans = ans | arg.eval(env)
            # Short circuit once truth is known.
            if ans.v >= truth:
                break
        return ans

    # All logic in PyLisp is fuzzy.  If you only use *true* and *false*
    # then you get normal T/F logic.  Once you introduce a fuzzy logic
    # value -- such as (logic 0.34) -- then the fuzziness propagates
    # as appropriate.  The normal lisp notion that anything that isn't
    # nil is true does *not* apply to this lisp.
    def do_logic(self, env, args):
        return LogicObject(args[0].eval(env))

    def do_read(self, env, args):
        self.read(args[0].eval(env))

    # Useful for complex macros.
    def do_gensym(self, env, args):
        env.set('*gensym-counter*', env.get('*gensym-counter*') + 1)
        return SymbolObject("%s%s" % (env.get('*gensym-string*'),
                                      env.get('*gensym-counter*')))

    def do_eval(self, env, args):
        return args[0].eval(env).eval(env)

    def do_listp(self, env, args):
        if isinstance(args[0].eval(env), ListObject):
            return TRUE
        else:
            return FALSE

    def do_pairp(self, env, args):
        if isinstance(args[0].eval(env), PairObject):
            return TRUE
        else:
            return FALSE

    def do_stringp(self, env, args):
        if isinstance(args[0].eval(env), StringObject):
            return TRUE
        else:
            return FALSE

    def do_symbolp(self, env, args):
        if isinstance(args[0].eval(env), SymbolObject):
            return TRUE
        else:
            return FALSE

    def do_numberp(self, env, args):
        if isinstance(args[0].eval(env), NumberObject):
            return TRUE
        else:
            return FALSE

    def do_logicp(self, env, args):
        if isinstance(args[0].eval(env), LogicObject):
            return TRUE
        else:
            return FALSE

    def do_symbol_name(self, env, args):
        sym = args[0].eval(env)
        return StringObject(sym.n)

    def do_top_level(self, env, args):
        self.unwind_e()
        return TRUE

    def do_the_environment(self, env, args):
        return self.e

    def do_get_environment(self, env, args):
        # Yank the environment bundled up with a lambda or macro
        form = args[0].eval(env)
        if isinstance(form, LambdaObject) or isinstance(form, MacroObject):
            return form.env
        else:
            raise Error, "get-environment: must take lambda or macro"

    def do_env_get(self, env, args):
        envform = args[0].eval(env)
        if isinstance(envform, Environment):
            return envform.get(args[1].eval(env).n)
        else:
            raise Error, "env-get: must get environment as first argument"

    def do_env_set(self, env, args):
        envform = args[0].eval(env)
        if isinstance(envform, Environment):
            value = args[2].eval(env)
            envform.set(args[1].eval(env).n, value)
            return value
        else:
            raise Error, "env-set: must get environment as first argument"

    def do_put(self, env, args):
        val = args[2].eval(env)
        args[0].eval(env).put(args[1].eval(env).n, val)
        return val

    def do_get(self, env, args):
        return args[0].eval(env).get(args[1].eval(env).n)

    def do_elt(self, env, args):
        return args[1].eval(env)[args[0].eval(env).v]

    def do_apply(self, env, args):
        # This shuffles the args about a bit, conses the function, then evals.
        return args[1].eval(env).cons(args[0]).eval(env)

    def do_send(self, env, args):
        return None

    def do_py_format(self, env, args):
        eargs = []
        for arg in args[1:]:
            eargs.append(arg.eval(env))
        fmt = args[0].eval(env)
        if isinstance(fmt, StringObject):
            return fmt.string % tuple(eargs)
        elif type(fmt) == types.StringType:
            return fmt % tuple(eargs)
        else:
            raise Error, "py-format: format must be a string"

    def do_py_type(self, env, args):
        """
        (py-type o) - try to convert object o into its Python value
        """
        # This is most useful when trying to extend PyLisp with external
        # Python capabilities.
        o = args[0].eval(env)
        if isinstance(o, NumberObject) or isinstance(o, LogicObject):
            return o.v
        elif isinstance(o, StringObject):
            return o.string
        elif isinstance(o, ListObject):
            return o.list
        else:
            return o

    def do_py_eval(self, env, args):
        """
        (py-eval "python code") - evaluate a python expression
        """
        return eval(args[0].eval(env))

    def do_py_exec(self, env, args):
        """
        (py-exec "python code") - execute python code
        """
        exec(args[0].eval(env))

    # MOVE THIS TO class ListObject!!!!
    def do_kw_to_pyhash(self, env, args):
        """
        (keyword->pyhash '(a b :text "this is cool" :rate 0.53))

        This turns Lisp-style keyword lists into a python dictionary.
        """
        hsh = {}
        margs = args[0].eval(env).list
        n = len(margs)
        i = 0
        while i < n:
            sym = margs[i]
            if isinstance(sym, SymbolObject) and sym.n[0] == ':':
                hsh[sym.n[1:]] = margs[i + 1]
                i = i + 1
            i = i + 1
        return hsh

    # macros/syntax
    def do_m_begin(self, env, args):
        answer = FALSE
        for code in args:
            answer = code.eval(env)
        return answer

    def do_m_setq(self, env, args):
        self.intern(args[0].n, args[1].eval(env))
        return self.e.get(args[0].n)

    def do_m_let(self, env, args):
        """
        Transform the let into a lambda
        (let ((x 15) (y (+ 2 3)) z) code) ==
        ((lambda (x y z) code) 15 (+ 2 3) '())
                 ^^^^^^^       ^^ ^^^^^^^ ^^^
                 bindings         vallist
        """
        bindings = args[0]
        code = args[1:]
        arglist = []
        vallist = []
        # Rip out the binding names and their initializers if they exist.
        for b in bindings:
            if isinstance(b, SymbolObject):
                # bare symbol - no initializer
                arglist.append(b)
                vallist.append(ListObject([QUOTE, ListObject([])]))
            elif isinstance(b, ListObject):
                # list form - symbol and initializer
                arglist.append(b.first())
                vallist.append(b.second())
            else:
                raise Error, "malformed (let ...)"
        # Pull the whole mess together into the lambda form, then eval.
        return ListObject(
            [ListObject([SymbolObject('lambda'), ListObject(arglist)] + code)] +
                          vallist).eval(env)

    def do_m_lambda(self, env, args):
        # (lambda (x y z) (* x y z))
        if self.e == env.get('*env*'):
            #print "NULL DEFINED ENV"
            return LambdaObject(args[0], args[1:], None)
        else:
            #print "LEXICALLY DEFINED ENV"
            return LambdaObject(args[0], args[1:], env)

    def do_m_macro(self, env, args):
        # (def incq (macro (x) `(setq ,x (+ ,x 1)))
        if self.e == env.get('*env*'):
            #print "NULL DEFINED ENV"
            return MacroObject(args[0], args[1:], None)
        else:
            #print "LEXICALLY DEFINED ENV"
            return MacroObject(args[0], args[1:], env)

    def do_m_macro_expand(self, env, args):
        """
        Grab the first/only argument, pull out the first element of
        that list and eval it -- it is a symbol which had better
        resolve to a macro -- expand with the rest of its arguments,
        which have to be ripped out of the argument list to trick
        the expand method into looking like an eval call.  Return
        the result, which is a list of PyLisp code.
        """
        return args[0].first().eval(env).expand(env, args[0].rest())

    def do_m_quote(self, env, args):
        return args[0]

    def do_m_iquote(self, env, args):
        if isinstance(args[0], ListObject):
            return args[0].iquote(env)
        else:
            return args[0]

    def do_m_if(self, env, args):
        bool = args[0].eval(env)
        if isinstance(bool, LogicObject):
            if bool >= env.get('*true-enough*'):
                return args[1].eval(env)
            else:
                if len(args) == 3:
                    return args[2].eval(env)
                else:
                    return bool
        elif hasattr(bool, 'nullp'):
            # Null is false.
            #print "hasattr nullp"
            if args[0].eval(env).nullp() == TRUE:
                if len(args) == 3:
                    return args[2].eval(env)
                else:
                    return bool
            else:
                return args[1].eval(env)
        else:
            # This is also testing for the false case.
            if bool in [0, 0.0, ""]:
                if len(args) == 3:
                    return args[2].eval(env)
                else:
                    return bool
            else:
                return args[1].eval(env)

    def do_m_cond(self, env, args):
        """
        (cond (test0 return0)
              (test1 return1)
              (*true* returnt) )
        """
        for clause in args:
            bool = clause.first().eval(env)
            if isinstance(bool, LogicObject):
                if bool >= env.get('*true-enough*'):
                    return clause.second().eval(env)
            elif hasattr(bool, 'nullp'):
                # Null is false.
                #print "hasattr nullp"
                if bool.nullp() == TRUE:
                    pass
                else:
                    return clause.second().eval(env)
            else:
                # This is also testing for the false case.
                if bool in [0, 0.0, ""]:
                    pass
                else:
                    return clause.second().eval(env)
        return FALSE

    def do_m_with_hash(self, env, args):
        """
        (with-py-hash-env some-hash-table ...)
        """
        hsh = args[0].eval(env)
        # Set up the new environment.
        self.push_e()
        # Intern the new values.
        for (key, value) in hsh.items():
            if type(value) == types.StringType:
                self.intern(key, value)
            else:
                self.intern(key, self.r.get_sexpr(`value`))
        # Eval the code.
        for code in args[1:]:
            answer = code.eval(env)
        # Pop off the hash-table environemt.
        self.pop_e()
        # Return final form value?  Perhaps this should return the final
        # environment somehow, too?  Or require this:
        #   (with-py-has-env some-hash
        #     ...
        #     ...
        #     (the-environment))
        return answer

class SExpression(object):
    """
    A wrapper class for the ListObject, Reader, and Lisper. This class allows
    one to build Lisp expressions, one node at a time. Particularly useful for
    genetic programming.
    """
    def __init__(self, expr=None):
        """

        """
        self.depth = 0
        self.depths = DynamicList()
        self.operatorCount = 0
        self.terminalCount = 0
        self.reader = Reader(str(expr))
        if expr:
            self.sexpr = self.reader.sexpr
        else:
            self.sexpr = ListObject()

    def __len__(self):
        return len(self.sexpr)

    def __iter__(self):
        return iter(self.sexpr)

    def __getitem__(self, index):
        return self.sexpr[index]

    def __repr__(self):
        return repr(self.sexpr)

    def getSize(self):
        """
        The size of the expression is determined by the number of operators
        (functions) it has.
        """
        self.operatorCount = 0
        self._processNodes()
        return self.operatorCount

    def append(self, expr):
        """
        Define append such that when it is called, another s-expression is
        added under the top-most operator in the origial s-expression.
        """
        sexpr = Reader(str(expr)).sexpr
        self.sexpr.append([sexpr])

    def eval(self):
        """
        The lisp environment is needed to do evaluations; this is a convenience
        method which sets that up.
        """
        return Lisper().eval(self.sexpr)

    def setDepths(self, sexpr=None, level=0):
        """
        The depths of an expression get set by interating through each node and
        determining the depth at that point.
        """
        depth = 0
        if not sexpr:
            sexpr = self.sexpr
        for node in sexpr:
            if isinstance(node, ListObject):
                depth = self.setDepths(node, level + 1)
            else:
                depth = level + 1
            self.depths[depth] = 1
        return depth

    def getDepth(self):
        """
        The depth of an expression is a measure based on the number of nodes
        that must be traversed in order to pass from the top-most, root node to
        the deepest node in the expression.
        """
        self.depths = DynamicList()
        self.setDepths()
        return len(self.depths) - 1

    def _processNodes(self, sexpr=None):
        if not sexpr:
            sexpr = self.sexpr
        for node in sexpr:
            #print node, node.__class__, get_type(node)
            if get_type(node) == FunctionObject:
                self.operatorCount += 1
            elif get_type(node) == SymbolObject:
                self.terminalCount += 1
            elif isinstance(node, ListObject):
                self._processNodes(node)

def get_obj(sym):
    """
    A utility function that parses a simple token and returns an appropriate
    PyLisp object representation of that token.
    """
    return Reader.get_simple_token(str(sym))

def get_type(sym):
    """
    A utility function that performs a symbol look-up and returns a lisp
    environment object for that symbol.
    """
    if isinstance(sym, ListObject):
        return ListObject
    return Lisper.get_symbol_type(str(sym))

