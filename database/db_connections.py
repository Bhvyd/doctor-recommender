import pymysql

def get_db_connection():
    return pymysql.connect(
        host='localhost',       # Replace with your DB host
        user='root',            # Replace with your DB username
        password='password',    # Replace with your DB password
        db='doctor_db',         # Replace with your database name
        cursorclass=pymysql.cursors.DictCursor
    )
