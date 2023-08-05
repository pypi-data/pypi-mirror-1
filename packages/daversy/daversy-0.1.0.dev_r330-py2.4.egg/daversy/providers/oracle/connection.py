
try:
    import cx_Oracle
except ImportError:
    OracleConnection = None
else:
    class OracleConnection(object):
        def __init__(self, info):
            self.connection = cx_Oracle.connect(info[0])
            self.setup_dbms_metadata()
            
        def cursor(self):
            return self.connection.cursor()
            
        def setup_dbms_metadata(self):
            cursor = self.connection.cursor()
            cursor.execute("""
                begin
                    dbms_metadata.set_transform_param(dbms_metadata.session_transform,'SQLTERMINATOR', true);
                end;""")
            cursor.close()

        def close(self):
            self.connection.close()
