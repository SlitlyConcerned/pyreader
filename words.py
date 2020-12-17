import model


class Page:
    def __init__(self, words, page, sentence_number):
        self._words = words
        self._page = page
        self._sentence_number = sentence_number

    @property
    def words_in_page(self):
        periodcount = 0
        for word in self._words:
            if 0 <= (periodcount - (self._page * self._sentence_number)) <= self._sentence_number:
                yield word
            if word == ".":
                periodcount += 1

    @property
    def word_models(self):
        return [model.Word.query.filter_by(word=word).first() for word in self.words_in_page]

    @property
    def states(self):
        for wordrow in self.word_models:
            if wordrow:
                yield wordrow.state
            else:
                yield "unknown"

    @property
    def translations(self):
        for wordrow in self.word_models:
            translation = ""
            transrow = model.Translation.query.filter_by(
                word=wordrow).first()
            if transrow:
                translation = transrow.translation
            yield translation


class Words:
    def __init__(self, tokenized_words):
        self._words = tokenized_words
        self.sentence_number = 4

    @property
    def maximum_possible_page_number(self):
        return self.words.count(".") / self._sentence_number

    def page(self, number):
        return Page(self._words, number, self.sentence_number)

    def get_pages(self):
        new = []
        states = []
        translations = []
        periodcount = 0
        for i in self.maximum_possible_page_number:
            yield Page(self._words, i, self.sentence_number)
