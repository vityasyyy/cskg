import feedparser
from bs4 import BeautifulSoup
import json


def clean_html(html_content):
    """Strips all HTML tags from a string."""
    soup = BeautifulSoup(html_content, "html.parser")
    return soup.get_text()


def fetch_articles(feed_url, max_articles=5):
    """Fetches and cleans articles from an RSS feed."""
    print(f"Fetching articles from: {feed_url}")
    feed = feedparser.parse(feed_url)
    articles = []

    for entry in feed.entries[:max_articles]:
        articles.append(
            {
                "title": entry.title,
                "link": entry.link,
                "published": entry.get("published", "N/A"),
                "content": clean_html(entry.get("summary", "")),
            }
        )
    return articles


if __name__ == "__main__":
    # Test the scraper with one feed
    HACKER_NEWS_FEED = "http://feeds.feedburner.com/TheHackersNews"
    scraped_articles = fetch_articles(HACKER_NEWS_FEED, max_articles=2)

    # Save to a temporary JSON file for the next step
    with open("articles.json", "w", encoding="utf-8") as f:
        json.dump(scraped_articles, f, indent=2)

    print(
        f"Successfully scraped {len(scraped_articles)} articles and saved to articles.json"
    )
