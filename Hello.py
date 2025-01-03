import streamlit as st

st.set_page_config(
    page_title="Hello",
    page_icon="👋",
)


if "logo_" not in st.session_state:
    st.session_state["logo_"] = "res/artefact_logo.png"

st.sidebar.success("Select AI for BI to begin exploring")

_, logo_, _ = st.columns([3, 4, 3])
with logo_:
    if st.session_state["logo_"]:
        st.markdown('\n')
        st.image(st.session_state["logo_"], use_column_width=True)
        st.markdown('\n')

st.write("# Welcome to AI for BI! 👋")

st.markdown(
    """
    AI for BI is a demo tool to show what is currently possible in terms of code generation on data schema
    using GPT-3.5 and GPT-4
    
    **👈 Select a demo from the sidebar** to see what AI for BI can do!
    - Use demo datasets
    - Use pre-defined prompts to get started
    - Introspect and run code on your db using the sandbox
    - Ask for modifications using the reply button
    - Add description to each column to give gpt details about the data
    - Select a transformation on the column not to leak data
    
    ### Want to do more?
    - Upload your own files in the sidebar to work with your own data
""")

