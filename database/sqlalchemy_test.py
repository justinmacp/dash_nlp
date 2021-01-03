from database.sqlalchemy_utils import *
from webcrawler import sudan_parser


def view_db():
    engine = sqlalchemy.create_engine('mysql://root:Ju5Ky1M@@localhost/news')
    connection = engine.connect()
    metadata = sqlalchemy.MetaData()
    news = sqlalchemy.Table('collection', metadata, autoload=True, autoload_with=engine)
    print(news.columns.keys())
    query = sqlalchemy.select([news])
    ResultProxy = connection.execute(query)
    print(ResultProxy.fetchall())


engine = create_table()
connection = engine.connect()
metadata = sqlalchemy.MetaData()
census = sqlalchemy.Table('collection', metadata, autoload=True, autoload_with=engine)
print(census.columns.keys())
print(repr(metadata.tables['collection']))
urls = sudan_parser.scrape_st_article_urls()
collection = sudan_parser.scrape_st_article(urls)
insert_data(collection, connection)
view_db()
