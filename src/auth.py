import hashlib
from hashlib import sha256
from time import sleep

import streamlit as st


def is_logged_in(u_session_state):
    return (
        u_session_state["authenticated"]
        if "authenticated" in u_session_state
        else False
    )


def login(u_session_state, password):
    if is_logged_in(u_session_state):
        return

    if password is None:
        # Placeholder for password
        password = st.text_input("Password", type="password")

    hashed_password = hashlib.sha256(password.encode("utf-8")).hexdigest()

    # Define your password here
    correct_password_hashed = (
        "eb628cae747841ff939e1059d3efed849226005dda5a69bc58ff4310312f83f1"
    )
    correct_password_hashed_tiktok = (
        "5beeafeac2e27eae5d4ba62590257718673461b2af52383ef7e3a53c7df14306"
    )

    if not password or password == "":
        st.info("Please enter a password")
        st.stop()

    if hashed_password == correct_password_hashed:
        u_session_state["authenticated"] = True
        u_session_state["tiktok_access"] = False
        st.balloons()
        sleep(2)
        st.experimental_rerun()

    if hashed_password == correct_password_hashed_tiktok:
        u_session_state["authenticated"] = True
        u_session_state["tiktok_access"] = True
        st.balloons()
        sleep(2)
        st.experimental_rerun()

    if not is_logged_in(u_session_state):
        st.error("The password you entered is incorrect")
        st.stop()
