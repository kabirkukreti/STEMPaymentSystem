# =============================================================================
# login.py - Food Lab | STEM Workshop - Login module
# =============================================================================
# INTEGRATION CONTRACT COMPLIANCE:
#   - Exposes exactly one callable: render_login()
#   - Does NOT call st.set_page_config() (root app.py owns this)
#   - Does NOT inject a <style> block or global CSS (root app.py owns theming;
#     any styling below is scoped INLINE to individual elements only, so it
#     can't leak into or override other modules' widgets)
#   - Does NOT render its own header/step-tracker/navigation (root app.py owns
#     the shared chrome that wraps every module)
#   - Reads/writes only shared session_state; never resets state that isn't
#     its own on every rerun
#   - users.csv is a repo asset - no external dependency
#
# On successful login, sets:
#   user, customer_name, logged_in, is_logged_in, current_module = "payment"
#
# HOW app.py IS EXPECTED TO USE THIS:
#
#   from login import render_login
#
#   if not st.session_state.get("logged_in"):
#       render_login()
#   elif st.session_state.get("current_module") == "payment":
#       render_payment()
# =============================================================================

import os
import pandas as pd
import streamlit as st

CSV_FILE = "users.csv"

# Colors used only for inline styling on elements this module renders
# directly - not a global stylesheet, so nothing here affects other modules.
NAVY = "#0B2545"
BLUE = "#1868DB"
MUTED = "#64748B"
GREEN = "#1E8E5A"


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
# (streamlit run login.py) for isolated testing. Never runs when app.py
# imports render_login(), since __name__ won't be "__main__" in that case.
# Intentionally does NOT call st.set_page_config() or inject CSS, so what
# you see here matches exactly what app.py will render once integrated.
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    render_login()
