-- Grant federated query permissions (from your original file)
GRANT SPARQL_FED TO "SPARQL";

-- Grant SELECT (read) permissions on your named graph
-- to the 'nobody' user (the default anonymous user for the SPARQL endpoint).
-- This allows your api_server to read the data.
GRANT SELECT ON GRAPH <http://group2.org/cskg> TO "nobody";
