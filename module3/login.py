# =============================================================================
# module3/login.py - Food Lab | STEM Workshop - Login module
# =============================================================================
# Imported by root app.py as: from module3.login import render_login
#
# INTEGRATION CONTRACT COMPLIANCE:
#   - Exposes exactly one callable: render_login()
#   - Does NOT call st.set_page_config() (root app.py owns this)
#   - Does NOT inject a <style> block (root app.py's inject_theme() already
#     styles .stButton > button and .stTextInput input app-wide - any inline
#     styles below are scoped to individual elements only, matched to the
#     SAME color values as app.py's theme so login doesn't look like a
#     different app from menu/payment)
#   - Does NOT render its own header/stepper (root app.py's render_header()
#     and render_stepper() already do this for current_module in
#     {"menu", "login"}, before render_login() is called)
#   - Reads/writes only shared session_state; never touches keys it doesn't
#     own on every rerun
#   - users.csv ships inside this module's own folder (module3/users.csv) and
#     is located via __file__, so it resolves correctly regardless of the
#     working directory app.py is launched from
#
# On successful login, sets:
#   user, customer_name, logged_in, is_logged_in, current_module = "payment"
# =============================================================================

import os
import pandas as pd
import streamlit as st

# users.csv lives next to this file, not relative to wherever streamlit was
# launched from - this avoids "file not found" if app.py's cwd differs.
CSV_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "users.csv")

# Matched exactly to app.py's inject_theme() CSS variables, so login text
# renders in the same colors as the rest of the app:
#   --blue:#056DAE  --navy:#003B70  --muted:#607D94  --green:#16803C
NAVY = "#003B70"
BLUE = "#056DAE"
MUTED = "#607D94"
GREEN = "#16803C"


# -----------------------------------------------------------------------------
# DATA: load (or bootstrap) users.csv
# -----------------------------------------------------------------------------
def load_users(csv_path: str = CSV_FILE) -> pd.DataFrame:
    if not os.path.exists(csv_path):
        sample = pd.DataFrame({
            "username": ["admin", "john"],
            "password": ["admin123", "john123"],
        })
        sample.to_csv(csv_path, index=False)
    return pd.read_csv(csv_path, dtype=str)


def verify_credentials(username: str, password: str, users_df: pd.DataFrame) -> bool:
    match = users_df[
        (users_df["username"] == username) & (users_df["password"] == password)
    ]
    return not match.empty


# -----------------------------------------------------------------------------
# render_login() - PUBLIC ENTRY POINT
# -----------------------------------------------------------------------------
def render_login():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "is_logged_in" not in st.session_state:
        st.session_state.is_logged_in = False
    if "user" not in st.session_state:
        st.session_state.user = ""
    if "customer_name" not in st.session_state:
        st.session_state.customer_name = ""

    users_df = load_users()

    # ---- Already logged in (safe to call render_login() repeatedly) ----
    if st.session_state.logged_in:
        st.markdown(
f"""<div style="color:{BLUE}; font-size:0.78rem; font-weight:700; letter-spacing:0.05em; margin-bottom:0.3rem;">YOU'RE SIGNED IN</div>
<h2 style="color:{NAVY}; margin:0 0 0.3rem 0;">Welcome back, {st.session_state.customer_name}</h2>
<p style="color:{MUTED}; font-size:0.95rem; margin:0 0 1.2rem 0;">Taking you to payment...</p>""",
unsafe_allow_html=True,
        )
        with st.container(border=True):
            st.markdown(
f"""<span style="background-color:{GREEN}1A; color:{GREEN}; padding:0.3rem 0.85rem; border-radius:999px; font-weight:600; font-size:0.85rem; display:inline-block;">Signed in</span>""",
unsafe_allow_html=True,
            )
            if st.button("Log out", key="logout_btn"):
                st.session_state.logged_in = False
                st.session_state.is_logged_in = False
                st.session_state.user = ""
                st.session_state.customer_name = ""
                st.rerun()
        return

    # ---- Sign-in form ----
    st.markdown(
f"""<div style="color:{BLUE}; font-size:0.78rem; font-weight:700; letter-spacing:0.05em; margin-bottom:0.3rem;">WELCOME TO THE FOOD LAB</div>
<h2 style="color:{NAVY}; margin:0 0 0.3rem 0;">Sign in to continue</h2>
<p style="color:{MUTED}; font-size:0.95rem; margin:0 0 1.2rem 0;">Enter your username and password to start ordering.</p>""",
unsafe_allow_html=True,
    )

    with st.container(border=True):
        with st.form(key="login_form", border=False):
            username = st.text_input("Username", key="username_input", placeholder="e.g. john")
            password = st.text_input(
                "Password", type="password", key="password_input",
                placeholder="Enter your password",
            )
            submitted = st.form_submit_button("Sign In")

        if submitted:
            if not username or not password:
                st.warning("Please enter both a username and password.")
            elif verify_credentials(username, password, users_df):
                st.session_state.user = username
                st.session_state.customer_name = username
                st.session_state.logged_in = True
                st.session_state.is_logged_in = True
                st.session_state.current_module = "payment"
                st.rerun()
            else:
                st.error("Incorrect username or password. Try again.")

        with st.expander("Need demo credentials?"):
            st.markdown(
                "Try **admin** / `admin123` or **john** / `john123` "
                "(auto-created in `users.csv` the first time this app runs)."
            )


# -----------------------------------------------------------------------------
# Standalone preview only - fires when this file is run directly
# (streamlit run module3/login.py), never when app.py imports render_login().
# Intentionally does NOT call st.set_page_config() or inject CSS, so this
# preview looks plainer than the integrated version - that's expected, since
# app.py's shared theme is what makes it match the rest of the app.
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    render_login()
