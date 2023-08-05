"""ODBC Storage Manager for Dejavu."""

import dbi, odbc
import threading
import warnings
import datetime
from dejavu import logic, LOGSQL
from dejavu.storage import db


class FieldTypeAdapterODBC(db.FieldTypeAdapter):
    
    # dbiDate objects have limited range. Use strings instead.
    def coerce_datetime_datetime(self, cls, key): return u"CHAR(19)"
    def coerce_datetime_date(self, cls, key): return u"CHAR(10)"
    def coerce_datetime_time(self, cls, key): return u"CHAR(8)"
    
    def coerce_decimal_Decimal(self, cls, key):
        warnings.warn("The precision of %s.%s cannot be determined for "
                      "ODBC stores. Values may be stored incorrectly."
                      % (cls.__name__, key), dejavu.StorageWarning)
        return u"NUMERIC"
    
    def coerce_fixedpoint_FixedPoint(self, cls, key):
        warnings.warn("The precision of %s.%s cannot be determined for "
                      "ODBC stores. Values may be stored incorrectly."
                      % (cls.__name__, key), dejavu.StorageWarning)
        return u"NUMERIC"
    
    def coerce_long(self, cls, key):
        prop = getattr(cls, key)
        bytes = int(prop.hints.get(u'bytes', 0))
        if bytes <= 4:
            return self.coerce_int(cls, key)
        elif bytes <= 8:
            # BIGINT is usually 8 bytes
            return "BIGINT"
        # Anything larger than 8 bytes, use decimal/numeric.
        warnings.warn("The precision of %s.%s cannot be determined for "
                      "ODBC stores. Values may be stored incorrectly."
                      % (cls.__name__, key), dejavu.StorageWarning)
        return u"NUMERIC"


class SQLDecompilerODBC(db.SQLDecompiler):
    
    # --------------------------- Dispatchees --------------------------- #
    
    def dejavu_icontainedby(self, op1, op2):
        if isinstance(op1, db.ConstWrapper):
            # Looking for text in a field. Use Like (reverse terms).
            return "{fn LCASE(" + op2 + ")} LIKE '%" + op1.strip("'\"").lower() + "%'"
        else:
            # Looking for field in (a, b, c).
            # Force all args to lowercase for case-insensitive comparison.
            atoms = [self.adapter.coerce(x).lower() for x in op2.basevalue]
            return "{fn LCASE(%s)} IN (%s)" % (op1, ", ".join(atoms))
    
    def dejavu_icontains(self, x, y):
        return self.dejavu_icontainedby(y, x)
    
    def dejavu_istartswith(self, x, y):
        y = y.strip("'\"")
        return "{fn LCASE(" + x + ")} LIKE '" + y + "%'"
    
    def dejavu_iendswith(self, x, y):
        y = y.strip("'\"")
        return "{fn LCASE(" + x + ")} LIKE '%" + y + "'"
    
    def dejavu_ieq(self, x, y):
        return "{fn LCASE(" + x + ")} = {fn LCASE(" + y + ")}"
    
    def dejavu_now(self):
        return self.adapter.coerce(datetime.datetime.now())
    
    def dejavu_today(self):
        return self.adapter.coerce(datetime.date.today())
    
    def dejavu_year(self, x):
##        return "{fn DATEPART(year, " + x + ")}"
        self.imperfect = True
        return db.cannot_represent
    
    def func__builtin___len(self, x):
        return "{fn LENGTH(" + x + ")}"


class StorageManagerODBC(db.StorageManagerDB):
    """StoreManager to save and retrieve Dejavu Units via ODBC."""
    
    identifier_caseless = True
    decompiler = SQLDecompilerODBC
    typeAdapter = FieldTypeAdapterODBC()
    
    def __init__(self, name, arena, allOptions={}):
        db.StorageManagerDB.__init__(self, name, arena, allOptions)
        self.connstring = allOptions['Connect']
    
    def _get_conn(self):
        return odbc.odbc(self.connstring)
    
    def execute(self, query, conn=None):
        """execute(query, conn=None) -> result set."""
        if conn is None:
            conn = self.connection()
        self.arena.log(query, LOGSQL)
        try:
            cursor = conn.cursor()
            cursor.execute(query.encode('utf8'))
            return cursor
        except Exception, x:
            x.args += (query,)
            raise x
        except dbi.progError, x:
            x += "\n" + str(query)
            raise x
    
    def fetch(self, query, conn=None):
        """fetch(query, conn=None) -> rowdata, columns."""
        res = self.execute(query, conn)
        return res.fetchall(), res.description
    
    def create_database(self):
        raise NotImplementedError
    
    def drop_database(self):
        raise NotImplementedError

