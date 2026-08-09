import json
import feedparser
from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()

TITLE_INSTRUCTIONS_FILE = 'prompts/title-instructions.txt'
FEED_URL = os.getenv("RSS_FEED_URL")
API_KEY = os.getenv("API_KEY")
client = OpenAI(api_key=API_KEY)


def get_rss_feed():
    if not FEED_URL:
        print("Error: RSS_FEED_URL not set in environment variables.")
        return None

    return feedparser.parse(FEED_URL)


def get_rss_feed_entries():
    rss_feed = get_rss_feed()
    if not rss_feed:
        print("Error: Could not retrieve RSS feed.")
        return None

    return rss_feed.entries


def evaluate_title(title):
    if not title:
        return False, "Empty title"

    with open(TITLE_INSTRUCTIONS_FILE, 'r') as file:
        instructions = file.read()
        response = client.responses.create(
            model="gpt-5.6-luna",
            instructions=instructions,
            input=title,
        )
        if response and response.output_text:
            response_data = response.output_text.strip()
            try:
                json_response = json.loads(response_data)
                suitable = json_response.get('suitable', False)
                reason = json_response.get('reason', 'No reason provided')
                return suitable, reason
            except json.JSONDecodeError:
                return False, "Invalid JSON response"

    return False, "No response from API"
