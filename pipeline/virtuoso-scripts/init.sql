-- Grant federated query permissions
GRANT SPARQL_FED TO "SPARQL";

GRANT SELECT ON GRAPH <http://group2.org/cskg> TO "nobody";

GRANT SPARQL_UPDATE TO "SPARQL";

RDF_DEFAULT_USER_PERMS_SET ('SPARQL', 7);

DB.DBA.RDF_GRAPH_USER_PERMS_SET ('http://group2.org/cskg', 'SPARQL', 7);
