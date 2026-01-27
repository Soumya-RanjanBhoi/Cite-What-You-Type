import json,boto3,uuid
from langchain_classic.schema import Document
from typing import List
from dotenv import load_dotenv
from src.Models.model import TitanEmbeddings,CustomHybridRetriever
from pinecone import Pinecone,ServerlessSpec
from pinecone_text.sparse import BM25Encoder
import os


load_dotenv()

def upload_file(document:List[Document],user_id,bucket_name):
    batch_size=2
    try:
        obj= boto3.client("s3")
        print("logined s3")

    except Exception as e :
        print("logined failed")
        raise e
    
    valid_texts = []
    valid_docs_original = []

    for doc in document:
        try:
            content = ""
            if hasattr(doc, "page_content") and doc.page_content:
                content = doc.page_content
            elif hasattr(doc, "metadata") and "original_content" in doc.metadata:
                content = doc.metadata['original_content']
            
            if content:
                valid_texts.append(content)
                valid_docs_original.append(doc)
            else:
                print(f"Skipping document with no content: {doc.metadata.get('source', 'unknown')}")
                
        except Exception as e:
            print(f"Error extracting text from doc: {e}")

    print(f"Extracted {len(valid_texts)} valid texts")

    if not valid_texts:
        raise ValueError("No valid texts extracted from documents.")
    
    embbed_model=TitanEmbeddings()
    try:
        sample_vec = embbed_model.invoke(valid_texts[0])
        dim = len(sample_vec)
        print("Created Dense Vectors, Dimension of each vector is: ", dim)
    except Exception as e:
        raise ValueError(f"Failed to generate valid embedding: {e}")

    
    bm25 = BM25Encoder.default()
    bm25.fit(valid_texts)

    print("Initializing Pinecone...")
    pc = Pinecone(api_key=os.environ.get('PINECONE_API_KEY'))
    existing_indexes = [i["name"] for i in pc.list_indexes()]
    print(user_id)
    if user_id not in existing_indexes:
        print(f"Creating new Pinecone index: {user_id}")
        pc.create_index(
            name=user_id,
            dimension=dim,
            metric="dotproduct",
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )
    else:
        print(f"Using existing Pinecone index: {user_id}")

    print("Created/Logined to Pinecone Successfully")
    index=pc.Index(user_id)
    vectors_to_upsert=[]
    for i, doc in enumerate(valid_docs_original):
        doc_id = uuid.uuid4().hex[:15]
        try:

            metadata_dict = doc.metadata if isinstance(doc.metadata, dict) else {}
            orig_cnt = json.loads(metadata_dict['original_content'])
            
            bucket_content = {
                "id": doc_id,
                "raw_text": orig_cnt.get('raw_text', ""),
                "summ_text": valid_texts[i],
                'table_as_html':orig_cnt.get('table_as_html', {}),
                'image_base64':orig_cnt.get('image_base64', {})
            }

            obj.put_object(
            Bucket=bucket_name,
            Key=f"{user_id}/{doc_id}.json",
            Body=json.dumps(bucket_content),
            ContentType="application/json"
        )


            dense_vector = embbed_model.invoke(valid_texts[i])
            sparse_vector = bm25.encode_documents(valid_texts[i])
            
            vector = {
                "id": doc_id,
                "values": dense_vector,
                "sparse_values": sparse_vector,
                "metadata": {
                    "text": valid_texts[i], 
                    "s3_uri": f"s3//{bucket_name}/{user_id}/{doc_id}.json"
    
                }
            }
            vectors_to_upsert.append(vector)

    
            if len(vectors_to_upsert) >= batch_size:
                index.upsert(vectors=vectors_to_upsert)
                vectors_to_upsert = []
                print(f"Upserted batch ending at {i}")

        except Exception as e:
            print(f"Error processing doc {i}: {e}")

            continue

    retriever =CustomHybridRetriever(
        user_id=user_id,
        emb_model=embbed_model,
        bm25=bm25
    )
    
    return retriever
