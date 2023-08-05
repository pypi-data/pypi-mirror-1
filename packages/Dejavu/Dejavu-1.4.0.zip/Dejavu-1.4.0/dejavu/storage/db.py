"""Base classes and tools for writing database Storage Managers.

Unit type -> [SQL repr ->] DB -> incoming Python value -> Unit type


DATA TYPES
==========
Since Dejavu relies on external database servers for its persistence,
Python datatypes must be converted to column types in the DB. When writing
a StorageManager, you should make sure that your type conversions can handle
at least the following limitations. If possible, implement the type with no
limits. Also, follow UnitProperty.hints['bytes'] where possible. A value
of zero for hints['bytes'] implies no limit. If no value is given, try to
assume no limit, although you may choose whatever default size you wish
(255 is common for strings).
"""

import datetime

try:
    # Builtin in Python 2.5?
    decimal
except NameError:
    try:
        # Module in Python 2.3, 2.4
        import decimal
    except ImportError:
        pass

try:
    import fixedpoint
except ImportError:
    pass

try:
    import cPickle as pickle
except ImportError:
    import pickle

import Queue
import threading
import time
from types import FunctionType
import warnings
import weakref


import dejavu
from dejavu import codewalk, logic, storage, LOGCONN, LOGSQL, xray


def getCoerceName(value, valuetype=None):
    mod = valuetype.__module__
    if mod == "__builtin__":
        xform = "coerce_%s" % valuetype.__name__
    else:
        xform = "coerce_%s_%s" % (mod, valuetype.__name__)
    xform = xform.replace(".", "_")
    return xform

def getCoerceMethod(obj, value, valuetype=None):
    if valuetype is None:
        valuetype = type(value)
    
    meth = getCoerceName(value, valuetype)
    if hasattr(obj, meth):
        return getattr(obj, meth)
    
    methods = []
    for base in valuetype.__bases__:
        meth = getCoerceName(value, base)
        methods.append(meth)
        if hasattr(obj, meth):
            return getattr(obj, meth)
    
    raise TypeError("'%s' is not handled by %s.  Looked for: %s " %
                    (valuetype, obj.__class__, ",".join(methods)))


class FieldTypeAdapter(object):
    """For a Python type, return the SQL column type name.
    
    This base class is designed to work out-of-the-box with PostgreSQL 8.
    """
    
    # 1000 is the max precision for NUMERIC columns for PostgreSQL 8.
    # Override in subclasses.
    numeric_max_precision = 1000
    
    def coerce(self, cls, key):
        """coerce(cls, key) -> SQL typename for valuetype."""
        valuetype = cls.property_type(key)
        mod = valuetype.__module__
        if mod == "__builtin__":
            xform = "coerce_%s" % valuetype.__name__
        else:
            xform = "coerce_%s_%s" % (mod, valuetype.__name__)
        xform = xform.replace(".", "_")
        try:
            xform = getattr(self, xform)
        except AttributeError:
            raise TypeError("'%s' is not handled by %s." %
                            (valuetype, self.__class__))
        return xform(cls, key)
    
    def coerce_float(self, cls, key):
        prop = getattr(cls, key)
        bytes = int(prop.hints.get(u'bytes', '8'))
        if bytes < 5:
            # In MySQL, REAL is still probably 8 bytes. Meh.
            return u"REAL"
        else:
            # Python floats are implemented using C doubles;
            # actual precision depends on platform. PostgreSQL
            # DOUBLE is 8 bytes (15 decimal-digit precision).
            return u"DOUBLE PRECISION"
    
    def coerce_str(self, cls, key):
        # The bytes hint shall not reflect the usual 4-byte base for varchar.
        prop = getattr(cls, key)
        bytes = int(prop.hints.get(u'bytes', '0'))
        if bytes:
            return u"VARCHAR(%s)" % bytes
        else:
            # TEXT is not an SQL standard, but it's common.
            return u"TEXT"
    
    def coerce_dict(self, cls, key):
        return self.coerce_str(cls, key)
    def coerce_list(self, cls, key):
        return self.coerce_str(cls, key)
    def coerce_tuple(self, cls, key):
        return self.coerce_str(cls, key)
    def coerce_unicode(self, cls, key):
        return self.coerce_str(cls, key)
    
    def coerce_bool(self, cls, key): return u"BOOLEAN"
    
    def coerce_datetime_datetime(self, cls, key): return u"TIMESTAMP"
    def coerce_datetime_date(self, cls, key): return u"DATE"
    def coerce_datetime_time(self, cls, key): return u"TIME"
    
    # I was seriously disinterested in writing a parser for interval.
    def coerce_datetime_timedelta(self, cls, key):
        return self.coerce_float(cls, key)
    
    def coerce_decimal_Decimal(self, cls, key):
        prop = getattr(cls, key)
        precision = int(prop.hints.get('precision', '0'))
        if precision == 0:
            precision = decimal.getcontext().prec
        if precision > self.numeric_max_precision:
            warnings.warn("Decimal precision %s > maximum %s for %s.%s, "
                          "using %s. Values may be stored incorrectly."
                          % (precision, self.numeric_max_precision,
                             cls.__name__, key, self.__class__.__name__),
                          dejavu.StorageWarning)
            precision = self.numeric_max_precision
        # Assume most people use decimal for money; default scale = 2.
        scale = int(prop.hints.get(u'scale', 2))
        return u"NUMERIC(%s, %s)" % (precision, scale)
    
    def coerce_decimal(self, cls, key):
        # If decimal ever becomes a builtin. Python 2.5?
        return self.coerce_decimal_Decimal(cls, key)
    
    def coerce_fixedpoint_FixedPoint(self, cls, key):
        prop = getattr(cls, key)
        precision = int(prop.hints.get('precision', '0'))
        if precision == 0:
            precision = self.numeric_max_precision
        # Assume most people use decimal for money; default scale = 2.
        scale = int(prop.hints.get(u'scale', 2))
        return u"NUMERIC(%s, %s)" % (precision, scale)
    
    def coerce_long(self, cls, key):
        prop = getattr(cls, key)
        bytes = int(prop.hints.get(u'bytes', 0))
        if bytes <= 4:
            return self.coerce_int(cls, key)
        elif bytes <= 8:
            # BIGINT is usually 8 bytes
            return "BIGINT"
        # Anything larger than 8 bytes, use decimal/numeric.
        if bytes > self.numeric_max_precision:
            warnings.warn("Long bytes %s > maximum %s for %s.%s, "
                          "using %s. Values may be stored incorrectly."
                          % (bytes, self.numeric_max_precision,
                             cls.__name__, key, self.__class__.__name__),
                          dejavu.StorageWarning)
            bytes = self.numeric_max_precision
        return "NUMERIC(%s, 0)" % bytes
    
    def coerce_int(self, cls, key):
        prop = getattr(cls, key)
        bytes = int(prop.hints.get(u'bytes', '4'))
        if bytes == 1:
            return "BOOLEAN"
        elif bytes == 2:
            return "SMALLINT"
