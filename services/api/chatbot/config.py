import google.generativeai as genai
from langchain.llms.base import LLM
from typing import List, Optional
from dotenv import load_dotenv
import os

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
QDRANT_HOST = os.getenv("QDRANT_HOST")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

QDRANT_COLLECTION_NAME = "dbms_collection_courses"
QDRANT_COLLECTION_NAME_LECTURES = "dbms_collection_lectures"
MODEL_NAME = "gemini-2.0-flash"

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_SIZE = 384