import hashlib
import json
import os
from typing import Optional, Union

import numpy as np
import torch
from langchain_core.embeddings import Embeddings
from transformers import AutoModel, AutoTokenizer

__all__ = [
    "SentenceEmbedding",
    "SimpleEmbedding",
]


class SentenceEmbedding(Embeddings):
    """
    Main class for generating sentence embeddings using a pre-trained language model.

    - **Description**:
        - This class initializes a tokenizer and a pre-trained model to generate embeddings for input texts.
        - It supports automatic CUDA device allocation and handles caching of models locally.
    """

    def __init__(
        self,
        pretrained_model_name_or_path: Union[str, os.PathLike] = "BAAI/bge-m3",
        max_seq_len: int = 8192,
        auto_cuda: bool = False,
        local_files_only: bool = False,
        cache_dir: str = "./cache",
        proxies: Optional[dict] = None,
    ):
        """
        Initializes the SentenceEmbedding instance.

        - **Parameters**:
            - `pretrained_model_name_or_path`: Name or path of the pre-trained model. Default is "BAAI/bge-m3".
            - `max_seq_len`: Maximum sequence length for inputs. Default is 8192.
            - `auto_cuda`: Automatically move the model to available CUDA device if True. Default is False.
            - `local_files_only`: Only try to load model from local files if True. Default is False.
            - `cache_dir`: Directory to cache models. Default is "./cache".
            - `proxies`: Proxy settings for HTTP/HTTPS. Default is None.
        """
        os.makedirs(cache_dir, exist_ok=True)
        self.tokenizer = AutoTokenizer.from_pretrained(
            pretrained_model_name_or_path,
            proxies=proxies,
            cache_dir=cache_dir,
            local_files_only=local_files_only,
        )
        self.model = AutoModel.from_pretrained(
            pretrained_model_name_or_path,
            proxies=proxies,
            cache_dir=cache_dir,
            local_files_only=local_files_only,
        )
        self._cuda = auto_cuda and torch.cuda.is_available()

        if self._cuda:
            self.model = self.model.cuda()

        self.model.eval()
        self.max_seq_len = max_seq_len

    def _embed(self, texts: list[str]) -> list[list[float]]:
        """
        Internal method to compute embeddings for a list of input texts.

        - **Parameters**:
            - `texts`: A list of strings representing the input texts.

        - **Returns**:
            - A list of lists containing floating-point numbers representing the embeddings.
        """
        # Tokenize sentences
        encoded_input = self.tokenizer(
            texts, padding=True, truncation=True, return_tensors="pt"
        )
        # for s2p(short query to long passage) retrieval task, add an instruction to query (not add instruction for passages)
        # encoded_input = tokenizer([instruction + q for q in queries], padding=True, truncation=True, return_tensors='pt')

        # check length of input
        # assert seq_len <= 8192
        assert encoded_input["input_ids"].shape[1] <= self.max_seq_len  # type: ignore

        if self._cuda:
            encoded_input = {k: v.cuda() for k, v in encoded_input.items()}
        # Compute token embeddings
        with torch.no_grad():
            model_output = self.model(**encoded_input)
            # Perform pooling. In this case, cls pooling.
            sentence_embeddings = model_output[0][:, 0]
        # normalize embeddings
        sentence_embeddings = torch.nn.functional.normalize(
            sentence_embeddings, p=2, dim=1
        )
        if self._cuda:
            sentence_embeddings = sentence_embeddings.cpu()
        return sentence_embeddings.tolist()

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """
        Embeds a list of documents.

        - **Parameters**:
            - `texts`: The documents to embed.

        - **Returns**:
            - A list of document embeddings.
        """
        return self._embed(texts)

    def embed_query(self, text: str) -> list[float]:
        """
        Embeds a single query text.

        - **Parameters**:
            - `text`: The query text to embed.

        - **Returns**:
            - The embedding of the query text.
        """
        return self._embed([text])[0]


