import json
from langchain_core.documents import Document
from dotenv import load_dotenv
from src.Models.model import ApnaChatModel

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

def create_ai_enhanced_summary(text: str,tables: list,images: list) -> str:

    model=ApnaChatModel()

    prompt = f"""
        You are an AI assistant creating a searchable description for document retrieval.

        --- TEXT CONTENT ---
        {text}
        """

    if tables:
        prompt += "\n--- TABLES ---\n"
        for i, table in enumerate(tables):
            prompt += f"Table {i+1}:\n{table}\n\n"

    prompt += """
        --- YOUR TASK ---
        Generate a comprehensive, searchable description.

        Cover:
        1. Key facts, exact numbers, and metrics
        2. Main topics and concepts
        3. Questions this content can answer
        4. Visual insights from images (charts, diagrams, patterns)
        5. Alternative keywords and synonyms

        Prioritize searchability over brevity.
        """

    content_blocks = []

    for img_b64 in images:
        content_blocks.append({
            "image": {
                "format": "jpeg",
                "source": {
                    "bytes": img_b64.strip()
                }
            }
        })

    content_blocks.append({
        "text": prompt
    })

    messages = [
        {
            "role": "user",
            "content": content_blocks
        }
    ]

    return model.invoke(messages)

def summarize_chunks(chunks):

    print("...Processing Chunks...")
    langchain_document = []

    total_chunk = len(chunks)

    for i, chunk in enumerate(chunks):
        current_chunk = i+1
        print(f"Processed Chunk {current_chunk}/{total_chunk}")

        content_data = seperate_content_types(chunk)

        print(f"Types Found: {content_data['types']}")
        print(f"Tables: {len(content_data['tables'])}, Images: {len(content_data['images'])}")

        enhanced_cnt = ""

        if content_data['tables'] or content_data['images']:
            print("Creating AI Summary...")
            try:
                enhanced_cnt = create_ai_enhanced_summary(
                    text=content_data['text'],
                    tables=content_data['tables'],
                    images=content_data['images'],
                )
                print("Summary created")
            except Exception as e:
                print(f"Summary failed: {e}")
                enhanced_cnt = content_data['text']
        else:
            print("No tables or Image Found")
            enhanced_cnt = content_data['text']

        doc = Document(
            page_content=enhanced_cnt,
            metadata={
                "original_content": json.dumps({
                    "raw_text": content_data['text'],
                    "table_html": content_data['tables'],
                    "image_base64": content_data['images']
                })
            }
        )

        langchain_document.append(doc)

    print(f"Processed {len(langchain_document)} chunks")
    return langchain_document