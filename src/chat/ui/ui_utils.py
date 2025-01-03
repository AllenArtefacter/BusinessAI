import altair
import streamlit as st
from matplotlib import pyplot as plt


def update_session_state_chat_messages(fn):
    def wrapper(instance, *args, **kwargs):
        print(
            f"============= calling function {fn.__name__} with 'silent' in kwargs {'silent' in kwargs} ============="
        )
        result = fn(instance, *args, **kwargs)
        chat_id = instance.id
        try:
            instance.session_state["messages"] = [
                message
                for message in instance.session_state["messages"]
                if message.chat_id != chat_id
            ] + instance.messages
        except KeyError:
            instance.session_state["messages"] = instance.messages
            st.warning(
                "No messages found state found. Creating new session state. (An error occurred, you might face unexpected behaviour)"
            )
            if "error" not in instance.session_state:
                instance.session_state["error"] = (
                    "No messages found state found. Creating new session state. (An error occurred, you might face unexpected behaviour)",
                    1,
                )
        if "silent" not in kwargs or not kwargs["silent"]:
            print(
                "============= update_session_state st.experimental_rerun() ============="
            )
            st.experimental_rerun()
        return result

    return wrapper


def update_session_state_conversation_messages(fn):
    def wrapper(instance, *args, **kwargs):
        print(
            f"============= calling function {fn.__name__} with 'silent' in kwargs {'silent' in kwargs} ============="
        )
        result = fn(instance, *args, **kwargs)
        instance.session_state["messages"] = instance.messages
        if "silent" not in kwargs or not kwargs["silent"]:
            print(
                "============= update_session_state st.experimental_rerun() ============="
            )
            st.experimental_rerun()
        return result

    return wrapper


def streamlit_plot_figure(figure):
    import streamlit as st

    if isinstance(figure, altair.vegalite.v4.api.Chart):
        st.altair_chart(figure)
    elif isinstance(figure, altair.vegalite.v4.api.LayerChart):
        st.altair_chart(figure)
    elif isinstance(figure, altair.vegalite.v4.api.VConcatChart):
        st.altair_chart(figure)
    elif isinstance(figure, altair.vegalite.v4.api.HConcatChart):
        st.altair_chart(figure)
    elif isinstance(figure, plt.Figure):
        st.pyplot(fig=figure)
    else:
        st.write(figure)
        st.warning(f"Figure type {type(figure)} not supported.")
