"""First-class Expression objects.

This work, including the source code, documentation
and related data, is placed into the public domain.

The original author is Robert Brewer, Amor Ministries.

THIS SOFTWARE IS PROVIDED AS-IS, WITHOUT WARRANTY
OF ANY KIND, NOT EVEN THE IMPLIED WARRANTY OF
MERCHANTABILITY. THE AUTHOR OF THIS SOFTWARE
ASSUMES _NO_ RESPONSIBILITY FOR ANY CONSEQUENCE
RESULTING FROM THE USE, MODIFICATION, OR
REDISTRIBUTION OF THIS SOFTWARE.

Python evaluates expressions like any other language; however,
the expression itself cannot be 'passed around' easily--that is,
the expression itself is a code block, not a callable. In most cases,
this is not an issue: if an evaluation step needs to be 'first-class',
it's usually wrapped up in a function (sometimes anonymous), and
that function is passed. This allows lazy evaluation, for example.

In some cases, however, we wish to manipulate the actual logic of the
expression:
    1. Inspection. Code might form an expression from user input,
           then take secondary actions depending upon the operands.
    2. Modification. For example, correction of an expression
           if it raises an Exception.
    3. Translation. A common case is converting Python expressions
           into SQL.

It is possible to provide these benefits through some combination
of the standard modules parser and compiler, and/or via the builtins
eval() and exec(). However, these approaches require placing the
expression in a string, which introduces problems of substituting
user data; for example, ("x.Name == r'%s'" % user_data) will break if
user_data contains quote-marks. This is by far not the only example of
the abuses of eval(). Solutions using parser and compiler also tend to
be quite slow in pure Python.

This module takes the approach that the Python developer should be
able to form first-class Expressions directly from Python code.

    "This, even if the rest were true, which it isn't, is patently
     impossible, say the doubters."
       -- The Restaurant at the End of the Universe, Douglas Adams

But we can come close.


Expression formation:

    >>> import logic
    >>> e = logic.Expression(lambda x: not (x.a == 3 and (x.b > 1 or x.b < -10)))
    >>> e
    logic.Expression(lambda x: not ((x.a == 3) and ((x.b > 1) or (x.b < -10))))
    
    You'll notice, in this first example, some extra parentheses in the final
    lambda. The lambda has already undergone an explicit compile/decompile
    step. These differences don't affect the logic in any way, but it's
    impossible to guess the exact original syntax when decompiling.
    
    However, be advised of this IMPORTANT point. When you form an Expression
    from a lambda, that lambda goes through a transformer which EARLY BINDS
    everything it can. If we had included global or free variables in our
    lambda, those would have been replaced with constants when the Expression
    was formed. See codewalk.EarlyBinder for more details.
    
    We *can*, however, use and define arbitrary comparison functions,
    such as containedby and startswith.


Lazy Evaluation:
    >>> e = logic.Expression(lambda x: (x.a == 3) and (x.b > 1 or x.b < -10))
    >>> class DumbObject(object):
    ...     a = 3
    ...     b = 5
    ...     
    >>> pass # Do some other things...
    >>> e(DumbObject())
    True
    
    When calling an Expression, it accepts any object instance(s),
    and returns the truth value of itself, getting any named attributes
    from the passed-in object(s). Notice that the passed-in objects do not
    need to be instantiated prior to the construction of the Expression.


Late binding of arguments (lazier yet!):
    >>> e = logic.Expression(lambda x, **kw: x.a == kw['Size'])
    >>> class DumbObject(object):
    ...     a = 3
    ...     
    >>> pass # Do some other things...
    >>> e(DumbObject(), Size=3)
    True
    >>> e.bind_args(Size=3)
    >>> e(DumbObject())
    True
    
    If the lambda possesses a **kwargs argument in its signature, that
    dictionary may be used to pass in late-bound locals. They may either
    be passed when calling the Expression, or may be bound to the
    Expression using the 'bind_args' method. If both are provided,
    the passed-in kwargs will overwrite any bound kwargs.


Derivation (Decompilation) and Translation:
    'Deriving' is the opposite of 'parsing'. The codewalk.LambdaDecompiler
    class walks a function or code object and produces equivalent Python
    code in a string.
    
    >>> e = logic.Expression(lambda x: x.a == 3 and (x.b > 1 or x.b < -10))
    >>> codewalk.LambdaDecompiler(e.func).code()
    'lambda x: not ((x.a == 3) and ((x.b > 1) or (x.b < -10)))'
    
    However, we are not limited to Python statements of our Expression!
    Another decompiler might produce our Expression in another language;
    this example produces a WHERE clause for SQL (a declarative language!):
    
    >>> e = logic.Expression(lambda x: x.Group == '3' and
                             x.Date > datetime.date(2004, 2, 14) and
                             x.Name.endswith('_'))
    >>> ADOSQLDecompiler(e).code()
    "([Group] = '3' and [Date] > #2/14/2004#) and [Name] Like '%\\_'"

Pickling:
    The Expression object includes custom pickling code (__getstate__ and
    __setstate__). You might notice that the function itself is *not*
    pickled; instead, its code() method is called, which produces a
    string representation of the function (decompilation). This makes
    pickled Expressions much more stable across Python versions than,
    say, storing the function's co_code. However, this presents a problem
    when the Expression is unpickled: the function must be eval'ed and
    run through an EarlyBinder again. When this occurs (in __setstate__),
    some of the free variables which were present in func_globals at the
    time of pickling may not be present when the Expression is unpickled.
    For example, an Expression which is built in myapp.py may include
    a datetime.date object in its co_consts. When that Expression is
    unpickled, its function is eval'ed within this module, not within
    myapp.py; since this module does not import 'datetime', it will not
    be included in the func_globals of the reconstituted function, and
    codewalk.EarlyBinder will fail on LOAD_GLOBAL.
    
    Therefore, code which uses this module must determine which objects
    will be referenced as Expressions are unpickled. Any that are neither
    builtins nor in this module's globals() need to be injected into this
    module, so they can be referenced in eval() when the Expression is
    unpickled.

"""

