# assicentVectorDb.py

import os
from typing import List
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_core.documents import Document

class AssicentVectorDB:
    def __init__(
        self,
        persist_directory: str = "./data/chroma_db",
        collection_name: str = "assicent_kb",
        embedding_model: str = "qwen3-embedding:0.6b",  # Ollama embedding
        embedding_base_url: str | None = None
    ):
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        os.makedirs(persist_directory, exist_ok=True)
        embedding_base_url = embedding_base_url or os.getenv("OLLAMA_BASE_URL", "http://192.168.124.155:8080")

        # Ollama  embedding
        self.embedding_function = OllamaEmbeddings(
        model=embedding_model,
        base_url=embedding_base_url
        )

        self.vectorstore = Chroma(
            persist_directory=persist_directory,
            collection_name=collection_name,
            embedding_function=self.embedding_function
        )

    def add_documents(self, documents: List[Document]) -> None:
        """Add document to vector library"""
        self.vectorstore.add_documents(documents)

    def get_llm_data(self, query: str, k: int = 3) -> List[str]:
        """Search related text"""
        results = self.vectorstore.similarity_search(query, k=k)
        return [doc.page_content for doc in results]

    def delete_collection(self) -> None:
        """Clear the collection (for debugging purposes)"""
        self.vectorstore.delete_collection()
        self.vectorstore = Chroma(
            persist_directory=self.persist_directory,
            collection_name=self.collection_name,
            embedding_function=self.embedding_function
        )