import redis
import json
import time
import rdflib
from SPARQLWrapper import SPARQLWrapper
from typing import cast, Tuple, Optional

# We still need build_graph to create the triples in memory
from pipeline.build_kg import build_graph

# Redis connection
R_HOST = "redis"
R_PORT = 6379
EXTRACTIONS_QUEUE = "extractions_queue"

# Virtuoso connection
SPARQL_ENDPOINT = "http://virtuoso:8890/sparql"


def connect_to_redis():
    while True:
        try:
            r = redis.Redis(host=R_HOST, port=R_PORT)
            r.ping()
            print("GraphBuilder connected to Redis.")
            return r
        except redis.ConnectionError as e:
            print(f"GraphBuilder waiting for Redis... ({e})")
            time.sleep(5)


def get_sparql_connection():
    """Configures the SPARQLWrapper for Virtuoso."""
    sparql = SPARQLWrapper(SPARQL_ENDPOINT)
    # This is an UPDATE endpoint, so we don't set a return format
    return sparql


def run_builder():
    r = connect_to_redis()
    print("Graph builder worker started. Waiting for extractions...")

    while True:
        try:
            # Wait for an extraction to appear
            task = cast(
                Optional[Tuple[bytes, bytes]], r.blpop([EXTRACTIONS_QUEUE], timeout=10)
            )
            if task is None:
                continue  # Just a safety guard

            _, extraction_json = task
            extraction_data = json.loads(extraction_json)

            print(
                f"  [BUILDER] Received extraction for: {extraction_data['source_url']}"
            )

            # 1. Use your existing code to build a TINY, in-memory graph
            g_new = rdflib.Graph()
            build_graph([extraction_data], existing_graph=g_new)

            # 2. Serialize just these new triples into a string
            if len(g_new) == 0:
                print("  [BUILDER] No triples were generated. Skipping.")
                continue

            triples_string = g_new.serialize(format="nt")

            # 3. Create a SPARQL INSERT DATA query
            #    We should specify a named graph, e.g., <http://group2.org/cskg>
            query = f"""
            INSERT DATA {{
                GRAPH <http://group2.org/cskg> {{
                    {triples_string}
                }}
            }}
            """

            # 4. Connect to Virtuoso and run the update
            sparql = get_sparql_connection()
            sparql.setMethod("POST")
            sparql.setCredentials("dba", "mysecretpassword")
            sparql.setQuery(query)
            sparql.query()  # This executes the INSERT

            print(f"  [BUILDER] {len(g_new)} triples INSERTED into Virtuoso.")

        except Exception as e:
            print(f"Error adding to graph: {e}")
            time.sleep(1)


if __name__ == "__main__":
    run_builder()
