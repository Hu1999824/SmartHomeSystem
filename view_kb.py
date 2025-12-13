import chromadb
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
import os

# --- 1. Configuration ---
PERSIST_DIRECTORY = './data/chroma_db'
# LangChain-integrated Chroma typically uses a default collection name.
# If your AssicentVectorDB specifies a custom name, replace 'assicent_kb' below.
COLLECTION_NAME = 'assicent_kb'

# Note: This script assumes your AssicentVectorDB is a thin wrapper around LangChain's Chroma.
# If your actual collection name differs (e.g., 'my_collection'), update COLLECTION_NAME accordingly.

def view_chroma_db(persist_path: str, collection_name: str):
    """Connect to a persistent ChromaDB instance and retrieve all documents from the specified collection."""
    
    print(f"Attempting to connect to Chroma DB at path: {os.path.abspath(persist_path)}")
    
    try:
        # Initialize Chroma persistent client
        client = chromadb.PersistentClient(path=persist_path)
        
        # Retrieve the collection by name
        collection = client.get_collection(name=collection_name)
        
        # Fetch all documents and metadata
        # Note: In Chroma v0.4.x+, the default limit is 100; use limit=None to fetch all
        results = collection.get(
            include=["documents", "metadatas"],
            limit=None  # Fetch all entries
        )
        
        doc_contents = results.get("documents", [])
        doc_metadatas = results.get("metadatas", [])
        
        if not doc_contents:
            print("❌ No documents found in the collection. Please verify the collection name.")
            return
            
        print(f"\n✅ Successfully retrieved {len(doc_contents)} knowledge base entries:")
        print("---------------------------------------")
        
        for i, (content, metadata) in enumerate(zip(doc_contents, doc_metadatas), 1):
            metadata_str = ', '.join(f"{k}: {v}" for k, v in (metadata or {}).items())
            print(f"--- Entry {i} ---")
            print(f"Content: {content}")
            print(f"Metadata: ({metadata_str})")
            print("---------------------------------------")

    except Exception as e:
        print(f"❌ Error: Failed to connect to or read from the database: {e}")
        print("Tip: Ensure the `chromadb` package is installed in your Python environment.")

if __name__ == "__main__":
    # Replace COLLECTION_NAME if your AssicentVectorDB uses a different collection name
    view_chroma_db(PERSIST_DIRECTORY, COLLECTION_NAME)