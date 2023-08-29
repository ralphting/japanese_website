import os

from flask import Flask, render_template, request, redirect, flash, url_for, json, jsonify
from flask_sqlalchemy import SQLAlchemy
import requests
import whisper

JAPANESE_API_URL = "https://chibachoose.pythonanywhere.com/"

app = Flask(__name__)
app.config['SECRET_KEY'] = "SecretKey"
app.config['UPLOAD_FOLDER'] = app.root_path + "\\tmp"

app.config['SQLALCHEMY_DATABASE_URI'] ='sqlite:///kanji.db'
db = SQLAlchemy(app)

model = whisper.load_model("base")


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

@app.route('/transcribe', methods=['GET', 'POST'])
def transcribe():
    if request.method == "POST":
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        file_name = "data.wav"
        # full_file_name = os.path.join(app.instance_path, file_name)
        full_file_name = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
        file.save(full_file_name)
        result = model.transcribe(full_file_name)
        transcript = result["text"]
        print(transcript)
        return jsonify({'transcript': transcript})
    else:
        return render_template('transcribe.html')

@app.route('/save_record', methods=['POST'])
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
    file_name = "data.wav"
    # full_file_name = os.path.join(app.instance_path, file_name)
    full_file_name = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
    file.save(full_file_name)
    result = model.transcribe(full_file_name)
    transcript = result["text"]
    print(transcript)
    return redirect(url_for('transcribe'))


if __name__ == "__main__":
    app.run(debug=True)