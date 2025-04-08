import re
import sqlite3
from collections import Counter

import nltk
import pandas as pd
import spacy
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.cluster import KMeans

# Only needed once
nltk.download("punkt")
nltk.download("stopwords")
nltk.download("averaged_perceptron_tagger")  # optional, useful later

nlp = spacy.load("en_core_web_md")
from configs import DB_PATH


def load_text_data():
    conn = sqlite3.connect(DB_PATH)
    query = "SELECT title, text FROM posts"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


def clean_text(text):
    text = re.sub(r"http\S+", "", text)  # remove URLs
    text = re.sub(r"[^a-zA-Z\s]", "", text)  # remove non-alphabetic
    text = text.lower()
    return text


def extract_keywords(df, top_n=20):
    stop_words = set(stopwords.words("english"))
    all_tokens = []

    for _, row in df.iterrows():
        combined_text = f"{row['title']} {row['text']}"
        cleaned = clean_text(combined_text)
        tokens = word_tokenize(cleaned)
        filtered = [word for word in tokens if word not in stop_words and len(word) > 2]
        all_tokens.extend(filtered)

    freq = Counter(all_tokens)
    return freq.most_common(top_n)


def cluster_keywords(keywords, n_clusters=5):
    # Convert keywords to vectors
    vectors = []
    valid_keywords = []

    for word, _ in keywords:
        token = nlp.vocab[word]
        if token.has_vector:
            vectors.append(token.vector)
            valid_keywords.append(word)

    if not vectors:
        print(
            "❌ No keyword vectors found. Check if your spaCy model has word vectors."
        )
        return

    # Cluster keywords
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    labels = kmeans.fit_predict(vectors)

    clusters = {}

    # Find keywords for each cluster
    for word, label in zip(valid_keywords, labels):
        clusters.setdefault(label, []).append(word)

    print("\n🌟 Top Keywords by Cluster (via spaCy embeddings + KMeans):\n")
    for label, words in clusters.items():
        print(f"Cluster {label + 1}: {', '.join(words)}")


def run_analysis():
    df = load_text_data()
    if df.empty:
        print("⚠️ No data found in the database for analysis.")
        return
    top_keywords = extract_keywords(df)
    cluster_keywords(top_keywords, n_clusters=5)

    print("\n🧠 Top Keywords in App Ideas:\n")
    print("{:<20} {:>5}".format("Keyword", "Freq"))
    print("-" * 28)
    for word, count in top_keywords:
        print(f"{word:<20} {count:>5}")


if __name__ == "__main__":
    run_analysis()
