-- Grant federated query permissions
GRANT SPARQL_FED TO "SPARQL";

-- Grant SELECT (read) permissions on your named graph to anonymous users
GRANT SELECT ON GRAPH <http://group2.org/cskg> TO "nobody";

-- CRITICAL: Grant WRITE permissions to SPARQL user
GRANT SPARQL_UPDATE TO "SPARQL";

-- Grant INSERT/DELETE permissions on the specific graph
RDF_DEFAULT_USER_PERMS_SET ('SPARQL', 7);

-- Set permissions for the specific graph (7 = read+write+sponge)
DB.DBA.RDF_GRAPH_USER_PERMS_SET ('http://group2.org/cskg', 'SPARQL', 7);
