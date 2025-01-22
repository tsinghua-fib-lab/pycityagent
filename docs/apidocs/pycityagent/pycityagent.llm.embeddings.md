# {py:mod}`pycityagent.llm.embeddings`

```{py:module} pycityagent.llm.embeddings
```

```{autodoc2-docstring} pycityagent.llm.embeddings
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`SentenceEmbedding <pycityagent.llm.embeddings.SentenceEmbedding>`
  - ```{autodoc2-docstring} pycityagent.llm.embeddings.SentenceEmbedding
    :summary:
    ```
* - {py:obj}`SimpleEmbedding <pycityagent.llm.embeddings.SimpleEmbedding>`
  - ```{autodoc2-docstring} pycityagent.llm.embeddings.SimpleEmbedding
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`__all__ <pycityagent.llm.embeddings.__all__>`
  - ```{autodoc2-docstring} pycityagent.llm.embeddings.__all__
    :summary:
    ```
````

### API

````{py:data} __all__
:canonical: pycityagent.llm.embeddings.__all__
:value: >
   ['SentenceEmbedding', 'SimpleEmbedding']

```{autodoc2-docstring} pycityagent.llm.embeddings.__all__
```

````

`````{py:class} SentenceEmbedding(pretrained_model_name_or_path: typing.Union[str, os.PathLike] = 'BAAI/bge-m3', max_seq_len: int = 8192, auto_cuda: bool = False, local_files_only: bool = False, cache_dir: str = './cache', proxies: typing.Optional[dict] = None)
:canonical: pycityagent.llm.embeddings.SentenceEmbedding

Bases: {py:obj}`langchain_core.embeddings.Embeddings`

```{autodoc2-docstring} pycityagent.llm.embeddings.SentenceEmbedding
```

```{rubric} Initialization
```

```{autodoc2-docstring} pycityagent.llm.embeddings.SentenceEmbedding.__init__
```

````{py:method} _embed(texts: list[str]) -> list[list[float]]
:canonical: pycityagent.llm.embeddings.SentenceEmbedding._embed

```{autodoc2-docstring} pycityagent.llm.embeddings.SentenceEmbedding._embed
```

````

````{py:method} embed_documents(texts: list[str]) -> list[list[float]]
:canonical: pycityagent.llm.embeddings.SentenceEmbedding.embed_documents

```{autodoc2-docstring} pycityagent.llm.embeddings.SentenceEmbedding.embed_documents
```

````

````{py:method} embed_query(text: str) -> list[float]
:canonical: pycityagent.llm.embeddings.SentenceEmbedding.embed_query

```{autodoc2-docstring} pycityagent.llm.embeddings.SentenceEmbedding.embed_query
```

````

`````

`````{py:class} SimpleEmbedding(vector_dim: int = 128, cache_size: int = 1000)
:canonical: pycityagent.llm.embeddings.SimpleEmbedding

Bases: {py:obj}`langchain_core.embeddings.Embeddings`

```{autodoc2-docstring} pycityagent.llm.embeddings.SimpleEmbedding
```

```{rubric} Initialization
```

```{autodoc2-docstring} pycityagent.llm.embeddings.SimpleEmbedding.__init__
```

````{py:method} _text_to_hash(text: str) -> str
:canonical: pycityagent.llm.embeddings.SimpleEmbedding._text_to_hash

```{autodoc2-docstring} pycityagent.llm.embeddings.SimpleEmbedding._text_to_hash
```

````

````{py:method} _tokenize(text: str) -> list[str]
:canonical: pycityagent.llm.embeddings.SimpleEmbedding._tokenize

```{autodoc2-docstring} pycityagent.llm.embeddings.SimpleEmbedding._tokenize
```

````

````{py:method} _update_vocab(tokens: list[str])
:canonical: pycityagent.llm.embeddings.SimpleEmbedding._update_vocab

```{autodoc2-docstring} pycityagent.llm.embeddings.SimpleEmbedding._update_vocab
```

````

````{py:method} _update_idf(tokens: list[str])
:canonical: pycityagent.llm.embeddings.SimpleEmbedding._update_idf

```{autodoc2-docstring} pycityagent.llm.embeddings.SimpleEmbedding._update_idf
```

````

````{py:method} _calculate_tf(tokens: list[str]) -> dict[str, float]
:canonical: pycityagent.llm.embeddings.SimpleEmbedding._calculate_tf

```{autodoc2-docstring} pycityagent.llm.embeddings.SimpleEmbedding._calculate_tf
```

````

````{py:method} _calculate_tfidf(tokens: list[str]) -> list[float]
:canonical: pycityagent.llm.embeddings.SimpleEmbedding._calculate_tfidf

```{autodoc2-docstring} pycityagent.llm.embeddings.SimpleEmbedding._calculate_tfidf
```

````

````{py:method} _embed(text: str) -> list[float]
:canonical: pycityagent.llm.embeddings.SimpleEmbedding._embed

```{autodoc2-docstring} pycityagent.llm.embeddings.SimpleEmbedding._embed
```

````

````{py:method} embed_documents(texts: list[str]) -> list[list[float]]
:canonical: pycityagent.llm.embeddings.SimpleEmbedding.embed_documents

```{autodoc2-docstring} pycityagent.llm.embeddings.SimpleEmbedding.embed_documents
```

````

````{py:method} embed_query(text: str) -> list[float]
:canonical: pycityagent.llm.embeddings.SimpleEmbedding.embed_query

```{autodoc2-docstring} pycityagent.llm.embeddings.SimpleEmbedding.embed_query
```

````

`````
