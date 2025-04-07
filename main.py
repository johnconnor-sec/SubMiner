import asyncio

# import os
# import sys

import pandas as pd

from analyze_topics import run_analysis
from cli import parse_args
from database import get_top_posts, save_to_sqlite
from fetch_reddit_posts import initialize_reddit, scrape_reddit
from utils import print_summary

# def save_to_csv(results, filename="output/reddit_app_ideas.csv"):
#     if not results:
#         print("⚠️ No results to save.")
#         return
#
#     os.makedirs(os.path.dirname(filename), exist_ok=True)
#     df = pd.DataFrame(results)
#     df.sort_values(by="upvotes", ascending=False, inplace=True)
#     df.to_csv(filename, index=False)
#     print(f"✅ Saved {len(df)} entries to {filename}")


# if sys.platform == "linux":
#     asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())


async def main():
    try:
        args = parse_args()

        # If --top is used, show results and exit early
        if args.top > 0:
            df = get_top_posts(args.top)
            if df.empty:
                print("⚠️ No results found in the database.")
            else:
                print(f"\n🔎 Top {args.top} Reddit App Ideas:\n")
                print(df.to_markdown(index=False))
            return

        # Otherwise, scrape and save
        print(
            f"\n🔍 Searching past {args.days} days, min upvotes: {args.min_upvotes}\n"
        )

        async with initialize_reddit() as reddit:
            results = await scrape_reddit(
                reddit,
                days=args.days,
                min_upvotes=args.min_upvotes,
                keyword_filter=args.keyword,
            )

        if results:
            save_to_sqlite(results)
            print_summary(results)
            if args.analyze:
                run_analysis()
        else:
            print("⚠️ No results found with the current filters.")
    except Exception as e:
        raise e


if __name__ == "__main__":
    asyncio.run(main())
