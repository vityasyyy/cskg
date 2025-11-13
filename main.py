import scraper
import extractor
import build_kg
import json
import os
from dotenv import load_dotenv
# --- Configuration ---

load_dotenv()
RSS_FEEDS = {
    "TheHackerNews": "http://feeds.feedburner.com/TheHackersNews",
    "BleepingComputer": "https://www.bleepingcomputer.com/feed/",
}
MAX_ARTICLES_PER_FEED = 30  # Keep this low for testing
ARTICLES_FILE = "articles.json"
EXTRACTIONS_FILE = "extractions.json"
KG_FILE = "group2_cskg.ttl"


def run_pipeline():
    # --- Step 1: Scrape ---
    all_articles = []
    for name, url in RSS_FEEDS.items():
        all_articles.extend(scraper.fetch_articles(url, MAX_ARTICLES_PER_FEED))

    with open(ARTICLES_FILE, "w", encoding="utf-8") as f:
        json.dump(all_articles, f, indent=2)
    print(f"Step 1 Complete: Scraped {len(all_articles)} articles.")

    # --- Step 2: Extract ---
    if not all_articles:
        print("No articles to process. Exiting.")
        return

    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY not found.")
        print("Please create a .env file and add OPENAI_API_KEY=your_key")
        return

    extractions = extractor.extract_entities(all_articles)
    with open(EXTRACTIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(extractions, f, indent=2)
    print(f"Step 2 Complete: Extracted entities from {len(extractions)} articles.")

    # --- Step 3: Build KG ---
    if not extractions:
        print("No extractions to build KG from. Exiting.")
        return

    kg = build_kg.build_graph(extractions)
    kg.serialize(destination=KG_FILE, format="turtle")
    print(f"Step 3 Complete: Built KG with {len(kg)} triples, saved to {KG_FILE}.")


if __name__ == "__main__":
    run_pipeline()