##        elif bytes == 3:
##            return "MEDIUMINT"
        else:
            return u"INTEGER"


class AdapterToSQL(object):
    """Coerce Expression constants to SQL.
    
    This base class is designed to work out-of-the-box with PostgreSQL 8.
    """
    
    # Notice these are ordered pairs. Escape \ before introducing new ones.
    escapes = [("'", "''"), ("\\", r"\\")]
    like_escapes = [("%", r"\%"), ("_", r"\_")]
    
    # These are not the same as coerce_bool (which is used on one side of 
    # a comparison). Instead, these are used when the whole (sub)expression
    # is True or False, e.g. "WHERE TRUE", or "WHERE TRUE and 'a'.'b' = 3".
    bool_true = "TRUE"
    bool_false = "FALSE"
    
    def escape_like(self, value):
        """Prepare a string value for use in a LIKE comparison."""
        # Notice we strip leading and trailing quote-marks.
        value = value.strip("'\"")
        for pat, repl in self.like_escapes:
            value = value.replace(pat, repl)
        return value
    
    def coerce(self, value, valuetype=None):
        """coerce(value, valuetype=None) -> value, coerced by valuetype."""
        meth = getCoerceMethod(self, value, valuetype)
        return meth(value)
    
    def tostr(self, value):
        return str(value)
    
    def coerce_NoneType(self, value):
        return "NULL"
    
    def coerce_bool(self, value):
        if value:
            return 'TRUE'
        return 'FALSE'
    
    # The great thing about these 3 date coercers is that you can use
    # them with (VAR)CHAR columns just as well as with DATETIME, etc.
    # and comparisons will still work!
    def coerce_datetime_datetime(self, value):
        return (u"'%04d-%02d-%02d %02d:%02d:%02d'" %
                (value.year, value.month, value.day,
                 value.hour, value.minute, value.second))
    
    def coerce_datetime_date(self, value):
        return u"'%04d-%02d-%02d'" % (value.year, value.month, value.day)
    
    def coerce_datetime_time(self, value):
        return u"'%02d:%02d:%02d'" % (value.hour, value.minute, value.second)
    
    def coerce_datetime_timedelta(self, value):
        float_val = value.days + (value.seconds / 86400.0)
        return repr(float_val)
    
    coerce_decimal = tostr
    coerce_decimal_Decimal = tostr
    
    def do_pickle(self, value):
        return self.coerce_str(pickle.dumps(value))
    
    coerce_dict = do_pickle
    
    coerce_fixedpoint_FixedPoint = tostr
    coerce_float = tostr
    coerce_int = tostr
    
    coerce_list = do_pickle
    
    coerce_long = tostr
    
    def coerce_str(self, value):
        for pat, repl in self.escapes:
            value = value.replace(pat, repl)
        return "'" + value + "'"
    
    coerce_tuple = do_pickle
    
    coerce_unicode = coerce_str


