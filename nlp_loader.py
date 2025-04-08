import nltk
import spacy

nltk.download("punkt")
nltk.download("stopwords")
nltk.download("averaged_perceptron_tagger")  # optional, useful later

nlp = spacy.load("en_core_web_md")
