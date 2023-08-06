        
class Database(object):
    placeholder = '?'
    
    def connect(self, dbtype, *args, **kwargs):
        if dbtype == 'sqlite3':
            import sqlite3
            self.connection = sqlite3.connect(*args)
        elif dbtype == 'spatialite':
            from pysqlite2 import dbapi2 as sqlite3
            from ctypes.util import find_library
            import os
            
            exists = os.path.exists(args[0])
            
            self.connection = sqlite3.connect(*args)
            self.connection.enable_load_extension(True)
            spatialite_lib = os.environ.get('SPATIALITE_LIBRARY_PATH', find_library('spatialite'))
            if not spatialite_lib:
                raise Exception("Spatialite library not found via ctypes.util.find_library, nor in the SPATIALITE_LIBRARY_PATH environment variable.")                
            self.connection.cursor().execute("select load_extension('%s')" % spatialite_lib)
            self.connection.enable_load_extension(False)
            
            if not exists:
                with open(os.path.join(os.path.dirname(__file__),"init_spatialite-2.3.sql")) as init_file:
                    cursor = self.connection.cursor()
                    cursor.executescript(init_file.read())
                    self.connection.commit()
            
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