class AdapterFromDB(object):
    """Coerce incoming values from DB types to Dejavu datatypes.
    
    You might notice that we pass coltype around a lot, but don't
    refer to it in this base class. It's there so subclasses can
    make decisions about coercion when they don't have control over
    the types of database columns, and must make do with legacy
    databases implementations.
    
    This base class is designed to work out-of-the-box with PostgreSQL 8.
    """
    
    def coerce(self, value, coltype, valuetype=None):
        """coerce(value, coltype, valuetype=None) -> value, coerced by valuetype."""
        if value is None:
            return None
        
        meth = getCoerceMethod(self, value, valuetype)
        return meth(value, coltype)
    
    def consume(self, unit, key, value, coltype):
        try:
            expectedType = unit.__class__.property_type(key)
            value = self.coerce(value, coltype, expectedType)
            unit._properties[key] = value
        except UnicodeDecodeError, x:
            x.reason += "[%s][%s][%s]" % (key, value, coltype)
            raise
        except Exception, x:
            x.args += (key, value, coltype)
            raise
    
    def do_pickle(self, value, coltype):
        # Coerce to str for pickle.loads restriction.
        value = str(value)
        return pickle.loads(value)
    
    def coerce_bool(self, value, coltype):
        return bool(value)
    
    def coerce_datetime_datetime(self, value, coltype):
        chunks = (value[0:4], value[5:7], value[8:10],
                  value[11:13], value[14:16], value[17:19])
        return datetime.datetime(*map(int, chunks))
    
    def coerce_datetime_date(self, value, coltype):
        chunks = (value[0:4], value[5:7], value[8:10])
        return datetime.date(*map(int, chunks))
    
    def coerce_datetime_time(self, value, coltype):
        chunks = (value[0:2], value[3:5], value[6:8])
        return datetime.time(*map(int, chunks))
    
    def coerce_datetime_timedelta(self, value, coltype):
        days, seconds = divmod(value, 1)
        return datetime.timedelta(days, int(seconds * 86400))
    
    def coerce_decimal(self, value, coltype):
        return decimal(str(value))
    
    def coerce_decimal_Decimal(self, value, coltype):
        return decimal.Decimal(str(value))
    
    coerce_dict = do_pickle
    
    def coerce_fixedpoint_FixedPoint(self, value, coltype):
        return fixedpoint.FixedPoint(value)
    
    def coerce_float(self, value, coltype):
        return float(value)
    
    def coerce_int(self, value, coltype):
        return int(value)
    
    coerce_list = do_pickle
    
    def coerce_long(self, value, coltype):
        return long(value)
    
    def coerce_str(self, value, coltype):
        return str(value)
    
    coerce_tuple = do_pickle
    
    def coerce_unicode(self, value, coltype):
        # You should REALLY check into your DB's encoding and override this.
        return unicode(value, "utf8")


# -------------------------- SQL DECOMPILATION -------------------------- #

class ConstWrapper(unicode):
    """Wraps a constant for use in SQLDecompiler's stack.
    
    When we hit LOAD_CONST while decompiling, we occasionally need to keep
    both the base and the coerced value around (see COMPARE_OP for use
    of ConstWrapper.basevalue).
    """
    def __new__(self, basevalue, coerced_value):
        newobj = unicode.__new__(ConstWrapper, coerced_value)
        newobj.basevalue = basevalue
        return newobj
    
    def __str__(self):
        return str(self)
    
    def __unicode__(self):
        return self
    
    def __repr__(self):
        return self


