# -*- coding: utf-8 -*-
try:
    import sqlite3
except ImportError:
    import sys
    print "sqlitefktg requires the sqlite3 module to be installed in PYTHONPATH"
    sys.exit(1)


class _row_container(object):
    """A simple class to simplify manipulating data returned by queries"""
    def __repr__(self):
        s = []
        for i in self.__dict__:
            if not i.startswith("__"):
                s.append (i + ' = ' + str(self.__dict__[i]))
        return "<" + ",".join(s) + ">"
    def __getitem__(*a): return getattr(*a)


def Q(dbconn, sql):
    """Run a query and return an array of rows"""
    cursor = dbconn.cursor()
    cursor.execute(sql)    
    data = cursor.fetchall()
    if (len(data)<=0): return []

    description = map (lambda x: x[0], cursor.description)
    
    rows = []
    for row in data:
        r = _row_container()
        for c,v in zip(description, row): setattr(r, c, v)
        rows.append (r)
    cursor.close()
    return rows

def analysis(database):
    """Look into an sqlite database, and fetch all meta-data required for
    foreign-key triggers generation:
    
       # list of tables
       # list of foreign keys
    
    :param database: a string pointing to the location of the sqlite database, or an sqlite3.connection object

    :returns: a list of tables found in the database with foreign-key constraints
    """
    
    if isinstance(database, str):
        dbconn = sqlite3.connect ( database )
    else:
        dbconn = database

    cursor = dbconn.cursor()

    tables = Q(dbconn, "SELECT * FROM sqlite_master WHERE type='table'")
    for t in tables:
        t.columns = Q(dbconn, "PRAGMA table_info({0})".format(t.tbl_name))
        t.fk = Q(dbconn, "PRAGMA foreign_key_list({0})".format(t.tbl_name))
        for fk in t.fk:
            fk.on_delete = "restrict"

    return tables

def generate(tables):
    """Generate SQL source for triggers enforcing foreign-key contraints.

    :param tables: the output of `analysis`
    :returns: the tables param with trigger source filled in
    """
    for t in tables:        
        for fk in t.fk:
            fk.drops = [
                "DROP TRIGGER IF EXISTS fki_{0.tbl_name}_{1.from}_{1.table}_{1.to};".format(t,fk),
                "DROP TRIGGER IF EXISTS fku_{0.tbl_name}_{1.from}_{1.table}_{1.to};".format(t,fk),
                "DROP TRIGGER IF EXISTS fkd_{0.tbl_name}_{1.from}_{1.table}_{1.to};".format(t,fk)
                ]
            fk.insert_trigger = """
CREATE TRIGGER fki_{0.tbl_name}_{1.from}_{1.table}_{1.to}
BEFORE INSERT ON {0.tbl_name}
FOR EACH ROW BEGIN
   SELECT RAISE(ROLLBACK, 'insert on table "{0.tbl_name}" violates foreign key constraint "fk_{0.tbl_name}_{1.from}"')
   WHERE NEW.{1.from} IS NOT NULL AND (SELECT {1.to} FROM {1.table} WHERE {1.to} = NEW.{1.from}) IS NULL;
END;""".format ( t, fk )
            fk.update_trigger = """
CREATE TRIGGER fku_{0.tbl_name}_{1.from}_{1.table}_{1.to}
BEFORE UPDATE ON [{0.tbl_name}]
FOR EACH ROW BEGIN
   SELECT RAISE(ROLLBACK, 'update on table "{0.tbl_name}" violates foreign key constraint "fk_{0.tbl_name}_{1.from}"')
   WHERE NEW.{1.from} IS NOT NULL AND (SELECT {1.to} FROM {1.table} WHERE {1.to} = NEW.{1.from}) IS NULL;
END;""".format (t, fk)
            if fk.on_delete == "restrict":
                fk.delete_trigger = """
CREATE TRIGGER fkd_{0.tbl_name}_{1.from}_{1.table}_{1.to}
BEFORE DELETE ON [{1.table}]
FOR EACH ROW BEGIN
   SELECT RAISE(ROLLBACK, 'delete on table "{1.table}" violates foreign key constraint "fk_{0.tbl_name}_{1.from}"')
   WHERE (SELECT {1.from} FROM {0.tbl_name} WHERE {1.from} = OLD.{1.to}) IS NOT NULL;
END;""".format (t, fk)
            elif fk.on_delete == "cascade":
                fk.delete_trigger = """
CREATE TRIGGER fkd_{0.tbl_name}_{1.from}_{1.table}_{1.to}
BEFORE DELETE ON [{1.table}]
FOR EACH ROW BEGIN
   DELETE FROM {0.tbl_name} WHERE {1.from} = OLD.{1.to};
END;""".format (t, fk)
    
    return tables

class Null:
    def write(*a): pass

def execute(database, drop_first=True, excluded_tables=[], cascade_deletes=[], verbose=False):
    """Generate and create foreign-key enforcing triggers in the given database.

    :param database: an sqlite connection object, or a string with location of the database
    :param drop_first: boolean indicating if the driggers should be dropped prior to creating. Default: ``True``.
    :param excluded_tables: a list of tables that should be ommited. Default: empty list.
    :param cascade_deletes: a list of (table, column) pairs, where table.column should support cascade deletion when
      the foreign key record is deleted. Default: empty list.
    :param verbose: should the function generate verbose output. Default: ``False``.    
    """
    import sys

    if verbose:
        out = sys.stdout
    else:
        out = Null()

    if isinstance(database, str):
        dbconn = sqlite3.connect ( database )
    else:
        dbconn = database
    cur = dbconn.cursor()

    tables = analysis(dbconn)
    
    for table in tables:
        if table.tbl_name in excluded_tables: continue
        for fk in table.fk:            
            if (table.tbl_name, fk["from"]) in cascade_deletes:
                fk.on_delete = "cascade"

    tables = generate(tables)
    
    for table in tables:
        if table.tbl_name in excluded_tables: continue
        for fk in table.fk:            
            print >>out, " + {0.tbl_name}.{1.from} -> {1.table}.{1.to}".format(table, fk)
            if drop_first:
                for d in fk.drops: cur.execute (d)
            cur.execute(fk.insert_trigger)
            cur.execute(fk.update_trigger)
            cur.execute(fk.delete_trigger)
    dbconn.commit()
    dbconn.close()

if __name__ == "__main__":
    conn = sqlite3.connect ( ":memory:" )
    cur = conn.cursor()

    cur.execute ( """CREATE TABLE country ( id integer PRIMARY KEY, name varchar(64) );""")
    cur.execute ( """CREATE TABLE city ( id integer PRIMARY KEY, name varchar(64), country integer not null REFERENCES country(id) );""")
    cur.execute ( """CREATE TABLE person ( id integer PRIMARY KEY, name varchar(64), nationality integer not null REFERENCES country(id), 
city integer NOT NULL REFERENCES city(id) );""")
    
    conn.commit()

    execute (conn, verbose=True)

