
from Vectordb.assicentVectorDb import AssicentVectorDB
from langchain_core.documents import Document

db = AssicentVectorDB()

docs = [
    Document(page_content="The main living room light is controlled by a smart switch, with the voice command 'Turn on the living room light'."),
    Document(page_content="The air conditioner brand is Daikin, with energy-saving mode enabled by default and the temperature set to 24 degrees Celsius."),
    Document(page_content="The user has a habit of turning off all lights after 10 PM, unless there are guests.")
]


db.add_documents(docs)
print("Knowledge base built successfully!")
