from sqlalchemy import create_engine, text
from sqlalchemy.pool import QueuePool
import os
import pandas as pd
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv


class DB:
    def __init__(self, dbname, user, port, password, host) -> None:
        # pool = QueuePool(max_overflow=5, pool_size=20, recycle=3600)
        self.engine = create_engine(
            f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}', pool_size=10, pool_recycle=3600, max_overflow=5)

    def getBooksId(self):
        with self.engine.connect() as conn:
            select_query = """SELECT id FROM public."Book" WHERE "isDeleted" is False and "privacy" is False """
            df = pd.read_sql(select_query, conn)
            return df

    def getBooksIdRatedByUser(self, user_id):
        with self.engine.connect() as conn:
            select_query = text("""
                SELECT "id"
                FROM public."Book"
                WHERE id IN (
                    SELECT "bookId"
                    FROM public."Rating"
                    WHERE "userId" = :user_id
                )
            """)
            params = {"user_id": user_id}
            df = pd.read_sql(select_query, conn, params=params)
            return df

    def getRatingsByUser(self, user_id):
        with self.engine.connect() as conn:
            select_query = text("""
                SELECT "id" as "ratingId", "bookId" as "id", "rate"
                FROM public."Rating"
                WHERE "userId" = :user_id
            """)
            params = {"user_id": user_id}
            df = pd.read_sql(select_query, conn, params=params)
            return df

    def getRatings(self, start: datetime = None, end: datetime = None):
        with self.engine.connect() as conn:
            if start and end:
                select_query = text(
                    """SELECT * FROM public."Rating" WHERE "isDeleted" is False AND "updatedAt" BETWEEN :start AND :end""")
                params = {"start": start, "end": end}
                df = pd.read_sql(select_query, conn, params=params)
                return df
            else:
                return None


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
    print(db.getRatings(datetime.now(timezone.utc) - timedelta(hours=1),
          datetime.now(timezone.utc)))
    # print(db.getBooksId())
    # print(db.getAllBooksRatedByUser('35704'))
