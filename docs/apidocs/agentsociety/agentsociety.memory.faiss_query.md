# {py:mod}`agentsociety.memory.faiss_query`

```{py:module} agentsociety.memory.faiss_query
```

```{autodoc2-docstring} agentsociety.memory.faiss_query
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`FaissQuery <agentsociety.memory.faiss_query.FaissQuery>`
  - ```{autodoc2-docstring} agentsociety.memory.faiss_query.FaissQuery
    :summary:
    ```
````

### API

`````{py:class} FaissQuery(embeddings: typing.Optional[langchain_core.embeddings.Embeddings] = None, index_type: typing.Any = faiss.IndexFlatL2, dimension: typing.Optional[int] = None)
:canonical: agentsociety.memory.faiss_query.FaissQuery

```{autodoc2-docstring} agentsociety.memory.faiss_query.FaissQuery
```

```{rubric} Initialization
```

```{autodoc2-docstring} agentsociety.memory.faiss_query.FaissQuery.__init__
```

````{py:property} embeddings
:canonical: agentsociety.memory.faiss_query.FaissQuery.embeddings
:type: langchain_core.embeddings.Embeddings

```{autodoc2-docstring} agentsociety.memory.faiss_query.FaissQuery.embeddings
```

````

````{py:property} vectors_store
:canonical: agentsociety.memory.faiss_query.FaissQuery.vectors_store
:type: langchain_community.vectorstores.FAISS

```{autodoc2-docstring} agentsociety.memory.faiss_query.FaissQuery.vectors_store
```

````

````{py:method} add_documents(agent_id: int, documents: typing.Union[str, collections.abc.Sequence[str]], extra_tags: typing.Optional[dict] = None) -> list[str]
:canonical: agentsociety.memory.faiss_query.FaissQuery.add_documents
:async:

```{autodoc2-docstring} agentsociety.memory.faiss_query.FaissQuery.add_documents
```

````

````{py:method} delete_documents(to_delete_ids: list[str])
:canonical: agentsociety.memory.faiss_query.FaissQuery.delete_documents
:async:

```{autodoc2-docstring} agentsociety.memory.faiss_query.FaissQuery.delete_documents
```

````

````{py:method} similarity_search(query: str, agent_id: int, k: int = 4, fetch_k: int = 20, return_score_type: typing.Union[typing.Literal[none], typing.Literal[similarity_score], typing.Literal[L2-distance]] = 'none', filter: typing.Optional[dict] = None) -> typing.Union[list[tuple[str, dict]], list[tuple[str, float, dict]]]
:canonical: agentsociety.memory.faiss_query.FaissQuery.similarity_search
:async:

```{autodoc2-docstring} agentsociety.memory.faiss_query.FaissQuery.similarity_search
```

````

````{py:method} similarity_search_by_embedding(embedding: list[float], agent_id: int, k: int = 4, fetch_k: int = 20, return_score_type: typing.Union[typing.Literal[none], typing.Literal[L2-distance]] = 'none', filter: typing.Optional[dict] = None) -> typing.Union[list[tuple[str, dict]], list[tuple[str, float, dict]]]
:canonical: agentsociety.memory.faiss_query.FaissQuery.similarity_search_by_embedding
:async:

```{autodoc2-docstring} agentsociety.memory.faiss_query.FaissQuery.similarity_search_by_embedding
```

````

````{py:method} marginal_relevance_search(query: str, agent_id: int, k: int = 4, fetch_k: int = 20, lambda_mult: float = 0.5, return_score_type: typing.Literal[none] = 'none', filter: typing.Optional[dict] = None) -> list[tuple[str, dict]]
:canonical: agentsociety.memory.faiss_query.FaissQuery.marginal_relevance_search
:async:

```{autodoc2-docstring} agentsociety.memory.faiss_query.FaissQuery.marginal_relevance_search
```

````

````{py:method} marginal_relevance_search_by_embedding(embedding: list[float], agent_id: int, k: int = 4, fetch_k: int = 20, lambda_mult: float = 0.5, return_score_type: typing.Union[typing.Literal[none], typing.Literal[similarity_score]] = 'none', filter: typing.Optional[dict] = None) -> typing.Union[list[tuple[str, dict]], list[tuple[str, float, dict]]]
:canonical: agentsociety.memory.faiss_query.FaissQuery.marginal_relevance_search_by_embedding
:async:

```{autodoc2-docstring} agentsociety.memory.faiss_query.FaissQuery.marginal_relevance_search_by_embedding
```

````

`````
