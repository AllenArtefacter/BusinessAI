import os

from langchain.agents import Tool
from langchain.agents import AgentType
from langchain.memory import ConversationBufferMemory
from langchain import OpenAI
from langchain.utilities import SerpAPIWrapper
from langchain.agents import initialize_agent

# Import necessary libraries
from dotenv import load_dotenv
import pytest
import openai
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import (
    PromptTemplate
)
from langchain.embeddings import OpenAIEmbeddings
from openai.error import InvalidRequestError


def setup():
    load_dotenv(dotenv_path='../azure.credentials.env')

    openai.api_key = os.getenv("OPENAI_API_KEY")
    openai.api_base = os.getenv("OPENAI_API_BASE")  # your endpoint like https://YOUR_RESOURCE_NAME.openai.azure.com/
    openai.api_type = 'azure'
    openai.api_version = '2023-05-15'  # this may change in the future


def test_chain():
    setup()
    chat = ChatOpenAI(
        temperature=0,
        engine="gpt-35-turbo-deployment",
    )
    prompt_template = "Tell me a {adjective} joke"
    llm_chain = LLMChain(
        llm=chat,
        prompt=PromptTemplate.from_template(prompt_template)
    )

    res = llm_chain(inputs={"adjective": "corny"})
    print(res)

    assert res['text'] == "Why did the tomato turn red? Because it saw the salad dressing!"


def test_seq_chain():
    from langchain.chains import SequentialChain
    from langchain.memory import SimpleMemory
    setup()

    # This is an LLMChain to write a synopsis given a title of a play.
    llm = OpenAI(temperature=0,
                 engine="gpt-35-turbo-deployment",
                 max_tokens=20,
                 )
    template = """You are a playwright. Given the title of play, it is your job to write a synopsis for that title.

    Title: {title}
    Playwright: This is a synopsis for the above play:"""
    prompt_template = PromptTemplate(input_variables=["title"], template=template)
    synopsis_chain = LLMChain(llm=llm, prompt=prompt_template)

    template = """You are a play critic from the New York Times. Given the synopsis of play, it is your job to write a review for that play.

    Play Synopsis:
    {synopsis}
    Review from a New York Times play critic of the above play:"""
    prompt_template = PromptTemplate(input_variables=["synopsis"], template=template)
    review_chain = LLMChain(llm=llm, prompt=prompt_template)

    # This is the overall chain where we run these two chains in sequence.
    from langchain.chains import SimpleSequentialChain
    overall_chain = SimpleSequentialChain(chains=[synopsis_chain, review_chain], verbose=True)

    review = overall_chain.run("Tragedy at sunset on the beach")

    print(review)
    assert review == ' \n    The play is a beautiful and poignant portrayal of love and loss. The setting of the beach'


def test_embeddings():
    setup()

    embeddings = OpenAIEmbeddings(
        deployment="text-embedding-ada-002-deployment",
    )
    text = "This is a test document."
    try:
        query_result = embeddings.embed_query(text)
        doc_result = embeddings.embed_documents([text])
    except InvalidRequestError:
        assert False, "InvalidRequestError"

    assert doc_result[0][:4] == [-0.003158408751234257, 0.011094410212838683, -0.004001317166816524, -0.011747414500761146]


if __name__ == "__main__":
    test_chain()
    test_seq_chain()
    test_embeddings()
