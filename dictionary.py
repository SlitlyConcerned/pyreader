import langcodes
import requests

from app import db
from model import Language, Translation, Word


class DictionaryService(dict):

    def __init__(self, apikey, l1, l2):
        self.apikey = apikey
        self.l1 = l1
        self.l2 = l2

    def __getitem__(self, key):
        return self.get(key)

    def url(self):
        raise NotImplementedError

    def get(self, text):
        data = self.get_data(text)
        resp = requests.get(self.url(), params=data)
        result = resp.json()
        return self.get_translation(result)

    def get_translation(self, result_data):
        raise NotImplementedError

    def get_data(self, text):
        data = {
            self.langkey(): self.langvalue(),
            self.textkey(): text
        }

        if self.keyvalue():
            data = {**data, self.keykey():self.keyvalue()}

        return data

    def langvalue(self):
        l1 = self.lang_convert(self.l1)
        l2 = self.lang_convert(self.l2)
        return f"{l2}-{l1}"

    def lang_convert(self, language):
        return langcodes.find(language).language

    def keyvalue(self):
        return self.apikey

    def keykey(self):
        return "key"

    def langkey(self):
        return "lang"

    def textkey(self):
        return "text"


class YandexDictionary(DictionaryService):
    def url(self):
        return "https://dictionary.yandex.net/api/v1/dicservice.json/lookup"

    def get_translation(self, result_data):
        return result_data["def"][0]["tr"][0]["text"]


def _add_translation_if_not_exist(word="", tr="", l1="", l2=""):
    language = Language(l1=l1, l2=l2)
    wordrow = Word.query.filter_by(word=word).first()
    if not wordrow:
        wordrow = Word(word=word, state="learning", language=language)
        db.session.add(wordrow)

    translation = Translation(translation=tr, word=wordrow)
    db.session.add(translation)
    db.session.commit()


def add_translation(text, l1, l2):
    services = [YandexDictionary(
        apikey=os.environ.get("YANDEX_APIKEY"),
        l1=l1,
        l2=l2
    )]
    for service in services:
        result = service[text]
        if result is not None:
            _add_translation_if_not_exist(word=text, tr=result, l1=l1, l2=l2)
        return result
