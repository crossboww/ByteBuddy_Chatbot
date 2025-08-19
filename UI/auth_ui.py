import streamlit as st
from services.auth import signup_user, login_user

def show_auth_ui():
    st.subheader("🔐 Login / Signup")
    mode = st.radio("Choose:", ["Login", "Signup"], horizontal=True)
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    col1, col2 = st.columns([1,1])
    with col1:
        if st.button("Login", use_container_width=True, disabled=(mode!="Login")):
            ok, msg = login_user(username, password)
            if ok:
                st.session_state.user = username
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)
    with col2:
        if st.button("Signup", use_container_width=True, disabled=(mode!="Signup")):
            if not username or not password:
                st.error("Username and password are Required.")
            else:
                ok, msg = signup_user(username, password)
                if ok:
                    st.session_state.user = username   # 👈 mark user as logged in
                    st.success("Signup successful! Redirecting to chatbot...")
                    st.rerun()  # 👈 immediately rerun to load chatbot
                else:
                    st.error(msg)