from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

import psycopg2

from psycopg2 import pool


class DB:
    def __init__(self, dbname, user, port, password, host) -> None:
        self.dbname = dbname
        self.user = user
        self.port = port
        self.password = password
        self.host = host
        self.connection_pool = pool.SimpleConnectionPool(
            minconn=1, maxconn=10,
            dbname=self.dbname, user=self.user, port=self.port,
            password=self.password, host=self.host)

    def getBooks(self):
        conn = self.connection_pool.getconn()
        try:
            with conn.cursor() as curs:
                select_query = """SELECT * FROM public."Book" LIMIT 5;"""
                curs.execute(select_query)
                rows = curs.fetchall()
                return rows
        finally:
            self.connection_pool.putconn(conn)

    def getRatings(self, start: datetime = None, end: datetime = None):
        conn = self.connection_pool.getconn()
        try:
            with conn.cursor() as curs:
                if start and end:
                    select_query = """SELECT * FROM public."Rating" WHERE "createdAt" BETWEEN %s AND %s"""
                    curs.execute(select_query, (start, end))
                    rows = curs.fetchall()
                    return rows
                else:
                    return None
        finally:
            self.connection_pool.putconn(conn)


if __name__ == '__main__':
    load_dotenv()
    dbname = os.environ.get('PGDATABASE')
    user = os.environ.get('PGUSER')
    port = os.environ.get('PGPORT')
    password = os.environ.get('PGPASSWORD')
    host = os.environ.get('PGHOST')
    print(f'connecting to db..., {dbname}, {host}, {port}')
    db = DB(dbname, user, port, password, host)
    print(f'connected to db')
    print(db.getRatings(datetime(year=2023, month=4, day=8),
          datetime(year=2023, month=4, day=9)))
