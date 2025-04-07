from tabulate import tabulate


def print_summary(results):
    table = [[r["title"], r["upvotes"], r["subreddit"], r["url"]] for r in results[:10]]
    print(tabulate(table, headers=["Title", "Upvotes", "Subreddit", "URL"]))