from dejavu import codewalk
from types import CodeType, FunctionType

# Globals which assist in unpickling. If they're not present (can't be
# imported), that's OK--someone might want to build an app which
# doesn't use fixedpoints, for example.
import datetime

try:
    import fixedpoint
    from fixedpoint import FixedPoint
except ImportError:
    pass

try:
    import decimal
    from decimal import Decimal
except ImportError:
    pass


class Aggregator(codewalk.Rewriter):
    """Combine two code objects into one."""
    
    def __init__(self, obj):
        codewalk.Rewriter.__init__(self, obj)
        self.instr_index = [None] * len(self._bytecode)
    
    def combine(self, obj, conjunction):
        obj = codewalk.Rewriter(obj)
        bytecode = map(ord, obj.co_code)
        newtarget = len(bytecode)
        
        self._bytecode.pop()      # RETURN_VALUE
        self._bytecode.extend([conjunction, newtarget & 0xFF, newtarget >> 8])
        self._bytecode.append(1)  # POP_TOP
        self._bytecode.extend(bytecode)
        self.instr_index[-1:] = [obj] * (newtarget + 4)
        
        # Expand self.co_argcount, co_nlocals if needed.
        self.co_argcount = max(self.co_argcount, obj.co_argcount)
        self.co_nlocals = max(self.co_nlocals, obj.co_nlocals)
        
        # Expand self.co_varnames list if needed.
        for i, name in enumerate(obj.co_varnames):
            if i >= len(self.co_varnames):
                self.co_varnames.append(name)
        
        # Add the **kwargs flag if present
        if obj.co_flags & 0x08:
            self.co_flags |= 0x08
        
        # Add the *args flag if present
        if obj.co_flags & 0x04:
            self.co_flags |= 0x04
    
    def and_combine(self, obj):
        self.combine(obj, 111)
    
    def or_combine(self, obj):
        self.combine(obj, 112)
    
    def visit_LOAD_ATTR(self, lo, hi):
        src = self.instr_index[self.cursor]
        if src:
            value = src.co_names[lo + (hi << 8)]
            newindex = self.name_index(value)
            self.newcode[-2:] = [newindex & 0xFF, newindex >> 8]
    
    def visit_LOAD_CONST(self, lo, hi):
        src = self.instr_index[self.cursor]
        if src:
            value = src.co_consts[lo + (hi << 8)]
            newindex = self.const_index(value)
            self.newcode[-2:] = [newindex & 0xFF, newindex >> 8]


