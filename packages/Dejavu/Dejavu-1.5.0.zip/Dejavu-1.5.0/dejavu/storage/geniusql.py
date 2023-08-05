"""Classes to model database realities.

Dejavu's Units are storage-agnostic, and the db.StorageManagerDB class is
DB-provider-agnostic. However, each application is deployed in the real
world, where we have to care about shifting column datatypes, indices, and
names. These objects model those realities, and provide StorageManagerDB a
way to create, read, update, and delete them.

The Column, and Index objects present this metadata, and are
intentionally abstract. They should rarely contain any SQL or "smarts"
of any kind, besides the "qname", the quoted name, of the column or index.
At most, subclasses and consumers might put implementation-specific data
into them.

The IndexSet, Table, and Database objects are all dict-like containers,
and therefore have a key for each value. Those keys should equate to things
at the consumer layer; for example, a Database may possess a pair of the
form: {'YoYo': Table('yoyo')} -- the key is the "friendly" name, but the
Table.name is a lowercase version of that, because that's what the database
uses in SQL to refer to that table.

"""

__all__ = [
    # Adapters
    'AdapterFromDB', 'AdapterToSQL', 'TypeAdapter',
    'getCoerceMethod', 'getCoerceName', 'maxfloat_digits', 'maxint_bytes',
    
    # Connections
    'ConnectionFactory', 'ConnectionPool', 'ConnectionWrapper',
    'SingleConnection',
    
    # Decompilation
    'SQLDecompiler', 'Sentinel', 'ConstWrapper', 'cannot_represent', 'kw_arg', 
    
    # DB Objects
    'Database', 'Table', 'Column', 'Index', 'IndexSet',
    
    # Other
    'OutOfConnectionsError',  'TransactionLock',
    ]

import datetime
try:
    import cPickle as pickle
except ImportError:
    import pickle
import Queue


import sys
# Determine max bytes for int on this system.
maxint_bytes = 1
while True:
    if sys.maxint <= 2 ** ((maxint_bytes * 8) - 1):
        break
    maxint_bytes += 1

# Determine max digits for float on this system. Crude but effective.
maxfloat_digits = 2
while True:
    L = (2 ** (maxfloat_digits + 1)) - 1
    if int(float(L)) != L:
        break
    maxfloat_digits += 1
del L
del sys


import time
import threading
from types import FunctionType
import warnings
import weakref


try:
    # Builtin in Python 2.5?
    decimal
except NameError:
    try:
        # Module in Python 2.3, 2.4
        import decimal
    except ImportError:
        decimal = None

try:
    import fixedpoint
except ImportError:
    fixedpoint = None


import dejavu
from dejavu import codewalk, errors
from dejavu.storage import isolation as _isolation


# ---------------------------- TYPE ADAPTERS ---------------------------- #


def getCoerceName(pytype):
    """Return the name of the coercion method for a given Python type."""
    mod = pytype.__module__
    if mod == "__builtin__":
        xform = "%s" % pytype.__name__
    else:
        xform = "%s_%s" % (mod, pytype.__name__)
    xform = xform.replace(".", "_")
    return xform

def getCoerceMethod(adapter, totype, fromtype):
    """Return the coercion method for a given 'from' and 'to' type.
    
    Possible coercion methods are searched in the following order:
      1. Exact match:    coerce       <fromtype> to <totype>
      2. Exact totype:   coerce              any to <totype>
      3. Exact fromtype: coerce       <fromtype> to any
      4. totype.bases:   coerce       <fromtype> to <totype.base1>
                         coerce              any to <totype.base1>
                         coerce       <fromtype> to <totype.base2>...
      5. fromtype.bases: coerce <fromtype.base1> to <totype>
                         coerce <fromtype.base1> to any
                         coerce <fromtype.base2> to <totype>...
    
    If no matching coercion method is found, a TypeError is raised.
    """
    if isinstance(fromtype, str):
        frombases = ()
    else:
        frombases = fromtype.__bases__
        fromtype = getCoerceName(fromtype)
    
    if isinstance(totype, str):
        tobases = ()
    else:
        tobases = totype.__bases__
        totype = getCoerceName(totype)
    
    methods = []
    if fromtype and totype:
        methods.append("coerce_" + fromtype + "_to_" + totype)
    if totype:
        methods.append("coerce_any_to_" + totype)
    if fromtype:
        methods.append("coerce_" + fromtype + "_to_any")
    
    for meth in methods:
        if hasattr(adapter, meth):
            return getattr(adapter, meth)
    
    for base in tobases:
        base = getCoerceName(base)
        if fromtype:
            meth = "coerce_" + fromtype + "_to_" + base
            methods.append(meth)
            if hasattr(adapter, meth):
                return getattr(adapter, meth)
        meth = "coerce_any_to_" + base
        methods.append(meth)
        if hasattr(adapter, meth):
            return getattr(adapter, meth)
    
    for base in frombases:
        base = getCoerceName(base)
        if totype:
            meth = "coerce_" + base + "_to_" + totype
            methods.append(meth)
            if hasattr(adapter, meth):
                return getattr(adapter, meth)
        meth = "coerce_" + base + "_to_any"
        methods.append(meth)
        if hasattr(adapter, meth):
            return getattr(adapter, meth)
    
    raise TypeError("%s -> %s is not handled by %s.  Looked for: %s" %
                    (fromtype, totype, adapter.__class__, ", ".join(methods)))


