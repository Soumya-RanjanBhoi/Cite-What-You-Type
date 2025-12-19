from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS,Chroma
from dotenv import load_dotenv
from pinecone import Pinecone,ServerlessSpec
from langchain_pinecone import PineconeVectorStore
import os


load_dotenv()



# def create_vector_store(documents,persist_directory="FAISS/pdfsVector"):

#     embedding_model= GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")

#     vectorstore= Chroma.from_documents(
#         documents=documents,
#         embedding=embedding_model,
#         persist_directory=persist_directory,
#         collection_metadata={'hnsw:space':"cosine"}
#     )

#     print('finished')
#     return vectorstore



def initializePinecone(index_name):
    try:
        # 1. Initialize official client for Admin/Index operations
        pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
        
        # Check if index exists
        existing_indexes = [index_info["name"] for index_info in pc.list_indexes()]
        print(existing_indexes)
        
        if index_name not in existing_indexes:
            print(f"Creating index: {index_name}")
            pc.create_index(
                name=index_name,
                dimension=512, # Must match your embedding model dimensions
                metric='cosine',
                spec=ServerlessSpec(cloud="gcp", region="us-central1") 
            )
        
        return index_name 
    except Exception as e:
        print("Could not connect to Pinecone:", e)
        raise

def create_vector_store(text_chunks, indexName):
    # 2. Setup Embeddings
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    
    # Ensure index exists
    index_name = initializePinecone(indexName)
    
    print("Pushing vectors to Pinecone...")
    
    # 3. Use LangChain's PineconeVectorStore for 'from_texts'
    # DO NOT use the 'Pinecone' class from the official client here
    vector_store = PineconeVectorStore.from_documents(
        documents=text_chunks,
        embedding=embeddings,
        index_name=index_name
    )
    
    print('Finished')
    return vector_store
