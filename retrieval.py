from databricks.ai_search.client import AISearchClient

ENDPOINT = "privacylens-endpoint"
INDEX = "workspace.privacylens.silver_chunks_index"
COLUMNS = ["chunk_id", "law", "section_num", "citation", "page_start", "chunk_text"]

_index = None

def _get_index():
    global _index
    if _index is None:
        client = AISearchClient(disable_notice=True)
        _index = client.get_index(endpoint_name=ENDPOINT, index_name=INDEX)
    return _index

def retrieve(question, law=None, k=5, query_type="ANN"):
    kwargs = dict(query_text=question, columns=COLUMNS,
                  num_results=k, query_type=query_type)
    if law:
        kwargs["filters"] = {"law": law}
    res = _get_index().similarity_search(**kwargs)
    cols = [c["name"] for c in res["manifest"]["columns"]]
    return [dict(zip(cols, row)) for row in res["result"].get("data_array", [])]

def retrieve_context(question, law=None):
    """ANN search. Both laws by default (3 cards each); 5 cards when one law is chosen."""
    if law:
        return retrieve(question, law=law, k=5)
    return retrieve(question, "GDPR", 3) + retrieve(question, "DPDP", 3)