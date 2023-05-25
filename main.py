from flask import Flask, jsonify
import os

app = Flask(__name__)


@app.route('/')
def index():
    return jsonify({"Choo Choo": "Welcome to your Flask app 🚅"})


@app.route('/save_file')
def saveFile():
    # open a file in write mode
    file = open('example.txt', 'w')

    # write some text to the file
    file.write('Hello, world!')

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
