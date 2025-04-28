Many graph machine learning applications require real-time APIs to automate tasks using predictive models
so the ultimate output of a property graph factory is to instantiate a cloud search engine and graph
database and load the nodes and edges of the graph. Most graph databases tightly integrate with a search
engine to provide real-time graph queries. Most graph queries in a graph database start with a search for
one or more matching nodes and proceed to walk across the graph, deﬁning a motif, which can be labeled
with orbits to create a property graphlet.

## Batch and Realtime Inference
Inference or prediction can often be pre-computed using batch computing systems like Spark in ﬁtting with
the ingest / build / reﬁne / publish pattern used in most big data applications. Inferences create new edges
that deﬁne semantics which enable simple queries or graph analytics that satisfy application requirements.
Models powering these inferences can be applied to the graph in batch in advance of being indexed and
queried. A model management system like Spark and MLFlow, which operates on top of DataBricks via its
Managed MLFlow oﬀering, can be employed to provide task automation using real-time APIs for machine
learning. Amazon Neptune supports the openCypher query language and integrates with the Amazon
OpenSearch Server to initialize or ﬁlter graph walks as part of queries based on the full lucene query
language.
19
