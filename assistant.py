from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

llm = ChatOpenAI(
    model="gpt-5.2"
)

if __name__ == "__main__":
    response = llm.invoke("Привет, ты на связи?")
    print(response.content)