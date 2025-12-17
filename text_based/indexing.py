import pandas as pd
from io import StringIO
from pydantic import BaseModel,Field
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

text = open("pdfs/trail.txt").read()

class TableRow(BaseModel):
    col1_name: str = Field(description="Description of column 1")
    value: float = Field(description="Value in column 2")

class ExtractedTable(BaseModel):
    rows: list[TableRow]


llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro")
structured_llm = llm.with_structured_output(ExtractedTable)

result = structured_llm.invoke(f"Extract the data from this text: {text}")
print(result)



