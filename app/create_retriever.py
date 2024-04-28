import dotenv
import os
from langchain.document_loaders.csv_loader import CSVLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
import pandas as pd

ORGS_CSV_PATH = "../data/organization_data_updated.csv"
ORGS_CHROMA_PATH = "chroma_data"

dotenv.load_dotenv()

loader = CSVLoader(file_path=ORGS_CSV_PATH)
# loader = CSVLoader(file_path=ORGS_CSV_PATH, source_column="Purpose")
orgs = loader.load()

reviews_vector_db = Chroma.from_documents(
    orgs, OpenAIEmbeddings(), persist_directory=ORGS_CHROMA_PATH
)