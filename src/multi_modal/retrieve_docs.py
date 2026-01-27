from typing import List
import boto3,json,os
from langchain_classic.schema import Document
from dotenv import load_dotenv

def retreive_document(docs) ->List[Document]:
    load_dotenv()

    BUCKET_NAME=os.environ.get("BUCKET_NAME_AWS","")
    if not BUCKET_NAME:
        print("could not find Bucket name")
        raise
    
    retreived_documents=[]
    try:

        s3=boto3.client("s3")
        print("aws logined")


        for dox in docs:
            if hasattr(dox,"metadata") and "s3_uri" in dox.metadata:
                _,uri = dox.metadata['s3_uri'].split("//")
                _,user_id,doc_id=uri.split('/')

            
                obj=s3.get_object(
                    Bucket=BUCKET_NAME,
                    Key=f"{user_id}/{doc_id}"
                )
            try:
                data = json.loads(obj["Body"].read().decode("utf-8"))
            except json.JSONDecodeError as e:
                print("Could not load file in json format")
                raise e
            d=Document(
                page_content=data['raw_text'],
                metadata={
                    "table_as_html":data['table_as_html'],
                    "image_base64":data['image_base64']
                }
            )

            retreived_documents.append(d)

        
        return retreived_documents
    
    except Exception as e:
        print("failed due to ",e)
        raise 