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
    
       #. list of tables
       #. list of foreign keys

    The list of tables is acquired by executing ``SELECT * FROM sqlite_master WHERE type='table'``.
    
    Then the foreign keys for each table are fetched using ``PRAGMA foreign_key_list (table)``.

    Additionally the column information is added by executing ``PRAGMA table_info (table)``.

    The return value is a list of object instances, with attributes set to corresponding column 
    values of in the ``sqlite_master`` table. The foreign key lists are stored in the ``fk`` attribute,
    as a similar list of instances mapping the values returned by ``PRAGMA foreign_key_list``, and column
    information is likewise stored in the ``columns`` attribute.   

    ::
    
       table_list = sqlitefktg.analysis (database)
       for t in table_list:
          print "table ", t.tbl_name
          do_something_with_columns (t.columns)
          do_something_with_fks (t.fk)


    :param database: a string pointing to the location of the sqlite database, or an sqlite3.connection object

    :returns: a list of table data
    :rtype: list of instances
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
            fk.on_update = "restrict"            
            fk.insert_trigger = "SELECT 1;"
            fk.update_trigger = "SELECT 1;"
            fk.update_trigger_ref = "SELECT 1;"
            fk.delete_trigger = "SELECT 1;"

    return tables

def generate(tables):
    """Generate SQL source for triggers enforcing foreign-key contraints.
    
    The triggers' source was mostly copied from the SQLite site: `ForeignKeyTriggers <http://www.sqlite.org/cvstrac/wiki?p=ForeignKeyTriggers>`_ .

    This function adds the following attributes to each table.fk list element:
    
      - insert_trigger
      - update_trigger
      - update_trigger_ref
      - delete_trigger

    These attributes then contain the SQL for creating the foreign key enforcing triggers.

    The triggers for insert and update operations on the referencing table, have restricting function,
    the update trigger for the referenced table may have *restrict* or *cascade* action, and the
    delete triggers for the referenced table have *restrict*, *cascade* or *setnull* as possible
    actions. The action to be taken is determined by the ``on_update`` and ``on_delete`` attributes
    on each ``fk`` list element, and they both default to restrict. The may be changed manually
    by modifying the output of ``analysis`` and passing it to ``generate`` by hand.

    :param tables: the output of `analysis`
    :returns: the tables param with trigger source filled in
    """
    for t in tables:        
        for fk in t.fk:
            fk.drops = [
                "DROP TRIGGER IF EXISTS fki_{0.tbl_name}_{1.from}_{1.table}_{1.to};".format(t,fk),
                "DROP TRIGGER IF EXISTS fku_{0.tbl_name}_{1.from}_{1.table}_{1.to};".format(t,fk),
                "DROP TRIGGER IF EXISTS fkur_{0.tbl_name}_{1.from}_{1.table}_{1.to};".format(t,fk),
                "DROP TRIGGER IF EXISTS fkd_{0.tbl_name}_{1.from}_{1.table}_{1.to};".format(t,fk)
                ]
            #INSERT ON THE REFERENCING TABLE (always restrict)
            fk.insert_trigger = """
CREATE TRIGGER fki_{0.tbl_name}_{1.from}_{1.table}_{1.to}
BEFORE INSERT ON {0.tbl_name}
FOR EACH ROW BEGIN
   SELECT RAISE(ROLLBACK, 'insert on table "{0.tbl_name}" violates foreign key constraint "fk_{0.tbl_name}_{1.from}"')
   WHERE NEW.{1.from} IS NOT NULL AND (SELECT {1.to} FROM {1.table} WHERE {1.to} = NEW.{1.from}) IS NULL;
END;""".format ( t, fk )

            #UPDATE ON THE REFERENCING TABLE (always restrict)
            fk.update_trigger = """
CREATE TRIGGER fku_{0.tbl_name}_{1.from}_{1.table}_{1.to}
BEFORE UPDATE ON [{0.tbl_name}]
FOR EACH ROW BEGIN
   SELECT RAISE(ROLLBACK, 'update on table "{0.tbl_name}" violates foreign key constraint "fk_{0.tbl_name}_{1.from}"')
   WHERE NEW.{1.from} IS NOT NULL AND (SELECT {1.to} FROM {1.table} WHERE {1.to} = NEW.{1.from}) IS NULL;
END;""".format (t, fk)

            #UPDATE ON THE REFERENCED TABLE (cascade/restrict)
            if fk.on_update == "cascade":
                fk.update_trigger_ref = """
CREATE TRIGGER fkur_{0.tbl_name}_{1.from}_{1.table}_{1.to}
AFTER UPDATE ON [{1.table}]
FOR EACH ROW BEGIN
   UPDATE {0.tbl_name} SET {1.from} = NEW.{1.to} WHERE {1.from} = OLD.{1.to};
END;""".format (t, fk)                
            elif fk.on_update == "restrict":
                fk.update_trigger_ref = """
CREATE TRIGGER fkur_{0.tbl_name}_{1.from}_{1.table}_{1.to}
BEFORE UPDATE ON [{1.table}]
FOR EACH ROW BEGIN
   SELECT RAISE(ROLLBACK, 'update on table "{1.table}" violated foreign key constraint "fk_{0.tbl_name}_{1.from}"')
   WHERE (SELECT {1.from} FROM {0.tbl_name} WHERE {1.from} = OLD.{1.to}) IS NOT NULL;
END;""".format (t, fk)                
            
            #DELETE ON THE REFERENCED TABLE (cascade/restrict/setnull)
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
            elif fk.on_delete == "setnull":
                fk.delete_trigger = """
CREATE TRIGGER fkd_{0.tbl_name}_{1.from}_{1.table}_{1.to}
BEFORE DELETE ON [{1.table}]
FOR EACH ROW BEGIN
   UPDATE {0.tbl_name} SET {1.from} = NULL WHERE {1.from} = OLD.{1.to};
END;""".format (t, fk)
    
    return tables

