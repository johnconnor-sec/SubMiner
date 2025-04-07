import argparse


def parse_args():
    parser = argparse.ArgumentParser(description="Scrape Reddit for app ideas.")
    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="Number of days to look back (e.g., 7, 30, default: 7)",
    )
    parser.add_argument(
        "--min-upvotes",
        type=int,
        default=10,
        help="Minimum upvotes for a post to be included (default: 10)",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=0,
        help="Number of top posts to display (0 to skip, default: 0)",
    )
    parser.add_argument(
        "--keyword",
        type=str,
        default=None,
        help="Custom keyword to search for (overrides default keywords)",
    )
    parser.add_argument(
        "--analyze", action="store_true", help="Run NLP topic analysis after scraping"
    )
    return parser.parse_args()
