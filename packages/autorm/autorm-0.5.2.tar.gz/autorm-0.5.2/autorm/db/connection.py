        
class Database(object):
    placeholder = '?'
    
    def connect(self, dbtype, *args, **kwargs):
        if dbtype == 'sqlite3':
            import sqlite3
            self.connection = sqlite3.connect(*args)
        elif dbtype == 'mysql':
            import MySQLdb
            self.connection = MySQLdb.connect(**kwargs)
            self.placeholder = '%s'
        else:
            raise Exception("Unknown database type '%s'" % dbtype)

class DBConn(object):
    def __init__(self):
        self.b_debug = False
        self.b_commit = True
        self.conn = None

autorm_db = DBConn()
autorm_db.conn = Database()
