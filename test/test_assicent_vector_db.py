# test/test_assicent_vector_db.py
import unittest
from unittest.mock import patch, MagicMock
import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from Vectordb.assicentVectorDb import AssicentVectorDB
from langchain_core.documents import Document


class TestAssicentVectorDB(unittest.TestCase):

    @patch('Vectordb.assicentVectorDb.Chroma')
    @patch('Vectordb.assicentVectorDb.OllamaEmbeddings')
    @patch('os.makedirs')
    def setUp(self, mock_makedirs, mock_embeddings_class, mock_chroma_class):
        # Setup mocks
        self.mock_embeddings = MagicMock()
        mock_embeddings_class.return_value = self.mock_embeddings

        self.mock_chroma_instance = MagicMock()
        mock_chroma_class.return_value = self.mock_chroma_instance

        # Create instance — now mock persists beyond setUp
        self.db = AssicentVectorDB(
            persist_directory="./test_db",
            collection_name="test_kb",
            embedding_model="test-embed"
        )

        # Save for assertions
        self.mock_chroma_class = mock_chroma_class
        self.mock_embeddings_class = mock_embeddings_class

    def test_initialization(self):
        self.mock_embeddings_class.assert_called_once_with(
            model="test-embed",
            base_url="http://192.168.124.155:8080"
        )
        self.mock_chroma_class.assert_called_once_with(
            persist_directory="./test_db",
            collection_name="test_kb",
            embedding_function=self.mock_embeddings
        )

    def test_add_documents(self):
        documents = [Document(page_content="Test doc")]
        self.db.add_documents(documents)
        self.mock_chroma_instance.add_documents.assert_called_once_with(documents)

    def test_get_llm_data(self):
        mock_docs = [
            Document(page_content="Result 1"),
            Document(page_content="Result 2")
        ]
        self.mock_chroma_instance.similarity_search.return_value = mock_docs

        results = self.db.get_llm_data("test query", k=2)
        self.mock_chroma_instance.similarity_search.assert_called_once_with("test query", k=2)
        self.assertEqual(results, ["Result 1", "Result 2"])

    def test_delete_collection(self):
        # Before delete: Chroma called once (in __init__)
        self.assertEqual(self.mock_chroma_class.call_count, 1)

        # Call delete_collection
        self.db.delete_collection()

        # Now should be called twice: initial + rebuild
        self.assertEqual(self.mock_chroma_class.call_count, 2)

        # Check second call args
        calls = self.mock_chroma_class.call_args_list
        second_call = calls[1]
        self.assertEqual(second_call.kwargs['persist_directory'], "./test_db")
        self.assertEqual(second_call.kwargs['collection_name'], "test_kb")
        self.assertEqual(second_call.kwargs['embedding_function'], self.mock_embeddings)

        # Also check delete_collection was called on the original instance
        self.mock_chroma_instance.delete_collection.assert_called_once()