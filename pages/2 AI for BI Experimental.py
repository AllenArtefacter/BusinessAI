import logging
import os
import time

import pandas as pd
import streamlit as st

from src.auth import login
from src.chat.ui.ai_message_ui import AIMessageState
from src.chat.ui.conversation_ui import ConversationUI
from src.chat.ui.human_message_ui import HumanMessageUI
from src.chat.ui.ui_utils import streamlit_plot_figure
from src.config import (
    QUICK_MODEL_NAME,
    all_models,
    get_pre_written_prompts,
    models_description,
)
from src.database.datasource_manager import (
    DatasourceManager,
    human_name_to_system_name,
    system_name_to_human_name,
)
from src.database.factory_data_loader import DataLoaderFactory
from src.database.mask.dataset_masker import DataFilter, DataMasker, possibles_configs
from src.handle_completion import request_reply
from src.models.assistant import get_assistant
from src.prompt_engineering import USER_KEYWORDS
from src.tools.progress_bar import get_progress_bar_data
from src.tools.prompting import db_schema_generation, rules
from src.tools.states import (
    CANCELED,
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
from src.tools.utils import exec_on_tables, mic

st.set_page_config(
    page_title="AI for BI",
    layout="wide",
    # page_icon="./res/client_logo.png",
    initial_sidebar_state="auto",
)

u_session_state = st.session_state  # to make sure the reference is the same everywhere

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


if MODE not in u_session_state:
    u_session_state[MODE] = NEW_CONVERSATION

if "model_name" not in u_session_state:
    u_session_state["model_name"] = QUICK_MODEL_NAME

if "tiktok_access" not in u_session_state:
    u_session_state["tiktok_access"] = False

# Model is saved to keep model.response alive between pages reload while generating
if "model" not in u_session_state:
    u_session_state["model"] = all_models[u_session_state["model_name"]]

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
        f"Loaded ds {data_sources[u_session_state['selected_data_idx_']] if 'selected_data_idx_' in u_session_state else 1}"
    )

    selected_data = st.selectbox(
        "Data Source",
        data_sources,
        index=u_session_state["selected_data_idx_"]
        if "selected_data_idx_" in u_session_state
        else 1,
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
            if (
                u_session_state["new_ds_result"] == "created"
                and human_name_to_system_name(ds_name) in data_sources
            ):
                st.success("Data Source created successfully")
            elif (
                u_session_state["new_ds_result"] == "created"
                and human_name_to_system_name(ds_name) not in data_sources
            ):
                st.error("Data Source creation failed")

    with st.expander("Your Data using **path to folder**"):
        ds_name = st.text_input(
            "Data Source Name", value="Custom Datasource", key="ds_name_opt2"
        )
        path_to_custom_data_folder = st.text_input(
            "Path to folder", value="./res/data/demo"
        )
        confirm_ds = st.button("Confirm", key="confirm_ds_opt2")

        if confirm_ds and ds_name and path_to_custom_data_folder:
            data_sources_manager.from_path(path_to_custom_data_folder, ds_name=ds_name)
            st.experimental_rerun()

    # ==================== #
    # Model                #
    # ==================== #
    model_selected = st.selectbox("Model", all_models.keys(), index=len(all_models) - 1)
    st.markdown(f"*{models_description[model_selected]}*")
    if model_selected != u_session_state["model_name"]:
        u_session_state["model_name"] = model_selected
        u_session_state["model"] = all_models[model_selected]


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
main_tab, sandbox_tab, data_configuration, exp = st.tabs(
    ["Main", "Sandbox", "Data Config", "Experiments"]
)


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
        if conv.chat.last_message.result_error:
            text_area_value = f"""Note: if last message was an error, try to rephrase your request and/or use another model"""

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
            type="primary",
            disabled=u_session_state[STATE] not in [IDLE],
            on_click=clear_preselected_prompt,
        )

    with reply_button_col:
        reply_button = st.button(
            label=f"Reply",
            use_container_width=True,
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
        request_reply(
            conv=conv,
            progress_bar=progress_bar,
            db_schema=db_schema,
            s_state=u_session_state,
            tables_selected=selected_tables_df,
            masker=None,
        )

    if send_button:
        print(f"send button pressed with input {user_input}")
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
        print(f"reply button pressed with input {user_input}")
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
    # import pygwalker as pyg

    # merged_df = pd.merge(
    #     tables_df["inventory_df"],
    #     tables_df["product_price_df"],
    #     on=["Month", "Distributor", "ProductID"],
    #     how="left",
    # )
    # merged_df = pd.merge(
    #     merged_df,
    #     tables_df["sell_in_df"],
    #     on=["Month", "Distributor", "ProductID"],
    #     how="left",
    # )
    # gwalker = pyg.walk(merged_df, env='Streamlit', dark="light")
    # Python query input field

    python_code: str = st.text_area(
        "Python Sandbox",
        placeholder="Enter your Python code here. saved_dataframe variable will be shown below",
        help="Enter the Python code you want to execute",
        label_visibility="collapsed",
        disabled=u_session_state[STATE] != IDLE,
    )

    # Query button
    query_button = st.button(
        label="Run Python Code", type="primary", disabled=u_session_state[STATE] != IDLE
    )

    # Execute Python query and display result (or error)
    if query_button:
        try:
            saved_dataframe, saved_figure = exec_on_tables(
                python_code, selected_tables_df
            )
            if isinstance(saved_dataframe, pd.DataFrame):
                st.dataframe(saved_dataframe.iloc[:100, :])
                if saved_dataframe.shape[0] > 100:
                    st.info(
                        f"Only the first 100 rows are displayed. The dataframe has {saved_dataframe.shape[0]} rows"
                    )
            elif saved_dataframe is not None:
                st.write(saved_dataframe)
                st.warning(
                    f"The query did not return a dataframe. saved_dataframe variable type: {type(saved_dataframe)}"
                )
            else:
                st.write("No dataframe returned by the query")

            if (
                saved_figure is not None
            ):  # matplotlib.figure.Figure | altair.vegalite.v4.api.Chart
                streamlit_plot_figure(saved_figure)

        except Exception as e:
            st.error(f"An error occurred while executing the query: {e}")

    # Display the tables and columns in the database (if selected in the sidebar)
    if selected_tables_names:
        st.subheader("Selected Tables and Columns")
        show_columns = st.checkbox("Show Columns", value=True)
        show_samples = st.checkbox("Show Data Samples", value=False)
        show_samples_masked = st.checkbox("Show Masked Data Samples", value=False)
        for table_name in selected_tables_names:
            st.markdown(f"**{system_name_to_human_name(table_name)}: {table_name}**")
            table_columns = dfs_columns[table_name]
            if show_columns:
                st.dataframe(
                    pd.DataFrame(
                        {
                            "Column Name": table_columns,
                            "Column Type": selected_tables_df[
                                table_name
                            ].dtypes.values.tolist(),
                        }
                    ),
                    width=500,
                )
            if show_samples:
                st.dataframe(selected_tables_df[table_name].head())
            if show_samples_masked:
                st.dataframe(masked_tables_df[table_name].head())
    else:
        st.warning("No tables selected in the sidebar.")

# ======================================================================================================================
# FEATURES TAB
# ======================================================================================================================
with exp:
    # ==================================================================================================================
    # logo_ UPLOAD
    # ==================================================================================================================
    def save_uploaded_logo(file, path):
        with open(path, "wb") as f:
            f.write(file.getbuffer())
        u_session_state["logo_"] = path
        st.success("Saved File:{} to tempDir".format(file.name))

    uploaded_logo_ = st.file_uploader("exp (WIP)", type=["jpg", "png", "jpeg"])

    if uploaded_logo_ is not None and (
        "logo_" not in u_session_state
        or (
            "logo_" in u_session_state
            and uploaded_logo_.name not in u_session_state["logo_"]
        )
    ):
        path = os.path.join("../", uploaded_logo_.name)
        save_uploaded_logo(uploaded_logo_, path)
        st.experimental_rerun()


def update_description(table_name, col, descriptions):
    descriptions[table_name][col] = st.session_state[f"{table_name}_{col}_input"]
    dl.descriptions = descriptions


def update_config(table_name, col_name, config):
    print(f"update config for {table_name} {col_name} in {config}")
    # config[table_name][col_name] = st.session_state[f"{table_name}_{col_name}_input_conf"]
    dl.update_config(
        table_name, col_name, st.session_state[f"{table_name}_{col_name}_input_conf"]
    )
    # dl.columns_config = config


with data_configuration:
    st.subheader("Set Description for Tables and Columns")
    for table_name in descriptions:
        with st.expander(table_name, expanded=False):
            table = descriptions[table_name]
            for col, description in table.items():
                name_col, description_col = st.columns([2, 9])
                with name_col:
                    st.write(col)
                with description_col:
                    st.text_input(
                        col,
                        description,
                        label_visibility="collapsed",
                        on_change=update_description,
                        args=(table_name, col, descriptions),
                        key=f"{table_name}_{col}_input",
                    )

    st.subheader("Set Configuration for Tables and Columns")

    possibles_configs_l = list(possibles_configs)

    for table_name in cols_config:
        with st.expander(table_name, expanded=False):
            table = cols_config[table_name]
            for col, col_config in table.items():
                name_col, cols_config_col = st.columns([5, 9])
                with name_col:
                    st.write(col)
                with cols_config_col:
                    st.selectbox(
                        label="Select the configuration you want to use",
                        index=possibles_configs_l.index(col_config),
                        options=possibles_configs_l,
                        label_visibility="collapsed",
                        on_change=update_config,
                        args=(table_name, col, cols_config),
                        key=f"{table_name}_{col}_input_conf",
                    )
