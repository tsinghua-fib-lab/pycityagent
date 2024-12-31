import os
from typing import Optional, Union

import torch
from langchain_core.embeddings import Embeddings
from transformers import AutoModel, AutoTokenizer

__all__ = ["SentenceEmbedding"]


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


if __name__ == "__main__":
    se = SentenceEmbedding(
        pretrained_model_name_or_path="ignore/BAAI--bge-m3", cache_dir="ignore"
    )
    print(se.embed_query("hello world"))
