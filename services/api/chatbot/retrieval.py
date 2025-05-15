import qdrant_client
from langchain.vectorstores import Qdrant
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
import os
import json
import re
from config import EMBEDDING_MODEL, QDRANT_HOST, QDRANT_API_KEY, QDRANT_COLECTION_NAME, EMBEDDING_SIZE

embedding_model = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

def load_json(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_data(filepath):
    products = load_json(filepath)  

    documents = []
    for p in products:
        text = f"""
        URL: {p.get("url", "Không có thông tin")},
        Tên: {p.get("product_name", "Không có tên")},
        Mã sản phẩm: {p.get("product_id", "Không có mã")},
        Model: {p.get("model", "Không có model")},
        Giá gốc: {p.get("old_price", "Không có giá")} VND,
        Giá KM: {p.get("price", "Không có giá")} VND,
        Giảm giá: {p.get("discount_rate", "Không có thông tin")},
        Mô tả: {p.get("description", "Không có mô tả")},
        Thông số kỹ thuật: {json.dumps(p.get("specifications", {}), ensure_ascii=False)}
        """
        text = re.sub(r'\n\s*', ' ', text)
        documents.append(Document(page_content=text, 
        metadata={"L1": p.get("L1", "N/A"),
                  "L2": p.get("L2", "N/A"),
                  "L3": p.get("L3", "N/A"),
                  "L4": p.get("L4", "N/A"),
                  "SKU": p.get("SKU", "N/A"),
                  "Price": p.get("price", "N/A")}))
    
    return documents


client = qdrant_client.QdrantClient(
    QDRANT_HOST,
    api_key = QDRANT_API_KEY,
)

def load_vectordb():
    collections_info = client.get_collections()
    if not any(col.name == QDRANT_COLECTION_NAME for col in collections_info.collections):
        vectors_config = qdrant_client.http.models.VectorParams(
            size=EMBEDDING_SIZE,
            distance=qdrant_client.http.models.Distance.COSINE,
        )

        client.create_collection(
            collection_name= QDRANT_COLECTION_NAME,
            vectors_config=vectors_config,
        )
        vector_store = Qdrant(
            client=client,
            collection_name=QDRANT_COLECTION_NAME,
            embeddings=embedding_model,
            content_payload_key="page_content",
            metadata_payload_key="metadata",
        )
        vector_store.add_documents(load_data("data/rangdong.json"))
    else:
        vector_store = Qdrant(
            client=client,
            collection_name=QDRANT_COLECTION_NAME,
            embeddings=embedding_model,
            content_payload_key="page_content",
            metadata_payload_key="metadata",
        )
    return vector_store
