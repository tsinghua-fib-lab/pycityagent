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
    def __init__(
        self,
        pretrained_model_name_or_path: Union[str, os.PathLike] = "BAAI/bge-m3",
        max_seq_len: int = 8192,
        auto_cuda: bool = False,
        local_files_only: bool = False,
        cache_dir: str = "./cache",
        proxies: Optional[dict] = None,
    ):
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
        """Embed documents."""
        return self._embed(texts)

    def embed_query(self, text: str) -> list[float]:
        """Embed query text."""
        return self._embed([text])[0]


class SimpleEmbedding(Embeddings):
    """简单的基于内存的embedding实现

    使用简单的词袋模型(Bag of Words)和TF-IDF来生成文本的向量表示。
    所有向量都保存在内存中，适用于小规模应用。
    """

    def __init__(self, vector_dim: int = 128, cache_size: int = 1000):
        """初始化

        Args:
            vector_dim: 向量维度
            cache_size: 缓存大小，超过此大小将清除最早的缓存
        """
        self.vector_dim = vector_dim
        self.cache_size = cache_size
        self._cache: dict[str, list[float]] = {}
        self._vocab: dict[str, int] = {}  # 词汇表
        self._idf: dict[str, float] = {}  # 逆文档频率
        self._doc_count = 0  # 文档总数

    def _text_to_hash(self, text: str) -> str:
        """将文本转换为hash值"""
        return hashlib.md5(text.encode()).hexdigest()

    def _tokenize(self, text: str) -> list[str]:
        """简单的分词"""
        # 这里使用简单的空格分词，实际应用中可以使用更复杂的分词方法
        return text.lower().split()

    def _update_vocab(self, tokens: list[str]):
        """更新词汇表"""
        for token in set(tokens):  # 使用set去重
            if token not in self._vocab:
                self._vocab[token] = len(self._vocab)

    def _update_idf(self, tokens: list[str]):
        """更新IDF值"""
        self._doc_count += 1
        unique_tokens = set(tokens)
        for token in unique_tokens:
            self._idf[token] = self._idf.get(token, 0) + 1

    def _calculate_tf(self, tokens: list[str]) -> dict[str, float]:
        """计算词频(TF)"""
        tf = {}
        total_tokens = len(tokens)
        for token in tokens:
            tf[token] = tf.get(token, 0) + 1
        # 归一化
        for token in tf:
            tf[token] /= total_tokens
        return tf

    def _calculate_tfidf(self, tokens: list[str]) -> list[float]:
        """计算TF-IDF向量"""
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
        """生成文本的向量表示

        Args:
            text: 输入文本

        Returns:
            np.ndarray: 文本的向量表示
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
        """Embed documents."""
        return [self._embed(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        """Embed query text."""
        return self._embed(text)

if __name__ == "__main__":
    # se = SentenceEmbedding(
    #     pretrained_model_name_or_path="ignore/BAAI--bge-m3", cache_dir="ignore"
    # )
    se = SimpleEmbedding()
    print(se.embed_query("hello world"))
    print(se.embed_query("hello world"))
    print(se.embed_query("hello world"))
    print(se.embed_query("hello world"))
