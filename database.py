import os
import sqlite3

import pandas as pd

from configs import DB_PATH


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id TEXT PRIMARY KEY,
            title TEXT,
            text TEXT,
            url TEXT,
            upvotes INTEGER,
            comments INTEGER,
            subreddit TEXT,
            created TEXT,
            comments_text TEXT
        )
    """)
    conn.commit()
    return conn


def save_to_sqlite(results):
    conn = init_db()
    cursor = conn.cursor()

    inserted = 0
    for post in results:
        try:
            cursor.execute(
                """
                INSERT OR IGNORE INTO posts (id, title, text, url, upvotes, comments, subreddit, created, comments_text)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    post["id"],
                    post["title"],
                    post["text"],
                    post["url"],
                    post["upvotes"],
                    post["comments"],
                    post["subreddit"],
                    post["created"],
                    post["comments_text"],
                ),
            )
            if cursor.rowcount > 0:
                inserted += 1
        except Exception as e:
            print(f"⚠️ Skipped post due to error: {e}")

    conn.commit()
    conn.close()
    print(f"✅ Inserted {inserted} new posts into {DB_PATH}")


def get_top_posts(n):
    conn = sqlite3.connect(DB_PATH)
    query = f"""
        SELECT id, title, url, upvotes, subreddit, created
        FROM posts
        ORDER BY upvotes DESC
        LIMIT {n}
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


def get_post_by_id(post_id):
    conn = sqlite3.connect(DB_PATH)
    query = """
        SELECT id, title, text, url, upvotes, comments, subreddit, created, comments_text
        FROM posts
        WHERE id = ?
        LIMIT 1
    """
    df = pd.read_sql_query(query, conn, params=(post_id,))
    conn.close()
    return df
