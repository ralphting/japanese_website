import os

from flask import Flask, render_template, request, redirect, flash, url_for, json, jsonify
from flask_sqlalchemy import SQLAlchemy
import requests
import random
import whisper

JAPANESE_API_URL = "https://chibachoose.pythonanywhere.com/api/"

app = Flask(__name__)
#Part of the website
app.config['SECRET_KEY'] = "SecretKey"
app.config['UPLOAD_FOLDER'] = app.root_path + "\\tmp"

#Part of the API
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///kanji.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

#part of the website
model = whisper.load_model("base")

class Kanji(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kanji = db.Column(db.String, unique=True, nullable=False)
    kunyomi = db.Column(db.String, nullable=False)
    onyomi = db.Column(db.String, nullable=False)
    meaning = db.Column(db.String, nullable=False)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

#This is part of the website.
@app.route('/', methods=["GET", "POST"])
def home():
    return render_template('index.html')

@app.route('/word')
def word():
    # response = requests.get(f"{JAPANESE_API_URL}random")
    string_path = str(request.url_root + url_for('random_kanji'))
    response = requests.get(string_path)
    word_data = response.json()
    return render_template('word.html', word=word_data)

@app.route('/list')
def list():
    # response = requests.get(f"{JAPANESE_API_URL}all")
    string_path = str(request.url_root + url_for('get_all'))
    response = requests.get(string_path)
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
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        file_name = "data.wav"
        full_file_name = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
        file.save(full_file_name)
        result = model.transcribe(full_file_name)
        transcript = result["text"]
        os.remove(full_file_name)
        print(transcript)
        return jsonify({'transcript': transcript})
    else:
        return render_template('transcribe.html')

#Added API into the same Flask server
@app.route('/api')
def api_home():
    return "Japanese Kanji API Version 1.0.0 by Ralph Ting"

@app.route('/api/random', methods=["GET"])
def random_kanji():
    if request.method == "GET":
        rows = db.session.query(Kanji).count()
        random_id = random.randint(1, rows)
        random_word = Kanji.query.get(random_id)
        return jsonify(random_word.to_dict())

@app.route('/api/all', methods=["GET"])
def get_all():
    if request.method == "GET":
        all_kanji_db = db.session.execute(db.select(Kanji).order_by(Kanji.id)).scalars().all()
        all_kanji_list = [kanji.to_dict() for kanji in all_kanji_db]
        if all_kanji_list:
            return jsonify(all_kanji_list)
        else:
            return jsonify({"error": "No entries in database. Please try again."})

@app.route('/api/search', methods=["GET"])
def search_kanji():
    if request.method == "GET":
        kanji_id = request.args.get('id')
        try:
            kanji = db.session.query(Kanji).get(kanji_id)
            return jsonify(kanji.to_dict())
        except Exception as err:
            return jsonify({"error": str(err)})

@app.route('/api/add', methods=["POST"])
def add_kanji():
    if request.method == "POST":
        api_key = request.headers.get('apikey')
        if api_key == os.getenv('API_KEY'):
            new_kanji = Kanji(
                kanji=request.args.get('kanji'),
                kunyomi=request.args.get('kunyomi'),
                onyomi=request.args.get('onyomi'),
                meaning=request.args.get('meaning')
            )
            db.session.add(new_kanji)
            try:
                db.session.commit()
                return jsonify(response={"success": "Successfully added the new kanji."})
            except Exception as err:
                return jsonify(error={"failed": str(err)})
        else:
            return jsonify(error={"failed": "Invalid API_KEY."})

@app.route('/api/edit', methods=["PATCH"])
def edit_kanji():
    if request.method == "PATCH":
        api_key = request.headers.get('apikey')
        if api_key == os.getenv('API_KEY'):
            kanji_id  = request.args.get('id')
            try:
                kanji_to_edit = db.session.query(Kanji).get(kanji_id)
                if request.args.get('kunyomi'):
                    kanji_to_edit.kunyomi = request.args.get('kunyomi')
                if request.args.get('onyomi'):
                    kanji_to_edit.onyomi = request.args.get('onyomi')
                if request.args.get('meaning'):
                    kanji_to_edit.meaning = request.args.get('meaning')
                db.session.commit()
                return jsonify({"success": "The kanji has beeen successfully updated"})
            except Exception as err:
                return jsonify({"error": str(err)})

@app.route('/api/delete', methods=["DELETE"])
def delete_kanji():
    if request.method == "DELETE":
        api_key = request.headers.get('apikey')
        if api_key == os.getenv('API_KEY'):
            kanji_id = request.args.get('id')
            try:
                kanji_to_delete = db.session.query(Kanji).get(kanji_id)
                db.session.delete(kanji_to_delete)
                db.session.commit()
                return jsonify({"success": "The kanji has been successfully deleted"})
            except Exception as err:
                return jsonify({"error": str(err)})
        else:
            return jsonify({"error": "Invalid API_KEY."})

if __name__ == "__main__":
    app.run(debug=True)
