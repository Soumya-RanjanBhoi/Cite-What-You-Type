from unstructured.partition.pdf import partition_pdf
from  unstructured.chunking.title import chunk_by_title


def extract_pdf_elements(filepath) -> list:
        elements = partition_pdf(
            filename=filepath,
            strategy="hi_res",
            infer_table_structure=True,
            extract_image_block_types=['Image'],
            extract_image_block_to_payload=True,
        )
        print("Total elements extracted -> ",len(elements))
        return elements
    

    
def create_chunks_by_title(elements):
        chunks = chunk_by_title(
            elements,
            max_characters=1500,
            combine_text_under_n_chars=200
        )

        print("Chunks created: ", len(chunks))
        return chunks

def get_chunks(filepath:str):
    elements = extract_pdf_elements(filepath)
    chunk = create_chunks_by_title(elements)

    return chunk
        