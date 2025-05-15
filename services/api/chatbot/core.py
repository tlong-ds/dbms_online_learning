from .llm import gemini_llm
# from .retrieval import load_vectordb
# from .prompts import chat_prompt_no_memory, chat_prompt_memory, classification_prompt, category_tree_json
# from langchain.chains import RetrievalQA
# from langchain.retrievers.self_query.base import SelfQueryRetriever
# from langchain.retrievers.self_query.qdrant import QdrantTranslator



def get_chat_response(user_input: str) -> str:
    response = gemini_llm.invoke(user_input)
    return response
