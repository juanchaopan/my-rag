from os import getenv
from banks import ChatMessage
from chromadb import PersistentClient
from chromadb.config import Settings as ChromaSettings
from fastapi import FastAPI, Body
from fastapi.responses import StreamingResponse
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.llms.nvidia import NVIDIA
from llama_index.embeddings.nvidia import NVIDIAEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore


def init_chat_engine():
    chroma_client = PersistentClient(
        path="./chroma_db",
        settings=ChromaSettings(
            anonymized_telemetry=False,
        ),
    )
    collection = chroma_client.get_collection(name="vector_store")
    vector_store = ChromaVectorStore(chroma_collection=collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    embed_model = NVIDIAEmbedding(
        api_key=getenv("NVIDIA_API_KEY"),
        model=getenv("EMBEDDING_MODEL"),
    )
    language_model = NVIDIA(
        api_key=getenv("NVIDIA_API_KEY"),
        model=getenv("LLM_MODEL"),
    )
    vector_store_index = VectorStoreIndex.from_vector_store(
        vector_store=vector_store,
        storage_context=storage_context,
        embed_model=embed_model,
    )
    chat_engine = vector_store_index.as_chat_engine(llm=language_model)
    return chat_engine


app = FastAPI()

chat_engine = init_chat_engine()


@app.post("/chat")
async def post_conversation_message(
    body: list = Body(..., media_type="application/json")
):
    message = body[-1]["content"]
    chat_history = [
        ChatMessage(role=x["role"], content=x["content"]) for x in body[:-1]
    ]
    chat_response = await chat_engine.astream_chat(message, chat_history=chat_history)

    async def stream():
        async for chunk in chat_response.async_response_gen():
            yield chunk

    return StreamingResponse(stream(), media_type="text/event-stream")
