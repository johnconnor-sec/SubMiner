from tabulate import tabulate


def print_summary(results):
    table = [[r["title"], r["upvotes"], r["subreddit"], r["url"]] for r in results[:10]]
    print(tabulate(table, headers=["Title", "Upvotes", "Subreddit", "URL"]))


def print_post_from_id(post):
    markdown_output = f"""
---
{post["id"]}
r/{post["subreddit"]}: {post["url"]}
{post["created"]}
{post["upvotes"]} upvotes
---

# {post["title"]}

{post["text"]}

--- 

## COMMENTS: {post["comments"]}

{post["comments_text"]}
"""
    print(markdown_output)
