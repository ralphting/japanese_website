import os
import uuid

from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
import requests
import speech_recognition as sr

JAPANESE_API_URL = "https://chibachoose.pythonanywhere.com/"

app = Flask(__name__)
app.config['SECRET_KEY'] = "SecretKey"
app.config['UPLOAD_FOLDER'] = 'D://pythonProject/japanese_website/data'

app.config['SQLALCHEMY_DATABASE_URI'] ='sqlite:///kanji.db'
db = SQLAlchemy(app)

@app.route('/', methods=["GET", "POST"])
def home():
    return render_template('index.html')

@app.route('/word')
def word():
    response = requests.get(f"{JAPANESE_API_URL}random")
    word_data = response.json()
    return render_template('word.html', word=word_data)

@app.route('/list')
def list():
    response = requests.get(f"{JAPANESE_API_URL}all")
    word_list = response.json()
    return render_template('list.html', word_list=word_list)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/save-record', methods=['POST'])
def save_record():
    # check if the post request has the file part
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    # if user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    file_name = str(uuid.uuid4()) + ".wav"
    full_file_name = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
    file.save(full_file_name)
    return '<h1>Success</h1>'

if __name__ == "__main__":
    app.run(debug=True)