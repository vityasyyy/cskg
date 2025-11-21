import requests

# This script assumes you are running it from the host machine
# and Virtuoso is exposed on port 8890 (as per your compose.yml)
VIRTUOSO_ENDPOINT = "http://localhost:8890/sparql"
GRAPH_URI = "http://group2.org/cskg"
OUTPUT_FILE = "cskg_full_dump.ttl"


def dump_ttl():
    print(f"Connecting to {VIRTUOSO_ENDPOINT}...")

    query = f"CONSTRUCT {{ ?s ?p ?o }} WHERE {{ GRAPH <{GRAPH_URI}> {{ ?s ?p ?o }} }}"

    params = {
        "query": query,
        "format": "text/turtle",  # Request Turtle format
    }

    try:
        response = requests.get(VIRTUOSO_ENDPOINT, params=params, stream=True)
        response.raise_for_status()

        print(f"Downloading graph to '{OUTPUT_FILE}'...")

        with open(OUTPUT_FILE, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        print("Dump complete!")

    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to Virtuoso. Is Docker running?")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    dump_ttl()