class AdapterToSQL(object):
    """Coerce Expression constants to SQL.
    
    This base class is designed to work out-of-the-box with PostgreSQL 8.
    """
    
    # You should REALLY check into your DB's encoding and override this.
    encoding = 'utf8'
    
    # Notice these are ordered pairs. Escape \ before introducing new ones.
    # Values in these two lists should be strings encoded with self.encoding.
    escapes = [("'", "''"), ("\\", r"\\")]
    like_escapes = [("%", r"\%"), ("_", r"\_")]
    
    # These are not the same as coerce_bool (which is used on one side of 
    # a comparison). Instead, these are used when the whole (sub)expression
    # is True or False, e.g. "WHERE TRUE", or "WHERE TRUE and 'a'.'b' = 3".
    bool_true = "TRUE"
    bool_false = "FALSE"
    
    def __init__(self):
        self._memoized_methods = {}
    
    def escape_like(self, value):
        """Prepare a string value for use in a LIKE comparison."""
        if not isinstance(value, str):
            value = value.encode(self.encoding)
        # Notice we strip leading and trailing quote-marks.
        value = value.strip("'\"")
        for pat, repl in self.like_escapes:
            value = value.replace(pat, repl)
        return value
    
    def coerce(self, value, dbtype="", pytype=None):
        """Return value, coerced from (optional pytype) to dbtype."""
        if pytype is None:
            pytype = type(value)
        if "(" in dbtype:
            dbtype = dbtype[:dbtype.find("(")]
        
        key = (dbtype, pytype)
        try:
            meth = self._memoized_methods[key]
        except KeyError:
            meth = getCoerceMethod(self, dbtype, pytype)
            self._memoized_methods[key] = meth
        
        return meth(value)
    
    def coerce_NoneType_to_any(self, value):
        return "NULL"
    
    def coerce_bool_to_any(self, value):
        if value:
            return 'TRUE'
        return 'FALSE'
    
    # The great thing about these 3 date coercers is that you can use
    # them with (VAR)CHAR columns just as well as with DATETIME, etc.
    # and comparisons will still work!
    def coerce_datetime_datetime_to_any(self, value):
        return ("'%04d-%02d-%02d %02d:%02d:%02d'" %
                (value.year, value.month, value.day,
                 value.hour, value.minute, value.second))
    
    def coerce_datetime_date_to_any(self, value):
        return "'%04d-%02d-%02d'" % (value.year, value.month, value.day)
    
    def coerce_datetime_time_to_any(self, value):
        return "'%02d:%02d:%02d'" % (value.hour, value.minute, value.second)
    
    def coerce_datetime_timedelta_to_any(self, value):
        float_val = value.days + (value.seconds / 86400.0)
        return repr(float_val)
    
    def _to_TEXT(self, value):
        return "'%s'" % str(value)
    
    coerce_decimal_to_any = str
    coerce_decimal_Decimal_to_any = str
    coerce_decimal_to_TEXT = _to_TEXT
    coerce_decimal_Decimal_to_TEXT = _to_TEXT
    
    def do_pickle(self, value):
        # dumps with protocol 0 uses the 'raw-unicode-escape' encoding,
        # and we take pains not to re-encode it with self.encoding.
        # We can't use protocol 1 or 2 (which would use UTF-8) because
        # that introduces null bytes into the SQL, which is a no-no.
        value = pickle.dumps(value)
        value = self.coerce_str_to_any(value, skip_encoding=True)
        return value
    
    coerce_dict_to_any = do_pickle
    
    coerce_fixedpoint_FixedPoint_to_any = str
    coerce_fixedpoint_FixedPoint_to_TEXT = _to_TEXT
    
    # Very important we use repr here so we get all 17 decimal digits.
    coerce_float_to_any = repr
    coerce_float_to_TEXT = _to_TEXT
    coerce_int_to_any = str
    coerce_int_to_TEXT = _to_TEXT
    coerce_list_to_any = do_pickle
    coerce_long_to_any = str
    coerce_long_to_TEXT = _to_TEXT
    
    def coerce_str_to_any(self, value, skip_encoding=False):
        if not skip_encoding and not isinstance(value, str):
            value = value.encode(self.encoding)
        for pat, repl in self.escapes:
            value = value.replace(pat, repl)
        return "'" + value + "'"
    
    coerce_tuple_to_any = do_pickle
    
    coerce_unicode_to_any = coerce_str_to_any


class AdapterFromDB(object):
    """Coerce incoming values from DB types to Python datatypes.
    
    This base class is designed to work out-of-the-box with PostgreSQL 8.
    """
    
    # You should REALLY check into your DB's encoding and override this.
    encoding = 'utf8'
    
    def __init__(self):
        self._memoized_methods = {}
    
    def coerce(self, value, dbtype, pytype):
        """Return value, coerced from dbtype to pytype."""
        # All columns could conceivably hold NULL => Python None
        if value is None:
            return None
        
        if "(" in dbtype:
            dbtype = dbtype[:dbtype.find("(")]
        
        key = (pytype, dbtype)
        try:
            meth = self._memoized_methods[key]
        except KeyError:
            meth = getCoerceMethod(self, pytype, dbtype)
            self._memoized_methods[key] = meth
        
        return meth(value)
    
    def do_pickle(self, value):
        # Coerce to str for pickle.loads restriction.
        value = self.coerce_any_to_str(value)
        return pickle.loads(value)
    
    coerce_any_to_bool = bool
    
    def coerce_any_to_datetime_datetime(self, value):
        chunks = (value[0:4], value[5:7], value[8:10],
                  value[11:13], value[14:16], value[17:19],
                  value[20:26] or 0)
        return datetime.datetime(*map(int, chunks))
    
    def coerce_any_to_datetime_date(self, value):
        chunks = (value[0:4], value[5:7], value[8:10])
        return datetime.date(*map(int, chunks))
    
    def coerce_any_to_datetime_time(self, value):
        chunks = (value[0:2], value[3:5], value[6:8])
        return datetime.time(*map(int, chunks))
    
    def coerce_any_to_datetime_timedelta(self, value):
        days, seconds = divmod(value, 1)
        return datetime.timedelta(days, int(seconds * 86400))
    
    def coerce_any_to_decimal(self, value):
        return decimal(str(value))
    
    def coerce_any_to_decimal_Decimal(self, value):
        return decimal.Decimal(str(value))
    
    coerce_any_to_dict = do_pickle
    
    def coerce_any_to_fixedpoint_FixedPoint(self, value):
        if (isinstance(value, basestring) or
            decimal and isinstance(value, decimal.Decimal)):
            # Unicode really screws up fixedpoint; for example:
            # >>> fixedpoint.FixedPoint(u'111111111111111111111111111.1')
            # FixedPoint('111111111111111104952008704.00', 2)
            value = str(value)
            
            scale = 0
            atoms = value.rsplit(".", 1)
            if len(atoms) > 1:
                scale = len(atoms[-1])
            return fixedpoint.FixedPoint(value, scale)
        else:
            return fixedpoint.FixedPoint(value)
    
    coerce_any_to_float = float
    coerce_any_to_int = int
    coerce_any_to_list = do_pickle
    coerce_any_to_long = long
    
    def coerce_any_to_str(self, value):
        if isinstance(value, unicode):
            return value.encode(self.encoding)
        else:
            return str(value)
    
    coerce_any_to_tuple = do_pickle
    
    def coerce_any_to_unicode(self, value):
        if isinstance(value, unicode):
            return value
        else:
            return unicode(value, self.encoding)


