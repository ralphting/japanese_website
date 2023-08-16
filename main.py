from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import requests
import speech_recognition as sr

JAPANESE_API_URL = "https://chibachoose.pythonanywhere.com/"

app = Flask(__name__)
app.config['SECRET_KEY'] = "SecretKey"

app.config['SQLALCHEMY_DATABASE_URI'] ='sqlite:///kanji.db'
db = SQLAlchemy(app)

@app.route('/')
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


if __name__ == "__main__":
    app.run(debug=True)