import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage


def gen_final_ans(chunks, query):
    try:
        llm = ChatGoogleGenerativeAI(model='gemini-2.5-pro', temperature=0.1)

        prompt_text = f"""
        Based on the following document context, please answer this question: {query}
        
        CONTENT_TO_ANALYZE:
        """
        all_images_base64 = []
        for i, chunk in enumerate(chunks):
            prompt_text += f"\n--- Document Fragment {i+1} ---\n"
            
            if hasattr(chunk, "metadata") and "original_content" in chunk.metadata:
                try:
                    original_data = json.loads(chunk.metadata['original_content'])
                    
                    raw_text = original_data.get("raw_text", "")
                    if raw_text:
                        prompt_text += f"Text:\n{raw_text}\n\n"

                    tables_html = original_data.get("tables_html", [])
                    if tables_html:
                        prompt_text += 'TABLES:\n'
                        for j, table in enumerate(tables_html):
                            prompt_text += f"Table {j+1}:\n{table}\n\n"
                    
                    
                    imgs = original_data.get("images_base64", [])
                    if imgs:
                        all_images_base64.extend(imgs)

                except json.JSONDecodeError:
                    prompt_text += f"Text:\n{chunk.page_content}\n\n"
            else:
                prompt_text += f"Text:\n{chunk.page_content}\n\n"

        prompt_text += """ 
        INSTRUCTIONS:
        Provide a clear, comprehensive answer using the text, tables, and images provided above. 
        If the documents don't contain sufficient information to answer the question, state: "I don't have enough information to answer the question."
        
        ANSWER:"""
    
        message_content = [{'type': 'text', 'text': prompt_text}]

        for img_b64 in all_images_base64:
            message_content.append({"type": "image_url","image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}})

        message = HumanMessage(content=message_content)
        response = llm.invoke([message])

        return response.content
        
    except Exception as e:
        print(f"Answer gen failed: {e}")
        return 'Sorry, I encountered an error generating the answer.'