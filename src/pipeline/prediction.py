from src.logger import logging
from src.exception import CustomException
from src.multi_modal.chunking import get_chunks
from src.multi_modal.SeperationAndSummarization import summarize_chunks



class PredictionPipeline:
    def __init__(self,filepath):
        self.filepath = filepath

    def process(self):
        chunks = get_chunks(self.filepath)
        sum_chunks=summarize_chunks(chunks)
        



    
    
    

