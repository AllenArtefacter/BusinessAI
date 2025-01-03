import logging
import time

import streamlit as st

from src.auth import login
from src.chat.ui.ai_message_ui import AIMessageState
from src.chat.ui.conversation_ui import ConversationUI
from src.chat.ui.human_message_ui import HumanMessageUI
from src.config import MAIN_MODEL, get_pre_written_prompts, models
from src.database.datasource_manager import DatasourceManager, system_name_to_human_name
from src.database.factory_data_loader import DataLoaderFactory
from src.database.mask.dataset_masker import DataFilter, DataMasker
from src.handle_completion import request_reply
from src.prompt_engineering import USER_KEYWORDS
from src.tools.prompting import db_schema_generation, rules
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
from src.tools.ui_utils import display_chat

st.set_page_config(
    page_title="AI for BI",
    layout="wide",
    # page_icon="./res/client_logo.png",
    initial_sidebar_state="auto",
)
u_session_state = st.session_state  # to make sure the reference is the same everywhere

logging.info("Running app.py")

if "logo_" not in u_session_state:
    # u_session_state["logo_"] = None
    u_session_state["logo_"] = "res/artefact_logo.png"

params = st.experimental_get_query_params()
password = params.get("password", None)
if password is not None:
    password = password[0]
login(u_session_state, password)
# http://localhost:8501/AI_for_BI?password=artefactai


if MODE not in u_session_state:
    u_session_state[MODE] = NEW_CONVERSATION

if "model_name" not in u_session_state:
    u_session_state["model_name"] = MAIN_MODEL

if "tiktok_access" not in u_session_state:
    u_session_state["tiktok_access"] = False

# Model is saved to keep model.response alive between pages reload while generating
if "model" not in u_session_state:
    u_session_state["model"] = models[u_session_state["model_name"]]

if STATE not in u_session_state:
    u_session_state[STATE] = IDLE

if "error" in u_session_state:
    st.error(u_session_state["error"][0])
    u_session_state["error"][1] -= 1
    if u_session_state["error"][1] == 0:
        del u_session_state["error"]

# Load chat from session state
conv = ConversationUI.from_session_state(u_session_state)

# If rerun of the app during execution, the state becomes unstable, so we reset it
if u_session_state[STATE] in [GENERATING, PARSING, EXECUTION]:
    u_session_state[STATE] = IDLE
    logging.info("Resetting state to IDLE")
    conv.delete_chat(conv.chat)  # Will rerun the app


def chat_is_ready():
    return u_session_state[STATE] == IDLE and len(conv.chat)


def new_human_message_received():
    return conv.chat.last_message_is_from_human()


def new_incomplete_ai_message_received():
    return (
        conv.chat.last_message_is_from_ai()
        and conv.chat.last_message.state == AIMessageState.INCOMPLETE
    )


if chat_is_ready() and new_human_message_received():
    u_session_state[STATE] = INIT
    u_session_state[MODE] = u_session_state[MODE]  # Defined in previous run
elif chat_is_ready() and new_incomplete_ai_message_received():
    u_session_state[MODE] = REPLY
    conv.chat.add_message(
        HumanMessageUI.from_content(
            content="Continue writing the code", user_input="Continue writing the code"
        )
    )  # Rerun the app and trigger the code of the first if

path_to_data_folder = "./res/data"
data_sources_manager = DatasourceManager(path_to_data_folder)
if not u_session_state["tiktok_access"]:
    data_sources = data_sources_manager.get_datasources(exclude=["Tiktok"])
else:
    data_sources = data_sources_manager.get_datasources()

