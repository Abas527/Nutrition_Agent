from langchain_ollama import ChatOllama


def get_llm(query:str):
    llm = ChatOllama(model="qwen2.5:7b ")
    response = llm.invoke(query)
    return response.content
