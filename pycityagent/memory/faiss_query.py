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
    def __init__(
        self,
        embeddings: Optional[Embeddings] = None,
        index_type: Any = faiss.IndexFlatL2,
        dimension: Optional[int] = None,
    ) -> None:
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
        if self._embeddings is None:
            raise RuntimeError(f"No embedding set, please `set_embeddings` first!")
        return self._embeddings

    @property
    def vectors_store(
        self,
    ) -> FAISS:
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
        Return content most similar to the given query.

        Args:
            query (str): The text to look up documents similar to.
            agent_id (int): The identifier of the agent to filter specific documents. Only documents associated with this agent will be considered.
            k (int, optional): The number of top similar contents to return. Defaults to 4.
            fetch_k (int, optional): The number of documents to fetch before applying any filters. Defaults to 20.
            return_score_type (Union[Literal["none"], Literal["similarity_score"], Literal["L2-distance"]], optional):
                Specifies whether and how to return similarity scores with the results:
                    - "none": Do not return scores; only return the contents (default).
                    - "similarity_score": Return a tuple of content and its similarity score.
                    - "L2-distance": Return a tuple of content and its L2 distance from the query.
            filter (dict, optional): The filter dict for metadata.

        Returns:
            Union[list[tuple[str,dict]], list[tuple[str, float,dict]]]:
                Depending on the `return_score_type` parameter, returns either a list of strings representing the top-k similar contents,
                or a list of tuples where each tuple contains a string and a floating-point score.
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
                _result = await self.vectors_store.asimilarity_search_with_relevance_scores(
                    query=query,
                    k=k,
                    filter=_filter,
                    fetch_k=fetch_k,
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
        Return content most similar to the given query.

        Args:
            embedding (list[float]): The vector to look up documents similar to.
            agent_id (int): The identifier of the agent to filter specific documents. Only documents associated with this agent will be considered.
            k (int, optional): The number of top similar contents to return. Defaults to 4.
            fetch_k (int, optional): The number of documents to fetch before applying any filters. Defaults to 20.
            return_score_type (Union[Literal["none"], Literal["similarity_score"], Literal["L2-distance"]], optional):
                Specifies whether and how to return similarity scores with the results:
                    - "none": Do not return scores; only return the contents (default).
                    - "L2-distance": Return a tuple of content and its L2 distance from the query.
            filter (dict, optional): The filter dict for metadata.

        Returns:
            Union[list[tuple[str,dict]], list[tuple[str, float,dict]]]:
                Depending on the `return_score_type` parameter, returns either a list of strings representing the top-k similar contents,
                or a list of tuples where each tuple contains a string and a floating-point score.
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
        Return contents selected using the maximal marginal relevance asynchronously.

        Args:
            query (str): The text to look up documents similar to.
            agent_id (int): The identifier of the agent to filter specific documents. Only documents associated with this agent will be considered.
            k (int, optional): The number of top similar contents to return. Defaults to 4.
            fetch_k (int, optional): The number of documents to fetch before applying any filters. Defaults to 20.
            lambda_mult (float): Number between 0 and 1 that determines the degree of diversity among the results with 0 corresponding to maximum diversity and 1 to minimum diversity. Defaults to 0.5.
            return_score_type (Literal["none"].,optional):
                Specifies whether and how to return similarity scores with the results:
                    - "none": Do not return scores; only return the contents (default).
            filter (dict, optional): The filter dict for metadata.

        Returns:
            list[tuple[str,dict]]: the result contents.
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
        Return contents selected using the maximal marginal relevance asynchronously.

        Args:
            embedding (list[float]): The vector to look up documents similar to.
            agent_id (int): The identifier of the agent to filter specific documents. Only documents associated with this agent will be considered.
            k (int, optional): The number of top similar contents to return. Defaults to 4.
            fetch_k (int, optional): The number of documents to fetch before applying any filters. Defaults to 20.
            lambda_mult (float): Number between 0 and 1 that determines the degree of diversity among the results with 0 corresponding to maximum diversity and 1 to minimum diversity. Defaults to 0.5.
            return_score_type (Union[Literal["none"], Literal["similarity_score"]], optional):
                Specifies whether and how to return similarity scores with the results:
                    - "none": Do not return scores; only return the contents (default).
                    - "similarity_score": Return a tuple of content and its similarity score.
            filter (dict, optional): The filter dict for metadata.

        Returns:
            Union[list[tuple[str,dict]], list[tuple[str, float,dict]]]:
                Depending on the `return_score_type` parameter, returns either a list of strings representing the top-k similar contents,
                or a list of tuples where each tuple contains a string and a floating-point score.
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
