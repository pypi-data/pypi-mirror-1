# Use libpq directly to avoid all of the DB-API overhead.
from pyPgSQL import libpq
import datetime
import dejavu
from dejavu.storage import db


class AdapterToPgSQL(db.AdapterToSQL):
    
    like_escapes = [("%", r"\\%"), ("_", r"\\_")]


class PgSQLDecompiler(db.SQLDecompiler):
    
    def dejavu_icontainedby(self, op1, op2):
        if isinstance(op1, db.ConstWrapper):
            # Looking for text in a field. Use ILike (reverse terms).
            return op2 + " ILIKE '%" + self.adapter.escape_like(op1) + "%'"
        else:
            # Looking for field in (a, b, c).
            # Force all args to lowercase for case-insensitive comparison.
            atoms = [self.adapter.coerce(x).lower() for x in op2.basevalue]
            return "LOWER(%s) IN (%s)" % (op1, ", ".join(atoms))
    
    def dejavu_istartswith(self, x, y):
        return x + " ILIKE '" + self.adapter.escape_like(y) + "%'"
    
    def dejavu_iendswith(self, x, y):
        return x + " ILIKE '%" + self.adapter.escape_like(y) + "'"
    
    def dejavu_ieq(self, x, y):
        # ILIKE with no wildcards should behave like ieq.
        return x + " ILIKE '" + self.adapter.escape_like(y) + "'"
    
    def dejavu_year(self, x):
        return "date_part('year', " + x + ")"



class StorageManagerPgSQL(db.StorageManagerDB):
    """StoreManager to save and retrieve Units via pyPgSQL 1.35."""
    
    sql_name_max_length = 63
    close_connection_method = 'finish'
    decompiler = PgSQLDecompiler
    toAdapter = AdapterToPgSQL()
    
    def __init__(self, name, arena, allOptions={}):
        db.StorageManagerDB.__init__(self, name, arena, allOptions)
        
        # connstring = (host=h port=p dbname=d user=u password=p options=o tty=t)
        self.connstring = allOptions[u'Connect']
        atoms = self.connstring.split(" ")
        for atom in atoms:
            k, v = atom.split("=", 1)
            setattr(self, k, v)
    
    def sql_name(self, name, quoted=True):
        name = db.StorageManagerDB.sql_name(self, name, quoted)
        if quoted:
            name = '"' + name.replace('"', '""') + '"'
        return name
    
    def _get_conn(self):
        try:
            return libpq.PQconnectdb(self.connstring)
        except libpq.DatabaseError, x:
            if x.args[0].startswith('could not connect'):
                raise db.OutOfConnectionsError
            raise
    
    def _template_conn(self):
        atoms = self.connstring.split(" ")
        tmplconn = ""
        for atom in atoms:
            k, v = atom.split("=", 1)
            if k == 'dbname': v = 'template1'
            tmplconn += "%s=%s " % (k, v)
        return libpq.PQconnectdb(tmplconn)
    
    def version(self):
        c = self._template_conn()
        v = c.version
        c.finish()
        return v
    
    def fetch(self, query, conn=None):
        """fetch(query, conn=None) -> rowdata, columns."""
        res = self.execute(query, conn)
        
        columns = []
        if res.resultType != libpq.EMPTY_QUERY:
            for index in xrange(res.nfields):
                columns.append((res.fname(index), res.ftype(index)))
        
        data = [[res.getvalue(row, col) for col in xrange(res.nfields)]
                for row in xrange(res.ntuples)]
        res.clear()
        
        return data, columns
    
    def create_database(self):
        c = self._template_conn()
        self.execute('CREATE DATABASE %s' % self.sql_name(self.dbname), c)
        c.finish()
    
    def drop_database(self):
        c = self._template_conn()
        self.execute("DROP DATABASE %s;" % self.sql_name(self.dbname), c)
        c.finish()
    
    def has_storage(self, cls):
        # For some odd reason, libpq errors if you try to filter by tablename.
        sql = u"SELECT tablename FROM pg_tables"
        data, cols = self.fetch(sql)
        return [self.table_name(cls.__name__, quoted=False)] in data

