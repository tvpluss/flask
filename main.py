from datetime import datetime, timedelta, timezone
from functools import wraps
import time
from dotenv import load_dotenv
from flask import Flask, jsonify, request, Response
import os
import river
import pickle
from river import reco
from logging.config import dictConfig
from db import DB
from model import MFModel
from flask_apscheduler import APScheduler
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

model = MFModel('./model/MF_model.pkl')
scheduler = APScheduler()


try:
    dbname = os.environ.get('PGDATABASE')
    user = os.environ.get('PGUSER')
    port = os.environ.get('PGPORT')
    password = os.environ.get('PGPASSWORD')
    host = os.environ.get('PGHOST')
    app.logger.info(f'connecting to db..., {dbname}, {host}, {port}')
    db = DB(dbname, user, port, password, host)
except Exception as e:
    app.logger.error(f'Error connecting to db: {e}')


def api_key_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        key = request.headers.get('x-api-key')
        if key is None or key != api_secret_key:
            return Response(response="Unauthorized", status=401)
        return f(*args, **kwargs)
    return decorated


@app.route('/')
def index():
    return jsonify({"Choo Choo": "Welcome to your Flask app 🚅"})


# @app.route('/test_db')
# @api_key_required
# def testDB():
#     books = db.getBooksId()
#     print(books)
#     return jsonify(db.getBooksId())


@app.route('/recommender/<uid>')
@api_key_required
def recommender(uid):
    try:
        model.load_model()
        app.logger.info(f'getting recommender for uid: {uid}')
        rated_books = db.getBooksIdRatedByUser(uid)
        if len(rated_books.index) < 3:
            return Response(response="Not enough data for this user", status=400)
        unrated_books = db.getBooksId()
        cond = unrated_books['id'].isin(rated_books['id'])
        unrated_books.drop(unrated_books[cond].index, inplace=True)
        prediction = model.predict(uid, unrated_books)
        return jsonify(prediction.to_dict('records'))
    except Exception as e:
        return Response(response=e, status=404)
    finally:
        model.unload_model()


def update_model():
    try:
        now = datetime.now(timezone.utc)
        prev = datetime.now(timezone.utc) - timedelta(hours=1)
        app.logger.info(f'update model at {now}')
        model.load_model()
        updated_ratings = db.getRatings(prev, now)
        # Keep only rate, userId, and bookId columns and rename them
        updated_ratings = updated_ratings.loc[:, ['rate', 'userId', 'bookId']].rename(columns={
            'userId': 'user',
            'bookId': 'item'
        })
        if len(updated_ratings.index):
            app.logger.info(
                f'adding {len(updated_ratings.index)} records to model')
            model.train(updated_ratings)
            model.save_model()
        else:
            app.logger.info(f'no new date for model')
    except Exception as e:
        app.logger.error(e)
    finally:
        model.unload_model()


scheduler.add_job(id='Scheduled task', func=update_model,
                  trigger='interval', hours=1)
scheduler.start()


if __name__ == '__main__':

    app.logger.info(f'Running on port {os.environ.get("PORT")}')
    app.run(port=os.getenv("PORT", default=5000))
