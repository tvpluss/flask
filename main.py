from dotenv import load_dotenv
from flask import Flask, jsonify, request, Response
import os
import river
import pickle
from river import reco
from logging.config import dictConfig
from db import DB

load_dotenv()
dictConfig(

    {

        "version": 1,

        "formatters": {

            "default": {

                "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",

            }

        },

        "handlers": {

            "console": {

                "class": "logging.StreamHandler",

                "stream": "ext://sys.stdout",

                "formatter": "default",

            }

        },

        "root": {"level": "DEBUG", "handlers": ["console"]},

    }

)
api_secret_key = os.environ.get('api_secret_key')
app = Flask(__name__)
try:
    dbname = os.environ.get('PGDATABASE')
    user = os.environ.get('PGUSER')
    port = os.environ.get('PGPORT')
    password = os.environ.get('PGPASSWORD')
    host = os.environ.get('PGHOST')
    db = DB(dbname, user, port, password, host)
except Exception as e:
    app.logger.error(f'Error connecting to db: {e}')


@app.route('/')
def index():
    return jsonify({"Choo Choo": "Welcome to your Flask app 🚅"})


@app.route('/save_model')
def saveModel():
    model = reco.BiasedMF()
    with open('MF_model.pkl', 'wb') as f:
        pickle.dump(model, f)

    return 'Model saved'


@app.route('/read_model')
def readModel():
    with open('MF_model.pkl', 'rb') as f:
        model = pickle.load(f)
        return 'Readed model'


@app.route('/save_file/<content>')
def saveFile(content):
    # open a file in write mode
    file = open('example.txt', 'w')

    # write some text to the file
    file.write(f'Content: {content}')

    # close the file
    file.close()
    return "saved_file"


@app.route('/read_file')
def readFile():
    with open('example.txt') as file:
        contents = file.read()
        return contents


@app.route('/test_db')
def testDB():
    books = db.getBooks()
    print(books)
    return jsonify(db.getBooks())


@app.route('/recommender/<uid>')
def recommender(uid):
    key = request.headers.get('x-api-key')
    if key is None or key != api_secret_key:
        return Response(response="Unauthorized", status=401)
    print(f'getting recommender for uid: {uid}')
    return 'Authorized'


if __name__ == '__main__':

    app.logger.info(f'Running on port {os.environ.get("PORT")}')
    app.run(debug=True, port=os.getenv("PORT", default=5000))