class TableRef:
    def __init__(self, classname):
        self.classname = classname

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
    """SQLDecompiler(classnames, expr, sm, adapter=AdapterToSQL()).
    
    Produce SQL from a supplied Expression object, with a lambda of the form:
        lambda x, **kw: ...
    
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
    
    def __init__(self, classnames, expr, sm, adapter=AdapterToSQL()):
        self.classnames = classnames
        self.expr = expr
        self.adapter = adapter
        self.sm = sm
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
        if result == self.adapter.coerce_bool(True):
            result = self.adapter.bool_true
        if result == self.adapter.coerce_bool(False):
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
                    term = trueval
                if clause is cannot_represent:
                    clause = trueval
                
                # Blurg. SQL Server is *so* picky.
                if term == self.adapter.coerce_bool(True):
                    term = trueval
                elif term == self.adapter.coerce_bool(False):
                    term = falseval
                if clause == self.adapter.coerce_bool(True):
                    clause = trueval
                elif clause == self.adapter.coerce_bool(False):
                    clause = falseval
                
                clause = "(%s) %s (%s)" % (term, oper.upper(), clause)
            
            # Replace TOS with the new clause, so that further
            # combinations have access to it.
            self.stack[-1] = clause
            self.debug("clause:", clause, "\n")
            
            if op == 1:
                # Py2.4: The current instruction is POP_TOP, which means
                # the previous is probably JUMP_*. If so, we're going to
                # pop the value we just placed on the stack and lose it.
                # We need to replace the entry that the JUMP_* made in
                # self.targets with our new TOS.
                target = self.targets[self.last_target_ip]
                target[-1] = ((clause, target[-1][1]))
                self.debug("newtarget:", self.last_target_ip, target)
    
    def visit_LOAD_DEREF(self, lo, hi):
        raise ValueError("Illegal reference found in %s." % self.expr)
    
    def visit_LOAD_GLOBAL(self, lo, hi):
        raise ValueError("Illegal global found in %s." % self.expr)
    
    def visit_LOAD_FAST(self, lo, hi):
        arg_index = lo + (hi << 8)
        if arg_index < self.co_argcount:
            self.stack.append(TableRef(self.classnames[arg_index]))
        else:
            self.stack.append(kw_arg)
    
    def visit_LOAD_ATTR(self, lo, hi):
        name = self.co_names[lo + (hi << 8)]
        tos = self.stack.pop()
        if isinstance(tos, TableRef):
            atom = self.sm.column_name(tos.classname, name, full=True)
        else:
            # tos.name will reference an attribute of the tos object.
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
            if op == 2:
                self.stack.append(op2 + " IS NULL")
            elif op == 3:
                self.stack.append(op2 + " IS NOT NULL")
            else:
                raise ValueError("Non-equality Null comparisons not allowed.")
        elif op2 == 'NULL':
            if op == 2:
                self.stack.append(op1 + " IS NULL")
            elif op == 3:
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
            return op1 + " IN (" + ", ".join(atoms) + ")"
    
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
    
    def func__builtin___len(self, x):
        return "LENGTH(" + x + ")"


class ConnectionWrapper(object):
    def __init__(self, conn=None):
        self.conn = conn
    
    def __getattr__(self, attr):
        return getattr(self.conn, attr)


class UnitClassWrapper(object):
    
    def __init__(self, wclass, sm):
        self.cls = wclass
        self.sm = sm
        
        wclsname = wclass.__name__
        self.tablename = sm.table_name(wclsname)
        self.alias = ""
    
    def columns(self):
        wclass = self.cls
        
        # Place the identifier properties first
        # in case others depend upon them.
        idnames = [prop.key for prop in wclass.identifiers]
        keys = idnames + [k for k in wclass.properties() if k not in idnames]
        cols = [(wclass, k) for k in keys]
        colnames = ['%s.%s' % (self.alias or self.tablename,
                               self.sm.column_name(wclass.__name__, k))
                    for k in keys]
        return cols, colnames
    
    def _joinname(self):
        if self.alias:
            return "%s AS %s" % (self.tablename, self.alias)
        else:
            return self.tablename
    joinname = property(_joinname, doc=("Table name for use in "
                                            "JOIN clause (read-only)."))
    
    def association(self, classes):
        for other in classes:
            ua = self.cls._associations.get(other.cls.__name__, None)
            if ua:
                nearClass = self.alias or self.tablename
                farClass = other.alias or other.tablename
                return ua, nearClass, farClass
            ua = other.cls._associations.get(self.cls.__name__, None)
            if ua:
                nearClass = other.alias or other.tablename
                farClass = self.alias or self.tablename
                return ua, nearClass, farClass
        return None


class StorageManagerDB(storage.StorageManager):
    """StoreManager to save and retrieve Units using a DB."""
    
    sql_name_max_length = 64
    sql_name_caseless = False
    close_connection_method = 'close'
    use_asterisk_to_get_all = False
    
    decompiler = SQLDecompiler
    typeAdapter = FieldTypeAdapter()
    toAdapter = AdapterToSQL()
    fromAdapter = AdapterFromDB()
    debug_connections = False
    
    def __init__(self, name, arena, allOptions={}):
        storage.StorageManager.__init__(self, name, arena, allOptions)
        
        # Adapter Overrides
        def get_adapter_option(name):
            adapter_class = allOptions.get(name)
            if isinstance(adapter_class, basestring):
                adapter_class = xray.classes(adapter_class)
            return adapter_class
        
        adapter = get_adapter_option(u'Type Adapter')
        if adapter: self.typeAdapter = adapter
        adapter = get_adapter_option(u'To Adapter')
        if adapter: self.toAdapter = adapter
        adapter = get_adapter_option(u'From Adapter')
        if adapter: self.fromAdapter = adapter
        
        self.pool_size = int(allOptions.get(u'Pool Size', '10'))
        
        self.refs = {}
        if self.pool_size > 0:
            self.pool = Queue.Queue(self.pool_size)
        else:
            self.pool = None
        self.retry = 5
        self.threaded = True
        
        self.prefix = allOptions.get(u'Prefix', u"djv")
        self.reserve_lock = threading.Lock()
        
        ec = {}
        for prop in allOptions.get(u'Expanded Columns', '').split(","):
            if prop:
                cls, type = [x.strip() for x in prop.split(":", 1)]
                lastdot = cls.rfind(".")
                clsname, key = cls[:lastdot], cls[lastdot + 1:]
                ec[(clsname, key)] = type
        self.expanded_columns = ec
    
    #                               Naming                               #
    
    def sql_name(self, name, quoted=True):
        """The name, escaped for SQL."""
        if self.sql_name_caseless:
            name = name.lower()
        
        maxlen = self.sql_name_max_length
        if maxlen and len(name) > maxlen:
            warnings.warn("The name '%s' is longer than the maximum of "
                          "%s characters." % (name, maxlen),
                          dejavu.StorageWarning)
            name = name[:maxlen]
        
        # This base class doesn't use the "quoted" arg,
        # but most subclasses will.
        return name
    
    def column_name(self, classname, name, full=False, quoted=True):
        """The column name, escaped for SQL. If full, include tablename."""
        # If you want to use a map from UnitProperty names
        # to DB column names, override this method.
        name = self.sql_name(name, quoted=quoted)
        if not full:
            return name
        
        alias = getattr(classname, "alias", None)
        if alias is None:
            tname = self.table_name(classname, quoted=quoted)
        else:
            tname = (classname.alias or classname.tablename)
        return '%s.%s' % (tname, name)
    
    def table_name(self, name, quoted=True):
        """The table name, escaped for SQL."""
        # If you want to use a map from Unit class names
        # to DB table names, override this method.
        return self.sql_name(self.prefix + name, quoted=quoted)
    
    #                             Connecting                              #
    
    def _get_conn(self):
        # Override this with the connection call for your DB. Example:
        #     return libpq.PQconnectdb(self.connstring)
        raise NotImplementedError
    
    def connection(self):
        if not self.threaded:
            # Place a single 'conn' entry in self.refs.
            try:
                return self.refs['conn']
            except KeyError:
                self.refs['conn'] = conn = self._get_conn()
                return conn
        
        retry = 0
        while True:
            if self.pool is not None:
                try:
                    conn = self.pool.get_nowait()
                    # Okay, this is freaky. If we wrap here, all goes well.
                    # If we wrap on Queue.put(), mysql crashes after 1700
                    # or so inserts (when migrating Access tables to MySQL).
                    # Go figure.
                    w = ConnectionWrapper(conn)
                    self.refs[weakref.ref(w, self.release)] = w.conn
                    self.arena.log("-->get %s" % self.__class__.__name__,
                                   LOGCONN)
                    return w
                except Queue.Empty:
                    pass
            
            try:
                conn = self._get_conn()
                w = ConnectionWrapper(conn)
                self.refs[weakref.ref(w, self.release)] = w.conn
                self.arena.log("create %s" % self.__class__.__name__, LOGCONN)
                return w
            except OutOfConnectionsError:
                retry += 1
                if retry < self.retry:
                    time.sleep(retry * 1)
                    conn = None
                    continue
                raise OutOfConnectionsError()
    
    def release(self, ref):
        # This method should only be called if self.threaded is True
        conn = self.refs.pop(ref)
        
        if self.pool is not None:
            try:
                self.pool.put_nowait(conn)
                self.arena.log("<--put %s" % self.__class__.__name__, LOGCONN)
                return
            except Queue.Full:
                pass
        
        getattr(conn, self.close_connection_method)()
        self.arena.log("___close___ %s" % self.__class__.__name__, LOGCONN)
    
    def shutdown(self):
        # Empty the pool.
        if self.pool:
            while True:
                try:
                    self.pool.get(True, 0.5)
                except Queue.Empty:
                    break
        
        # Empty self.refs.
        while self.refs:
            ref, conn = self.refs.popitem()
            getattr(conn, self.close_connection_method)()
    
    def select(self, cls, expr, fields=None, distinct=False):
        clsname = cls.__name__
        tablename = self.table_name(clsname)
        if fields:
            fields = [self.column_name(clsname, x) for x in fields]
            if distinct:
                sql = u'SELECT DISTINCT %s FROM %s'
            else:
                sql = u'SELECT %s FROM %s'
            sql = sql % (u', '.join(fields), tablename)
        else:
            sql = u'SELECT * FROM %s' % tablename
        
        w, i = self.where((clsname,), expr)
        if len(w) > 0:
            w = u" WHERE " + w
        else:
            w = u""
        sql += w + ";"
        return sql, i
    
    def where(self, classnames, expr):
        decom = self.decompiler(classnames, expr, self, self.toAdapter)
        return decom.code(), decom.imperfect
    
    def execute(self, query, conn=None):
        """execute(query, conn=None) -> result set."""
        if conn is None:
            conn = self.connection()
        self.arena.log(query, LOGSQL)
        return conn.query(query.encode('utf8'))
    
    def fetch(self, query, conn=None):
        """fetch(query, conn=None) -> rowdata, columns.
        
        rowdata will be an iterable of iterables containing the result values.
        columns will be an iterable of (column name, data type) pairs.
        
        This base class uses SQLite3 syntax.
        """
        res = self.execute(query, conn)
        return res.row_list, res.col_defs
    
    def recall(self, cls, expr=None):
        clsname = cls.__name__
        
        if expr is None:
            expr = logic.Expression(lambda x: True)
        sql, imperfect = self.select(cls, expr)
        data, col_defs = self.fetch(sql)
        if data:
            columns = dict([(col[0], (index, col[1])) for index, col
                            in enumerate(col_defs)])
            
            # Get specs on properties. Put the identifier properties
            # first, in case other fields depend upon them.
            # See load_expanded, for example.
            props = []
            idnames = [prop.key for prop in cls.identifiers]
            for key in idnames + [x for x in cls.properties() if x not in idnames]:
                index, ftype = columns[self.column_name(clsname, key, quoted=False)]
                subtype = self.expanded_columns.get((clsname, key))
                props.append((key, index, ftype, subtype))
            
            consume = self.fromAdapter.consume
            for row in data:
                unit = cls()
                for key, index, ftype, subtype in props:
                    value = row[index]
                    if subtype:
                        self.load_expanded(unit, key, subtype)
                    else:
                        consume(unit, key, value, ftype)
                
                # If our SQL is imperfect, don't yield it to the
                # caller unless it passes expr(unit).
                if (not imperfect) or expr(unit):
                    unit.cleanse()
                    yield unit
    
    def reserve(self, unit):
        """reserve(unit). -> Reserve a persistent slot for unit.
        
        Notice in particular that we do not use the auto-number or
        sequence generation capabilities within some databases, etc.
        The identifiers should be supplied by UnitSequencers via reserve().
        """
        cls = unit.__class__
        clsname = cls.__name__
        tablename = self.table_name(clsname)
        self.reserve_lock.acquire()
        try:
            if not unit.sequencer.valid_id(unit.identity()):
                # Examine all existing IDs and grant the "next" one.
                id_fields = [self.column_name(clsname, prop.key)
                             for prop in cls.identifiers]
                data, cols = self.fetch(u'SELECT %s FROM %s;' %
                                        (', '.join(id_fields), tablename))
                if data:
                    # sqlite 2, for example, has empty cols tuple if no data.
                    coerce = self.fromAdapter.coerce
                    coltypes = [cols[x][1] for x in xrange(len(cols))]
                    expectedTypes = [prop.type for prop in cls.identifiers]
                    newdata = []
                    for row in data:
                        newrow = []
                        for x, cell in enumerate(row):
                            newrow.append(coerce(cell, coltypes[x],
                                                 expectedTypes[x]))
                        newdata.append(newrow)
                    data = newdata
                    del newdata
                cls.sequencer.assign(unit, data)
                del data
                del cols
            
            fields = []
            values = []
            for key in cls.properties():
                subtype = self.expanded_columns.get((clsname, key))
                if subtype:
                    self.save_expanded(unit, key, subtype)
                else:
                    val = self.toAdapter.coerce(getattr(unit, key))
                    fields.append(self.column_name(clsname, key))
                    values.append(val)
            
            fields = u", ".join(fields)
            values = u", ".join(values)
            self.execute('INSERT INTO %s (%s) VALUES (%s);' %
                         (tablename, fields, values))
            unit.cleanse()
        finally:
            self.reserve_lock.release()
    
    def id_clause(self, unit):
        clsname = unit.__class__.__name__
        col = self.column_name
        c = self.toAdapter.coerce
        idnames = [prop.key for prop in unit.identifiers]
        return " AND ".join(["%s = %s" % (col(clsname, key),
                                          c(getattr(unit, key)))
                             for key in idnames])
    
    def save(self, unit, forceSave=False):
        """save(unit, forceSave=False) -> Update storage from unit's data."""
        if unit.dirty() or forceSave:
            cls = unit.__class__
            clsname = cls.__name__
            
            parms = []
            idnames = [prop.key for prop in cls.identifiers]
            for key in cls.properties():
                if key not in idnames:
                    subtype = self.expanded_columns.get((clsname, key))
                    if subtype:
                        self.save_expanded(unit, key, subtype)
                    else:
                        val = self.toAdapter.coerce(getattr(unit, key))
                        parms.append('%s = %s' %
                                     (self.column_name(clsname, key), val))
            
            if parms:
                sql = ('UPDATE %s SET %s WHERE %s;' %
                       (self.table_name(clsname), u", ".join(parms),
                        self.id_clause(unit)))
                self.execute(sql)
            unit.cleanse()
    
    def save_expanded(self, unit, key, subtype):
        """save_expanded(unit, key, subtype). Save list in separate table."""
        unitcls = unit.__class__
        id = "_".join(map(str, unit.identity()))
        table = self.table_name("_%s_%s_%s" % (unitcls.__name__, id, key))
        
        # Just drop the old table and start with a new one.
        try:
            self.execute(u"DROP TABLE %s;" % table)
        except:
            pass
        
        val = getattr(unit, key)
        if val is None:
            # Don't create a new table at all. This will signal
            # recall() to set the attribute to None on load.
            pass
        else:
            ftype = getattr(self.typeAdapter, "coerce_" + subtype)(unitcls, key)
            self.execute(u"CREATE TABLE %s (EXPVAL %s);" % (table, ftype))
            
            for v in val:
                self.execute(u"INSERT INTO %s (EXPVAL) VALUES ('%s');"
                             % (table, self.toAdapter.coerce(v)))
    
    def load_expanded(self, unit, key, subtype):
        """load_expanded(unit, key, subtype). Load list from separate table."""
        unitcls = unit.__class__
        id = "_".join(map(str, unit.identity()))
        table = self.table_name("_%s_%s_%s" % (unitcls.__name__, id, key))
        try:
            data, col_defs = self.fetch(u"SELECT EXPVAL FROM %s" % table)
        except:
            values = None
        else:
            coltype = col_defs[0][1]
            coercer = getattr(self.fromAdapter, "coerce_" + subtype)
            values = [coercer(row[0], coltype) for row in data]
            
            expected_type = unitcls.property_type(key)
            values = expected_type(values)
        
        # Set the attribute directly to avoid __set__ overhead.
        unit._properties[key] = values
    
    def destroy(self, unit):
        """destroy(unit). Delete the unit."""
        if self.use_asterisk_to_get_all:
            star = " *"
        else:
            star = ""
        self.execute(u'DELETE%s FROM %s WHERE %s;' %
                     (star, self.table_name(unit.__class__.__name__),
                      self.id_clause(unit)))
    
    def view(self, cls, fields, expr=None):
        """view(cls, fields, expr=None) -> All value-tuples for given fields."""
        if expr is None:
            expr = logic.Expression(lambda x: True)
        
        sql, imperfect = self.select(cls, expr, fields)
        if imperfect:
            # ^%$#@! There's no way to handle imperfect queries without
            # creating all involved Units, which defeats the purpose of
            # view, which was a speed issue more than anything else.
            warnings.warn("The requested view() query for %s Units "
                          "cannot produce perfect SQL with a %s datasource. "
                          "It may take an absurd amount of time to run, "
                          "since each unit must be fully-formed. %s"
                          % (cls.__name__, self.__class__.__name__, expr),
                          dejavu.StorageWarning)
            for unit in self.recall(cls, expr):
                # Use tuples for hashability
                yield tuple([getattr(unit, f) for f in fields])
        else:
            data, columns = self.fetch(sql)
            actualTypes = [x[1] for x in columns]
            expectedTypes = [cls.property_type(x) for x in fields]
            
            coerce = self.fromAdapter.coerce
            # Use tuples for hashability
            for row in data:
                yield tuple([coerce(val, actualTypes[i], expectedTypes[i])
                             for i, val in enumerate(row)])
    
    def distinct(self, cls, fields, expr=None):
        """distinct(cls, fields, expr=None) -> Distinct values for given fields."""
        if expr is None:
            expr = logic.Expression(lambda x: True)
        
        sql, imperfect = self.select(cls, expr, fields, distinct=True)
        if imperfect:
            # ^%$#@! There's no way to handle imperfect queries without
            # creating all involved Units, which defeats the purpose of
            # distinct, which was a speed issue more than anything.
            warnings.warn("The requested distinct() query for %s Units "
                          "cannot produce perfect SQL with a %s datasource. "
                          "It may take an absurd amount of time to run, "
                          "since each unit must be fully-formed. %s"
                          % (cls.__name__, self.__class__.__name__, expr),
                          dejavu.StorageWarning)
            vals = {}
            for unit in self.recall(cls, expr):
                # Must use tuples for hashability
                val = tuple([getattr(unit, f) for f in fields])
                vals[val] = None
            return vals.keys()
        else:
            data, columns = self.fetch(sql)
            actualTypes = [x[1] for x in columns]
            expectedTypes = [cls.property_type(x) for x in fields]
            
            coerce = self.fromAdapter.coerce
            # Must use inner tuples for hashability in Sandbox.distinct()
            return [tuple([coerce(val, actualTypes[i], expectedTypes[i])
                           for i, val in enumerate(row)])
                     for row in data]
    
    def join(self, unitjoin):
        cls1, cls2 = unitjoin.class1, unitjoin.class2
        if isinstance(cls1, dejavu.UnitJoin):
            name1 = self.join(cls1)
            classlist1 = iter(cls1)
        else:
            # cls1 is a Unit class wrapper.
            name1 = cls1.joinname
            classlist1 = [cls1]
        
        if isinstance(cls2, dejavu.UnitJoin):
            name2 = self.join(cls2)
            classlist2 = iter(cls2)
        else:
            # cls2 is a Unit class wrapper.
            name2 = cls2.joinname
            classlist2 = [cls2]
        
        j = {None: "INNER", True: "LEFT", False: "RIGHT"}[unitjoin.leftbiased]
        
        # Find an association between the two halves.
        ua = None
        for clsA in classlist1:
            ua = clsA.association(classlist2)
            if ua:
                ua, nearClass, farClass = ua
                break
        if ua is None:
            msg = ("No association found between %s and %s." % (name1, name2))
            raise dejavu.AssociationError(msg)
        near = '%s.%s' % (nearClass, self.column_name(nearClass, ua.nearKey))
        far = '%s.%s' % (farClass, self.column_name(farClass, ua.farKey))
        
        return "(%s %s JOIN %s ON %s = %s)" % (name1, j, name2, near, far)
    
    def multiselect(self, classes, expr):
        
        # Create a new unitjoin tree where each class is wrapped.
        # Then we can tag the wrappers with metadata with impunity.
        seen = {}
        aliascount = [0]
        
        def wrap(unitjoin):
            cls1, cls2 = unitjoin.class1, unitjoin.class2
            if isinstance(cls1, dejavu.UnitJoin):
                wclass1 = wrap(cls1)
            else:
                wclass1 = UnitClassWrapper(cls1, self)
                if cls1 in seen:
                    aliascount[0] += 1
                    wclass1.alias = "t%d" % aliascount[0]
                else:
                    seen[cls1] = None
            if isinstance(cls2, dejavu.UnitJoin):
                wclass2 = wrap(cls2)
            else:
                wclass2 = UnitClassWrapper(cls2, self)
                if cls2 in seen:
                    aliascount[0] += 1
                    wclass2.alias = "t%d" % aliascount[0]
                else:
                    seen[cls2] = None
            return dejavu.UnitJoin(wclass1, wclass2, unitjoin.leftbiased)
        classes = wrap(classes)
        
        joins = self.join(classes)
        
        if expr is None:
            expr = logic.Expression(lambda *args: True)
        w, imp = self.where(list(classes), expr)
        
        cols = []
        colnames = []
        for wrapper in classes:
            c, names = wrapper.columns()
            cols.extend(c)
            colnames.extend(names)
        
        statement = ("SELECT %s FROM %s WHERE %s" %
                     (u', '.join(colnames), joins, w))
        return statement, imp, cols
    
    def multirecall(self, classes, expr):
        """multirecall(classes, expr) -> Full inner join units."""
        sql, imp, supplied_cols = self.multiselect(classes, expr)
        data, recvd_cols = self.fetch(sql)
        if data:
            # Get specs on properties.
            props = []
            for sup, rec in zip(supplied_cols, recvd_cols):
                c, key = sup
                name, ftype = rec[0], rec[1]
                subtype = self.expanded_columns.get((c.__name__, key))
                props.append((c, key, ftype, subtype))
            
            consume = self.fromAdapter.consume
            for row in data:
                index = 0
                units = {}
                for c, key, ftype, subtype in props:
                    if c in units:
                        unit = units[c]
                    else:
                        units[c] = unit = c()
                    value = row[index]
                    if subtype:
                        self.load_expanded(unit, key, subtype)
                    else:
                        consume(unit, key, value, ftype)
                    index += 1
                
                unitset = []
                for cls in classes:
                    unit = units[cls]
                    unit.cleanse()
                    unitset.append(unit)
                
                # If our SQL is imperfect, don't yield units to the
                # caller unless they pass expr(unit).
                acceptable = True
                if imp:
                    acceptable = expr(*unitset)
                if acceptable:
                    yield unitset
    
    #                               Schemas                               #
    
    def create_database(self):
        self.execute("CREATE DATABASE %s;" % self.sql_name(self.dbname))
    
    def drop_database(self):
        self.execute("DROP DATABASE %s;" % self.sql_name(self.dbname))
    
    def create_storage(self, cls):
        """Create storage for the given class."""
        clsname = cls.__name__
        tablename = self.table_name(clsname)
        typename = self.typeAdapter.coerce
        
        fields = []
        for key in cls.properties():
            fields.append(u'%s %s' % (self.column_name(clsname, key),
                                      typename(cls, key)))
        self.execute(u'CREATE TABLE %s (%s);' % (tablename, ", ".join(fields)))
        
        for index in cls.indices():
            i = self.table_name("i" + clsname + index)
            self.execute(u'CREATE INDEX %s ON %s (%s);' %
                         (i, tablename, self.column_name(clsname, index)))
    
    def has_storage(self, cls):
        try:
            # Must use fetch here instead of execute, because e.g. MySQL
            # must call store_result if the query has a result set
            # (or it will crash on a subsequent execute).
            self.fetch("SELECT * FROM %s;" % self.table_name(cls.__name__))
        except:
            return False
        return True
    
    def drop_storage(self, cls):
        self.execute(u'DROP TABLE %s;' % self.table_name(cls.__name__))
    
    def add_property(self, cls, name):
        if not self.has_property(cls, name):
            clsname = cls.__name__
            self.execute("ALTER TABLE %s ADD COLUMN %s %s;" %
                         (self.table_name(clsname),
                          self.column_name(clsname, name),
                          self.typeAdapter.coerce(cls, name),
                          ))
    
    def has_property(self, cls, name):
        clsname = cls.__name__
        try:
            # Must use fetch here instead of execute, because e.g. MySQL
            # must call store_result if the query has a result set
            # (or it will crash on a subsequent execute).
            self.fetch("SELECT %s FROM %s;" %
                       (self.column_name(clsname, name),
                        self.table_name(clsname)))
        except:
            return False
        return True
    
    def drop_property(self, cls, name):
        if self.has_property(cls, name):
            clsname = cls.__name__
            self.execute("ALTER TABLE %s DROP COLUMN %s;" %
                         (self.table_name(clsname),
                          self.column_name(clsname, name)))
    
    def rename_property(self, cls, oldname, newname):
        clsname = cls.__name__
        oldname = self.column_name(clsname, oldname)
        newname = self.column_name(clsname, newname)
        if oldname != newname:
            self.execute("ALTER TABLE %s RENAME COLUMN %s TO %s;" %
                         (self.table_name(clsname), oldname, newname))


class OutOfConnectionsError(dejavu.DejavuError):
    """Exception raised when a database store has run out of connections."""
    pass

