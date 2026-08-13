# =============================================================================
# login.py - Food Lab | STEM Workshop - Sign In
# =============================================================================
# Visual system matched to the provided Food Lab mockup:
#   - Logo mark + app name + tagline + "STEM WORKSHOP" badge header
#   - Bordered six-step journey tracker with colored dots
#   - Small blue uppercase "eyebrow" label above a big bold heading
#   - White bordered cards, rounded corners, light shadows
#   - Footer: "STEM Workshop" / "Educational simulation only"
#
# The mockup itself only shows the Menu/Cart screens, not Login - so this
# screen reuses the same header, tracker, card, and typography system for
# visual consistency, since no login-specific reference existed.
#
# Run with:
#   streamlit run login.py
# =============================================================================

import os
import pandas as pd
import streamlit as st

# -----------------------------------------------------------------------------
# COLORS (sampled from the mockup)
# -----------------------------------------------------------------------------
NAVY = "#0B2545"            # Headings, logo mark background
BLUE = "#1868DB"            # Links, prices, active states, eyebrow labels
MUTED = "#64748B"           # Secondary/caption text
BORDER = "#E5E9F0"          # Card + tracker borders
BADGE_BLUE_BG = "#EAF2FE"   # "STEM WORKSHOP" pill background
GREEN = "#1E8E5A"           # Completed step / success
RED_CTA = "#EF4444"         # Primary CTA red, matched from mockup's "Proceed" button

CSV_FILE = "users.csv"
STEPS = [("Login", "current"), ("Menu", "upcoming"), ("Pay", "upcoming"),
         ("Bank", "upcoming"), ("Receipt", "upcoming"), ("Delivery", "upcoming")]


# -----------------------------------------------------------------------------
# PAGE SETUP
# -----------------------------------------------------------------------------
st.set_page_config(page_title="Food Lab | STEM Workshop", page_icon="🍴", layout="centered")

st.markdown(
f"""<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
html, body, [class*="css"] {{
font-family: 'Inter', Arial, 'Segoe UI', sans-serif;
}}
.stApp {{
background-color: #FFFFFF;
}}
.block-container {{
max-width: 620px;
padding-top: 2.5rem;
}}
div[data-testid="stVerticalBlockBorderWrapper"] {{
border-radius: 14px !important;
border: 1px solid {BORDER} !important;
box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
}}
h1, h2, h3 {{
color: {NAVY} !important;
font-weight: 800 !important;
letter-spacing: -0.02em;
}}
div.stButton > button, div[data-testid="stFormSubmitButton"] > button {{
background-color: {BLUE};
color: #FFFFFF;
border-radius: 10px;
border: none;
padding: 0.65rem 1.5rem;
font-weight: 600;
width: 100%;
transition: transform 0.1s ease, background-color 0.15s ease;
}}
div.stButton > button:hover, div[data-testid="stFormSubmitButton"] > button:hover {{
background-color: {NAVY};
color: #FFFFFF;
transform: translateY(-1px);
}}
div[data-testid="stAlert"] {{
border-radius: 10px;
}}
div[data-testid="stExpander"] {{
border-radius: 10px;
border: 1px solid {BORDER};
}}
[data-testid="stWidgetLabel"] p, div[data-testid="stTextInput"] label {{
color: {NAVY} !important;
font-weight: 600 !important;
font-size: 0.88rem !important;
}}
div[data-testid="stTextInput"] input {{
background-color: #FFFFFF !important;
color: {NAVY} !important;
-webkit-text-fill-color: {NAVY} !important;
border: 1.5px solid {BORDER} !important;
border-radius: 10px !important;
}}
div[data-testid="stTextInput"] input::placeholder {{
color: #94A3B8 !important;
opacity: 1 !important;
}}
[data-testid="stExpander"] summary, [data-testid="stExpander"] summary p {{
color: {NAVY} !important;
font-weight: 600 !important;
}}
[data-testid="stExpanderDetails"] p, [data-testid="stExpanderDetails"] {{
color: {NAVY} !important;
}}
</style>""",
unsafe_allow_html=True,
)


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
# STATE
# -----------------------------------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = ""

users_df = load_users()


# -----------------------------------------------------------------------------
# HEADER: logo mark + name + tagline + workshop badge (matches mockup)
# -----------------------------------------------------------------------------
st.markdown(
f"""<div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:1.4rem;">
<div style="display:flex; align-items:center; gap:0.75rem;">
<div style="width:44px; height:44px; border-radius:10px; background:{NAVY}; display:flex; align-items:center; justify-content:center; font-size:1.3rem;">🍴</div>
<div>
<div style="font-size:1.3rem; font-weight:800; color:{NAVY}; line-height:1.1;">Food Lab</div>
<div style="font-size:0.82rem; color:{MUTED};">A STEM Workshop application</div>
</div>
</div>
<div style="background:{BADGE_BLUE_BG}; color:{BLUE}; font-size:0.72rem; font-weight:700; letter-spacing:0.03em; padding:0.4rem 0.9rem; border-radius:999px; white-space:nowrap;">STEM WORKSHOP</div>
</div>""",
unsafe_allow_html=True,
)


