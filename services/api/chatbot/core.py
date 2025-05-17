from .llm import gemini_llm
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from .retrieval import get_vectorstore, sync_courses_to_qdrant
from langchain.chains import RetrievalQA
from .prompts import courses_prompt, condense_prompt
# from langchain.retrievers.self_query.base import SelfQueryRetriever
# from langchain.retrievers.self_query.qdrant import QdrantTranslator

vector_store = get_vectorstore()

memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True,
    output_key="answer"
)

qa_chain = ConversationalRetrievalChain.from_llm(
    llm=gemini_llm,
    retriever=vector_store.as_retriever(search_kwargs={"k": 5}),
    memory=memory,
    condense_question_prompt=condense_prompt,  
    combine_docs_chain_kwargs={
        "prompt": courses_prompt  
    },
    return_source_documents=True
)



def get_chat_response(user_input: str) -> str:
    response = qa_chain({"question": user_input})
    print("Source Documents:")
    for i, doc in enumerate(response["source_documents"], start=1):
        cid = doc.metadata.get("CourseID", "N/A")
        content = doc.page_content
        print(f"{i}. CourseID={cid}\n   {content}\n")
    return response["answer"]
