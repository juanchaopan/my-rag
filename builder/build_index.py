from jsonlines import open
from llama_index.core import Document, Settings
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
from chromadb import HttpClient
from os import getenv
from smart_markdown_node_parser import SmartMarkdownNodeParser


def main():
    Settings.embed_model = OllamaEmbedding(
        base_url=getenv("OLLAMA_URL"),
        model_name="nomic-embed-text",
    )
    node_parser = SmartMarkdownNodeParser()
    chroma_client = HttpClient(
        host=getenv("CHROMA_HOST"),
        port=int(getenv("CHROMA_PORT")),
        ssl=getenv("CHROMA_SSL") == "true",
    )
    collection_name = "langchain-ai-docs"
    if collection_name in [x.name for x in chroma_client.list_collections()]:
        chroma_client.delete_collection(name=collection_name)
    collection = chroma_client.create_collection(name=collection_name)
    vector_store = ChromaVectorStore(chroma_collection=collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    documents = []
    with open("langchain-ai-docs.jsonl", "r") as reader:
        for obj in reader:
            document = Document(doc_id=obj["id"], text=obj["content"])
            documents.append(document)

    VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
        transformations=[node_parser],
        show_progress=True,
    )


if __name__ == "__main__":
    main()
