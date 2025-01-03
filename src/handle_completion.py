import logging

from langchain.chains import SequentialChain
from langchain.schema import AIMessage, BaseMessage, HumanMessage, SystemMessage

from src.chat.ui.ai_message_ui import AIMessageUI
from src.chat.ui.fake_ai_message_ui import FakeAIMessageUI
from src.chat.ui.human_message_ui import HumanMessageUI
from src.chat.ui.system_message_ui import SystemMessageUI
from src.models.assistant import get_assistant
from src.tools.progress_bar import get_progress_bar_data
from src.tools.states import (
    EXECUTION,
    FINISH,
    GENERATING,
    IDLE,
    INIT,
    MODE,
    NEW_CONVERSATION,
    PARSING,
    REPLY,
    STATE,
)
from src.tools.utils import extract_python, exec_on_tables


def request_reply(conv, progress_bar, db_schema, s_state, tables_selected, masker):
    mode = s_state[MODE]
    if mode == NEW_CONVERSATION:
        model = s_state["model"]
    else:
        model = get_assistant(conv.chat.get_base_messages()[:-1])

    assert isinstance(
        model, SequentialChain
    ), f"Model is not a SequentialChain. {type(model)=}"

    if s_state[STATE] in [INIT]:
        model_handler(conv, db_schema, mode, model, progress_bar, s_state, masker)
        # model_handler_fake(conv, db_schema, mode, model, progress_bar, s_state, masker)
    if s_state[STATE] in [PARSING]:
        progress_bar.progress(*get_progress_bar_data(s_state, s_state[STATE]))
        code = extract_python(s_state["completion_result"])
        s_state["code"] = code
        s_state[STATE] = EXECUTION

    if s_state[STATE] in [EXECUTION]:
        progress_bar.progress(*get_progress_bar_data(s_state, s_state[STATE]))
        code = s_state["code"]
        saved_dataframe, saved_figure, error = None, None, None
        try:
            print(f"tables selected {tables_selected.keys()}")
            if code is not None:
                saved_dataframe, saved_figure = exec_on_tables(code, tables_selected)
        except Exception as e:
            error = str(e)
            logging.error(e)
        s_state["results"] = (saved_dataframe, saved_figure, error)
        s_state[STATE] = FINISH

    if s_state[STATE] in [FINISH]:
        saved_dataframe, saved_figure, error = s_state["results"]
        progress_bar.progress(*get_progress_bar_data(s_state, s_state[STATE]))
        s_state[STATE] = IDLE
        conv.chat.add_message(  # Add final result
            AIMessageUI.from_content(
                content=s_state["completion_result"],
                result_dataframe=saved_dataframe,
                result_figure=saved_figure,
                result_error=error,
            )
        )  # Will rerun the app


def unmask(result, masker):
    return masker.unmask_str(result)


INCOMPLETE_REPLY_MOCK = """Indeed your question is cool. Here is your code:
Indeed your question is cool. Here is your code:
Indeed your question is cool. Here is your code:
Indeed your question is cool. Here is your code:
Indeed your question is cool. Here is your code:
Indeed your question is cool. Here is your code:
Indeed your question is cool. Here is your code:
"""
COMPLETE_REPLY_MOCK = """Indeed your question is cool. Here is your code:
```python
import pandas as pd
import matplotlib.pyplot as plt
import altair as alt

df = inventory_df # Cols: Month, Distributor, ProductID, Inventory_Qty
saved_dataframe = df
saved_figure = alt.Chart(df).mark_point().encode(
    x='Month',
    y='Inventory_Qty',
    color='ProductID',
    tooltip=['ProductID', 'Inventory_Qty']
).interactive()    
```"""
QUESTION_REPLY_MOCK = (
    """Indeed your question is cool. but I am not sure QUESTION: What do you mean?"""
)
ERROR_REPLY_MOCK = """Indeed your question is cool. Here is your code:
```python
import pandas as pd

I am a syntax error
df = pd.read_csv("https://raw.githubusercontent.com/mwaskom/seaborn-data/master/iris.csv")
saved_dataframe = df
```"""


def model_handler_fake(conv, db_schema, mode, model, progress_bar, s_state, masker):
    s_state[STATE] = GENERATING
    progress_bar.progress(*get_progress_bar_data(s_state, s_state[STATE]))
    # completion = model(
    #     {"request": conv.chat.last_human_message.user_input, "db_schema": db_schema}
    # )

    all_messages: list[BaseMessage] = [
        SystemMessage(content=db_schema),
        AIMessage(content="""I am a very good mock ai"""),
        HumanMessage(
            content=f"""request: '''{conv.chat.last_human_message.user_input}'''"""
        ),
    ]
    if mode == REPLY:
        all_messages = all_messages[-1:]  # Do not input the fake ai and system
        all_messages[0].additional_kwargs["user_input"] = conv.chat.last_message.content
    else:
        for message in all_messages:
            if message.type == "human":
                message.additional_kwargs["user_input"] = conv.chat.last_message.content

    # Remove last message from user as this message is to be replaced with the prompted one
    conv.chat.delete_message(conv.chat.last_message, silent=True)
    # Do not add the last one as the python code execution did not occur
    conv.chat.add_base_messages(all_messages, silent=True)
    s_state["completion_result"] = INCOMPLETE_REPLY_MOCK

    if len(conv.chat) > 7:
        s_state["completion_result"] = COMPLETE_REPLY_MOCK

    s_state[STATE] = PARSING


def model_handler(conv, db_schema, mode, model, progress_bar, s_state, masker):
    s_state[STATE] = GENERATING
    progress_bar.progress(*get_progress_bar_data(s_state, s_state[STATE]))
    completion = model(
        {"request": conv.chat.last_human_message.user_input, "db_schema": db_schema}
    )
    all_messages: list[BaseMessage] = [
        m
        for chain in model.chains
        for m in chain.prompt.format_prompt(**chain.prep_inputs(completion)).messages
    ]
    if mode == REPLY:
        all_messages = all_messages[-1:]
        all_messages[0].additional_kwargs["user_input"] = conv.chat.last_message.content
    else:
        all_messages[2].additional_kwargs[
            "user_input"
        ] = conv.chat.last_message.content  # FIXME not clear
    # Remove last message from user as this message is to be replaced with the prompted one
    conv.chat.delete_message(conv.chat.last_message, silent=True)
    # Do not add the last one as the python code execution did not occur
    conv.chat.add_base_messages(all_messages, silent=True)
    s_state["completion_result"] = completion["python_code_final"]
    s_state[STATE] = PARSING
