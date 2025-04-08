import sqlite3
from collections import Counter

import pandas as pd
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from textblob import TextBlob

from analyze_topics import clean_text
from configs import DB_PATH


def load_comments_data():
    conn = sqlite3.connect(DB_PATH)
    query = "SELECT comments_text FROM posts"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


def extract_keywords_from_comments(comments_text, top_n=10):
    stop_words = set(stopwords.words("english"))
    words = []

    for comment in comments_text:
        cleaned = clean_text(comment)
        tokens = word_tokenize(cleaned)
        filtered = [word for word in tokens if word not in stop_words and len(word) > 2]
        words.extend(filtered)

    freq = Counter(words)
    return freq.most_common(top_n)


def analyze_sentiment(comments_text):
    sentiments = []
    for comment in comments_text:
        blob = TextBlob(comment)
        sentiments.append(blob.sentiment.polarity)

    if not sentiments:
        return {"avg_sentiment": 0, "positive": 0, "neutral": 0, "negative": 0}

    avg = sum(sentiments) / len(sentiments)
    pos = len([s for s in sentiments if s > 0.1])
    neg = len([s for s in sentiments if s < -0.1])
    neu = len(sentiments) - pos - neg

    return {
        "avg_sentiment": round(avg, 3),
        "positive": pos,
        "neutral": neu,
        "negative": neg,
    }


def summarize_comments(post_row):
    comments_text = post_row["comments_text"]
    if not comments_text:
        return "⚠️ No comments to analyze."

    comments = [c.strip() for c in comments_text.split("---") if c.strip()]
    sentiment_summary = analyze_sentiment(comments)
    keyword_summary = extract_keywords_from_comments(comments)

    md = f"""
### 💬 Comment Summary for Post `{post_row["id"]}`

**Sentiment Analysis**
- Average sentiment: {sentiment_summary["avg_sentiment"]}
- Positive: {sentiment_summary["positive"]}
- Neutral: {sentiment_summary["neutral"]}
- Negative: {sentiment_summary["negative"]}

**Top Keywords:**
"""
    for word, count in keyword_summary:
        md += f"- {word} ({count})\n"

    return md.strip()
