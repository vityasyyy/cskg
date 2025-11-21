import os
import sys
import requests
from datetime import datetime
from pipeline.graph_eval import generate_brief

# Configuration
API_URL = "http://api:8000"
QUERY_ENDPOINT = f"{API_URL}/query"
STATUS_ENDPOINT = f"{API_URL}/"
REPORTS_DIR = "/app/reports"  # Directory to save the markdown files


def check_system_health():
    """
    Checks if the API is online AND if the Graph DB is reachable.
    Returns True if healthy, False otherwise.
    """
    print("[SUMMARY] Running pre-flight health checks...")
    try:
        # 1. Check API Status
        r = requests.get(STATUS_ENDPOINT, timeout=5)
        r.raise_for_status()
        status = r.json()

        # 2. Check Graph DB Backend Status
        if status.get("status") != "online":
            print(
                f"[SUMMARY] API is running but reports status: {status.get('status')}"
            )
            return False

        if status.get("graph_db_backend") != "Virtuoso":
            print("[SUMMARY] Graph DB backend is not connected.")
            return False

        # 3. Check if we actually have data
        total_triples = status.get("total_triples", 0)
        print(f"[SUMMARY] System Healthy. Total Triples: {total_triples}")

        if total_triples == 0:
            print("[SUMMARY] Graph is empty. Skipping summary generation.")
            return False

        return True

    except Exception as e:
        print(f"[SUMMARY] Health Check Failed: {e}")
        return False


def get_high_priority_threats():
    """
    Queries the ENTIRE graph, grouping Malware by Threat Actor.
    This provides a holistic view of each actor's capabilities.
    """
    sparql_query = """
    PREFIX stix: <http://docs.oasis-open.org/cti/ns/stix#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?actor_label (GROUP_CONCAT(DISTINCT ?malware_label; separator=", ") AS ?tools)
    WHERE {
      GRAPH <http://group2.org/cskg> {
        # Find Threat Actors
        ?actor a stix:ThreatActor ;
               rdfs:label ?actor_label .
        
        # Find Malware they use
        OPTIONAL {
            ?actor stix:uses ?malware .
            ?malware rdfs:label ?malware_label .
        }
      }
    }
    GROUP BY ?actor_label
    ORDER BY ?actor_label
    """
    try:
        response = requests.post(QUERY_ENDPOINT, json={"query": sparql_query})
        response.raise_for_status()
        return response.json().get("results", [])
    except Exception as e:
        print(f"[SUMMARY] Error querying graph: {e}")
        return []


def save_report(report_content, date_str):
    """Saves the report to a markdown file."""
    # Ensure directory exists
    os.makedirs(REPORTS_DIR, exist_ok=True)

    filename = f"{REPORTS_DIR}/daily_brief_{date_str}.md"

    try:
        with open(filename, "w") as f:
            f.write(f"# Daily Intelligence Brief - {date_str}\n\n")
            f.write(report_content)
        print(f"[SUMMARY] Report saved to: {filename}")
    except Exception as e:
        print(f"[SUMMARY] Error saving file: {e}")


if __name__ == "__main__":
    print("=== Starting Daily Summary Task ===")

    # 1. Check Health First
    if not check_system_health():
        print("[SUMMARY] Aborting task due to health check failure.")
        sys.exit(1)

    # 2. Get Data
    data = get_high_priority_threats()
    if not data:
        print("[SUMMARY] No threat actor relationships found to summarize.")
        sys.exit(0)

    # 3. Prepare Date
    today_str = datetime.now().strftime("%Y-%m-%d")

    # 4. Generate Report
    print(f"[SUMMARY] Generating report for {today_str}...")
    report = generate_brief(data, today_str)

    if report:
        # Print to logs
        print("\n" + "=" * 40)
        print(f"DAILY INTELLIGENCE BRIEF ({today_str})")
        print("=" * 40)
        print(report)
        print("=" * 40 + "\n")

        # Save to file
        save_report(report, today_str)

    print("Task Completed")
