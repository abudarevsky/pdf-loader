
## KNOWLEDGE GRAPH CONSTRUCTION
This section outlines the phases of the knowledge graph construction process for large knowledge graphs
using distributed systems and deep learning. This process is echoed in Databricks marketing on using big
data for ﬁnancial services. Once we outline the process, in the next section we will discuss problems one
encounters in knowledge graph construction before outlining a set of solutions to these problems Graphlet
AI will build.

## Ingestion
Datasets that make up a knowledge graph are ingested onto bulk storage systems such as Amazon S3,
Google Cloud Storage (GCP) or onto parquet based tables with a version tracking component such as Delta
Tables or Apache Iceberg, which has broad language and library support. This allows version tracking of
datasets and their varying metadata along with source code and predictive models over time so the
4

-- Page Images --
![Image 1](./images/image_1.png)

