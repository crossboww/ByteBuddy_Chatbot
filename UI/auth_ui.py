import streamlit as st
from services.auth import signup_user, login_user

def _set_token_in_url(token: str):
    # Works on all current Streamlit versions
    st.query_params["token"] = token

def show_auth_ui():
    st.subheader("🔐 Login / Signup")
    mode = st.radio("Choose:", ["Login", "Signup"], horizontal=True)
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    col1, col2 = st.columns([1,1])

    with col1:
        if st.button("Login", use_container_width=True, disabled=(mode!="Login")):
            ok, result = login_user(username, password)
            if ok:
                token = result  # login_user returns token on success
                st.session_state.user = username
                st.session_state.session_token = token
                _set_token_in_url(token)
                st.success("Login successful.")
                st.rerun()
            else:
                st.error(result)

    with col2:
        if st.button("Signup", use_container_width=True, disabled=(mode!="Signup")):
            if not username or not password:
                st.error("Username and password are required.")
            else:
                ok, msg = signup_user(username, password)
                if ok:
                    # After signup, log them in immediately via login_user
                    ok2, result2 = login_user(username, password)
                    if ok2:
                        token = result2
                        st.session_state.user = username
                        st.session_state.session_token = token
                        _set_token_in_url(token)
                        st.success("Signup successful! Redirecting to chatbot...")
                        st.rerun()
                    else:
                        st.error("Signup ok, but auto-login failed. Please login.")
                else:
                    st.error(msg)