class TypeAdapter(object):
    """Determine the best database type for a given column + Python type.
    
    This base class is designed to work out-of-the-box with PostgreSQL 8.
    """
    
    # Max binary precision for floating-point columns (= 53 for PostgreSQL 8).
    # Python floats are implemented using C doubles; actual precision
    # depends on platform (but is usually 53 binary digits, see maxfloat_digits).
    # PostgreSQL DOUBLE is 53 binary-digit precision.
    float_max_precision = 53
    
    # Max decimal precision for NUMERIC columns (= 1000 for PostgreSQL 8).
    numeric_max_precision = 1000
    
    # "The actual storage requirement is two bytes for each group of four
    # decimal digits, plus eight bytes overhead." Note we omit the overhead.
    numeric_max_bytes = 500
    
    # This type name will be returned when falling back to a character type
    # from a numeric type which cannot support the desired precision.
    # TEXT is not an SQL standard, but it's common.
    numeric_text_type = "TEXT"
    
    def coerce(self, col, pytype):
        """Return a database type for the given column object and Python type."""
        xform = "coerce_" + getCoerceName(pytype)
        try:
            xform = getattr(self, xform)
        except AttributeError:
            raise TypeError("'%s' is not handled by %s." %
                            (pytype, self.__class__))
        return xform(col)
    
    def float_type(self, precision):
        """Return a datatype which can handle floats of the given binary precision."""
        if precision <= 24:
            return "REAL"
        else:
            return "DOUBLE PRECISION"
    
    def coerce_float(self, col):
        # Note that 'precision' is binary digits, not decimal.
        precision = int(col.hints.get('precision', maxfloat_digits))
        if precision > self.float_max_precision:
            return self.numeric_text_type
        return self.float_type(precision)
    
    def coerce_str(self, col):
        # The bytes hint shall not reflect the usual 4-byte base for varchar.
        bytes = int(col.hints.get('bytes', 255))
        if bytes and bytes <= 255:
            return "VARCHAR(%s)" % bytes
        return "TEXT"
    
    def coerce_dict(self, col):
        return self.coerce_str(col)
    def coerce_list(self, col):
        return self.coerce_str(col)
    def coerce_tuple(self, col):
        return self.coerce_str(col)
    def coerce_unicode(self, col):
        return self.coerce_str(col)
    
    def coerce_bool(self, col): return "BOOLEAN"
    
    def coerce_datetime_datetime(self, col): return "TIMESTAMP"
    def coerce_datetime_date(self, col): return "DATE"
    def coerce_datetime_time(self, col): return "TIME"
    
    # I was seriously disinterested in writing a parser for interval.
    def coerce_datetime_timedelta(self, col):
        return self.coerce_float(col)
    
    def decimal_type(self, colname, precision, scale):
        if precision > self.numeric_max_precision:
            warnings.warn("The precision of '%s' (%s) is greater than the "
                          "maximum numeric precision (%s). Using %s instead."
                          % (colname, precision, self.numeric_max_precision,
                             self.numeric_text_type),
                          errors.StorageWarning)
            return self.numeric_text_type
        if scale > precision:
            scale = precision
        return "NUMERIC(%s, %s)" % (precision, scale)
    
    def coerce_decimal_Decimal(self, col):
        precision = int(col.hints.get('precision', self.numeric_max_precision))
        # Assume most people use decimal for money; default scale = 2.
        scale = int(col.hints.get('scale', 2))
        return self.decimal_type(col.name, precision, scale)
    
    def coerce_decimal(self, col):
        # If decimal ever becomes a builtin. Python 2.5?
        return self.coerce_decimal_Decimal(col)
    
    def coerce_fixedpoint_FixedPoint(self, col):
        # Note that fixedpoint has no theoretical precision limit.
        precision = int(col.hints.get('precision', self.numeric_max_precision))
        # Assume most people use fixedpoint for money; default scale = 2.
        scale = int(col.hints.get('scale', 2))
        return self.decimal_type(col.name, precision, scale)
    
    def int_type(self, bytes):
        """Return a datatype which can handle the given number of bytes."""
        if bytes <= 2:
            return "SMALLINT"
        elif bytes <= 4:
            return "INTEGER"
        elif bytes <= 8:
            # BIGINT is usually 8 bytes
            return "BIGINT"
        else:
            # Anything larger than 8 bytes, use decimal/numeric.
            # For PostgreSQL, "The actual storage requirement is two bytes
            # for each group of four decimal digits, plus eight bytes
            # overhead." Note we omit the overhead in our calculation.
            return "NUMERIC(%s, 0)" % (bytes * 2)
    
    def coerce_long(self, col):
        bytes = int(col.hints.get('bytes', self.numeric_max_bytes))
        if bytes > self.numeric_max_bytes:
            return self.numeric_text_type
        return self.int_type(bytes)
    
    def coerce_int(self, col):
        bytes = int(col.hints.get('bytes', maxint_bytes))
        if bytes > maxint_bytes:
            return self.coerce_long(col)
        return self.int_type(bytes)



# -------------------------- SQL DECOMPILATION -------------------------- #


class ConstWrapper(str):
    """Wraps a constant for use in SQLDecompiler's stack.
    
    When we hit LOAD_CONST while decompiling, we occasionally need to keep
    both the base and the coerced value around (see COMPARE_OP for use
    of ConstWrapper.basevalue).
    """
    def __new__(self, basevalue, coerced_value):
        newobj = str.__new__(ConstWrapper, coerced_value)
        newobj.basevalue = basevalue
        return newobj


# Stack sentinels
class Sentinel(object):
    
    def __init__(self, name):
        self.name = name
    
    def __repr__(self):
        return 'Stack Sentinel: %s' % self.name

kw_arg = Sentinel('Keyword Arg')
# cannot_represent exists so that a portion of an Expression can be
# labeled imperfect. For example, the function dejavu.iscurrentweek
# rarely has an SQL equivalent. All Units (which match the rest of the
# Expression) will be recalled; they can then be compared in expr(unit).
cannot_represent = Sentinel('Cannot Repr')


