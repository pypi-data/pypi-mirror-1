''' This implements the full-text indexer over two RDBMS tables. The first
is a mapping of words to occurance IDs. The second maps the IDs to (Class,
propname, itemid) instances.
'''
import re

from indexer_dbm import Indexer, is_stopword

class Indexer(Indexer):
    def __init__(self, db):
        self.db = db
        self.reindex = 0

    def close(self):
        '''close the indexing database'''
        # just nuke the circular reference
        self.db = None

    def force_reindex(self):
        '''Force a reindexing of the database.  This essentially
        empties the tables ids and index and sets a flag so
        that the databases are reindexed'''
        self.reindex = 1

    def should_reindex(self):
        '''returns True if the indexes need to be rebuilt'''
        return self.reindex

    def add_text(self, identifier, text, mime_type='text/plain'):
        ''' "identifier" is  (classname, itemid, property) '''
        if mime_type != 'text/plain':
            return

        # first, find the id of the (classname, itemid, property)
        a = self.db.arg
        sql = 'select _textid from __textids where _class=%s and '\
            '_itemid=%s and _prop=%s'%(a, a, a)
        self.db.cursor.execute(sql, identifier)
        r = self.db.cursor.fetchone()
        if not r:
            id = self.db.newid('__textids')
            sql = 'insert into __textids (_textid, _class, _itemid, _prop)'\
                ' values (%s, %s, %s, %s)'%(a, a, a, a)
            self.db.cursor.execute(sql, (id, ) + identifier)
            self.db.cursor.execute('select max(_textid) from __textids')
            id = self.db.cursor.fetchone()[0]
        else:
            id = int(r[0])
            # clear out any existing indexed values
            sql = 'delete from __words where _textid=%s'%a
            self.db.cursor.execute(sql, (id, ))

        # ok, find all the words in the text
        text = unicode(text, "utf-8", "replace").upper()
        wordlist = [w.encode("utf-8", "replace")
                for w in re.findall(r'(?u)\b\w{2,25}\b', text)]
        words = {}
        for word in wordlist:
            if is_stopword(word):
                continue
            words[word] = 1
        words = words.keys()

        # for each word, add an entry in the db
        for word in words:
            # don't dupe
            sql = 'select * from __words where _word=%s and _textid=%s'%(a, a)
            self.db.cursor.execute(sql, (word, id))
            if self.db.cursor.fetchall():
                continue
            sql = 'insert into __words (_word, _textid) values (%s, %s)'%(a, a)
            self.db.cursor.execute(sql, (word, id))

    def find(self, wordlist):
        '''look up all the words in the wordlist.
        If none are found return an empty dictionary
        * more rules here
        '''
        if not wordlist:
            return {}

        l = [word.upper() for word in wordlist if 26 > len(word) > 2]

        if not l:
            return {}

        if self.db.implements_intersect:
            # simple AND search
            sql = 'select distinct(_textid) from __words where _word=%s'%self.db.arg
            sql = '\nINTERSECT\n'.join([sql]*len(l))
            self.db.cursor.execute(sql, tuple(l))
            r = self.db.cursor.fetchall()
            if not r:
                return {}
            a = ','.join([self.db.arg] * len(r))
            sql = 'select _class, _itemid, _prop from __textids '\
                'where _textid in (%s)'%a
            self.db.cursor.execute(sql, tuple([int(id) for (id,) in r]))

        else:
            # A more complex version for MySQL since it doesn't implement INTERSECT

            # Construct SQL statement to join __words table to itself
            # multiple times.
            sql = """select distinct(__words1._textid)
                        from __words as __words1 %s
                        where __words1._word=%s %s"""

            join_tmpl = ' left join __words as __words%d using (_textid) \n'
            match_tmpl = ' and __words%d._word=%s \n'

            join_list = []
            match_list = []
            for n in xrange(len(l) - 1):
                join_list.append(join_tmpl % (n + 2))
                match_list.append(match_tmpl % (n + 2, self.db.arg))

            sql = sql%(' '.join(join_list), self.db.arg, ' '.join(match_list))
            self.db.cursor.execute(sql, l)

            r = map(lambda x: x[0], self.db.cursor.fetchall())
            if not r:
                return {}

            a = ','.join([self.db.arg] * len(r))
            sql = 'select _class, _itemid, _prop from __textids '\
                'where _textid in (%s)'%a

            self.db.cursor.execute(sql, tuple(map(int, r)))

        # self.search_index has the results as {some id: identifier} ...
        # sigh
        r = {}
        k = 0
        for c,n,p in self.db.cursor.fetchall():
            key = (str(c), str(n), str(p))
            r[k] = key
            k += 1
        return r

    def save_index(self):
        # the normal RDBMS backend transaction mechanisms will handle this
        pass

    def rollback(self):
        # the normal RDBMS backend transaction mechanisms will handle this
        pass

