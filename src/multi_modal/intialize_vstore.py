from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS,Chroma
from dotenv import load_dotenv
from pinecone import Pinecone,ServerlessSpec
from pinecone_text.sparse import BM25Encoder
from langchain_pinecone import PineconeVectorStore
import os


load_dotenv()

def intiliaze_vectorstore(user_id):
    
