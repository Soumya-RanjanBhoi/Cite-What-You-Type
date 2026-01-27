from src.multi_modal.chunking import get_chunks
from src.multi_modal.SeperationAndSummarization import summarize_chunks
from src.multi_modal.intialize_vstore import upload_file
from src.multi_modal.gen_final_ans import gen_ans
import os
import uuid


class Pipeline:
    def __init__(self):
        self.retriever = None
        self.bucket_name = os.environ.get("BUCKET_NAME_AWS")

    def process_pdf(self, filepath, user_id):
        chunks = get_chunks(filepath)
        print("Chunks created successfully")

        sum_chunks = summarize_chunks(chunks)
        print("Summarized chunks")

        self.retriever = upload_file(sum_chunks, user_id, self.bucket_name)
        print("Retriever initialized")

    def querying(self, query):
        if self.retriever is None:
            raise RuntimeError("Retriever not initialized. Call process_pdf first.")

        docs = self.retriever.get_relevant_documents(query)
        ans = gen_ans(docs, query)
        return ans


pp = Pipeline()
user_id = "user-" + uuid.uuid4().hex[1:12]
filename = "D:/Cite-What-You-Type/pdfs/Documentation-Project.pdf"

pp.process_pdf(filename, user_id)
ans = pp.querying("tell me about the project")
print(ans)