# -----------------------------------------------------------------------------
# SIX-STEP TRACKER (bordered pill row, matches mockup exactly)
# -----------------------------------------------------------------------------
step_items = ""
for label, state in STEPS:
    if state == "current":
        dot, text_color, weight = BLUE, BLUE, "700"
    elif state == "done":
        dot, text_color, weight = GREEN, GREEN, "700"
    else:
        dot, text_color, weight = "#CBD5E1", "#94A3B8", "500"
    step_items += f"""<div style="display:flex; align-items:center; gap:0.35rem;">
<span style="width:7px; height:7px; border-radius:50%; background:{dot}; display:inline-block;"></span>
<span style="font-size:0.85rem; font-weight:{weight}; color:{text_color};">{label}</span>
</div>"""

st.markdown(
f"""<div style="border:1px solid {BORDER}; border-radius:12px; padding:0.8rem 1.2rem; display:flex; justify-content:space-between; flex-wrap:wrap; gap:0.6rem; margin-bottom:1.6rem;">
{step_items}
</div>""",
unsafe_allow_html=True,
)


# -----------------------------------------------------------------------------
# LOGGED-IN VIEW
# -----------------------------------------------------------------------------
if st.session_state.logged_in:
    st.markdown(
f"""<div style="color:{BLUE}; font-size:0.78rem; font-weight:700; letter-spacing:0.05em; margin-bottom:0.3rem;">YOU'RE SIGNED IN</div>
<h1 style="font-size:2rem; margin:0 0 0.3rem 0;">Welcome back, {st.session_state.user}</h1>
<p style="color:{MUTED}; font-size:0.95rem; margin:0 0 1.4rem 0;">Head to the menu when you're ready to start ordering.</p>""",
unsafe_allow_html=True,
    )
    with st.container(border=True):
        st.markdown(
f"""<div style="padding:0.4rem;">
<span style="background-color:{GREEN}1A; color:{GREEN}; padding:0.3rem 0.85rem; border-radius:999px; font-weight:600; font-size:0.85rem; display:inline-block;">Signed in</span>
</div>""",
unsafe_allow_html=True,
        )
        if st.button("Log out", key="logout_btn"):
            st.session_state.logged_in = False
            st.session_state.user = ""
            st.rerun()


# -----------------------------------------------------------------------------
# SIGN-IN VIEW
# -----------------------------------------------------------------------------
else:
    st.markdown(
f"""<div style="color:{BLUE}; font-size:0.78rem; font-weight:700; letter-spacing:0.05em; margin-bottom:0.3rem;">WELCOME TO THE FOOD LAB</div>
<h1 style="font-size:2rem; margin:0 0 0.3rem 0;">Sign in to continue</h1>
<p style="color:{MUTED}; font-size:0.95rem; margin:0 0 1.4rem 0;">Enter your username and password to start ordering.</p>""",
unsafe_allow_html=True,
    )

    with st.container(border=True):
        st.markdown('<div style="padding:0.5rem 0.5rem 0 0.5rem;">', unsafe_allow_html=True)

        with st.form(key="login_form", border=False):
            username = st.text_input("Username", key="username_input", placeholder="e.g. john")
            password = st.text_input(
                "Password", type="password", key="password_input",
                placeholder="Enter your password",
            )
            st.write("")
            submitted = st.form_submit_button("Sign In")

        if submitted:
            if not username or not password:
                st.warning("Please enter both a username and password.")
            elif verify_credentials(username, password, users_df):
                st.session_state.logged_in = True
                st.session_state.user = username
                st.rerun()
            else:
                st.error("Incorrect username or password. Try again.")

        with st.expander("Need demo credentials?"):
            st.markdown(
                "Try **admin** / `admin123` or **john** / `john123` "
                "(auto-created in `users.csv` the first time this app runs)."
            )

        st.markdown('<div style="height:0.3rem;"></div>', unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# FOOTER (matches mockup: left label, right note, divider above)
# -----------------------------------------------------------------------------
st.markdown(
f"""<hr style="border:none; border-top:1px solid {BORDER}; margin:2.2rem 0 0.9rem 0;">
<div style="display:flex; justify-content:space-between; color:{MUTED}; font-size:0.82rem;">
<span>STEM Workshop</span>
<span>Educational simulation only</span>
</div>""",
unsafe_allow_html=True,
)