class Null:
    def write(*a): pass

def execute(database, drop_first=True, excluded_tables=[], cascade_deletes=[], verbose=False):
    """Generate and create foreign-key enforcing triggers in the given database.

    :param database: an sqlite connection object, or a string with location of the database
    :param drop_first: boolean indicating if the triggers should be dropped prior to creating. Default: ``True``.
    :param excluded_tables: a list of tables that should be ommited. Default: empty list.
    :param cascade_deletes: a list of (table, column) pairs, where table.column should support cascade deletion when
      the foreign key record is deleted. Default: empty list.
    :param verbose: should the function generate verbose output. Default: ``False``.    
    """
    if isinstance(database, str):
        dbconn = sqlite3.connect ( database )
        connected = True
    else:
        dbconn = database
        connected = False

    tables = analysis(dbconn)
    
    to_exclude = []
    for table in tables:
        if table.tbl_name in excluded_tables:
            to_exclude.append (table)
        for fk in table.fk:            
            if (table.tbl_name, fk["from"]) in cascade_deletes:
                fk.on_delete = "cascade"
    
    for exclude in to_exclude: tables.remove(exclude)

    tables = generate(tables)

    execute_generated(dbconn, tables, drop_first=drop_first, verbose=verbose)

    if connected:
        dbconn.close()

def execute_generated(dbconn, tables, drop_first = True, verbose=False):
    """
    This function is used by the ``execute`` function to actually write the triggers
    to the database. It may be used instead of ``execute`` if changes were made to the
    ``tables`` structure returned by ``analysis`` and ``generate``.

    :param dbconn: sqlite3.connection
    :param tables: a tables structure returned by ``analysis`` and processed by ``generate``,
                   possibly with some custom changes
    """

    import sys

    if verbose:
        out = sys.stdout
    else:
        out = Null()
    
    cur = dbconn.cursor()

    for table in tables:
        for fk in table.fk:            
            print >>out, " + {0.tbl_name}.{1.from} -> {1.table}.{1.to}".format(table, fk)
            if drop_first:
                for d in fk.drops: cur.execute (d)
            cur.execute(fk.insert_trigger)
            cur.execute(fk.update_trigger)
            cur.execute(fk.update_trigger_ref)
            cur.execute(fk.delete_trigger)

    dbconn.commit()
    

if __name__ == "__main__":
    conn = sqlite3.connect ( ":memory:" )
    cur = conn.cursor()

    cur.execute ( """CREATE TABLE country ( id integer PRIMARY KEY, name varchar(64) );""")
    cur.execute ( """CREATE TABLE city ( id integer PRIMARY KEY, name varchar(64), country integer not null REFERENCES country(id) );""")
    cur.execute ( """CREATE TABLE person ( id integer PRIMARY KEY, name varchar(64), nationality integer not null REFERENCES country(id), 
city integer NOT NULL REFERENCES city(id) );""")
    
    conn.commit()

    execute (conn, verbose=True)

