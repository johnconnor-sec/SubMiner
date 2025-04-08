import asyncio
import os
import random
import time
from aiohttp import ClientResponseError
from datetime import datetime

import asyncpraw
from dotenv import load_dotenv
from prawcore.exceptions import RequestException, ResponseException, ServerError

from configs import KEYWORDS, SUBREDDITS

load_dotenv()


# --- Step 1: Reddit API Authentication ---
def initialize_reddit():
    """
    Create your app and find the keys at https://www.reddit.com/prefs/apps/
    """
    return asyncpraw.Reddit(
        client_id=os.getenv("CLIENT_ID"),
        client_secret=os.getenv("CLIENT_SECRET"),
        user_agent="app-idea-generator",
    )


def post_matches(post, keyword, min_upvotes, time_threshold):
    post_text = post.selftext or ""
    return (
        post.score >= min_upvotes
        and post.created_utc >= time_threshold
        and (
            keyword.lower() in post.title.lower()
            or keyword.lower() in post_text.lower()
        )
    )


# --- Step 2: Fetch Reddit Posts ---
async def search_subreddit(
    reddit, subreddit, keyword, time_threshold, min_upvotes, limit
):
    """
    Searches a given subreddit for a specific keyword and returns a list of posts
    that meet the upvote and time criteria. Includes request throttling and retry logic.
    """
    results = []
    max_retries = 5
    backoff_base = 2

    for attempt in range(max_retries):
        try:
            # Simulate human-like delay
            await asyncio.sleep(random.uniform(0.5, 1.5))

            sub = await reddit.subreddit(subreddit)
            async for post in sub.search(keyword, limit=limit):
                if post_matches(post, keyword, min_upvotes, time_threshold):
                    await post.load()
                    comments = []
                    try:
                        async for comment in post.comments:
                            if hasattr(comment, "body"):
                                comments.append(comment.body.strip())
                            if len(comments) > 10:
                                break
                    except Exception as e:
                        print(f"⚠️ Could not load comments for post {post.id}: {e}")

                    results.append(
                        {
                            "id": post.id,
                            "title": post.title,
                            "text": post.selftext,
                            "url": post.url,
                            "upvotes": post.score,
                            "comments": post.num_comments,
                            "subreddit": subreddit,
                            "created": datetime.utcfromtimestamp(
                                post.created_utc
                            ).strftime("%Y-%m-%d"),
                            "comments_text": "\n\n---\n\n".join(comments),
                        }
                    )

            return results

        except ClientResponseError as e:
            if e.status == 429:
                delay = backoff_base**attempt + random.uniform(1.0, 3.0)
                print(f"""
                    ⚠️ Rate limit reached on r/{subreddit} (attempt {attempt + 1}/{max_retries})
                    """)
                await asyncio.sleep(delay)
            else:
                raise Exception(f"{ResponseException}")

        except (RequestException, ResponseException, ServerError) as e:
            delay = backoff_base**attempt + random.uniform(0.2, 0.6)
            print(
                f"⚠️ Error in r/{subreddit} for '{keyword}' (attempt {attempt + 1}/{max_retries}): {e}"
            )
            print(f"⏳ Backing off for {delay:.2f} seconds...")
            await asyncio.sleep(delay)
        except Exception as e:
            print(f"❌ Unexpected error in r/{subreddit}: {e}")
            break  # don't retry non-network-related errors

    return results  # return whatever was gathered (even if empty)


# --- Step 3: Threading the API calls ---
async def scrape_reddit(reddit, days, min_upvotes, keyword_filter=None, limit=100):
    time_threshold = time.time() - (days * 86400)  # 86400 secs in a day
    search_keywords = [keyword_filter] if keyword_filter else KEYWORDS

    sem = asyncio.Semaphore(3)

    async def limited_search(subreddit, keyword):
        async with sem:
            return await search_subreddit(
                reddit, subreddit, keyword, time_threshold, min_upvotes, limit
            )

    # --- Step 3: Loop Through Subreddits and Keywords ---
    tasks = []
    for subreddit in SUBREDDITS:
        for keyword in search_keywords:
            print(f"🔍 Scanning: r/{subreddit} for '{keyword}'")
            tasks.append(limited_search(subreddit, keyword))
            await asyncio.sleep(0.2)

    all_results = await asyncio.gather(*tasks)

    # Flatten and sort the results
    flattened = [post for result in all_results for post in result]
    sorted_posts = sorted(flattened, key=lambda x: x["upvotes"], reverse=True)

    return sorted_posts