class SQLDecompiler(codewalk.LambdaDecompiler):
    """Produce SQL from a supplied Expression object.
    
    Attributes of each argument in the signature will be mapped to table
    columns. Keyword arguments should be bound using Expression.bind_args
    before calling this decompiler.
    """
    
    # Some constants are function or class objects,
    # which should not be coerced.
    no_coerce = (FunctionType,
                 type,
                 type(len),       # <type 'builtin_function_or_method'>
                 )
    
    sql_cmp_op = ('<', '<=', '=', '!=', '>', '>=', 'in', 'not in')
    
    def __init__(self, tables, expr, adapter=AdapterToSQL()):
        self.tables = tables
        self.expr = expr
        self.adapter = adapter
        # Cache coerced booleans
        self.T = adapter.coerce_bool_to_any(True)
        self.F = adapter.coerce_bool_to_any(False)
        obj = expr.func
        codewalk.LambdaDecompiler.__init__(self, obj)
    
    def code(self):
        self.imperfect = False
        self.walk()
        # After walk(), self.stack should be reduced to a single string,
        # which is the SQL representation of our Expression.
        result = self.stack[0]
        if result is cannot_represent:
            # The entire expression could not be evaluated.
            result = self.adapter.bool_true
        if result == self.T:
            result = self.adapter.bool_true
        if result == self.F:
            result = self.adapter.bool_false
        return result
    
    def visit_instruction(self, op, lo=None, hi=None):
        # Get the instruction pointer for the current instruction.
        ip = self.cursor - 3
        if hi is None:
            ip += 1
            if lo is None:
                ip += 1
        
        terms = self.targets.get(ip)
        if terms:
            trueval = self.adapter.bool_true
            falseval = self.adapter.bool_false
            clause = self.stack[-1]
            while terms:
                term, oper = terms.pop()
                if term is cannot_represent:
                    # Use TRUE for the term, so all records are returned.
                    term = trueval
                if clause is cannot_represent:
                    # Use TRUE for the clause, so all records are returned.
                    clause = trueval
                
                # Blurg. SQL Server is *so* picky.
                if term == self.T:
                    term = trueval
                elif term == self.F:
                    term = falseval
                if clause == self.T:
                    clause = trueval
                elif clause == self.F:
                    clause = falseval
                
                clause = "(%s) %s (%s)" % (term, oper.upper(), clause)
            
            # Replace TOS with the new clause, so that further
            # combinations have access to it.
            self.stack[-1] = clause
            if self.verbose:
                self.debug("clause:", clause, "\n")
            
            if op == 1:
                # Py2.4: The current instruction is POP_TOP, which means
                # the previous is probably JUMP_*. If so, we're going to
                # pop the value we just placed on the stack and lose it.
                # We need to replace the entry that the JUMP_* made in
                # self.targets with our new TOS.
                target = self.targets[self.last_target_ip]
                target[-1] = ((clause, target[-1][1]))
                if self.verbose:
                    self.debug("newtarget:", self.last_target_ip, target)
    
    def visit_LOAD_DEREF(self, lo, hi):
        raise ValueError("Illegal reference found in %s." % self.expr)
    
    def visit_LOAD_GLOBAL(self, lo, hi):
        raise ValueError("Illegal global found in %s." % self.expr)
    
    def visit_LOAD_FAST(self, lo, hi):
        arg_index = lo + (hi << 8)
        if arg_index < self.co_argcount:
            # We've hit a reference to a positional arg, which in our
            # case implies a reference to a DB table.
            self.stack.append(self.tables[arg_index])
        else:
            # Since lambdas don't support local bindings,
            # any remaining local name must be a keyword arg.
            self.stack.append(kw_arg)
    
    def visit_LOAD_ATTR(self, lo, hi):
        name = self.co_names[lo + (hi << 8)]
        tos = self.stack.pop()
        if isinstance(tos, tuple):
            # The name in question refers to a DB column.
            tablename, table = tos
            col = table[name]
            if col.imperfect_type:
                atom = cannot_represent
                self.imperfect = True
            else:
                atom = '%s.%s' % (tablename, col.qname)
        else:
            # 'tos.name' will reference an attribute of the tos object.
            # Stick the tos and name in a tuple for later processing.
            atom = (tos, name)
        self.stack.append(atom)
    
    def visit_LOAD_CONST(self, lo, hi):
        val = self.co_consts[lo + (hi << 8)]
        if not isinstance(val, self.no_coerce):
            val = ConstWrapper(val, self.adapter.coerce(val))
        self.stack.append(val)
    
    def visit_BUILD_TUPLE(self, lo, hi):
        terms = ", ".join([self.stack.pop() for i in range(lo + hi << 8)])
        self.stack.append("(" + terms + ")")
    
    visit_BUILD_LIST = visit_BUILD_TUPLE
    
    def visit_CALL_FUNCTION(self, lo, hi):
        kwargs = {}
        for i in xrange(hi):
            val = self.stack.pop()
            key = self.stack.pop()
            kwargs[key] = val
        kwargs = [k + "=" + v for k, v in kwargs.iteritems()]
        
        args = []
        for i in xrange(lo):
            arg = self.stack.pop()
            args.append(arg)
        args.reverse()
        
        if kwargs:
            args += kwargs
        
        func = self.stack.pop()
        
        # Handle function objects.
        if isinstance(func, tuple):
            tos, name = func
            dispatch = getattr(self, "attr_" + name, None)
            if dispatch:
                self.stack.append(dispatch(tos, *args))
                return
        else:
            funcname = func.__module__ + "_" + func.__name__
            funcname = funcname.replace(".", "_")
            if funcname.startswith("_"):
                funcname = "func" + funcname
            dispatch = getattr(self, funcname, None)
            if dispatch:
                self.stack.append(dispatch(*args))
                return
        
        self.stack.append(cannot_represent)
        self.imperfect = True
    
    def visit_COMPARE_OP(self, lo, hi):
        op2, op1 = self.stack.pop(), self.stack.pop()
        if op1 is cannot_represent or op2 is cannot_represent:
            self.stack.append(cannot_represent)
            return
        
        op = lo + (hi << 8)
        if op in (6, 7):     # in, not in
            value = self.containedby(op1, op2)
            if op == 7:
                value = "NOT " + value
            self.stack.append(value)
        elif op1 == 'NULL':
            if op in (2, 8):    # '==', is
                self.stack.append(op2 + " IS NULL")
            elif op in (3, 9):  # '!=', 'is not'
                self.stack.append(op2 + " IS NOT NULL")
            else:
                raise ValueError("Non-equality Null comparisons not allowed.")
        elif op2 == 'NULL':
            if op in (2, 8):    # '==', 'is'
                self.stack.append(op1 + " IS NULL")
            elif op in (3, 9):  # '!=', 'is not'
                self.stack.append(op1 + " IS NOT NULL")
            else:
                raise ValueError("Non-equality Null comparisons not allowed.")
        else:
            # Comparison operators for strings are case-sensitive in PG et al.
            self.stack.append(op1 + " " + self.sql_cmp_op[op] + " " + op2)
    
    def binary_op(self, op):
        op2, op1 = self.stack.pop(), self.stack.pop()
        self.stack.append(op1 + " " + op + " " + op2)
    
    def visit_BINARY_SUBSCR(self):
        # The only BINARY_SUBSCR used in Expressions should be kwargs[key].
        name = self.stack.pop()
        tos = self.stack.pop()
        if tos is not kw_arg:
            raise ValueError("Subscript %s of %s object not allowed."
                             % (name, tos))
        # name, since formed in LOAD_CONST, may have extraneous quotes.
        name = name.strip("'\"")
        value = self.expr.kwargs[name]
        if not isinstance(value, self.no_coerce):
            value = ConstWrapper(value, self.adapter.coerce(value))
        self.stack.append(value)
    
    def visit_UNARY_NOT(self):
        op = self.stack.pop()
        if op is cannot_represent:
            self.stack.append(cannot_represent)
        else:
            self.stack.append("NOT (" + op + ")")
    
    # --------------------------- Dispatchees --------------------------- #
    
    def attr_startswith(self, tos, arg):
        return tos + " LIKE '" + self.adapter.escape_like(arg) + "%'"
    
    def attr_endswith(self, tos, arg):
        return tos + " LIKE '%" + self.adapter.escape_like(arg) + "'"
    
    def containedby(self, op1, op2):
        if isinstance(op1, ConstWrapper):
            # Looking for text in a field. Use Like (reverse terms).
            return op2 + " LIKE '%" + self.adapter.escape_like(op1) + "%'"
        else:
            # Looking for field in (a, b, c)
            atoms = [self.adapter.coerce(x) for x in op2.basevalue]
            if atoms:
                return op1 + " IN (" + ", ".join(atoms) + ")"
            else:
                # Nothing will match the empty list, so return none.
                return self.adapter.bool_false
    
    def dejavu_icontainedby(self, op1, op2):
        if isinstance(op1, ConstWrapper):
            # Looking for text in a field. Use Like (reverse terms).
            return ("LOWER(" + op2 + ") LIKE '%" +
                    self.adapter.escape_like(op1).lower() + "%'")
        else:
            # Looking for field in (a, b, c).
            # Force all args to lowercase for case-insensitive comparison.
            atoms = [self.adapter.coerce(x).lower() for x in op2.basevalue]
            return "LOWER(%s) IN (%s)" % (op1, ", ".join(atoms))
    
    def dejavu_icontains(self, x, y):
        return self.dejavu_icontainedby(y, x)
    
    def dejavu_istartswith(self, x, y):
        return "LOWER(" + x + ") LIKE '" + self.adapter.escape_like(y) + "%'"
    
    def dejavu_iendswith(self, x, y):
        return "LOWER(" + x + ") LIKE '%" + self.adapter.escape_like(y) + "'"
    
    def dejavu_ieq(self, x, y):
        return "LOWER(" + x + ") = LOWER(" + y + ")"
    
    def dejavu_now(self):
        return "NOW()"
    
    def dejavu_today(self):
        return "CURRENT_DATE"
    
    def dejavu_year(self, x):
        return "YEAR(" + x + ")"

    def dejavu_month(self, x):
        return "MONTH(" + x + ")"
    
    def dejavu_day(self, x):
        return "DAY(" + x + ")"
    
    def func__builtin___len(self, x):
        return "LENGTH(" + x + ")"



# ------------------------- Connection Factories ------------------------- #


class ConnectionWrapper(object):
    """Connection object wrapper, so it can be used as a weak reference."""
    
    def __init__(self, conn=None):
        self.conn = conn
    
    def __getattr__(self, attr):
        return getattr(self.conn, attr)


class OutOfConnectionsError(errors.DejavuError):
    """Exception raised when a database store has run out of connections."""
    pass


