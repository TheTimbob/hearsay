# Hearsay

A satire engine that reads real headlines and writes the news that didn't happen.

Hearsay pulls stories from an RSS news feed, judges which headlines are worth satirizing, then
generates a fabricated article and a matching image for the ones that make the cut. In the vein of
The Onion or the Babylon Bee — the headline is real, everything after it is invented.

## How it works

1. **Scrape** — pull entries from a configured RSS feed
2. **Evaluate** — a model scores each headline for satirical potential and returns a verdict with a reason
3. **Generate** — accepted headlines get a full article and an accompanying image
4. **Store** — headlines, verdicts, articles, and image filenames persist to SQLite so nothing is processed twice
5. **Publish** — a static page renders whatever is in the database as a grid of cards

The evaluation step is the part worth pointing at. Rather than satirizing every headline that comes
through the feed, the pipeline filters first and records *why* each one was accepted or rejected —
which turns prompt tuning into something you can look at after the fact instead of guess at.

## Stack

Python 3.9+, OpenAI (`gpt-5.6-terra` for articles, `gpt-5.6-luna` for headline evaluation,
`gpt-image-2` for images), feedparser, SQLite, Poetry.

## Configuration

Three environment variables, read from `.env`:

| Variable | Purpose |
| --- | --- |
| `API_KEY` | OpenAI API key |
| `RSS_FEED_URL` | RSS feed to pull headlines from |
| `DB_CONNECTION_STRING` | Path to the SQLite database file |

Prompt files live in `prompts/` and are committed, so the pipeline runs as-is. They are also the
part most worth rewriting — the instructions are the voice:

- `prompts/inputs.json` — the article prompt, under the `default` key
- `prompts/title-instructions.txt` — headline evaluation criteria, must return JSON with `suitable` and `reason`
- `prompts/article-instructions.txt` — article voice and structure
- `prompts/image-instructions.txt` — image style

The evaluation step's `reason` is passed forward into the article prompt, so whatever angle made a
headline worth using is handed to the writer rather than discarded.

The SQLite database expects two tables, `titles` and `articles`. See `src/database.py` for the
columns each one is written with.

## Running

```
poetry install
poetry run python src/main.py
```

One run walks the feed, stops at the first headline it hasn't already seen and judges suitable,
generates the article and image, writes both to the database, and exits.

To render what's been generated so far:

```
poetry run python src/build_site.py
```

This writes `site/index.html` — a single self-contained page, no server and no build step, that
lays out every stored article as a card with its image. Open it directly in a browser. It reads the
database and nothing else, so it is safe to re-run any time and is not part of the generation path.
