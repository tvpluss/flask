from flask import Flask, jsonify
import os
import river
import pickle
from river import reco
app = Flask(__name__)


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


if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))
