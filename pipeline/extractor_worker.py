import redis
import json
import os
from pipeline.extractor import get_extraction_chain
from typing import cast, Tuple, Optional
from dotenv import load_dotenv

# Redis connection
R_HOST = "redis"
R_PORT = 6379
ARTICLES_QUEUE = "articles_queue"
EXTRACTIONS_QUEUE = "extractions_queue"


def connect_to_redis():
    """Connects to Redis with retries."""
    while True:
        try:
            r = redis.Redis(host=R_HOST, port=R_PORT)  # No decode_responses here
            r.ping()
            print("Extractor connected to Redis.")
            return r
        except redis.ConnectionError as e:
            print(f"Extractor waiting for Redis... ({e})")
            raise e


def run_extractor():
    load_dotenv()
    if not os.getenv("GOOGLE_API_KEY"):
        print("ERROR: GOOGLE_API_KEY not found. Extractor cannot start.")
        raise Exception("Missing GOOGLE_API_KEY")

    print("Initializing LLM chain...")
    chain = get_extraction_chain()
    r = connect_to_redis()
    print("Extractor worker started. Waiting for articles...")

    while True:
        try:
            if chain is None:
                print("Extractor chain is not initialized. Exiting.")
                return
            # blpop blocks until an item appears in the list
            # It returns a tuple: (list_name, item_bytes)
            task = cast(
                Optional[Tuple[bytes, bytes]], r.blpop([ARTICLES_QUEUE], timeout=10)
            )
            if task is None:
                continue  # Just a safety guard

            _, article_json = task
            article = json.loads(article_json)

            print(f"  [EXTRACTOR] Processing article: {article['title']}")

            # format the prompt, send to llm, parse the llm response
            response = chain.invoke({"article_text": article["content"]})

            # Combine the source_url with the extracted entities
            extraction_data = {
                "source_url": article["link"],
                "entities": response.model_dump(),
            }

            # Push the result to the next queue
            r.rpush(EXTRACTIONS_QUEUE, json.dumps(extraction_data))
            print(
                f"  [EXTRACTOR] Finished processing. Pushed to '{EXTRACTIONS_QUEUE}'."
            )

        except Exception as e:
            print(f"Error processing article: {e}")
            # In a real system, you might push this to an error queue
            raise e


if __name__ == "__main__":
    try:
        print("=== Worker Starting ===")
        run_extractor()  # or run_builder()
        print("=== Worker Completed ===")
    except Exception as e:
        print(f"FATAL ERROR: {e}")
        import traceback

        traceback.print_exc()
        raise
