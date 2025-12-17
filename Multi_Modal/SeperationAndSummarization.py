import json
from typing import List
from langchain_google_genai import ChatGoogleGenerativeAI,GoogleGenerativeAIEmbeddings
from langchain_core.messages import HumanMessage
from langchain_core.documents import Document
from dotenv import load_dotenv

load_dotenv()

def seperate_content_types(chunk):

    content_data ={
        "text": chunk.text,
        "tables":[],
        "images":[],
        "types":['text']
    }

    if hasattr(chunk ,"metadata") and hasattr(chunk.metadata, "orig_elements"):
        for element in chunk.metadata.orig_elements:

            element_type = type(element).__name__

            if element_type =="Table":
                content_data['types'].append('Table')
                table_html = getattr(element.metadata , 'text_as_html', element.text)
                content_data['tables'].append(table_html)

            elif element_type == "Image":
                if hasattr(element,"metadata") and hasattr(element.metadata ,"image_base64"):
                    content_data['types'].append("Image")
                    content_data['images'].append(element.metadata.image_base64)
    
    content_data['types'] = list(set(content_data['types']))
    return content_data
                

def create_ai_enhanced_summary(text: str, tables: List[str], images: List[str]) -> str:
    try:
        model = ChatGoogleGenerativeAI(model='gemini-2.5-pro', temperature=0.3)

        prompt_text = f"""
        You are an AI assistant creating a searchable description for document retrieval.

        --- CONTENT TO ANALYZE ---
        
        TEXT CONTENT:
        {text}
        """

        if tables:
            prompt_text += "\nTABLES:\n"
            for i, table_obj in enumerate(tables):
                prompt_text += f"Table {i+1}:\n{table_obj}\n\n"

        prompt_text += """ 
                --- YOUR TASK ---
                Generate a comprehensive, searchable description of the content above. 
                Focus on creating metadata that will help a search engine find this document.
                
                Cover these 5 points:
                1. Key facts, exact numbers, and data points (from text and tables)
                2. Main topics and concepts discussed
                3. Questions this content could answer (e.g., "What is the revenue for Q3?")
                4. Visual Content Analysis (describe charts, diagrams, and patterns in the attached images)
                5. Alternative keywords or synonyms users might search for.

                Prioritize findability over brevity.
                
                SEARCHABLE DESCRIPTION: 
                """

        message_content = [{'type': 'text', 'text': prompt_text}]

        for image_base64 in images:
            clean_base64 = image_base64.strip()
            
            message_content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{clean_base64}"}})

        message = HumanMessage(content=message_content)
        
        response = model.invoke([message])

        return response.content

    except Exception as e:
        print(f"AI Summarization Failed: {e}")
        return text
    

def summarize_chunks(chunks):

    print("...Processing Chunk ...")

    langchain_document=[]

    total_chunk = len(chunks)

    for i , chunk in enumerate(chunks):
        current_chunk = i+1
        print(f"Processed Chunk {current_chunk}/{total_chunk}")

        content_data =seperate_content_types(chunk)

        print(f'Types Found: ',content_data['types'])
        print(f"Tables: {len(content_data['tables'])} , Image: {len(content_data['images'])}")

        enhanced_cnt =""

        if content_data['tables'] or content_data['images']:
            print("Creating Summary...")
            try:
                enhanced_cnt = create_ai_enhanced_summary(content_data['text'],content_data['tables'],content_data['images'])

                if enhanced_cnt:
                    print("Successfully Summarized")
                    print(f"Preview:{enhanced_cnt[:100]}...")
                else:
                    enhanced_cnt = content_data['text']
            except Exception as e:
                print(f"AI Summary Failed: {e}")
                enhanced_cnt= content_data['text']

        else:
            print("No tables or Image Found")
            enhanced_cnt= content_data['text']

        doc = Document(
            page_content=enhanced_cnt,
            metadata={
                "original_content":json.dumps({
                    'raw_text':content_data['text'],
                    "table_html":content_data['tables'],
                    "image_base64":content_data['images']
                })
            }
        )

        langchain_document.append(doc)

    print(f"Processed {len(langchain_document)} chunks")
    return langchain_document


