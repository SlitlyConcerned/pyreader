import re
import string
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy


def make_tokenizer_from_regex(re_string):
    return lambda inp: [word for word in re.findall(re_string, inp) if word]


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cat.db'
db = SQLAlchemy(app)

import dictionary
import model

puncs = [*string.punctuation, "\n"]
print(puncs)
TOKENIZERS = {
    "german": make_tokenizer_from_regex(f"[a-zA-ZäöüÄÖÜß]*[{''.join(puncs)}]*?")
}


def language():
    return model.User.query.first().language


db.create_all()


@app.route("/", methods=["GET", "POST"])
def root():
    if request.method == "POST":
        l1 = request.form["l1-name"]
        l2 = request.form["l2-name"]
        lang = model.Language(l1=l1, l2=l2)
        user = model.User(language=lang)
        db.session.add(user)
        db.session.commit()

    if not model.User.query.all():
        return render_template("language_setup.html")
    else:
        return render_template("main.html", articles=model.Article.query.all(), language=language())


@app.route("/<int:id>/read/<int:page>", methods=["GET", "POST"])
def read_article(id, page):
    if request.method == "POST":
        word = request.form["word"]
        translation = request.form["translation"]
        state = request.form["state"]
        wordrow = model.Word.query.filter_by(word=word).first()
        if wordrow:
            wordrow.state = state
            tr = model.Translation(translation=translation, word=wordrow)
            db.session.add(tr)
            db.session.commit()
    article = model.Article.query.get(id)
    tokenizer = TOKENIZERS[language().l2.lower()]
    words = tokenizer(article.text)
    print(words)
    wordnew = []
    dct = []
    translations = []
    periodcount = 0
    for word in words:
        print(periodcount / (4 * (page + 1)))
        if word == ".":
            periodcount += 1
        elif 1 > periodcount / (4 * (page + 1)) >= 0:
            wordnew.append(word)
            wordrow = model.Word.query.filter_by(word=word).first()
            transrow = model.Translation.query.filter_by(word=wordrow).first()
            translation = ""
            if wordrow:
                dct.append(wordrow.state)
            else:
                dct.append("unknown")

            if transrow:
                translation = transrow.translation

            translations.append(translation)


    return render_template("read.html", words=wordnew, status=dct, translations=translations, id=id, page=page)


@app.route("/<int:id>/delete", methods=["POST"])
def delete_article(id):
    db.session.query(model.Article).filter(model.Article.id == id).delete()
    db.session.commit()
    return redirect(url_for("root"))


@app.route("/add_article", methods=["POST"])
def add_article():
    title = request.form["title"]
    text = request.form["text"]
    article = model.Article(title=title, text=text, language=language())
    db.session.add(article)
    db.session.commit()
    return redirect(url_for("root"))


@app.route("/_get_translation", methods=["POST"])
def get_translation():
    word = request.json["text"]
    print(word)
    wordrow = model.Word.query.filter_by(word=word).first()
    transrow = model.Translation.query.filter_by(word=wordrow).first()
    if not transrow:
        lang = language()
        l1 = lang.l1
        l2 = lang.l2
        translation = dictionary.add_translation(word, l1, l2)
    else:
        translation = transrow.translation
    return jsonify(result=translation)


@app.route("/_set_word_status", methods=["POST"])
def set_word_status():
    word = request.json["word"]
    state = request.json["state"]
    wordrow = model.Word.query.filter_by(word=word).first()
    if not wordrow:
        word = model.Word(word=word, state="learning", language=language())
        db.session.add(word)
    else:
        wordrow.state = state
    db.session.commit()
    return jsonify(result=True)


@app.route("/_get_word_status", methods=["POST"])
def get_word_status():
    word = request.json["word"]
    wordrow = model.Word.query.filter_by(word=word).first()
    if not wordrow:
        return jsonify(result="unknown")
    return jsonify(result=wordrow.state)


@app.route("/_finish_page/<int:id>/<int:page>", methods=["POST"])
def finish_page(id, page):
    article = model.Article.query.get(id)
    tokenizer = TOKENIZERS[language().l2.lower()]
    words = tokenizer(article.text)
    periodcount = 0
    for word in words:
        if word == ".":
            periodcount += 1
        elif 2 > periodcount / (4 * (page + 1)) > 1:
            wordrow = model.Word.query.filter_by(word=word).first()
            if not wordrow:
                wordrow = model.Word(word=word, state="known", language=language())
                db.session.add(wordrow)
    db.session.commit()
    return redirect(url_for("read_article", id=id, page=page+1))