class ConnectionFactory(object):
    """A connection factory which creates a new connection for each request."""
    
    def __init__(self, open, close, retry=5):
        self.open = open
        self.close = close
        self.retry = retry
        self.refs = {}
    
    def __call__(self):
        """Return a connection."""
        for i in xrange(self.retry):
            try:
                conn = self.open()
                w = ConnectionWrapper(conn)
                self.refs[weakref.ref(w, self._release)] = w.conn
                return w
            except OutOfConnectionsError:
                time.sleep(i + 1)
                conn = None
        raise OutOfConnectionsError()
    
    def _release(self, ref):
        """Release a connection."""
        self.close(self.refs.pop(ref))
    
    def shutdown(self):
        """Release all database connections."""
        # Empty self.refs.
        while self.refs:
            ref, conn = self.refs.popitem()
            self.close(conn)


class ConnectionPool(object):
    """A database connection factory which keeps a pool of connections."""
    
    def __init__(self, open, close, size=10, retry=5):
        self.open = open
        self.close = close
        self.refs = {}
        self.pool = Queue.Queue(size)
        self.retry = retry
    
    def __call__(self):
        """Return a connection from the pool."""
        for i in xrange(self.retry):
            try:
                conn = self.pool.get_nowait()
                # Okay, this is freaky. If we wrap here, all goes well.
                # If we wrap on Queue.put(), mysql crashes after 1700
                # or so inserts (when migrating Access tables to MySQL).
                # Go figure.
                w = ConnectionWrapper(conn)
                self.refs[weakref.ref(w, self._release)] = w.conn
                return w
            except Queue.Empty:
                pass
            
            try:
                conn = self.open()
                w = ConnectionWrapper(conn)
                self.refs[weakref.ref(w, self._release)] = w.conn
                return w
            except OutOfConnectionsError:
                time.sleep(i + 1)
                conn = None
        raise OutOfConnectionsError()
    
    def _release(self, ref):
        """Release a connection."""
        conn = self.refs.pop(ref)
        try:
            self.pool.put_nowait(conn)
            return
        except Queue.Full:
            pass
        self.close(conn)
    
    def shutdown(self):
        """Release all database connections."""
        # Empty the pool.
        while True:
            try:
                self.pool.get(block=False)
            except Queue.Empty:
                break
        
        # Empty self.refs.
        while self.refs:
            ref, conn = self.refs.popitem()
            self.close(conn)


class SingleConnection(object):
    """A single database connection for all consumers.
    
    Use this when your database cannot handle multiple connections at once,
    but can handle multiple threads using the same connection.
    """
    
    def __init__(self, open, close):
        self.open = open
        self.close = close
        # Delay opening the connection, because the
        # SM may need to create the database first.
        self._conn = None
    
    def __call__(self):
        """Return our only connection."""
        if self._conn is None:
            self._conn = self.open()
        return self._conn
    
    def shutdown(self):
        """Release all database connections."""
        if self._conn is not None:
            self.close(self._conn)
            self._conn = None



# -------------------------- DATABASE OBJECTS -------------------------- #


class Index:
    """An index on a table column (or columns) in a database."""
    
    def __init__(self, name, qname, tablename, colname, unique=True):
        self.name = name
        self.qname = qname
        self.tablename = tablename
        self.colname = colname
        self.unique = unique
    
    def __repr__(self):
        return ("%s.%s(%r, %r, %r, %r, unique=%r)" %
                (self.__module__, self.__class__.__name__,
                 self.name, self.qname, self.tablename,
                 self.colname, self.unique))
    
    def __copy__(self):
        return self.__class__(self.name, self.qname, self.tablename,
                              self.colname, self.unique)
    copy = __copy__


class IndexSet(dict):
    
    def __new__(cls, table):
        return dict.__new__(cls)
    
    def __init__(self, table):
        dict.__init__(self)
        self.table = table
    
    def alias(self, oldname, newname):
        """Add a new key for the Index with the given, existing key.
        
        Consumer code should call this method when user-supplied index
        names do not match the names in the database. This does not
        remove the old key; both keys may be used to refer to the same
        Index object.
        """
        obj = self[oldname]
        if newname in self:
            dict.__delitem__(self, newname)
        dict.__setitem__(self, newname, obj)
    
    def __setitem__(self, key, index):
        """Drop the specified index."""
        t = self.table
        if t.db is not None:
            t.db.lock("Creating index. Transactions not allowed.")
            try:
                t.db.execute('CREATE INDEX %s ON %s (%s);' %
                             (index.qname, t.qname,
                              t.db.quote(index.colname)))
            finally:
                t.db.unlock()
        dict.__setitem__(self, key, index)
    
    def __delitem__(self, key):
        """Drop the specified index."""
        t = self.table
        if t.db is not None:
            t.db.lock("Dropping index. Transactions not allowed.")
            try:
                t.db.execute('DROP INDEX %s ON %s;' % (self[key].qname, t.qname))
            finally:
                t.db.unlock()
        dict.__delitem__(self, key)


class Column:
    """A column in a table in a database.
    
    name: the SQL name for this table (unquoted).
    qname: the SQL name for this table (quoted).
    dbtype: the database type name (as used in a CREATE TABLE statement).
    default: default value for this column for new rows.
    hints: a dict of implementation hints, such as precision, scale, or bytes.
    key: True if this column is part of the table's primary key.
    
    imperfect_type: if True, signals that we are deliberately using a
        database type other than the default (usually in order to handle
        irregular values, such as huge numbers).
    autoincrement: if True, uses the database's built-in sequencing.
    sequence_name: for databases that use separate statements to create and
        drop sequences, this stores the name of the sequence.
    initial: if autoincrement, holds the initial value for the sequence.
    """
    
    def __init__(self, name, qname, dbtype, default=None, hints=None, key=False):
        self.name = name
        self.qname = qname
        self.dbtype = dbtype
        self.default = default
        if hints is None:
            hints = {}
        self.hints = hints
        self.key = key
        
        # If autoincrement, the initial value should be put in self.initial.
        self.autoincrement = False
        self.sequence_name = None
        self.initial = 0
        self.imperfect_type = False
    
    def __repr__(self):
        return ("%s.%s(%r, %r, dbtype=%r, default=%r, hints=%r, key=%r)" %
                (self.__module__, self.__class__.__name__,
                 self.name, self.qname, self.dbtype,
                 self.default, self.hints, self.key)
                )
    
    def __copy__(self):
        newcol = self.__class__(self.name, self.qname, self.dbtype,
                                self.default, self.hints.copy(), self.key)
        newcol.autoincrement = self.autoincrement
        newcol.initial = self.initial
        newcol.imperfect_type = self.imperfect_type
        return newcol
    copy = __copy__


