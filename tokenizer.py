import string


def make_tokenizer_from_regex(re_string):
    return lambda inp: [word for word in re.findall(re_string, inp) if word]


puncs = [*string.punctuation, "\n"]

TOKENIZERS = {
    "german": make_tokenizer_from_regex(f"[a-zA-ZäöüÄÖÜß0-9]*[{''.join(puncs)}]*?")
}
