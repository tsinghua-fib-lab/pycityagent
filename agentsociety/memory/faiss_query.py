import asyncio
import warnings
from collections.abc import Sequence
from typing import Any, Literal, Optional, Union

import faiss
import numpy as np
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

from ..utils.decorators import lock_decorator


class FaissQuery:
    """
    A class for handling similarity searches and document management using FAISS.

    - **Description**:
        - This class provides functionalities to manage embeddings and perform similarity searches over a set of documents.
        - It allows adding, deleting, and querying documents based on their semantic content through embeddings.
        - The class initializes with an optional embedding model and index type, setting up the environment for vector operations.
        - If no embedding model is provided during initialization, certain methods will not be available until one is set.
    """

    def __init__(
        self,
        embeddings: Optional[Embeddings] = None,
        index_type: Any = faiss.IndexFlatL2,
        dimension: Optional[int] = None,
    ) -> None:
        """
        Initialize the FaissQuery instance.

        - **Parameters**:
            - `embeddings` (Optional[Embeddings], optional): An embedding function that converts text into vectors. Defaults to None.
            - `index_type` (Any, optional): The type of FAISS index to use for vector storage and retrieval. Defaults to faiss.IndexFlatL2.
            - `dimension` (Optional[int], optional): The dimensionality of the vectors produced by the embedding function. Defaults to None.
                If not specified, it's inferred from the embedding of a sample text ("hello world").
        """
        self._embeddings = embeddings
        self._lock = asyncio.Lock()
        if embeddings is None:
            self._index = None
            self._vectors_store = None
        else:
            if dimension is None:
                dimension = len(embeddings.embed_query("hello world"))
            self._index = index_type(dimension)
            self._vectors_store = FAISS(
                embedding_function=embeddings,
                index=self._index,
                docstore=InMemoryDocstore(),
                index_to_docstore_id={},
            )

    @property
    def embeddings(
        self,
    ) -> Embeddings:
        """
        Access the current embedding model.

        - **Description**:
            - Getter for the embedding model used to convert text into vector representations.
            - If no embedding model has been set, a RuntimeError is raised prompting the user to set one first.

        - **Returns**:
            - `Embeddings`: The current embedding model.
        """
        if self._embeddings is None:
            raise RuntimeError(f"No embedding set, please `set_embeddings` first!")
        return self._embeddings

    @property
    def vectors_store(
        self,
    ) -> FAISS:
        """
        Access the current vector store.

        - **Description**:
            - Getter for the FAISS vector store which holds the indexed documents and allows for similarity searches.
            - If the vector store hasn't been initialized due to a missing embedding model, a RuntimeError is raised.

        - **Returns**:
            - `FAISS`: The current vector store instance.
        """
        if self._vectors_store is None:
            raise RuntimeError(f"No embedding set, thus no vector stores initialized!")
        return self._vectors_store

    @lock_decorator
    async def add_documents(
        self,
        agent_id: int,
        documents: Union[str, Sequence[str]],
        extra_tags: Optional[dict] = None,
    ) -> list[str]:
        """
        Add documents to the vector store with metadata.

        - **Description**:
            - Asynchronously adds one or more documents to the vector store, associating them with an agent ID and optional extra tags.
            - Each document is converted into a vector using the embedding model before being added to the index.

        - **Args**:
            - `agent_id` (int): Identifier of the agent to associate with the documents.
            - `documents` (Union[str, Sequence[str]]): A single document string or a sequence of document strings to add.
            - `extra_tags` (Optional[dict], optional): Additional metadata tags to associate with the documents. Defaults to None.

        - **Returns**:
            - `list[str]`: List of document IDs that were added to the vector store.
        """
        if isinstance(documents, str):
            documents = [documents]
        _metadata = {"_id": agent_id}
        if extra_tags is not None:
            _metadata.update(extra_tags)
        to_add_documents = [
            Document(page_content=doc, metadata=_metadata) for doc in documents
        ]
        return await self.vectors_store.aadd_documents(
            documents=to_add_documents,
        )

    @lock_decorator
    async def delete_documents(
        self,
        to_delete_ids: list[str],
    ):
        """
        Delete documents from the vector store by IDs.

        - **Description**:
            - Asynchronously deletes documents from the vector store based on provided document IDs.

        - **Args**:
            - `to_delete_ids` (list[str]): List of document IDs to delete from the vector store.
        """
        await self.vectors_store.adelete(
            ids=to_delete_ids,
        )

    @lock_decorator
    async def similarity_search(
        self,
        query: str,
        agent_id: int,
        k: int = 4,
        fetch_k: int = 20,
        return_score_type: Union[
            Literal["none"], Literal["similarity_score"], Literal["L2-distance"]
        ] = "none",
        filter: Optional[dict] = None,
    ) -> Union[list[tuple[str, dict]], list[tuple[str, float, dict]]]:
        """
        Perform a similarity search for documents related to the given query.

        - **Description**:
            - Conducts an asynchronous search for the top-k documents most similar to the query text.
            - The search can be customized by specifying how many documents to fetch (`fetch_k`), how many to return (`k`),
              and whether to include scores in the results (`return_score_type`).
            - Filters can be applied to narrow down the search results based on metadata.

        - **Args**:
            - `query` (str): The text to look up documents similar to.
            - `agent_id` (int): The identifier of the agent to filter specific documents.
            - `k` (int, optional): The number of top similar contents to return. Defaults to 4.
            - `fetch_k` (int, optional): The number of documents to fetch before applying any filters. Defaults to 20.
            - `return_score_type` (Union[Literal["none"], Literal["similarity_score"], Literal["L2-distance"]], optional):
                Specifies whether and how to return similarity scores with the results.
            - `filter` (Optional[dict], optional): The filter dict for metadata.

        - **Returns**:
            - `Union[list[tuple[str, dict]], list[tuple[str, float, dict]]]`: Depending on the `return_score_type` parameter,
              returns either a list of tuples containing the content and its associated metadata, or also including a floating-point score.
        """
        _filter = {
            "_id": agent_id,
        }
        if filter is not None:
            _filter.update(filter)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            if return_score_type == "L2-distance":
                _result = await self.vectors_store.asimilarity_search_with_score(
                    query=query,
                    k=k,
                    filter=_filter,
                    fetch_k=fetch_k,
                )
                return [(r.page_content, s, r.metadata) for r, s in _result]
            elif return_score_type == "none":
                _result = await self.vectors_store.asimilarity_search(
                    query=query,
                    k=k,
                    filter=_filter,
                    fetch_k=fetch_k,
                )
                return [(r.page_content, r.metadata) for r in _result]
            elif return_score_type == "similarity_score":
                _result = (
                    await self.vectors_store.asimilarity_search_with_relevance_scores(
                        query=query,
                        k=k,
                        filter=_filter,
                        fetch_k=fetch_k,
                    )
                )
                return [(r.page_content, s, r.metadata) for r, s in _result]
            else:
                raise ValueError(f"Invalid `return_score_type` {return_score_type}!")

    @lock_decorator
    async def similarity_search_by_embedding(
        self,
        embedding: list[float],
        agent_id: int,
        k: int = 4,
        fetch_k: int = 20,
        return_score_type: Union[Literal["none"], Literal["L2-distance"]] = "none",
        filter: Optional[dict] = None,
    ) -> Union[list[tuple[str, dict]], list[tuple[str, float, dict]]]:
        """
        Perform a similarity search for documents related to the given vector.

        - **Description**:
            - Conducts an asynchronous search for the top-k documents most similar to the provided embedding vector.
            - The search can be customized by specifying how many documents to fetch (`fetch_k`), how many to return (`k`),
              and whether to include L2 distances in the results (`return_score_type`).
            - Filters can be applied to narrow down the search results based on metadata.

        - **Args**:
            - `embedding` (list[float]): The vector to look up documents similar to.
            - `agent_id` (int): The identifier of the agent to filter specific documents.
            - `k` (int, optional): The number of top similar contents to return. Defaults to 4.
            - `fetch_k` (int, optional): The number of documents to fetch before applying any filters. Defaults to 20.
            - `return_score_type` (Union[Literal["none"], Literal["L2-distance"]], optional):
                Specifies whether and how to return similarity scores with the results:
                    - "none": Do not return scores; only return the contents (default).
                    - "L2-distance": Return a tuple of content and its L2 distance from the query.
            - `filter` (Optional[dict], optional): The filter dict for metadata.

        - **Returns**:
            - `Union[list[tuple[str, dict]], list[tuple[str, float, dict]]]`: Depending on the `return_score_type` parameter,
              returns either a list of tuples containing the content and its associated metadata, or also including a floating-point score.
        """
        _filter = {
            "_id": agent_id,
        }
        if filter is not None:
            _filter.update(filter)
        if return_score_type == "L2-distance":
            _result = await self.vectors_store.asimilarity_search_with_score_by_vector(
                embedding=embedding,
                k=k,
                filter=_filter,
                fetch_k=fetch_k,
            )
            return [(r.page_content, s, r.metadata) for r, s in _result]
        elif return_score_type == "none":
            _result = await self.vectors_store.asimilarity_search_by_vector(
                embedding=embedding,
                k=k,
                filter=_filter,
                fetch_k=fetch_k,
            )
            return [(r.page_content, r.metadata) for r in _result]
        else:
            raise ValueError(f"Invalid `return_score_type` {return_score_type}!")

    @lock_decorator
    async def marginal_relevance_search(
        self,
        query: str,
        agent_id: int,
        k: int = 4,
        fetch_k: int = 20,
        lambda_mult: float = 0.5,
        return_score_type: Literal["none"] = "none",
        filter: Optional[dict] = None,
    ) -> list[tuple[str, dict]]:
        """
        Select contents using maximal marginal relevance asynchronously.

        - **Description**:
            - Asynchronously selects a set of documents that are relevant to the query while ensuring diversity among the results.
            - The selection process balances between relevance to the query and diversity, controlled by `lambda_mult`.

        - **Args**:
            - `query` (str): The text to look up documents similar to.
            - `agent_id` (int): The identifier of the agent to filter specific documents.
            - `k` (int, optional): The number of top similar contents to return. Defaults to 4.
            - `fetch_k` (int, optional): The number of documents to fetch before applying any filters. Defaults to 20.
            - `lambda_mult` (float, optional): Number between 0 and 1 that determines the degree of diversity among the results. Defaults to 0.5.
            - `return_score_type` (Literal["none"], optional):
                Specifies whether and how to return similarity scores with the results:
                    - "none": Do not return scores; only return the contents (default).
            - `filter` (Optional[dict], optional): The filter dict for metadata.

        - **Returns**:
            - `list[tuple[str, dict]]`: A list of tuples containing the content and its associated metadata.
        """
        _filter = {
            "_id": agent_id,
        }
        if filter is not None:
            _filter.update(filter)

        if return_score_type == "none":
            _result = await self.vectors_store.amax_marginal_relevance_search(
                query=query,
                k=k,
                filter=_filter,
                fetch_k=fetch_k,
                lambda_mult=lambda_mult,
            )
            return [(r.page_content, r.metadata) for r in _result]
        else:
            raise ValueError(f"Invalid `return_score_type` {return_score_type}!")

    @lock_decorator
    async def marginal_relevance_search_by_embedding(
        self,
        embedding: list[float],
        agent_id: int,
        k: int = 4,
        fetch_k: int = 20,
        lambda_mult: float = 0.5,
        return_score_type: Union[Literal["none"], Literal["similarity_score"]] = "none",
        filter: Optional[dict] = None,
    ) -> Union[list[tuple[str, dict]], list[tuple[str, float, dict]]]:
        """
        Select contents using maximal marginal relevance asynchronously based on embedding.

        - **Description**:
            - Asynchronously selects a set of documents that are relevant to the provided embedding vector while ensuring diversity among the results.
            - The selection process balances between relevance to the embedding and diversity, controlled by `lambda_mult`.

        - **Args**:
            - `embedding` (list[float]): The vector to look up documents similar to.
            - `agent_id` (int): The identifier of the agent to filter specific documents.
            - `k` (int, optional): The number of top similar contents to return. Defaults to 4.
            - `fetch_k` (int, optional): The number of documents to fetch before applying any filters. Defaults to 20.
            - `lambda_mult` (float, optional): Number between 0 and 1 that determines the degree of diversity among the results. Defaults to 0.5.
            - `return_score_type` (Union[Literal["none"], Literal["similarity_score"]], optional):
                Specifies whether and how to return similarity scores with the results:
                    - "none": Do not return scores; only return the contents (default).
                    - "similarity_score": Return a tuple of content and its similarity score.
            - `filter` (Optional[dict], optional): The filter dict for metadata.

        - **Returns**:
            - `Union[list[tuple[str, dict]], list[tuple[str, float, dict]]]`: Depending on the `return_score_type` parameter,
              returns either a list of tuples containing the content and its associated metadata, or also including a floating-point score.
        """

        _filter = {
            "_id": agent_id,
        }
        if filter is not None:
            _filter.update(filter)
        if return_score_type == "none":
            _result = await self.vectors_store.amax_marginal_relevance_search_by_vector(
                embedding=embedding,
                k=k,
                filter=_filter,
                fetch_k=fetch_k,
                lambda_mult=lambda_mult,
            )
            return [(r.page_content, r.metadata) for r in _result]
        elif return_score_type == "similarity_score":
            _result = await self.vectors_store.amax_marginal_relevance_search_with_score_by_vector(
                embedding=embedding,
                k=k,
                filter=_filter,
                fetch_k=fetch_k,
                lambda_mult=lambda_mult,
            )
            return [(r.page_content, s, r.metadata) for r, s in _result]

        else:
            raise ValueError(f"Invalid `return_score_type` {return_score_type}!")
