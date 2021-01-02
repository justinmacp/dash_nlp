import sqlalchemy as db
import pandas as pd
from mysql.connector import Error
import datetime
from database.Upsert import Upsert


def create_table():
    engine = db.create_engine('mysql://root:Ju5Ky1M@@localhost/news')
    connection = engine.connect()
    metadata = db.MetaData()

    emp = db.Table('collection', metadata,
                   db.Column('title', db.String(128), nullable=False, primary_key=True),
                   db.Column('article_text', db.Text(), nullable=False),
                   db.Column('url', db.Text(), nullable=False),
                   db.Column('country', db.Text(), nullable=False),
                   db.Column('newspaper', db.Text(), nullable=False),
                   db.Column('city', db.Text(), nullable=False),
                   db.Column('publication_date', db.Date(), nullable=False, default=datetime.date(2000, 1, 1))
                   )

    metadata.create_all(engine)
    return engine


def insert_data(collection, connection):
    metadata = db.MetaData()
    emp = db.Table('collection', metadata,
                   db.Column('title', db.String(128), nullable=False, primary_key=True),
                   db.Column('article_text', db.Text(), nullable=False),
                   db.Column('url', db.Text(), nullable=False),
                   db.Column('country', db.Text(), nullable=False),
                   db.Column('newspaper', db.Text(), nullable=False),
                   db.Column('city', db.Text(), nullable=False),
                   db.Column('publication_date', db.Date(), nullable=False, default=datetime.date(2000, 1, 1))
                   )
    query = Upsert(emp, collection)
    connection.execute(query)


def create_database(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        print("Database created successfully")
    except Error as e:
        print(f"The error '{e}' occurred")


def pandas_df_to_mysql(connection, df, table_name):
    try:
        df.to_sql(name=table_name,
                  con=connection,
                  schema=None,
                  if_exists='fail',
                  index=True,
                  index_label=None,
                  chunksize=None,
                  dtype=None,
                  method=None
                  )
        print("Query executed successfully")
    except Error as e:
        print(f"The error '{e}' occurred")


def mysql_to_pandas_df(connection, query):
    try:
        pd.read_sql(sql=query,
                    con=connection,
                    index_col=None,
                    coerce_float=True,
                    params=None,
                    parse_dates=None,
                    chunksize=None)
        print("Query executed successfully")
    except Error as e:
        print(f"The error '{e}' occurred")


def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query executed successfully")
    except Error as e:
        print(f"The error '{e}' occurred")


def execute_read_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as e:
        print(f"The error '{e}' occurred")
