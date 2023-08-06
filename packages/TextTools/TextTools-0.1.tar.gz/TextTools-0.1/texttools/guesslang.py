import os
from texttools.trigram import Trigram

SAMPLES = os.path.join(os.path.dirname(__file__), 'samples')

def guesslang(text):

    text_trigram = Trigram()
    text_trigram.parse_text(text)
    refs = [(lang, Trigram(os.path.join(SAMPLES, '%s.txt' % lang)))
            for lang in ('en', 'fr')]

    similarities = [(text_trigram.similarity(trigram), lang)
                    for lang, trigram in refs]
    similarities.sort(reverse=True)
    return similarities

def guessfilelang(file):
    with open(file) as f:
        return guesslang(f.read())