class SimpleEmbedding(Embeddings):
    """
    A simple in-memory embedding implementation using Bag of Words and TF-IDF for generating text vectors.

    - **Description**:
        - This class provides a basic approach to creating text embeddings based on term frequency-inverse document frequency (TF-IDF).
        - It maintains an in-memory cache of computed embeddings and updates its vocabulary dynamically as new texts are processed.
    """

    def __init__(self, vector_dim: int = 128, cache_size: int = 1000):
        """
        Initializes the SimpleEmbedding instance.

        - **Parameters**:
            - `vector_dim`: Dimensionality of the vectors. Default is 128.
            - `cache_size`: Cache size; oldest entries are removed when exceeded. Default is 1000.
        """
        self.vector_dim = vector_dim
        self.cache_size = cache_size
        self._cache: dict[str, list[float]] = {}
        self._vocab: dict[str, int] = {}  # 词汇表
        self._idf: dict[str, float] = {}  # 逆文档频率
        self._doc_count = 0  # 文档总数

    def _text_to_hash(self, text: str) -> str:
        """
        Converts text into a hash value.

        - **Parameters**:
            - `text`: The input text to hash.

        - **Returns**:
            - A string representing the MD5 hash of the input text.
        """
        return hashlib.md5(text.encode()).hexdigest()

    def _tokenize(self, text: str) -> list[str]:
        """
        Performs simple tokenization on the input text.

        - **Parameters**:
            - `text`: The input text to tokenize.

        - **Returns**:
            - A list of tokens extracted from the input text.
        """
        # 这里使用简单的空格分词，实际应用中可以使用更复杂的分词方法
        return text.lower().split()

    def _update_vocab(self, tokens: list[str]):
        """
        Updates the vocabulary with new tokens.

        - **Description**:
            - This method adds unique tokens from the input list to the vocabulary.
            - It ensures that each token is only added once using a set for deduplication.

        - **Parameters**:
            - `tokens`: A list of strings representing the tokens to add to the vocabulary.
        """
        for token in set(tokens):  # 使用set去重
            if token not in self._vocab:
                self._vocab[token] = len(self._vocab)

    def _update_idf(self, tokens: list[str]):
        """
        Updates the IDF values based on the tokens.

        - **Description**:
            - Increases the document count and updates the inverse document frequency (IDF) for each unique token.

        - **Parameters**:
            - `tokens`: A list of strings representing the tokens from a single document.
        """
        self._doc_count += 1
        unique_tokens = set(tokens)
        for token in unique_tokens:
            self._idf[token] = self._idf.get(token, 0) + 1

    def _calculate_tf(self, tokens: list[str]) -> dict[str, float]:
        """
        Calculates term frequency (TF) for the tokens.

        - **Description**:
            - Computes the frequency of each token within the provided list and normalizes it by the total number of tokens.

        - **Parameters**:
            - `tokens`: A list of strings representing the tokens to calculate TF for.

        - **Returns**:
            - A dictionary mapping each token to its normalized term frequency.
        """
        tf = {}
        total_tokens = len(tokens)
        for token in tokens:
            tf[token] = tf.get(token, 0) + 1
        # 归一化
        for token in tf:
            tf[token] /= total_tokens
        return tf

    def _calculate_tfidf(self, tokens: list[str]) -> list[float]:
        """
        Calculates the TF-IDF vector for the tokens.

        - **Description**:
            - Generates a vector representation of the input tokens using the Term Frequency-Inverse Document Frequency (TF-IDF) weighting scheme.

        - **Parameters**:
            - `tokens`: A list of strings representing the tokens to generate the TF-IDF vector for.

        - **Returns**:
            - A list of floating-point numbers representing the TF-IDF vector.
        """
        vector = np.zeros(self.vector_dim)
        tf = self._calculate_tf(tokens)

        for token, tf_value in tf.items():
            if token in self._idf:
                idf = np.log(self._doc_count / self._idf[token])
                idx = self._vocab[token] % self.vector_dim  # 使用取模运算来控制向量维度
                vector[idx] += tf_value * idf

        # L2归一化
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector /= norm

        return list(vector)

    def _embed(self, text: str) -> list[float]:
        """
        Generates a vector representation for the input text.

        - **Description**:
            - Creates an embedding for the given text by first checking if it's already cached,
              then tokenizing, updating the vocabulary and IDF, calculating the TF-IDF vector,
              and finally caching the result.

        - **Parameters**:
            - `text`: The input text to generate the vector for.

        - **Returns**:
            - A list of floating-point numbers representing the vector of the input text.
        """
        # 检查缓存
        text_hash = self._text_to_hash(text)
        if text_hash in self._cache:
            return self._cache[text_hash]

        # 分词
        tokens = self._tokenize(text)
        if not tokens:
            return list(np.zeros(self.vector_dim))

        # 更新词汇表和IDF
        self._update_vocab(tokens)
        self._update_idf(tokens)

        # 计算向量
        vector = self._calculate_tfidf(tokens)

        # 更新缓存
        if len(self._cache) >= self.cache_size:
            # 删除最早的缓存
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
        self._cache[text_hash] = vector

        return list(vector)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """
        Embeds a list of documents.

        - **Parameters**:
            - `texts`: A list of strings representing the documents to embed.

        - **Returns**:
            - A list of lists containing the embeddings of the documents.
        """
        return [self._embed(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        """
        Embeds a single query text.

        - **Parameters**:
            - `text`: The query text to embed.

        - **Returns**:
            - A list of floating-point numbers representing the embedding of the query text.
        """
        return self._embed(text)


if __name__ == "__main__":
    se = SimpleEmbedding()
    print(se.embed_query("hello world"))
