import os
import tomllib
import pathlib
import contextlib
from typing import List

from pymongo.database import Database
from pymongo.collection import Collection
from pymongo.mongo_client import MongoClient
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_mongodb.vectorstores import MongoDBAtlasVectorSearch


@contextlib.contextmanager
def get_mongo_vectorstore():

    if os.getenv("MONGODB_URI") is None:
        secret_file = pathlib.Path(__file__).parent / ".streamlit"/ "secrets.toml"
        with open(secret_file, "rb") as f:
            config = tomllib.load(f)
        os.environ["MONGODB_URI"] = config["MONGODB_URI"]

    if os.getenv("OPENAI_API_KEY") is None:
        secret_file = pathlib.Path(__file__).parent / ".streamlit"/ "secrets.toml"
        with open(secret_file, "rb") as f:
            config = tomllib.load(f)
        os.environ["OPENAI_API_KEY"] = config["OPENAI_API_KEY"]

    client = MongoClient(host = os.getenv("MONGODB_URI"))

    try:
        database = Database(client, name = "MediGuide")
        vectorstore = MongoDBAtlasVectorSearch(
            collection=Collection(database, name = "Symptom"),
            embedding=OpenAIEmbeddings(model = "text-embedding-3-small"),
            index_name="default",
            embedding_key="question_embedding",
            text_key = "question"
        )
        yield vectorstore

    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        raise e
    finally:
        client.close()


def insert_symptom_subject_datas(datas: List[dict]):
    with get_mongo_vectorstore() as vectorstore:
        documents = []
        for data in datas:
            if vectorstore.collection.find_one({"subject_id": data["subject_id"]}):
                continue

            documents.append(Document(page_content=data.pop("question"), metadata=data))

        vectorstore.add_documents(documents, batch_size=100)