class Table(dict):
    """A table in a database; a dict of Column objects.
    
    Values in this dict must be instances of Column (or a subclass of it).
    Keys should be consumer-friendly names for each Column value.
    
    name: the SQL name for this table (unquoted).
    qname: the SQL name for this table (quoted).
    db: the database for this table. If None (the default), then changes to
        Table items can be made with impunity. If not None, then appropriate
        ALTER TABLE commands are executed whenever a consumer adds or deletes
        items from the Table, or calls methods like 'rename'. Therefore,
        when creating Table objects from an existing database, you should
        set the 'db' arg late.
    indices: a dict-like IndexSet of Index objects.
    """
    
    indexsetclass = IndexSet
    
    def __new__(cls, name, qname, db=None):
        return dict.__new__(cls)
    
    def __init__(self, name, qname, db=None):
        dict.__init__(self)
        self.name = name
        self.qname = qname
        self.db = db
        self.indices = self.indexsetclass(self)
    
    def __repr__(self):
        name = getattr(self, "name", "<unknown>")
        qname = getattr(self, "qname", "<unknown>")
        return ("%s.%s(%r, %r)" %
                (self.__module__, self.__class__.__name__, name, qname))
    
    def __copy__(self):
        # Don't set db when copying!
        newtable = self.__class__(self.name, self.qname)
        for key, c in self.iteritems():
            dict.__setitem__(newtable, key, c.copy())
        for key, i in self.indices.iteritems():
            dict.__setitem__(newtable.indices, key, i.copy())
        return newtable
    copy = __copy__
    
    def alias(self, oldname, newname):
        """Add a new key for the Column with the given, existing key.
        
        Consumer code should call this method when user-supplied column
        names do not match the names in the database. This does not
        remove the old key; both keys may be used to refer to the same
        Column object.
        """
        obj = self[oldname]
        if newname in self:
            dict.__delitem__(self, newname)
        dict.__setitem__(self, newname, obj)
    
    def _add_column(self, column):
        """Internal function to add the column to the database."""
        coldef = self.db.col_def(column)
        self.db.execute("ALTER TABLE %s ADD COLUMN %s;" % (self.qname, coldef))
    
    def __setitem__(self, key, column):
        if self.db is None:
            dict.__setitem__(self, key, column)
            return
        
        if key in self:
            del self[key]
        
        self.db.lock("Adding property. Transactions not allowed.")
        try:
            if column.autoincrement:
                # This may or may not be a no-op, depending on the DB.
                self.db.create_sequence(self, column)
            self._add_column(column)
            dict.__setitem__(self, key, column)
        finally:
            self.db.unlock()
    
    def _drop_column(self, column):
        """Internal function to drop the column from the database."""
        self.db.execute("ALTER TABLE %s DROP COLUMN %s;" %
                        (self.qname, column.qname))
    
    def __delitem__(self, key):
        if key in self.indices:
            del self.indices[key]
        
        if self.db is None:
            dict.__delitem__(self, key)
            return
        
        self.db.lock("Dropping property. Transactions not allowed.")
        try:
            column = self[key]
            self._drop_column(column)
            if column.autoincrement:
                # This may or may not be a no-op, depending on the DB.
                self.db.drop_sequence(column)
            dict.__delitem__(self, key)
        finally:
            self.db.unlock()
    
    def _rename(self, oldcol, newcol):
        # Override this to do the actual rename at the DB level.
        self.db.execute("ALTER TABLE %s RENAME COLUMN %s TO %s;" %
                        (self.qname, oldcol.qname, newcol.qname))
    
    def rename(self, oldkey, newkey):
        """Rename a Column. This will change the table name in the database."""
        oldcol = self[oldkey]
        
        if self.db is None:
            dict.__delitem__(self, oldkey)
            dict.__setitem__(self, newkey, oldcol)
            return
        
        oldname = oldcol.name
        newname = self.db.column_name(self.name, newkey)
        
        if oldname != newname:
            newcol = oldcol.copy()
            newcol.name = newname
            newcol.qname = self.db.quote(newname)
            self.db.lock("Renaming property. Transactions not allowed.")
            try:
                self._rename(oldcol, newcol)
            finally:
                self.db.unlock()
        
        # Use the superclass calls to avoid DROP COLUMN/ADD COLUMN.
        dict.__delitem__(self, oldkey)
        dict.__setitem__(self, newkey, newcol)


