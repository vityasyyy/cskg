from rdflib import Graph

KG_FILE = "group2_cskg.ttl"

g = Graph()
g.parse(KG_FILE, format="turtle")

print(f"--- KG Statistics for {KG_FILE} ---")
print(f"Total Triples: {len(g)}\n")

# SPARQL query for node types
query_nodes = """
    PREFIX stix: <http://docs.oasis-open.org/cti/ns/stix#>
    SELECT ?type (COUNT(?s) AS ?count)
    WHERE {
        ?s a ?type .
        FILTER(STRSTARTS(STR(?type), STR(stix:)))
    }
    GROUP BY ?type
    ORDER BY DESC(?count)
"""
print("--- Node Counts by STIX Type ---")
for row in g.query(query_nodes):
    print(f"{row.type.split('#')[-1]}: {row['count']}")

# SPARQL query for links to SEPSES
query_links = """
    SELECT (COUNT(?s) as ?count)
    WHERE {
        ?s a <http://docs.oasis-open.org/cti/ns/stix#Vulnerability> .
        FILTER(STRSTARTS(STR(?s), "https://w3id.org/sepses/resource/cve/"))
    }
"""
print("\n--- Evaluation ---")
for row in g.query(query_links):
    print(f"Total Links to SEPSES CVEs: {row['count']}")
