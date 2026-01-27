import boto3,json
from langchain_classic.schema import Document
from pinecone import Pinecone


class ApnaChatModel:
    def __init__(self, region="us-east-1"):
        self.client = boto3.client(
            "bedrock-runtime",
            region_name=region
        )
        self.model_id = "amazon.nova-pro-v1:0"

    def invoke(self, messages, max_tokens=500):
        response = self.client.invoke_model(
            modelId=self.model_id,
            contentType="application/json",
            accept="application/json",
            body=json.dumps({
                "messages": messages,
                "inferenceConfig": {
                    "max_new_tokens": max_tokens
                }
            })
        )

        result = json.loads(response["body"].read())
        return result["output"]["message"]["content"][0]["text"]

class TitanEmbeddings:
    accept = "application/json"
    content_type = "application/json"
    
    def __init__(self, model_id="amazon.titan-embed-text-v2:0"):
        self.bedrock = boto3.client(service_name='bedrock-runtime')
        self.model_id = model_id
        self.dimensions=1024
        self.normalize=True

    
    def invoke(self, text):
        body = json.dumps({
            "inputText": text,
            "dimensions": self.dimensions,
            "normalize": self.normalize
        })
        response = self.bedrock.invoke_model(
            body=body, modelId=self.model_id, accept=self.accept, contentType=self.content_type
        )
        response_body = json.loads(response.get('body').read())
        return response_body['embedding']
    

class CustomHybridRetriever:
    def __init__(self, user_id, emb_model, bm25, k=5, alpha=0.7):
        self.user_id = user_id
        self.emb_model = emb_model
        self.bm25 = bm25
        self.k = k
        self.alpha = alpha
        pc1=Pinecone()
        self.index_obj=pc1.Index(self.user_id)

    def get_relevant_documents(self, query):
        dense = self.emb_model.invoke(query)
        sparse = self.bm25.encode_queries(query)

        dense = [v * self.alpha for v in dense]
        sparse["values"] = [v * (1 - self.alpha) for v in sparse["values"]]

        res = self.index_obj.query(
            vector=dense,
            sparse_vector=sparse,
            top_k=self.k,
            include_metadata=True
        )

        seen_ids = set()
        docs = []

        for m in res["matches"]:
            doc_id = m["id"]  

            if doc_id in seen_ids:
                continue

            seen_ids.add(doc_id)

            docs.append(
                Document(
                    page_content=m["metadata"]["text"],
                    metadata={
                        **m["metadata"],
                        "id": doc_id
                    }
                )
            )

        return docs

