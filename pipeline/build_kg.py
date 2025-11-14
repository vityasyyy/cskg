import re
import json
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, RDFS

# --- 1. Define your Namespaces ---
# Your custom namespace
MY_KG = Namespace("http://group2.org/cskg/")
# The STIX 2.1 Ontology namespace
STIX = Namespace("http://docs.oasis-open.org/cti/ns/stix#")
SEPSES_CVE = Namespace("https://w3id.org/sepses/resource/cve/")

RELATIONSHIP_MAP = {
    "uses": STIX.uses,
    "targets": STIX.targets,
    "exploits": STIX.exploits,
    "mitigates": STIX.mitigates,
    "attributed_to": STIX.attributed_to,
    "variant_of": STIX.variant_of,
    "located_in": STIX.located_in,
    "impersonates": STIX.impersonates,
    "reports": STIX.reports,
    "patched": STIX.patched,
    "resolved": STIX.resolved,
    "disrupted": STIX.disrupted,
    "aligned_with": STIX.aligned_with,
    "observes": STIX.observes,
    "has_similarities_with": STIX.has_similarities_with,
    "propagated_via": STIX.propagated_via,
}


def build_graph(extractions, existing_graph=None):
    """Builds an RDF graph from the extracted entities and relations."""
    if existing_graph is not None:
        g = existing_graph
        print("Adding new triples to existing graph...")
    else:
        g = Graph()
        print("Building new RDF graph...")
        # Bind prefixes only when creating a new graph
        g.bind("cskg", MY_KG)
        g.bind("stix", STIX)
        g.bind("rdfs", RDFS)

    print("Building RDF graph...")

    for item in extractions:
        report_url = item["source_url"]
        entities = item["entities"]

        # Create a URI for the report itself
        report_uri = URIRef(report_url)
        g.add((report_uri, RDF.type, STIX.Report))

        # Helper function to create a safe URI
        def safe_uri(namespace, text):
            # Simple slugify for URI
            safe_text = text.replace(" ", "_").replace(".", "").replace("/", "")
            return namespace[safe_text]

        # --- 2. Add all named entities as nodes ---
        for actor in entities.get("threat_actors") or []:
            actor_uri = safe_uri(MY_KG, actor)
            g.add((actor_uri, RDF.type, STIX.ThreatActor))
            g.add((actor_uri, RDFS.label, Literal(actor)))
            g.add((report_uri, STIX.mentions, actor_uri))  # Link report to entity

        for malware in entities.get("malware") or []:
            malware_uri = safe_uri(MY_KG, malware)
            g.add((malware_uri, RDF.type, STIX.Malware))
            g.add((malware_uri, RDFS.label, Literal(malware)))
            g.add((report_uri, STIX.mentions, malware_uri))

        for vuln in entities.get("vulnerabilities") or []:
            # Check if the vulnerability string is a CVE
            cve_match = re.search(r"(CVE-\d{4}-\d{4,})", vuln, re.IGNORECASE)

            if cve_match:
                # It's a CVE! Use the SEPSES URI.
                cve_id = cve_match.group(1).upper()
                vuln_uri = SEPSES_CVE[cve_id]  # e.g., .../cve/CVE-2023-1234
            else:
                # Not a CVE, use our own namespace
                vuln_uri = safe_uri(MY_KG, vuln)

            g.add((vuln_uri, RDF.type, STIX.Vulnerability))
            g.add((vuln_uri, RDFS.label, Literal(vuln)))
            g.add((report_uri, STIX.mentions, vuln_uri))

        for ind in entities.get("indicators") or []:
            ind_uri = safe_uri(MY_KG, ind)
            g.add((ind_uri, RDF.type, STIX.Indicator))
            g.add((ind_uri, RDFS.label, Literal(ind)))
            g.add((report_uri, STIX.mentions, ind_uri))

        for pattern in entities.get("attack_patterns") or []:
            pattern_uri = safe_uri(MY_KG, pattern)
            g.add((pattern_uri, RDF.type, STIX.AttackPattern))
            g.add((pattern_uri, RDFS.label, Literal(pattern)))
            g.add((report_uri, STIX.mentions, pattern_uri))

        # --- 3. Add all relationships as edges ---
        for rel in entities.get("relations") or []:
            subj_uri = safe_uri(MY_KG, rel["subject"])
            obj_uri = safe_uri(MY_KG, rel["object"])

            # Use the mapping to get the correct STIX property
            relationship_str = rel["relationship"]

            # Get the real STIX property, or fall back to your custom one if not found
            rel_prop = RELATIONSHIP_MAP.get(
                relationship_str, safe_uri(MY_KG, relationship_str)
            )

            g.add((subj_uri, rel_prop, obj_uri))

    return g


if __name__ == "__main__":
    # Load the extractions
    with open("extractions.json", "r", encoding="utf-8") as f:
        extractions_to_process = json.load(f)

    kg = build_graph(extractions_to_process)

    # Save the final KG
    output_file = "group2_cskg.ttl"
    kg.serialize(destination=output_file, format="turtle")

    print(f"Successfully built Knowledge Graph and saved to {output_file}")
    print(f"Total triples in graph: {len(kg)}")
