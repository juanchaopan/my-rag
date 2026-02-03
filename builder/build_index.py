from jsonlines import open
from llama_index.core import Document, Settings as LlamaSettings
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.embeddings.nvidia import NVIDIAEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
from chromadb import PersistentClient
from chromadb.config import Settings as ChromaSettings
from os import getenv
from node_parser import UnstructuredMdNodeParser


def build_vector_store_index(
    chroma_client: PersistentClient, documents: list[Document]
) -> None:
    collection_name = "vector_store"
    if collection_name in [x.name for x in chroma_client.list_collections()]:
        chroma_client.delete_collection(name=collection_name)
    collection = chroma_client.create_collection(name=collection_name)
    vector_store = ChromaVectorStore(chroma_collection=collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    transformations = [UnstructuredMdNodeParser()]
    VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
        transformations=transformations,
        show_progress=True,
    )


def main():
    chroma_client = PersistentClient(
        path="./chroma_db",
        settings=ChromaSettings(
            anonymized_telemetry=False,
        ),
    )

    documents = []
    with open("langchain-ai-docs.jsonl", "r") as reader:
        for obj in reader:
            document = Document(doc_id=obj["id"], text=obj["content"])
            documents.append(document)

    LlamaSettings.embed_model = NVIDIAEmbedding(
        api_key=getenv("NVIDIA_API_KEY"),
        model=getenv("EMBEDDING_MODEL"),
    )

    build_vector_store_index(chroma_client, documents)


if __name__ == "__main__":
    main()
