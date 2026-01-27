import base64
from src.Models.model import ApnaChatModel

def gen_ans(docs, query):
    try:
        llm = ApnaChatModel()

        prompt_text = f"""
            Based on the following document context, answer the question.

            QUESTION:
            {query}

            CONTENT:
            """

        all_images = []

        for i, chunk in enumerate(docs):
            prompt_text += f"\n--- Document Fragment {i+1} ---\n"

            if not hasattr(chunk, "page_content"):
                continue

            prompt_text += f"TEXT:\n{chunk.page_content}\n"

            metadata = getattr(chunk, "metadata", {})

            tables = metadata.get("table_as_html", {})
            if isinstance(tables, dict):
                tables = tables.values()

            if tables:
                prompt_text += "\nTABLES:\n"
                for j, table in enumerate(tables):
                    prompt_text += f"Table {j+1}:\n{table}\n\n"

            imgs = metadata.get("image_base64", [])
            if isinstance(imgs, str):
                imgs = [imgs]

            for img in imgs:
                decoded = base64.b64decode(img)
                all_images.append(decoded)

        prompt_text += """
INSTRUCTIONS:
- Use ONLY the provided content
- If insufficient info, say: "I don't have enough information to answer the question."
- Be concise and factual

ANSWER:
"""

        content_block = [{
            "text": prompt_text
        }]

        for img_bytes in all_images:
            content_block.append({
                "image": {
                    "format": "jpeg",
                    "source": {
                        "bytes": img_bytes
                    }
                }
            })

        message = [{
            "role": "user",
            "content": content_block
        }]

        return llm.invoke(message)

    except Exception as e:
        print(f"Answer gen failed: {e}")
        raise RuntimeError("Sorry, I encountered an error generating the answer.")
