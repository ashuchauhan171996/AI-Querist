import dotenv
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

ORGS_CHROMA_PATH = "chroma_data/"

dotenv.load_dotenv()


orgs_vector_db = Chroma(
    persist_directory=ORGS_CHROMA_PATH,
    embedding_function=OpenAIEmbeddings(),
)

question = """I am interested in organization that would expose me to indian culture."""
relevant_docs = orgs_vector_db.similarity_search(question, k=3)

print(type(relevant_docs[0].page_content + relevant_docs[1].page_content))
# print(relevant_docs[1].page_content)
# print(relevant_docs[2].page_content)