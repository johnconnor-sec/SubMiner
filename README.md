# 🧠 Next Steps

## Want to add

### CLI args

- [x] Add filtering by upvotes (e.g. score > 10)

- [~] Sort by most upvoted

- [x] CLI arg for --min-upvotes?

- [x] Add SQLite storage with deduping?

Filter posts per subreddit (CLI: --sub=AppIdeas)

- [x] --top results

- [x] --keyword <custom search>

- [x] Query --top results within last N days

Add --dry-run mode to just print scraped results

### Processing

- [x] Clean the text (remove emojis, junk)

- [x] Analyze frequent topics (basic NLP)

Filter keyword/noun clusters by subreddit or time range

Plot them with matplotlib or wordcloud

Add FTS5 or `whoosh` for full-text search on title/text

LLM summarization pipeline to summarize top ideas / Integrate similarity-based LLM summarization

### Scraping

- [x] Add threading for faster scraping

- [x] Add support for asyncio and aiohttp for full async data scraping

Queue async insertions into SQLite

Cache subreddit results to reduce repeated scrapes

Connect async scraping with LLM agent for real-time summarization

Stream real-time scraping to terminal (async generators)

Stream ideas to WebSocket dashboard

### Output

Dump results to JSON, Markdown, or Notion

Dump keyword clusters to Markdown/CSV

Turn this into a TUI app with Textual or Rich?

Visualize with Matplotlib or seaborn

Turn promising ideas into a todo list or dev project board

Run as background job and log to file (logging module)
