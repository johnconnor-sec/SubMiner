import asyncio

import pyfiglet

from analyze_comments import summarize_comments
from analyze_topics import run_analysis
from cli import parse_args
from database import get_post_by_id, get_top_posts, save_to_sqlite
from fetch_reddit_posts import initialize_reddit, scrape_reddit
from utils import print_post_from_id, print_summary

text = "SubMiner"
ascii_banner = pyfiglet.figlet_format(text, font="slant")
print(ascii_banner)
print("\nSubMiner - Mine Reddit for gold\n")


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

        # If --get is used, show results and exit early
        if args.get:
            df = get_post_by_id(args.get)
            if df.empty:
                print("⚠️ No results found in the database.")
            else:
                # print(f"\n🔎 Post ID: {args.get}\n")
                post = df.iloc[0]
                print_post_from_id(post)
                if args.analyze_comments:
                    print(summarize_comments(post))
            return

        # Otherwise, scrape and save
        print(
            f"\n🔍 Searching past {args.days} days, min upvotes: {args.min_upvotes}\n"
        )

        async with initialize_reddit() as reddit:
            results = await scrape_reddit(
                reddit,
                subreddits=args.subreddits,
                keywords=args.keywords,
                days=args.days,
                min_upvotes=args.min_upvotes,
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
