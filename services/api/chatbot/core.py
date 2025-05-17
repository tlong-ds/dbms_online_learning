from .llm import gemini_llm
from .retrieval import get_vectorstore, sync_courses_to_qdrant
from langchain.chains import RetrievalQA
from .prompts import courses_prompt
# from langchain.retrievers.self_query.base import SelfQueryRetriever
# from langchain.retrievers.self_query.qdrant import QdrantTranslator

vector_store = get_vectorstore()

qa_chain = RetrievalQA.from_chain_type(
    llm=gemini_llm,
    retriever=vector_store.as_retriever(search_kwargs={"k": 5}),
    return_source_documents=True,
    chain_type_kwargs={
        "prompt": courses_prompt, 
    },
    output_key="result"
)




def get_chat_response(user_input: str) -> str:
    response = qa_chain({"query": user_input})
    print("Source Documents:")
    for i, doc in enumerate(response["source_documents"], start=1):
        cid = doc.metadata.get("CourseID", "N/A")
        content = doc.page_content
        print(f"{i}. CourseID={cid}\n   {content}\n")
    return response["result"]
