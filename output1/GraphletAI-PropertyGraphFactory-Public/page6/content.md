pipeline producing the knowledge graph from scratch is always uniquely versioned from end-to-end. Nodes
and edges can be stored in their own intermediate silver tables.

## Data Cleaning and ETL
Data from diﬀerent sources about the same thing often contain diﬀerent schemas, and for eﬃciency’s sake
it is necessary to transform - rather than link - the data into a single ontology representing your problem
domain. Multiple datasets need to be transformed into a single, generic form that ﬁts the query and access
patterns for your application - for example Github, GitLab and BitBucket repositories can become Repos
with a type ﬁeld referring to the source.
5

-- Page Images --
![Image 1](./images/image_1.png)

