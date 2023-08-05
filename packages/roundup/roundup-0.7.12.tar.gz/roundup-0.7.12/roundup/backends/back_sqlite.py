# $Id$
'''Implements a backend for SQLite.

See https://pysqlite.sourceforge.net/ for pysqlite info


NOTE: we use the rdbms_common table creation methods which define datatypes
for the columns, but sqlite IGNORES these specifications.
'''
__docformat__ = 'restructuredtext'

import os, base64, marshal

from roundup import hyperdb, date, password
from roundup.backends import locking
from roundup.backends import rdbms_common
import sqlite

class Database(rdbms_common.Database):
    # char to use for positional arguments
    arg = '%s'

    # used by some code to switch styles of query
    implements_intersect = 1

    hyperdb_to_sql_datatypes = {
        hyperdb.String : 'VARCHAR(255)',
        hyperdb.Date   : 'VARCHAR(30)',
        hyperdb.Link   : 'INTEGER',
        hyperdb.Interval  : 'VARCHAR(255)',
        hyperdb.Password  : 'VARCHAR(255)',
        hyperdb.Boolean   : 'BOOLEAN',
        hyperdb.Number    : 'REAL',
    }
    hyperdb_to_sql_value = {
        hyperdb.String : str,
        hyperdb.Date   : lambda x: x.serialise(),
        hyperdb.Link   : int,
        hyperdb.Interval  : str,
        hyperdb.Password  : str,
        hyperdb.Boolean   : int,
        hyperdb.Number    : lambda x: x,
        hyperdb.Multilink : lambda x: x,    # used in journal marshalling
    }
    sql_to_hyperdb_value = {
        hyperdb.String : str,
        hyperdb.Date   : lambda x: date.Date(str(x)),
        hyperdb.Link   : str, # XXX numeric ids
        hyperdb.Interval  : date.Interval,
        hyperdb.Password  : lambda x: password.Password(encrypted=x),
        hyperdb.Boolean   : int,
        hyperdb.Number    : rdbms_common._num_cvt,
        hyperdb.Multilink : lambda x: x,    # used in journal marshalling
    }

    def sql_open_connection(self):
        db = os.path.join(self.config.DATABASE, 'db')
        conn = sqlite.connect(db=db)
        cursor = conn.cursor()
        return (conn, cursor)

    def open_connection(self):
        # ensure files are group readable and writable
        os.umask(0002)

        # lock the database
        lockfilenm = os.path.join(self.dir, 'lock')
        self.lockfile = locking.acquire_lock(lockfilenm)
        self.lockfile.write(str(os.getpid()))
        self.lockfile.flush()

        (self.conn, self.cursor) = self.sql_open_connection()

        try:
            self.load_dbschema()
        except sqlite.DatabaseError, error:
            if str(error) != 'no such table: schema':
                raise
            self.init_dbschema()
            self.cursor.execute('create table schema (schema varchar)')
            self.cursor.execute('create table ids (name varchar, num integer)')
            self.cursor.execute('create index ids_name_idx on ids(name)')
            self.create_version_2_tables()

    def create_version_2_tables(self):
        self.cursor.execute('create table otks (otk_key varchar, '
            'otk_value varchar, otk_time integer)')
        self.cursor.execute('create index otks_key_idx on otks(otk_key)')
        self.cursor.execute('create table sessions (session_key varchar, '
            'session_time integer, session_value varchar)')
        self.cursor.execute('create index sessions_key_idx on '
                'sessions(session_key)')

        # full-text indexing store
        self.cursor.execute('CREATE TABLE __textids (_class varchar, '
            '_itemid varchar, _prop varchar, _textid integer primary key) ')
        self.cursor.execute('CREATE TABLE __words (_word varchar, '
            '_textid integer)')
        self.cursor.execute('CREATE INDEX words_word_ids ON __words(_word)')
        sql = 'insert into ids (name, num) values (%s,%s)'%(self.arg, self.arg)
        self.cursor.execute(sql, ('__textids', 1))

    def add_new_columns_v2(self):
        # update existing tables to have the new actor column
        tables = self.database_schema['tables']
        for classname, spec in self.classes.items():
            if tables.has_key(classname):
                dbspec = tables[classname]
                self.update_class(spec, dbspec, force=1, adding_v2=1)
                # we've updated - don't try again
                tables[classname] = spec.schema()

    def fix_version_3_tables(self):
        # NOOP - no restriction on column length here
        pass

    def update_class(self, spec, old_spec, force=0, adding_v2=0):
        ''' Determine the differences between the current spec and the
            database version of the spec, and update where necessary.

            If 'force' is true, update the database anyway.

            SQLite doesn't have ALTER TABLE, so we have to copy and
            regenerate the tables with the new schema.
        '''
        new_has = spec.properties.has_key
        new_spec = spec.schema()
        new_spec[1].sort()
        old_spec[1].sort()
        if not force and new_spec == old_spec:
            # no changes
            return 0

        if __debug__:
            print >>hyperdb.DEBUG, 'update_class FIRING for', spec.classname

        # detect multilinks that have been removed, and drop their table
        old_has = {}
        for name, prop in old_spec[1]:
            old_has[name] = 1
            if new_has(name) or not isinstance(prop, hyperdb.Multilink):
                continue
            # it's a multilink, and it's been removed - drop the old
            # table. First drop indexes.
            self.drop_multilink_table_indexes(spec.classname, ml)
            sql = 'drop table %s_%s'%(spec.classname, prop)
            if __debug__:
                print >>hyperdb.DEBUG, 'update_class', (self, sql)
            self.cursor.execute(sql)
        old_has = old_has.has_key

        # now figure how we populate the new table
        if adding_v2:
            fetch = ['_activity', '_creation', '_creator']
        else:
            fetch = ['_actor', '_activity', '_creation', '_creator']
        properties = spec.getprops()
        for propname,x in new_spec[1]:
            prop = properties[propname]
            if isinstance(prop, hyperdb.Multilink):
                if not old_has(propname):
                    # we need to create the new table
                    self.create_multilink_table(spec, propname)
                elif force:
                    tn = '%s_%s'%(spec.classname, propname)
                    # grabe the current values
                    sql = 'select linkid, nodeid from %s'%tn
                    if __debug__:
                        print >>hyperdb.DEBUG, 'update_class', (self, sql)
                    self.cursor.execute(sql)
                    rows = self.cursor.fetchall()

                    # drop the old table
                    self.drop_multilink_table_indexes(spec.classname, propname)
                    sql = 'drop table %s'%tn
                    if __debug__:
                        print >>hyperdb.DEBUG, 'migration', (self, sql)
                    self.cursor.execute(sql)

                    # re-create and populate the new table
                    self.create_multilink_table(spec, propname)
                    sql = '''insert into %s (linkid, nodeid) values 
                        (%s, %s)'''%(tn, self.arg, self.arg)
                    for linkid, nodeid in rows:
                        self.cursor.execute(sql, (int(linkid), int(nodeid)))
            elif old_has(propname):
                # we copy this col over from the old table
                fetch.append('_'+propname)

        # select the data out of the old table
        fetch.append('id')
        fetch.append('__retired__')
        fetchcols = ','.join(fetch)
        cn = spec.classname
        sql = 'select %s from _%s'%(fetchcols, cn)
        if __debug__:
            print >>hyperdb.DEBUG, 'update_class', (self, sql)
        self.cursor.execute(sql)
        olddata = self.cursor.fetchall()

        # TODO: update all the other index dropping code
        self.drop_class_table_indexes(cn, old_spec[0])

        # drop the old table
        if __debug__:
            print >>hyperdb.DEBUG, 'update_class "drop table _%s"'%cn
        self.cursor.execute('drop table _%s'%cn)

        # create the new table
        self.create_class_table(spec)

        if olddata:
            inscols = ['id', '_actor', '_activity', '_creation', '_creator']
            for propname,x in new_spec[1]:
                prop = properties[propname]
                if isinstance(prop, hyperdb.Multilink):
                    continue
                elif isinstance(prop, hyperdb.Interval):
                    inscols.append('_'+propname)
                    inscols.append('__'+propname+'_int__')
                elif old_has(propname):
                    # we copy this col over from the old table
                    inscols.append('_'+propname)

            # do the insert of the old data - the new columns will have
            # NULL values
            args = ','.join([self.arg for x in inscols])
            cols = ','.join(inscols)
            sql = 'insert into _%s (%s) values (%s)'%(cn, cols, args)
            if __debug__:
                print >>hyperdb.DEBUG, 'update_class', (self, sql, olddata[0])
            for entry in olddata:
                d = []
                for name in inscols:
                    # generate the new value for the Interval int column
                    if name.endswith('_int__'):
                        name = name[2:-6]
                        if entry.has_key(name):
                            v = hyperdb.Interval(entry[name]).as_seconds()
                        else:
                            v = None
                    elif entry.has_key(name):
                        v = entry[name]
                    else:
                        v = None
                    d.append(v)
                self.cursor.execute(sql, tuple(d))

        return 1

    def sql_close(self):
        ''' Squash any error caused by us already having closed the
            connection.
        '''
        try:
            try:
                self.conn.close()
            except sqlite.ProgrammingError, value:
                if str(value) != 'close failed - Connection is closed.':
                    raise
        finally:
            # always release the lock
            if self.lockfile is not None:
                locking.release_lock(self.lockfile)
                self.lockfile.close()
                self.lockfile = None

    def sql_rollback(self):
        ''' Squash any error caused by us having closed the connection (and
            therefore not having anything to roll back)
        '''
        try:
            self.conn.rollback()
        except sqlite.ProgrammingError, value:
            if str(value) != 'rollback failed - Connection is closed.':
                raise

    def __repr__(self):
        return '<roundlite 0x%x>'%id(self)

    def sql_commit(self):
        ''' Actually commit to the database.

            Ignore errors if there's nothing to commit.
        '''
        try:
            self.conn.commit()
        except sqlite.DatabaseError, error:
            if str(error) != 'cannot commit - no transaction is active':
                raise

    def sql_index_exists(self, table_name, index_name):
        self.cursor.execute('pragma index_list(%s)'%table_name)
        for entry in self.cursor.fetchall():
            if entry[1] == index_name:
                return 1
        return 0

    # old-skool id generation
    def newid(self, classname):
        ''' Generate a new id for the given class
        '''
        # get the next ID
        sql = 'select num from ids where name=%s'%self.arg
        if __debug__:
            print >>hyperdb.DEBUG, 'newid', (self, sql, classname)
        self.cursor.execute(sql, (classname, ))
        newid = int(self.cursor.fetchone()[0])

        # update the counter
        sql = 'update ids set num=%s where name=%s'%(self.arg, self.arg)
        vals = (int(newid)+1, classname)
        if __debug__:
            print >>hyperdb.DEBUG, 'newid', (self, sql, vals)
        self.cursor.execute(sql, vals)

        # return as string
        return str(newid)

    def setid(self, classname, setid):
        ''' Set the id counter: used during import of database

        We add one to make it behave like the sequences in postgres.
        '''
        sql = 'update ids set num=%s where name=%s'%(self.arg, self.arg)
        vals = (int(setid)+1, classname)
        if __debug__:
            print >>hyperdb.DEBUG, 'setid', (self, sql, vals)
        self.cursor.execute(sql, vals)

    def clear(self):
        rdbms_common.Database.clear(self)

        # set the id counters to 0 (setid adds one) so we start at 1
        for cn in self.classes.keys():
            self.setid(cn, 0)

    def create_class(self, spec):
        rdbms_common.Database.create_class(self, spec)
        sql = 'insert into ids (name, num) values (%s, %s)'
        vals = (spec.classname, 1)
        if __debug__:
            print >>hyperdb.DEBUG, 'create_class', (self, sql, vals)
        self.cursor.execute(sql, vals)

class sqliteClass:
    def filter(self, search_matches, filterspec, sort=(None,None),
            group=(None,None)):
        ''' If there's NO matches to a fetch, sqlite returns NULL
            instead of nothing
        '''
        return filter(None, rdbms_common.Class.filter(self, search_matches,
            filterspec, sort=sort, group=group))

class Class(sqliteClass, rdbms_common.Class):
    pass

class IssueClass(sqliteClass, rdbms_common.IssueClass):
    pass

class FileClass(sqliteClass, rdbms_common.FileClass):
    pass


