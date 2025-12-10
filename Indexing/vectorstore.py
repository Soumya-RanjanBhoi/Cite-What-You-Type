from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS,Chroma
from dotenv import load_dotenv


load_dotenv()



def create_vector_store(documents,persist_directory="FAISS/pdfsVector"):

    embedding_model= GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")

    vectorstore= Chroma.from_documents(
        documents=documents,
        embedding=embedding_model,
        persist_directory=persist_directory,
        collection_metadata={'hnsw:space':"cosine"}
    )

    print('finished')
    return vectorstore