class Database(dict):
    """A dict for managing a set of tables.
    
    Values in this dict must be instances of Table. Keys should be
    consumer-friendly names for each Table value. For example, it's
    easiest to use all lowercase table names in MySQL; however, a
    geniusql consumer might want their code to use TitledNames to
    refer to each table.
    
    When a consumer adds and deletes items from a Database object,
    appropriate CREATE TABLE/DROP TABLE commands are executed.
    This means that a Table object to be added should have all
    of its columns populated before adding it to the Database.
    """
    
    decompiler = SQLDecompiler
    adaptertosql = AdapterToSQL()
    adapterfromdb = AdapterFromDB()
    typeadapter = TypeAdapter()
    
    tableclass = Table
    
    def __new__(cls, name, **kwargs):
        return dict.__new__(cls)
    
    def __init__(self, name, **kwargs):
        self._discover_lock = threading.Lock()
        
        dict.__init__(self)
        for k, v in kwargs.iteritems():
            setattr(self, k, v)
        
        self.name = self.sql_name(name)
        self.qname = self.quote(self.name)
        self.transactions = {}
        self.connect()
        self.discover_dbinfo()
    
    def __repr__(self):
        name = getattr(self, "name", "<unknown>")
        return "%s.%s(%r)" % (self.__module__, self.__class__.__name__, name)
    
    def log(self, msg):
        pass
    
    
    #                              Discovery                              #
    
    def _get_dbinfo(self, conn=None):
        return {}
    
    def discover_dbinfo(self, conn=None):
        """Set attributes on self with actual DB metadata, where possible."""
        for k, v in self._get_dbinfo().iteritems():
            setattr(self, k, v)
    
    def _get_tables(self, conn=None):
        raise NotImplementedError
    
    def _get_table(self, tablename, conn=None):
        # Fallback behavior. This is slow and should be optimized by each DB.
        for t in self._get_tables():
            if t.name == tablename:
                return t
        raise errors.MappingError(tablename)
    
    def _get_columns(self, tablename, conn=None):
        raise NotImplementedError
    
    def _get_indices(self, tablename, conn=None):
        raise NotImplementedError
    
    def _discover_table(self, table, conn=None):
        """Populate the columns and indices of the given Table object."""
        for col in self._get_columns(table.name, conn):
            # Use the superclass call to avoid ALTER TABLE
            if col.name in table:
                dict.__delitem__(table, col.name)
            dict.__setitem__(table, col.name, col)
        
        for idx in self._get_indices(table.name, conn):
            # Use the superclass call to avoid CREATE INDEX
            if idx.name in table.indices:
                dict.__delitem__(table.indices, idx.name)
            dict.__setitem__(table.indices, idx.name, idx)
    
    def discover(self, tablename, conn=None):
        """Attach a new Table from the underlying DB to self (and return it).
        
        Table objects (and their Column and Index subobjects) will be
        added to self using keys that match the database's names.
        Consumers should call the "alias(oldname, newname)" method
        of Database, Table, and IndexSet in order to re-map the
        discovered objects using consumer-friendly names.
        
        If no such table exists, a MappingError should be raised.
        """
        self._discover_lock.acquire()
        try:
            table = self._get_table(tablename)
            
            self._discover_table(table, conn)
            
            # Use the superclass calls to avoid CREATE TABLE
            if table.name in self:
                dict.__delitem__(self, table.name)
            dict.__setitem__(self, table.name, table)
            
            return table
        finally:
            self._discover_lock.release()
    
    def discover_all(self, conn=None):
        """(Re-)populate self (all table items) from the underlying DB.
        
        Table objects (and their Column and Index subobjects) will be
        added to self using keys that match the database's names.
        Consumers should call the "alias(oldname, newname)" method
        of Database, Table, and IndexSet in order to re-map the
        discovered objects using consumer-friendly names.
        
        This method is idempotent, but that doesn't mean cheap. Try not
        to call it very often (once at app startup is usually enough).
        If you already know the names of all the tables you want to
        discover, it's often faster to skip this method and just use
        the discover(tablename) method for each known name instead.
        """
        self._discover_lock.acquire()
        try:
            for table in self._get_tables(conn):
                self._discover_table(table, conn)
                
                # Use the superclass calls to avoid CREATE TABLE
                if table.name in self:
                    dict.__delitem__(self, table.name)
                dict.__setitem__(self, table.name, table)
        finally:
            self._discover_lock.release()
    
    def alias(self, oldname, newname):
        """Add a new key for the Table with the given, existing key.
        
        Consumer code should call this method when user-supplied table
        names do not match the names in the database. This does not
        remove the old key; both keys may be used to refer to the same
        Table object.
        """
        obj = self[oldname]
        if newname in self:
            dict.__delitem__(self, newname)
        dict.__setitem__(self, newname, obj)
    
    def python_type(self, dbtype):
        """Return a Python type which can store values of the given dbtype."""
        raise TypeError("Database type %r could not be converted "
                        "to a Python type." % dbtype)
    
    def isrelatedtype(self, pytype1, pytype2):
        """If values of both types are expressed with the same SQL, return True."""
        if issubclass(pytype1, pytype2) or issubclass(pytype2, pytype1):
            return True
        if issubclass(pytype1, basestring) and issubclass(pytype2, basestring):
            return True
        if ((issubclass(pytype1, int) or issubclass(pytype1, long)) and
            (issubclass(pytype2, int) or issubclass(pytype2, long))):
            return True
        if fixedpoint:
            if decimal:
                if ((issubclass(pytype1, fixedpoint.FixedPoint)
                     or issubclass(pytype1, decimal.Decimal)) and
                    (issubclass(pytype2, fixedpoint.FixedPoint)
                     or issubclass(pytype2, decimal.Decimal))):
                    return True
            else:
                if (issubclass(pytype1, fixedpoint.FixedPoint) and
                    issubclass(pytype2, fixedpoint.FixedPoint)):
                    return True
        else:
            if decimal:
                if (issubclass(pytype1, decimal.Decimal) and
                    issubclass(pytype2, decimal.Decimal)):
                    return True
        return False
    
    
    #                              Container                              #
    
    def col_def(self, column):
        """Return a clause for the given column for CREATE or ALTER TABLE.
        
        This will be of the form "name type [DEFAULT x]".
        
        Most subclasses will override this to add autoincrement support.
        """
        dbtype = column.dbtype
        
        default = column.default or ""
        if default:
            default = self.adaptertosql.coerce(default, dbtype)
            default = " DEFAULT %s" % default
        
        return "%s %s%s" % (column.qname, dbtype, default)
    
    def create_sequence(self, table, column):
        """Create a SEQUENCE for the given column and set its sequence_name."""
        # By default, this does nothing. Databases which require a separate
        # statement to create a sequence generator should override this.
        pass
    
    def drop_sequence(self, column):
        """Drop a SEQUENCE for the given column and remove its sequence_name."""
        # By default, this does nothing. Databases which require a separate
        # statement to drop a sequence generator should override this.
        pass
    
    def __setitem__(self, key, table):
        if key in self:
            del self[key]
        
        # Set table.db to self, which should "turn on"
        # any future ALTER TABLE statements.
        table.db = self
        
        self.lock("Creating storage. Transactions not allowed.")
        try:
            fields = []
            pk = []
            for column in table.itervalues():
                if column.autoincrement:
                    # This may or may not be a no-op, depending on the DB.
                    self.create_sequence(table, column)
                
                fields.append(self.col_def(column))
                if column.key:
                    pk.append(column.qname)
            
            if pk:
                pk = ", PRIMARY KEY (%s)" % ", ".join(pk)
            else:
                pk = ""
            
            self.execute('CREATE TABLE %s (%s%s);' %
                         (table.qname, ", ".join(fields), pk))
            
            for index in table.indices.itervalues():
                self.execute('CREATE INDEX %s ON %s (%s);' %
                             (index.qname, table.qname,
                              self.quote(index.colname)))
            dict.__setitem__(self, key, table)
        finally:
            self.unlock()
    
    def __delitem__(self, key):
        self.lock("Dropping storage. Transactions not allowed.")
        try:
            table = self[key]
            self.execute('DROP TABLE %s;' % table.qname)
            for col in table.itervalues():
                if col.autoincrement:
                    self.drop_sequence(col)
            dict.__delitem__(self, key)
        finally:
            self.unlock()
    
    def _rename(self, oldtable, newtable):
        # Override this to do the actual rename at the DB level.
        raise NotImplementedError
    
    def rename(self, oldkey, newkey):
        """Rename a Table."""
        oldtable = self[oldkey]
        oldname = oldtable.name
        newname = self.table_name(newkey)
        
        if oldname != newname:
            newtable = oldtable.copy()
            newtable.db = self
            newtable.name = newname
            newtable.qname = self.quote(newname)
            self.lock("Renaming storage. Transactions not allowed.")
            try:
                self._rename(oldtable, newname)
            finally:
                self.unlock()
        
        # Use the superclass calls to avoid DROP TABLE/CREATE TABLE.
        dict.__delitem__(self, oldkey)
        dict.__setitem__(self, newkey, newtable)
    
    #                               Naming                               #
    
    sql_name_max_length = 64
    sql_name_caseless = False
    Prefix = ""
    
    def quote(self, name):
        """Return name, quoted for use in an SQL statement."""
        # This base class doesn't use "quote",
        # but most subclasses will.
        return name
    
    def sql_name(self, key):
        """Return the native SQL version of key."""
        if self.sql_name_caseless:
            key = key.lower()
        
        maxlen = self.sql_name_max_length
        if maxlen and len(key) > maxlen:
            warnings.warn("The name '%s' is longer than the maximum of "
                          "%s characters." % (key, maxlen),
                          errors.StorageWarning)
            key = key[:maxlen]
        
        return key
    
    def column_name(self, tablekey, columnkey):
        """Return the SQL column name for the given table and column keys."""
        # If you want to use a map from UnitProperty names
        # to DB column names, override this method (that's why
        # the tablename must be included in the args).
        return self.sql_name(columnkey)
    
    def make_column(self, tablekey, columnkey, pytype, default, hints):
        """Return a Column object from the given table and column keys."""
        name = self.column_name(tablekey, columnkey)
        col = Column(name, self.quote(name), None, default, hints.copy())
        col.dbtype = self.typeadapter.coerce(col, pytype)
        pytype2 = self.python_type(col.dbtype)
        col.imperfect_type = not self.isrelatedtype(pytype, pytype2)
        return col
    
    def table_name(self, key):
        """Return the SQL table name for the given key."""
        # If you want to use a map from Unit class names
        # to DB table names, override this method.
        return self.sql_name(self.Prefix + key)
    
    def make_index(self, tablekey, columnkey):
        name = self.table_name("i" + tablekey + columnkey)
        return Index(name, self.quote(name), self.table_name(tablekey),
                     self.column_name(tablekey, columnkey))
    
    #                              Retrieval                              #
    
    def select(self, tablekey, expr, columnkeys=None, distinct=False):
        """Return an SQL SELECT statement, and an 'imperfect' flag.
        
        imperfect: True or False depending on whether the generated SQL
            perfectly satisfies the given expression.
        """
        t = self[tablekey]
        if columnkeys:
            colnames = [t[x].qname for x in columnkeys]
            if distinct:
                sql = 'SELECT DISTINCT %s FROM %s'
            else:
                sql = 'SELECT %s FROM %s'
            sql = sql % (', '.join(colnames), t.qname)
        else:
            sql = 'SELECT * FROM %s' % t.qname
        
        w, i = self.where(t, expr)
        if len(w) > 0:
            w = " WHERE " + w
        else:
            w = ""
        
        sql += w + ";"
        return sql, i
    
    def where(self, tables, expr):
        """Return an SQL WHERE clause, and an 'imperfect' flag.
        
        tables: a Table object, a list of Table objects,
            or a list of (quoted-name-or-alias, Table) tuples
        
        imperfect: True or False depending on whether the generated SQL
            perfectly satisfies the given expression.
        """
        if not isinstance(tables, list):
            tables = [tables]
        for i, t in enumerate(tables):
            if not isinstance(t, (tuple, list)):
                tables[i] = (t.qname, t)
        
        decom = self.decompiler(tables, expr, self.adaptertosql)
        return decom.code(), decom.imperfect
    
    #                             Connecting                              #
    
    poolsize = 10
    
    def connect(self):
        if self.poolsize > 0:
            self.connection = ConnectionPool(self._get_conn, self._del_conn,
                                             self.poolsize)
        else:
            self.connection = ConnectionFactory(self._get_conn, self._del_conn)
    
    def _get_conn(self):
        """Create and return a connection object."""
        # Override this with the connection call for your DB. Example:
        #     return libpq.PQconnectdb(self.connstring)
        raise NotImplementedError
    
    def _del_conn(self, conn):
        """Close a connection object."""
        # Override this with the close call (if any) for your DB.
        conn.close()
    
    def disconnect(self):
        """Release all database connections."""
        self.connection.shutdown()
    
    def execute(self, query, conn=None):
        """execute(query, conn=None) -> result set."""
        if conn is None:
            conn = self.connection()
        if isinstance(query, unicode):
            query = query.encode(self.adaptertosql.encoding)
        self.log(query)
        return conn.query(query)
    
    def fetch(self, query, conn=None):
        """Return rowdata, columns (name, type) for the given query.
        
        query should be a SQL query in string format
        rowdata will be an iterable of iterables containing the result values.
        columns will be an iterable of (column name, data type) pairs.
        
        This base class uses _sqlite syntax.
        """
        res = self.execute(query, conn)
        return res.row_list, res.col_defs
    
    def create_database(self):
        self.lock("Creating database. Transactions not allowed.")
        try:
            self.execute("CREATE DATABASE %s;" % self.qname)
            self.clear()
        finally:
            self.unlock()
    
    def drop_database(self):
        self.lock("Dropping database. Transactions not allowed.")
        try:
            # Must shut down all connections to avoid
            # "being accessed by other users" error.
            self.connection.shutdown()
            self.execute("DROP DATABASE %s;" % self.qname)
            self.clear()
        finally:
            self.unlock()
    
    #                            Transactions                             #
    
    transaction_key = threading._get_ident
    implicit_trans = False
    
    # The "default_isolation" value should be a value native to the DB.
    default_isolation = None
    
    # The values in "isolation_levels" should match the names of
    # IsolationLevel objects in dejavu.storage.isolation.
    isolation_levels = ["READ UNCOMMITTED", "READ COMMITTED",
                        "REPEATABLE READ", "SERIALIZABLE"]
    
    def get_transaction(self, new=False, isolation=None):
        """Return the (possibly new) connection for the current transaction.
        
        If we are already in a transaction, this returns the connection for
        that transaction. The "current transaction" is determined by a key
        (obtained by a call to self.transaction_key); by default, the key
        is the current thread ID (but subclasses are free to change this).
        
        If there is no "current transaction", a new connection object is
        obtained by calling self.connection (which is usually a connection
        pool object). If self.implicit_trans is True, new connections will
        be associated with self.transaction_key(), and repeated calls to
        get_transaction will then return the same connection object.
        If self.implicit_trans is False, you'll get a new connection
        (from the pool) each time.
        """
        key = self.transaction_key()
        if key in self.transactions:
            conn = self.transactions[key]
            if isinstance(conn, TransactionLock):
                raise conn
        else:
            conn = self.connection()
            if self.implicit_trans or new:
                self.transactions[key] = conn
                if not new:
                    self.start(isolation)
        return conn
    
    def is_lock_error(self, exc):
        """If the given exception instance is a lock timeout, return True.
        
        This should return True for errors which arise from transaction
        locking timeouts; for example, if the database prevents 'dirty
        reads' by raising an error.
        """
        # You should definitely override this for your database.
        return False
    
    def isolate(self, conn, isolation=None):
        """Set the isolation level of the given connection.
        
        If 'isolation' is None, our default_isolation will be used for new
        connections. Valid values for the 'isolation' argument may be native
        values for your particular database. However, it is recommended you
        pass items from the global 'levels' list instead; these will be
        automatically replaced with native values.
        
        For many databases, this must be executed after START TRANSACTION.
        """
        if isolation is None:
            isolation = self.default_isolation
        
        if isinstance(isolation, _isolation.IsolationLevel):
            # Map the given IsolationLevel object to a native value.
            isolation = isolation.name
            if isolation not in self.isolation_levels:
                raise ValueError("IsolationLevel %r not allowed by %s. "
                                 "Try one of %r instead."
                                 % (isolation, self.__class__.__name__,
                                    self.isolation_levels))
        
        # This is SQL92 syntax, and should work with most DB's.
        self.execute("SET TRANSACTION ISOLATION LEVEL %s;" % isolation, conn)
    
    def start(self, isolation=None):
        """Start a transaction. Not needed if self.implicit_trans is True."""
        conn = self.get_transaction(new=True)
        self.execute("START TRANSACTION;", conn)
        self.isolate(conn, isolation)
    
    def rollback(self):
        """Roll back the current transaction, if any."""
        key = self.transaction_key()
        if key in self.transactions:
            self.execute("ROLLBACK;", self.transactions[key])
            del self.transactions[key]
        else:
            # This is critical in order to support polygonal SM structures
            # (same store being called twice by separate proxies).
            pass
    
    def commit(self):
        """Commit the current transaction, if any."""
        key = self.transaction_key()
        try:
            conn = self.transactions.pop(key)
        except KeyError:
            # This is critical in order to support polygonal SM structures
            # (same store being called twice by separate proxies).
            pass
        else:
            self.execute("COMMIT;", conn)
    
    # Change this to 'error' if you don't want autocommit on schema ops.
    lock_contention = 'commit'
    
    def lock(self, msg=None):
        """Deny transactions during schema operations (DDL statements).
        
        Any code which calls this should also call 'unlock' in a try/finally:
        
        db.lock('dropping storage')
        try:
            drop_storage(cls)
        finally:
            db.unlock()
        """
        key = self.transaction_key()
        if key in self.transactions:
            if isinstance(self.transactions[key], TransactionLock):
                return
            if self.lock_contention == 'error':
                raise TransactionLock("Schema operations are not allowed "
                                      "inside transactions.")
            self.commit()
        
        if msg is None:
            msg = "Transactions not allowed at the moment."
        self.transactions[key] = TransactionLock(msg)
    
    def unlock(self):
        """Allow transactions."""
        key = self.transaction_key()
        trans = self.transactions.get(key, None)
        if trans is None:
            return
        if not isinstance(trans, TransactionLock):
            raise TransactionLock("Unlock called inside transaction.")
        del self.transactions[key]


class TransactionLock(Exception):
    """Exception raised when a transaction is requested but not allowed.
    
    This is also used as a sentinel by a Database, to signal that a
    given thread should not start a new transaction because the thread
    is currently performing schema changes (DDL statements).
    """
    pass