class Expression(object):
    """A filter for objects."""
    
    def __init__(self, func=None, kwtypes=None):
        """Expression(func, [kwtypes]={}). func(obj, [**kw]) must return bool.
        
        func: a function, with one positional arg and optional keyword args,
            which must return bool. If func is None, it is initialized to
            lambda x: True
        kwtypes: a dictionary of {keyword: type} pairs.
        """
        if func is None:
            func = lambda x: True
        self._load_func(func)
        if kwtypes is None:
            kwtypes = {}
        self.kwtypes = kwtypes
        self.kwargs = {}
    
    def _load_func(self, func):
        # Early-bind as much as possible.
        binder = codewalk.EarlyBinder(func, bind_late=[datetime.datetime.now,
                                                       datetime.date.today])
        self.func = binder.function()
    
    def code(self):
        return codewalk.LambdaDecompiler(self.func).code()
    
    def __repr__(self):
        return 'logic.Expression(%s)' % self.code()
    
    def __and__(self, other):
        """Logical-and this Expression with another."""
        if not isinstance(other, Expression):
            raise TypeError("'%s' is not an Expression" % other)
        ag = Aggregator(self.func)
        ag.and_combine(other.func)
        agfunc = ag.function()
        return Expression(agfunc)
    __add__ = __and__
    
    def __or__(self, other):
        """Logical-or this Expression with another."""
        if not isinstance(other, Expression):
            raise TypeError("'%s' is not an Expression" % other)
        ag = Aggregator(self.func)
        ag.or_combine(other.func)
        agfunc = ag.function()
        return Expression(agfunc)
    
    def bind_args(self, **kwargs):
        self.kwargs = {}
        self.kwargs.update(kwargs)
    
    def evaluate(self, *args, **kwargs):
        kw = {}
        kw.update(self.kwargs)
        kw.update(kwargs)
        return self.func(*args, **kw)
    __call__ = evaluate
    
    def __getstate__(self):
        return (self.code(), self.kwtypes, self.kwargs)
    
    def __setstate__(self, state):
        if len(state) == 2:
            # Older versions of Expression had a 2-tuple.
            func, self.kwtypes = state
            self.kwargs = {}
        else:
            func, self.kwtypes, self.kwargs = state
        # The most difficult thing about Expressions is unpickling.
        # Any func_globals at the time of pickling are lost, so any
        # late-bound objects must be available at this point. Any
        # such objects need to be injected into logic's globals()
        # if you want them to be available here.
        f = eval(func)
        self._load_func(f)


def filter(**kwargs):
    """Form an Expression from keyword arguments.
    
    Allows you to write:
        e = logic.filter(a=3, b=1)
    ...instead of:
        e = logic.Expression(lambda x: x.a == 3 and x.b == 1)
    """
    co, names, consts = [], ['x', ], [None, ]
    i = 0
    for key, val in kwargs.iteritems():
        i += 1
        names.append(key)
        consts.append(val)
        co += [124, 0, 0,
               105, i, 0,
               100, i, 0,
               106, 2, 0,
               111, 0, 0,
               1,
               ]
    if kwargs:
        # pop extraneous final JUMP and POP_TOP.
        del co[-4:]
    co.append(83)
    
    # Figure JUMP targets
    for op in range(len(co)):
        if co[op] == 111:
            co[op + 1] = (len(co) - 4) - op
    
    # Form code object and function.
    # code(argcount, nlocals, stacksize, flags, codestring,
    #      constants, names, varnames,
    #      filename, name, firstlineno, lnotab[, freevars[, cellvars]])
    co = CodeType(1, 1, 2, 67, ''.join(map(chr, co)),
                  tuple(consts), tuple(names), ('x', ),
                  '', '<lambda>', 1, '')
    func = FunctionType(co, {})
    return Expression(func)


def comparison(attr, cmp_op, criteria):
    """Form an Expression lambda x: x.attr cmp_op criteria.
    
    Allows you to write:
        e = logic.comparison('Size', cmp_op_index, 4)
    ...instead of:
        e = logic.Expression(lambda x: x.Size <= 4)
    
    This allows one to pass dynamic, isolated arguments, without having
    to construct a lambda out of them first.
    """
    # cmp_op (from opcode):
    # ('<', '<=', '==', '!=', '>', '>=', 'in', 'not in', 'is',
    #  'is not', 'exception match', 'BAD')
    if cmp_op < 0 or cmp_op > 11:
        raise ValueError("The cmp_op argument must be between 0 and 11")
    
    if not isinstance(attr, str):
        attr = str(attr)
    names = ('x', attr)
    
    consts = (None, criteria)
    co = [124, 0, 0,
          105, 1, 0,
          100, 1, 0,
          106, cmp_op, 0,
          83,
          ]
    
    # Form code object and function.
    # code(argcount, nlocals, stacksize, flags, codestring,
    #      constants, names, varnames,
    #      filename, name, firstlineno, lnotab[, freevars[, cellvars]])
    co = CodeType(1, 1, 2, 67, ''.join(map(chr, co)),
                  consts, names, ('x',), '', '<lambda>', 1, '')
    func = FunctionType(co, {})
    return Expression(func)

