import os
import re
import hashlib
import pymysql
import qdrant_client
from dotenv import load_dotenv
from langchain.schema import Document
from langchain.vectorstores import Qdrant
from langchain_huggingface import HuggingFaceEmbeddings
from qdrant_client.http.models import PointIdsList, Distance, VectorParams
from .config import (
    EMBEDDING_MODEL,
    QDRANT_HOST,
    QDRANT_API_KEY,
    QDRANT_COLLECTION_NAME,
    EMBEDDING_SIZE,
)

load_dotenv()

# --- MySQL connection ---
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_DB = os.getenv("MYSQL_DB")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))

def connect_db():
    return pymysql.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB,
        port=MYSQL_PORT,
        cursorclass=pymysql.cursors.DictCursor,
    )

def load_sql():
    """ Trả về list[dict] với đúng tên field từ DB """
    with connect_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM Courses")
            return cursor.fetchall()

# --- Embedding model & Qdrant client ---
embedding_model = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
client = qdrant_client.QdrantClient(QDRANT_HOST, api_key=QDRANT_API_KEY)

# --- Hash function ---
def hash_course(c: dict) -> str:
    text = "|".join([
        str(c.get("CourseName", "")),
        str(c.get("Descriptions", "")),
        str(c.get("Skills", "")),
        str(c.get("EstimatedDuration", "")),
        str(c.get("Difficulty", "")),
        str(c.get("AverageRating", "")),
    ])
    return hashlib.md5(text.encode("utf-8")).hexdigest()

# --- Convert MySQL rows to LangChain Documents ---
def convert_to_documents(courses: list[dict]) -> list[Document]:
    documents: list[Document] = []
    for c in courses:
        # 1) Build the textual content
        parts = [
            f"CourseName: {c.get('CourseName', 'No title')}",
            f"Descriptions: {c.get('Descriptions', 'No description')}",
            f"Skills: {c.get('Skills', 'None')}",
            f"EstimatedDuration (hours): {c.get('EstimatedDuration', 'Unknown')}",
            f"Difficulty: {c.get('Difficulty', 'Unknown')}",
            f"AverageRating: {c.get('AverageRating', '0.00')}",
        ]
        text = ", ".join(parts)
        text = re.sub(r"\s+", " ", text).strip()

        # 2) Assemble metadata
        metadata = {
            "CourseID": c["CourseID"],
            "Skills": c.get("Skills", ""),
            "EstimatedDuration": c.get("EstimatedDuration", 0),
            "Difficulty": c.get("Difficulty", ""),
            "AverageRating": float(c.get("AverageRating", 0.0)),
            "hash": hash_course(c),
        }

        documents.append(Document(page_content=text, metadata=metadata))
    return documents

# --- Get existing data from Qdrant ---
def get_existing_qdrant_data() -> tuple[set[int], dict[int,str]]:
    qdrant_ids: set[int] = set()
    qdrant_hash_map: dict[int,str] = {}

    scroll_offset = None
    while True:
        points, scroll_offset = client.scroll(
            collection_name=QDRANT_COLLECTION_NAME,
            limit=1000,
            with_payload=True,
            offset=scroll_offset,
        )
        for pt in points:
            cid = pt.payload["metadata"]["CourseID"]
            qdrant_ids.add(cid)
            qdrant_hash_map[cid] = pt.payload["metadata"].get("hash", "")
        if scroll_offset is None:
            break

    return qdrant_ids, qdrant_hash_map

# --- Sync function ---
def sync_courses_to_qdrant():
    # 1) Tạo collection nếu chưa có
    cols = client.get_collections().collections
    if not any(c.name == QDRANT_COLLECTION_NAME for c in cols):
        client.create_collection(
            collection_name=QDRANT_COLLECTION_NAME,
            vectors_config=VectorParams(size=EMBEDDING_SIZE, distance=Distance.COSINE),
        )

    # 2) Load data từ MySQL
    db_courses = load_sql()
    db_map = {c["CourseID"]: c for c in db_courses}
    db_ids = set(db_map.keys())

    # 3) Load data từ Qdrant
    qdrant_ids, qdrant_hash_map = get_existing_qdrant_data()

    # 4) Xác định new / removed / updated
    new_ids     = db_ids - qdrant_ids
    removed_ids = qdrant_ids - db_ids
    updated_ids = {
        cid
        for cid in db_ids & qdrant_ids
        if hash_course(db_map[cid]) != qdrant_hash_map.get(cid, "")
    }

    # 5) Upsert mới & cập nhật
    to_upsert = [db_map[cid] for cid in new_ids | updated_ids]
    if to_upsert:
        docs = convert_to_documents(to_upsert)
        vs = Qdrant(
            client=client,
            collection_name=QDRANT_COLLECTION_NAME,
            embeddings=embedding_model,
            content_payload_key="page_content",
            metadata_payload_key="metadata",
        )
        vs.add_documents(docs)
        print(f"✅ Added/Updated: {len(docs)} documents.")

    # 6) Xoá những khóa đã gỡ
    if removed_ids:
        client.delete(
            collection_name=QDRANT_COLLECTION_NAME,
            points_selector=PointIdsList(points=list(removed_ids)),
        )
        print(f"🗑 Removed: {len(removed_ids)} documents.")

    print(
        f"🔄 Sync completed. "
        f"New: {len(new_ids)}, "
        f"Updated: {len(updated_ids)}, "
        f"Removed: {len(removed_ids)}"
    )

# --- Lấy vectorstore cho các chain khác ---
def get_vectorstore() -> Qdrant:
    return Qdrant(
        client=client,
        collection_name=QDRANT_COLLECTION_NAME,
        embeddings=embedding_model,
        content_payload_key="page_content",
        metadata_payload_key="metadata",
    )
