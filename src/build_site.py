import html
import os
import sqlite3
from dotenv import load_dotenv

load_dotenv()

DB_CONNECTION_STRING = os.getenv("DB_CONNECTION_STRING")
SITE_PATH = 'site/'
OUTPUT_FILE = 'site/index.html'
IMAGES_RELATIVE_PATH = '../images/'

PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Hearsay</title>
<style>
* {{ box-sizing: border-box; }}
body {{
  margin: 0;
  padding: 3rem 1.5rem;
  font-family: Georgia, 'Times New Roman', serif;
  background: #f4f1ea;
  color: #1a1a1a;
}}
header {{
  max-width: 1100px;
  margin: 0 auto 3rem;
  border-bottom: 3px double #1a1a1a;
  padding-bottom: 1.5rem;
}}
h1 {{
  margin: 0;
  font-size: clamp(2.5rem, 8vw, 4.5rem);
  letter-spacing: -0.02em;
}}
.tagline {{
  margin: 0.5rem 0 0;
  font-style: italic;
  color: #5a5a5a;
}}
.grid {{
  max-width: 1100px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 2rem;
}}
article {{
  background: #fff;
  border: 1px solid #ddd8cc;
  display: flex;
  flex-direction: column;
}}
article img {{
  width: 100%;
  height: 220px;
  object-fit: cover;
  display: block;
}}
.body {{ padding: 1.25rem; }}
h2 {{
  margin: 0 0 0.75rem;
  font-size: 1.25rem;
  line-height: 1.3;
}}
p {{
  margin: 0;
  line-height: 1.6;
  white-space: pre-wrap;
}}
details summary {{
  cursor: pointer;
  margin-top: 0.75rem;
  font-size: 0.9rem;
  color: #7a6a4a;
}}
.empty {{
  max-width: 1100px;
  margin: 0 auto;
  font-style: italic;
  color: #5a5a5a;
}}
</style>
</head>
<body>
<header>
<h1>Hearsay</h1>
<p class="tagline">The news that didn't happen.</p>
</header>
{content}
</body>
</html>
"""

CARD_TEMPLATE = """<article>
{image}<div class="body">
<h2>{title}</h2>
<details><summary>Read it</summary><p>{output}</p></details>
</div>
</article>"""


def get_articles():
    connection = sqlite3.connect(DB_CONNECTION_STRING)
    cursor = connection.cursor()
    cursor.execute('''
        SELECT t.title, a.output, a.image_filename
        FROM articles a
        JOIN titles t ON t.rowid = a.title_id
        ORDER BY a.rowid DESC
    ''')
    rows = cursor.fetchall()
    cursor.close()
    connection.close()
    return rows


def render_card(title, output, image_filename):
    image = ''
    if image_filename:
        image = f'<img src="{IMAGES_RELATIVE_PATH}{html.escape(image_filename)}" alt="">\n'

    return CARD_TEMPLATE.format(
        image=image,
        title=html.escape(title),
        output=html.escape(output or ''),
    )


def build_site():
    if not DB_CONNECTION_STRING:
        print("Error: DB_CONNECTION_STRING not set in environment variables.")
        return False

    articles = get_articles()

    if articles:
        cards = '\n'.join(render_card(*row) for row in articles)
        content = f'<div class="grid">\n{cards}\n</div>'
    else:
        content = '<p class="empty">Nothing has been fabricated yet.</p>'

    os.makedirs(SITE_PATH, exist_ok=True)
    with open(OUTPUT_FILE, 'w') as file:
        file.write(PAGE_TEMPLATE.format(content=content))

    print(f"Built {OUTPUT_FILE} with {len(articles)} article(s).\n")
    return True


if __name__ == "__main__":
    build_site()
