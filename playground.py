import os
from dotenv import load_dotenv
import pandas as pd

from db import DB
from model import MFModel


load_dotenv()
dbname = os.environ.get('PGDATABASE')
user = os.environ.get('PGUSER')
port = os.environ.get('PGPORT')
password = os.environ.get('PGPASSWORD')
host = os.environ.get('PGHOST')
print(f'connecting to db..., {dbname}, {host}, {port}')
db = DB(dbname, user, port, password, host)
print(f'connected to db')
# print(db.getRatings(datetime(year=2023, month=4, day=8),
#       datetime(year=2023, month=4, day=9)))
# print(db.getBooksId())
user_id = '193458'
rated_books = db.getRatingsByUser(user_id)

model = MFModel()
model.load_model('./model/MF_model.pkl')
prediction = model.predict(user_id, rated_books)
print(prediction)
# data = [['278066', '0062737465', 4],
#         ['277978', '0896083535', 4],
#         ['277965', '1888387408', 3]]
# df = pd.DataFrame(data, columns=['user', 'item', 'rate'])
# print(df)
# print(model.test(df))