with st.sidebar:
    # ==================== #
    # Logo                 #
    # ==================== #
    _, logo_, _ = st.columns([1, 9, 1])
    with logo_:
        if u_session_state["logo_"]:
            st.markdown("\n")
            st.image(u_session_state["logo_"], use_column_width=True)
            st.markdown("\n")

    # ==================== #
    # Data Source          #
    # ==================== #
    logging.info(
        f"Loaded ds {data_sources[u_session_state['selected_data_idx_']] if 'selected_data_idx_' in u_session_state else 0}"
    )
    selected_data = st.selectbox(
        "Data Source",
        data_sources,
        index=u_session_state["selected_data_idx_"]
        if "selected_data_idx_" in u_session_state
        else 0,
        disabled=u_session_state[STATE] != IDLE,
        on_change=st.cache_resource.clear,
    )
    u_session_state["selected_data_idx_"] = data_sources.index(selected_data)
    logging.info(
        f"Selected data {selected_data} index {data_sources.index(selected_data)}"
    )
    if selected_data == "tiktok":
        st.warning("TikTok data has tables that cannot be joined")

    with st.expander("Your data using **csv, xlsx**"):
        ds_name = st.text_input(
            "Data Source Name",
            value="Custom Datasource",
            disabled=u_session_state[STATE] != IDLE,
        )
        st.info("Uploaded data cannot be remove. If you uploaded by accident contact the admin")
        st.warning("Any data you upload is accessible by other users")
        ds = st.file_uploader(
            "Upload your tables",
            type=["csv", "xlsx", "json"],
            accept_multiple_files=True,
            help="Upload your data using either csv or xlsx format but not both in the same datasource. Note that json files are only for configuration.",
            disabled=u_session_state[STATE] != IDLE,
        )
        confirm_ds = st.button("Confirm", disabled=u_session_state[STATE] != IDLE)
        if confirm_ds and ds is not None:
            if isinstance(ds, list):
                data_sources_manager.new_tables(ds, ds_name=ds_name)
            else:
                data_sources_manager.new_table(ds, ds_name=ds_name)
            if "new_ds_result" not in u_session_state:
                u_session_state["new_ds_result"] = "created"
            st.experimental_rerun()
        if "new_ds_result" in u_session_state:
            if u_session_state["new_ds_result"] == "created":
                st.success("Data Source created successfully")

    # ==================== #
    # Model                #
    # ==================== #
    # model_selected = st.selectbox(
    #     "Model", models.keys(), disabled=u_session_state[STATE] != IDLE
    # )

    model_selected = list(models.keys())[0]
    # st.markdown(f"*{models_description[model_selected]}*")
    if model_selected != u_session_state["model_name"]:
        u_session_state["model_name"] = model_selected
        u_session_state["model"] = models[model_selected]

data_transformers = {
    "mask": DataMasker,
    "filter": DataFilter,
}


# Load data details
@st.cache_resource
def get_data_loader(selected_data_, selected_transformers: list[type]):
    return DataLoaderFactory.from_folder(
        selected_data_, [i() for i in selected_transformers], path_to_data_folder
    )


dl = get_data_loader(selected_data, [data_transformers[i] for i in ["mask", "filter"]])
if not dl:
    st.error("No Data Source found")
    st.stop()

dl.transform()

tables_df = dl.data
masked_tables_df = dl.transformed_data
default_tables_selection = [
    a for a in list(dl.data.keys()) if "sell_out" not in a
]  # fixme
descriptions = dl.descriptions
cols_config = dl.columns_config

dfs_columns = {df_name: list(df.columns) for df_name, df in tables_df.items()}
table_names = list(dfs_columns.keys())

with st.sidebar:
    # ==================== #
    # Tables Selection     #
    # ==================== #
    selected_table_names = table_names
    selected_tables_names = st.multiselect(
        "Useful tables for your queries",
        table_names,
        default=default_tables_selection,
        disabled=u_session_state[STATE] != IDLE,
    )

selected_tables_df: dict = {
    k: v for k, v in tables_df.items() if k in selected_tables_names
}

selected_masked_tables_df: dict = {
    k: v for k, v in masked_tables_df.items() if k in selected_tables_names
}

db_schema = db_schema_generation(selected_masked_tables_df, descriptions) + rules
main_tab, sandbox_tab = st.tabs(["Chat", "Data"])


# ======================================================================================================================
# MAIN TAB
# ======================================================================================================================
def clear_preselected_prompt():
    u_session_state["pre_written_prompt_selected_to_clear"] = 1


if (
    "pre_written_prompt_selected_to_clear" in u_session_state
    and u_session_state["pre_written_prompt_selected_to_clear"] > 0
):
    u_session_state["pre_written_prompt_selected_to_clear"] += 1
    if (
        u_session_state["pre_written_prompt_selected_to_clear"] > 2
        and "pre_written_prompt_selected" in u_session_state
    ):
        u_session_state["pre_written_prompt_selected"] = "None"


def update_pre_written_prompt_selected():
    u_session_state["pre_written_prompt_selected_to_clear"] = 0


