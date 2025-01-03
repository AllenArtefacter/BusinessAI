from langchain.chat_models import ChatOpenAI

llm_chat_gpt4 = ChatOpenAI(
    temperature=0,
    model_name="gpt-4",
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0,
    request_timeout=120,
)

llm_chat_gpt3 = ChatOpenAI(
    temperature=0,
    model_name="gpt-3.5-turbo",
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0,
    request_timeout=120,
)
