from app import db
import tokenizer


class Translation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    translation = db.Column(db.Text, nullable=False)
    word_id = db.Column(db.Integer, db.ForeignKey("word.id"),
                        nullable=False)
    word = db.relationship("Word")


class Word(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.Text, nullable=False)
    state = db.Column(db.Text, nullable=False)
    language_id = db.Column(db.Integer, db.ForeignKey('language.id'),
                            nullable=False)
    language = db.relationship("Language")


class Language(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    l1 = db.Column(db.Text, nullable=False)
    l2 = db.Column(db.Text, nullable=False)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    language_id = db.Column(db.Integer, db.ForeignKey('language.id'),
                            nullable=False)
    language = db.relationship("Language")


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    text = db.Column(db.Text, unique=True, nullable=False)
    language_id = db.Column(db.Integer, db.ForeignKey('language.id'),
                            nullable=False)
    language = db.relationship("Language")

    @classmethod
    def tokenize(cls, id, language):
        article = cls.query.get(id)
        tokenizer_func = tokenizer.TOKENIZERS[language.l2.lower()]
        return tokenizer_func(article.text)
