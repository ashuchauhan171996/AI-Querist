from langchain_openai import ChatOpenAI
import dotenv

dotenv.load_dotenv()

openai_model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0, max_tokens=40)

