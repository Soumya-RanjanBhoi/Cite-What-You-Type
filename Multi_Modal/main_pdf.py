from Multi_Modal.ans_generation import gen_final_ans
from Multi_Modal.chunking import get_chunks
from Multi_Modal.SeperationAndSummarization import summarize_chunks
from Multi_Modal.vectorstore import create_vector_store
from langchain_core.runnables import RunnableParallel,RunnablePassthrough,RunnableLambda
import time




def get_ans(filepath, query:str,vector_dir="Vector Stores"):


    try:
        print("Chunking Started")
        chunks = get_chunks(filepath)
        print("Chunking Completed")

        print("Seperation and Summarization Process Started")
        processed_chunk = summarize_chunks(chunks)
        print("Seperation and Summarization Process Completed")

        print("Creating Vector Store")
        db= create_vector_store(processed_chunk,persist_directory=vector_dir)
        print("Vector Store Completed")

        print("Retreving & Answer Generation")
        retriver = db.as_retriever(search_kwargs={"k":10})

        parallel_chain = RunnableParallel({ "query":RunnablePassthrough(),"context": retriver })

        chain = parallel_chain | RunnableLambda(lambda inputs: gen_final_ans(inputs['context'], inputs['query']))

        final_answer = chain.invoke(query)


        return final_answer
    
    except Exception as e:
        print(f"Process Failed,Error-{e}")

    
# filepath= "D:/Cite-What-You-Type/pdfs/22-25 Clustering, K-means, DBSCAN.pdf"
# query="what are the steps for DBSCAN Clustering And When should we use DBSCAN over KMeans"

# start=time.time()
# ans = get_ans(filepath,query)
# print("Ans:",ans)
# print("Completed Whole process in :",time.time()-start)