with main_tab:
    pre_written_prompts = get_pre_written_prompts(selected_data)

    pre_written_prompt_selected = st.selectbox(
        "Select a pre-written prompt",
        options=pre_written_prompts.keys(),
        disabled=u_session_state[STATE] != IDLE,
        key="pre_written_prompt_selected",
        on_change=update_pre_written_prompt_selected,
    )

    def human_reply_expected():
        return (
            conv.chat.last_message_is_from_ai()
            and conv.chat.last_message.state == AIMessageState.QUESTION
        )

    text_area_value = (
        pre_written_prompts[
            list(pre_written_prompts.keys())[pre_written_prompts.__len__() // 2]
        ]
        if pre_written_prompts.__len__()
        else ""
    )

    if u_session_state[STATE] not in [IDLE]:
        text_area_value = None
    elif conv.chat.last_message_is_from_ai():
        if conv.chat.last_message.state == AIMessageState.ERROR:
            text_area_value = (
                f"""Note: if last message was an error, try to rephrase your request"""
            )
        elif conv.chat.last_message.state == AIMessageState.QUESTION:
            text_area_value = f"""Your request was not fully understood, please reply to the question and click `reply`. Or write a new request and click `send`"""

    value = pre_written_prompts[pre_written_prompt_selected]

    user_input = st.text_area(
        f"Chat",
        value=value,
        placeholder=text_area_value,
        help=f"Send your request to gpt and let it do the rest. Use keywords {', '.join(USER_KEYWORDS)} to have them replaced by relevant information",
        label_visibility="collapsed",
        disabled=u_session_state[STATE] != IDLE,
        key="user_input",
    )

    (
        send_button_col,
        reply_button_col,
        clear_chat_col,
        show_details_col,
    ) = st.columns(4)

    with send_button_col:
        send_button = st.button(
            label=f"Send",
            use_container_width=True,
            type="primary" if not human_reply_expected() else "secondary",
            disabled=u_session_state[STATE] not in [IDLE],
            on_click=clear_preselected_prompt,
        )

    with reply_button_col:
        reply_button = st.button(
            label=f"Reply",
            use_container_width=True,
            type="primary" if human_reply_expected() else "secondary",
            disabled=len(conv.chat) == 0 or u_session_state[STATE] not in [IDLE],
            on_click=clear_preselected_prompt,
        )

    with clear_chat_col:
        if st.button(
            "Clear Chat",
            use_container_width=True,
            disabled=not conv.len_msgs() or u_session_state[STATE] not in [IDLE],
        ):
            conv.clear()

    with show_details_col:
        show_details = st.checkbox(
            "Show Details",
            value=False,
            disabled=u_session_state[STATE] not in [IDLE],
        )

    progress_bar = display_chat(conv, show_details, u_session_state)
    if u_session_state[STATE] in [INIT, GENERATING, PARSING, EXECUTION, FINISH]:
        time.sleep(
            0.5
        )  # Wait for components to be rendered before executing the thread blocking request
        print(f"[Main] tables selected {selected_tables_df.keys()}")

        request_reply(
            conv=conv,
            progress_bar=progress_bar,
            db_schema=db_schema,
            s_state=u_session_state,
            tables_selected=selected_tables_df,
            masker=None,
        )

    if send_button:
        # check if the user has entered a request
        if not user_input:
            st.error("Please enter a request")
        else:
            u_session_state[MODE] = NEW_CONVERSATION

            conv.new_chat()
            print(
                f"add message {user_input} to chat. Should reload the app and show the chat"
            )
            conv.chat.add_message(
                HumanMessageUI.from_content(user_input, user_input)
            )  # Will rerun the app # This message is to be updated with the prompt used
            print("should not appear")

    if reply_button:
        if not user_input:
            st.error("Please enter a request")
        else:
            u_session_state[MODE] = REPLY
            print("add message {} to chat".format(user_input))
            conv.chat.add_message(
                HumanMessageUI.from_content(user_input, user_input)
            )  # Will rerun the app # This message is to be updated with the prompt used

# ======================================================================================================================
# DATABASE TAB
# ======================================================================================================================
with sandbox_tab:
    # Display the tables and columns in the database (if selected in the sidebar)
    if selected_tables_names:
        st.subheader("Selected Tables and Columns")

        for table_name in selected_tables_names:
            st.markdown(
                f"**{system_name_to_human_name(table_name).replace(' df', '')}**"
            )
            st.dataframe(selected_tables_df[table_name].head())
    else:
        st.warning("No tables selected in the sidebar.")
