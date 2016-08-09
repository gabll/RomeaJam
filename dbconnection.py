import credentials
import pymysql

def sql_formatter(s):
    """removes special characters from strings"""
    try:
        return str(s).replace("'","").replace(";","").replace(",","")
    except:
        return s

class dbconnection:

    def __init__(self, host, user, pwd, db):
        self.db = pymysql.connect(host=host, user=user, passwd=pwd, db=db,
                                  autocommit=True,
                                  cursorclass=pymysql.cursors.DictCursor)
        self.cursor = self.db.cursor()

    def execute_query(self, query_string):
        """ Execute query and return cursor """
        self.cursor.execute(query_string)
        return self.cursor

    def close(self):
        """ Close active connection """
        self.cursor.close()
        self.db.close()

if __name__ == "__main__":
    conn = dbconnection(credentials.mysql_host,
                           credentials.mysql_user,
                           credentials.mysql_pwd,
                           credentials.mysql_db)
    print conn.execute_query("select * from jams;").fetchall()[0]
    print sql_formatter("'test;,")
    conn.close()
    conn = dbconnection(credentials.mysql_host,
                           credentials.mysql_user,
                           credentials.mysql_pwd,
                           credentials.mysql_db)
    print conn.execute_query("INSERT INTO table_test (id, name) VALUES (1,5)")
    conn.close()
