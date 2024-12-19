"""简单的基于内存的embedding实现"""

import numpy as np
from typing import List, Dict, Optional
import hashlib
import json


class SimpleEmbedding:
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
        self._cache: Dict[str, np.ndarray] = {}
        self._vocab: Dict[str, int] = {}  # 词汇表
        self._idf: Dict[str, float] = {}  # 逆文档频率
        self._doc_count = 0  # 文档总数

    def _text_to_hash(self, text: str) -> str:
        """将文本转换为hash值"""
        return hashlib.md5(text.encode()).hexdigest()

    def _tokenize(self, text: str) -> List[str]:
        """简单的分词"""
        # 这里使用简单的空格分词，实际应用中可以使用更复杂的分词方法
        return text.lower().split()

    def _update_vocab(self, tokens: List[str]):
        """更新词汇表"""
        for token in set(tokens):  # 使用set去重
            if token not in self._vocab:
                self._vocab[token] = len(self._vocab)

    def _update_idf(self, tokens: List[str]):
        """更新IDF值"""
        self._doc_count += 1
        unique_tokens = set(tokens)
        for token in unique_tokens:
            self._idf[token] = self._idf.get(token, 0) + 1

    def _calculate_tf(self, tokens: List[str]) -> Dict[str, float]:
        """计算词频(TF)"""
        tf = {}
        total_tokens = len(tokens)
        for token in tokens:
            tf[token] = tf.get(token, 0) + 1
        # 归一化
        for token in tf:
            tf[token] /= total_tokens
        return tf

    def _calculate_tfidf(self, tokens: List[str]) -> np.ndarray:
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

        return vector

    async def embed(self, text: str) -> np.ndarray:
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
            return np.zeros(self.vector_dim)

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

        return vector

    def save(self, file_path: str):
        """保存模型"""
        state = {
            "vector_dim": self.vector_dim,
            "cache_size": self.cache_size,
            "vocab": self._vocab,
            "idf": self._idf,
            "doc_count": self._doc_count,
        }
        with open(file_path, "w") as f:
            json.dump(state, f)

    def load(self, file_path: str):
        """加载模型"""
        with open(file_path, "r") as f:
            state = json.load(f)
        self.vector_dim = state["vector_dim"]
        self.cache_size = state["cache_size"]
        self._vocab = state["vocab"]
        self._idf = state["idf"]
        self._doc_count = state["doc_count"]
        self._cache = {}  # 清空缓存
