import scraper
import extractor
import build_kg
import json
import os
from dotenv import load_dotenv
from rdflib import Graph, URIRef
from rdflib.namespace import RDF

# --- Configuration ---
load_dotenv()

# Define the shared data directory inside the container
DATA_DIR = "/app/data"

# Ensure the data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

RSS_FEEDS = {
    "TheHackerNews": "http://feeds.feedburner.com/TheHackersNews",
    "BleepingComputer": "https://www.bleepingcomputer.com/feed/",
}
MAX_ARTICLES_PER_FEED = 10  # Keep this low for testing

# We still save these for debugging, but they are temporary
ARTICLES_FILE = os.path.join(DATA_DIR, "articles.json")
EXTRACTIONS_FILE = os.path.join(DATA_DIR, "extractions.json")

# This is our persistent, cumulative graph
KG_FILE = os.path.join(DATA_DIR, "group2_cskg.ttl")


def load_existing_graph():
    """Loads the cumulative KG from disk if it exists."""
    g = Graph()
    if os.path.exists(KG_FILE):
        print(f"Loading existing graph from {KG_FILE}...")
        try:
            g.parse(KG_FILE, format="turtle")
            print(f"Loaded {len(g)} existing triples.")
        except Exception as e:
            print(f"Error parsing {KG_FILE}, starting with new graph. Error: {e}")
            g = Graph()  # Start fresh if file is corrupt
    else:
        print("No existing graph found. Starting a new one.")

    # Bind prefixes every time, just in case it's a new graph
    g.bind("cskg", build_kg.MY_KG)
    g.bind("stix", build_kg.STIX)
    g.bind("rdfs", build_kg.RDFS)
    return g


def check_if_article_exists(graph, article_url):
    """Checks if a report for this URL is already in the graph."""
    report_uri = URIRef(article_url)
    # Check if the triple <report_uri> <rdf:type> <stix:Report> exists
    if (report_uri, RDF.type, build_kg.STIX.Report) in graph:
        return True
    return False


def run_pipeline():
    # --- Step 1: Load Existing KG ---
    cumulative_graph = load_existing_graph()

    # --- Step 2: Scrape ---
    print("Step 2: Scraping new articles...")
    all_articles = []
    for name, url in RSS_FEEDS.items():
        all_articles.extend(scraper.fetch_articles(url, MAX_ARTICLES_PER_FEED))

    # --- Step 3: Deduplicate ---
    print("Step 3: Filtering out articles already in the KG...")
    new_articles_to_process = []
    for article in all_articles:
        if not check_if_article_exists(cumulative_graph, article["link"]):
            new_articles_to_process.append(article)

    print(
        f"Found {len(new_articles_to_process)} new articles out of {len(all_articles)} scraped."
    )

    if not new_articles_to_process:
        print("No new articles to process. Pipeline complete.")
        return

    # Save just the new ones for debugging
    with open(ARTICLES_FILE, "w", encoding="utf-8") as f:
        json.dump(new_articles_to_process, f, indent=2)

    # --- Step 4: Extract ---
    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY not found.")
        return

    print("Step 4: Extracting entities from new articles...")
    extractions = extractor.extract_entities(new_articles_to_process)
    with open(EXTRACTIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(extractions, f, indent=2)
    print(f"Extracted entities from {len(extractions)} new articles.")

    # --- Step 5: Build KG ---
    if not extractions:
        print("No new extractions to build KG from. Exiting.")
        return

    print("Step 5: Adding new extractions to the cumulative graph...")
    # Pass the existing graph to the build function!
    cumulative_graph = build_kg.build_graph(
        extractions, existing_graph=cumulative_graph
    )

    # --- Step 6: Serialize ---
    print("Step 6: Saving cumulative graph...")
    cumulative_graph.serialize(destination=KG_FILE, format="turtle")
    print(
        f"Step 6 Complete: Saved cumulative KG with {len(cumulative_graph)} total triples to {KG_FILE}."
    )


if __name__ == "__main__":
    run_pipeline()
