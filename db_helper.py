import sys
import sqlite3
import re


class SQLite(object):
    def __init__(self, filename):
        conn = sqlite3.connect(filename)
        conn.text_factory = str
        self._cursor = conn.cursor()
        # first we need to get a list of tables
        self._tables = self._cursor.execute("select name from sqlite_master "
                                            "where type='table';").fetchall()
        self._tables = [row[0] for row in self._tables[1:]]
        # create variable for each table
        for table in self._tables:
            vars(self)[table] = SQLiteTable(self._cursor, table)


class SQLiteTable(object):
    def __init__(self, cursor, name):
        self.cursor = cursor
        self.name = name
        cursor.execute("pragma table_info('%s')" % name)
        self.cols = [row[1] for row in cursor.fetchall()]
        self.var_names = ['by_%s' % col for col in self.cols]

        for col in self.cols:
            vars(self)['by_%s' % col] = lambda search, col=col:\
                [dict(zip(self.cols, row)) for row in
                    self.cursor.execute("select * from %s where %s='%s'"
                                        % (name, col, search)).fetchall()]

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
