import sys
import sqlite3
import re


class SQLite(object):
    def __init__(self, filename):
        conn = sqlite3.connect(filename)
        conn.text_factory = str
        self._cursor = conn.cursor()
        # first we need to get a list of tables
        self._schemas = self._cursor.execute("select sql from sqlite_master "
                                             "where type='table';").fetchall()
        self._schemas = [row[0] for row in self._schemas]
        # now we need to get a name of every table from that list of commands
        exp = re.compile('CREATE TABLE \"(.*)\".*')
        self._table_names = [exp.match(row).group(1) for row in self._schemas]
        prim_keys = [row.splitlines()[-2] for row in self._schemas]
        columns = [row.splitlines()[1:-2] for row in self._schemas]
        table_metadata = zip(self._table_names, prim_keys, columns)
        # create variable for each table
        for table in table_metadata:
            vars(self)[table[0]] = SQLiteTable(self._cursor, table[0],
                                               table[1], table[2])


class SQLiteTable(object):
    def __init__(self, cursor, name, prim_key, columns):
        self.cursor = cursor
        self.name = name
        exp = re.compile('.*"(.*)"')
        self.prim = exp.match(prim_key).group(1)
        self.cols = [exp.match(col).group(1) for col in columns]
        self.var_names = ['by_%s' % col for col in self.cols]

        def method(col):
            return lambda search: [dict(zip(self.cols, row)) for row in
                                   self.cursor.execute(
                                       "select * from %s where %s='%s'" \
                                       % (name, col, search)).fetchall()]
        for col in self.cols:
            vars(self)['by_%s' % col] = method(col)

    def get_all(self):
        return [dict(zip(self.cols, row)) for row in self.cursor.execute(
            'select * from %s' % self.name
        )]


def main():
    print('connecting to DB %s' % sys.argv[1])
    global db
    db = SQLite(sys.argv[1])

if __name__ == '__main__':
    main()
