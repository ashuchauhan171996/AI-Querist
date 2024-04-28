import dotenv
from openai_model import openai_model
from prompt_template import org_prompt_template

from langchain_core.output_parsers import StrOutputParser
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.schema.runnable import RunnablePassthrough

ORGS_CHROMA_PATH = "chroma_data/"
dotenv.load_dotenv()

orgs_vector_db = Chroma(
    persist_directory=ORGS_CHROMA_PATH,
    embedding_function=OpenAIEmbeddings()
)

orgs_retriever  = orgs_vector_db.as_retriever(k=2)

org_chain = (
    {"context": orgs_retriever, "question": RunnablePassthrough()}
    | org_prompt_template
    | openai_model
    | StrOutputParser()
)