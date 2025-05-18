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
    QDRANT_COLLECTION_NAME_LECTURES,
)

load_dotenv()

# --- MySQL connection ---
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_DB = os.getenv("MYSQL_DB")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))

embedding_model = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
client = qdrant_client.QdrantClient(QDRANT_HOST, api_key=QDRANT_API_KEY)

def connect_db():
    return pymysql.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB,
        port=MYSQL_PORT,
        cursorclass=pymysql.cursors.DictCursor,
    )


def load_sql_courses(): #-> list[dict]
    with connect_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT LectureID, Title, Description, Content
                FROM Lectures
            """)
            return cursor.fetchall()

def load_sql_lectures():  # -> list[dict]
    with connect_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT LectureID, Title, Description, Content
                FROM Lectures
            """)
            return cursor.fetchall()

def convert_to_documents_lectures(lectures: list[dict]) -> list[Document]:
    documents: list[Document] = []
    for l in lectures:
        # 1) Build the textual content
        parts = [
            f"Lecture Title: {l.get('Title', 'No title')}",  

def convert_to_documents_lectures(lectures: list[dict]) -> list[Document]:
    documents: list[Document] = []
    for l in lectures:
        parts = [
            f"Lecture Title: {l.get('Title', 'No title')}", 
            f"Description: {l.get('Description', 'No description')}",
            f"Content: {l.get('Content', 'None')}",
        ]
        text = ", ".join(parts)
        text = re.sub(r"\s+", " ", text).strip()


        # 2) Assemble metadata
        metadata = {
            "LectureID": l["LectureID"],
            # "CourseID": l["CourseID"],  # Optional if needed

        metadata = {
            "LectureID": l["LectureID"],
            "hash": hash_lectures(l)

        }

        documents.append(Document(page_content=text, metadata=metadata))
    return documents

embedding_model = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
client = qdrant_client.QdrantClient(QDRANT_HOST, api_key=QDRANT_API_KEY)

def get_existing_qdrant_data_lectures() -> tuple[set[int], dict[int,str]]:
    qdrant_ids: set[int] = set()
    qdrant_hash_map: dict[int,str] = {}

    scroll_offset = None
    while True:
        points, scroll_offset = client.scroll(
            collection_name=QDRANT_COLLECTION_NAME_LECTURES,
            limit=1000,
            with_payload=True,
            offset=scroll_offset,
        )
        for pt in points:
            cid = pt.payload["metadata"]["LectureID"]
            qdrant_ids.add(cid)
            qdrant_hash_map[cid] = pt.payload["metadata"].get("hash", "")
        if scroll_offset is None:
            break

    return qdrant_ids, qdrant_hash_map

def sync_lectures_to_qdrant():
    cols = client.get_collections().collections
    if not any(c.name == QDRANT_COLLECTION_NAME_LECTURES for c in cols):
        client.create_collection(
            collection_name=QDRANT_COLLECTION_NAME_LECTURES,
            vectors_config=VectorParams(size=EMBEDDING_SIZE, distance=Distance.COSINE),
        )

    # 2) Load data from MySQL
    db_lectures = load_sql_lectures()
    db_map = {l["LectureID"]: l for l in db_lectures}
    db_ids = set(db_map.keys())

    # 3) Load data from Qdrant
    qdrant_ids, qdrant_hash_map = get_existing_qdrant_data_lectures()

    # 4) detemine new / removed / updated
    new_ids     = db_ids - qdrant_ids
    removed_ids = qdrant_ids - db_ids
    updated_ids = {
        cid
        for cid in db_ids & qdrant_ids
        if hash_lectures(db_map[cid]) != qdrant_hash_map.get(cid, "")
    }

    # 5) Upsert & update
    to_upsert = [db_map[cid] for cid in new_ids | updated_ids]
    if to_upsert:
        docs = convert_to_documents_lectures(to_upsert)
        vs = Qdrant(
            client=client,
            collection_name=QDRANT_COLLECTION_NAME_LECTURES,
            embeddings=embedding_model,
            content_payload_key="page_content",
            metadata_payload_key="metadata",
        )
        vs.add_documents(docs)
        print(f"Added/Updated: {len(docs)} documents.")

    # 6) Delete Unavailable courses
    if removed_ids:
        client.delete(
            collection_name=QDRANT_COLLECTION_NAME_LECTURES,
            points_selector=PointIdsList(points=list(removed_ids)),
        )
        print(f"Removed: {len(removed_ids)} documents.")

    print(
        f"Sync completed. "
        f"New: {len(new_ids)}, "
        f"Updated: {len(updated_ids)}, "
        f"Removed: {len(removed_ids)}"
    )
    collection_info = client.get_collection(QDRANT_COLLECTION_NAME_LECTURES)
    total_points = collection_info.points_count
    print(f"Number of vector in Vectordb: {total_points}")

def get_vectorstore_lectures() -> Qdrant:
    return Qdrant(
        client=client,
        collection_name=QDRANT_COLLECTION_NAME_LECTURES,
        embeddings=embedding_model,
        content_payload_key="page_content",
        metadata_payload_key="metadata",
    )
def reset_qdrant_collection():
    collections = client.get_collections().collections
    if any(c.name == QDRANT_COLLECTION_NAME_LECTURES for c in collections):
        client.delete_collection(QDRANT_COLLECTION_NAME_LECTURES)
        print(f"Đã xoá collection: {QDRANT_COLLECTION_NAME_LECTURES}")

    client.create_collection(
        collection_name=QDRANT_COLLECTION_NAME_LECTURES,
        vectors_config=VectorParams(size=EMBEDDING_SIZE, distance=Distance.COSINE),
    )
    print(f"Đã khởi tạo lại collection: {QDRANT_COLLECTION_NAME_LECTURES}")












#---- Courses processing
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

def load_sql(): #-> list[dict]
    with connect_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM Courses")
            return cursor.fetchall()
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

def sync_courses_to_qdrant():
    cols = client.get_collections().collections
    if not any(c.name == QDRANT_COLLECTION_NAME for c in cols):
        client.create_collection(
            collection_name=QDRANT_COLLECTION_NAME,
            vectors_config=VectorParams(size=EMBEDDING_SIZE, distance=Distance.COSINE),
        )

    # 2) Load data from MySQL
    db_courses = load_sql()
    db_map = {c["CourseID"]: c for c in db_courses}
    db_ids = set(db_map.keys())

    # 3) Load data from Qdrant
    qdrant_ids, qdrant_hash_map = get_existing_qdrant_data()

    # 4) detemine new / removed / updated
    new_ids     = db_ids - qdrant_ids
    removed_ids = qdrant_ids - db_ids
    updated_ids = {
        cid
        for cid in db_ids & qdrant_ids
        if hash_course(db_map[cid]) != qdrant_hash_map.get(cid, "")
    }

    # 5) Upsert & update
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
        print(f"Added/Updated: {len(docs)} documents.")

    # 6) Delete Unavailable courses
    if removed_ids:
        client.delete(
            collection_name=QDRANT_COLLECTION_NAME,
            points_selector=PointIdsList(points=list(removed_ids)),
        )
        print(f"🗑 Removed: {len(removed_ids)} documents.")

    print(
        f"Sync completed. "
        f"New: {len(new_ids)}, "
        f"Updated: {len(updated_ids)}, "
        f"Removed: {len(removed_ids)}"
    )
    collection_info = client.get_collection(QDRANT_COLLECTION_NAME)
    total_points = collection_info.points_count
    print(f"Number of vector in Vectordb: {total_points}")

def get_vectorstore() -> Qdrant:
    return Qdrant(
        client=client,
        collection_name=QDRANT_COLLECTION_NAME,
        embeddings=embedding_model,
        content_payload_key="page_content",
        metadata_payload_key="metadata",
    )


def reset_qdrant_collection():
    collections = client.get_collections().collections
    if any(c.name == QDRANT_COLLECTION_NAME for c in collections):
        client.delete_collection(QDRANT_COLLECTION_NAME)
        print(f"Đã xoá collection: {QDRANT_COLLECTION_NAME}")

    client.create_collection(
        collection_name=QDRANT_COLLECTION_NAME,
        vectors_config=VectorParams(size=EMBEDDING_SIZE, distance=Distance.COSINE),
    )
    print(f"Đã khởi tạo lại collection: {QDRANT_COLLECTION_NAME}")
