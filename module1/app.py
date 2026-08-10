"""Main integration shell for the STEM Workshop food-ordering application."""

import streamlit as st

from menu import render_menu


st.set_page_config(
    page_title="Food Lab | STEM Workshop",
    page_icon="🍴",
    layout="wide",
    initial_sidebar_state="expanded",
)


# Shared state contract for all future modules.
DEFAULT_STATE = {
    "current_module": "menu",
    "user": None,
    "is_logged_in": False,
    "cart": [],
    "subtotal": 0.0,
    "tax": 0.0,
    "delivery_charge": 0.0,
    "total": 0.0,
    "payment_status": "Pending",
    "order_id": None,
    "delivery_status": "Not started",
}

for key, value in DEFAULT_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = value


def inject_theme() -> None:
    """Common visual system. Other module teams can reuse this CSS."""
    st.markdown(
        """
        <style>
        :root {
            --blue: #056DAE;
            --navy: #003B70;
            --red: #E31837;
            --light-blue: #EAF5FB;
            --background: #F6F9FC;
            --text: #17324D;
            --muted: #607D94;
            --green: #16803C;
            --amber: #F59E0B;
        }

        .stApp { background: var(--background); color: var(--text); }
        [data-testid="stHeader"] { background: transparent; }
        .block-container { max-width: 1200px; padding-top: 1.25rem; padding-bottom: 2rem; }
        [data-testid="stSidebar"] { background: white; border-right: 1px solid #DCEBF3; }
        [data-testid="stSidebar"] .block-container { padding-top: 1.25rem; }

        .topbar { display: flex; align-items: center; justify-content: space-between; margin-bottom: .9rem; }
        .brand { display: flex; align-items: center; gap: .7rem; }
        .brand-mark { width: 40px; height: 40px; display: grid; place-items: center; border-radius: 13px; background: var(--blue); color: white; font-size: 1.35rem; box-shadow: 0 6px 16px rgba(5,109,174,.2); }
        .brand-name { color: var(--navy); font-size: 1.2rem; line-height: 1.1; font-weight: 800; }
        .brand-subtitle { color: var(--muted); font-size: .72rem; margin-top: .18rem; }
        .workshop-badge { background: var(--light-blue); color: var(--blue); border: 1px solid #C9E5F3; border-radius: 999px; padding: .43rem .78rem; font-size: .72rem; font-weight: 800; }

        .stepper { display: flex; align-items: center; gap: .25rem; background: white; border: 1px solid #DCEBF3; border-radius: 15px; padding: .65rem .8rem; margin-bottom: 1.7rem; box-shadow: 0 3px 12px rgba(0,59,112,.04); }
        .step { flex: 1; color: #9AAEBC; text-align: center; font-size: .71rem; font-weight: 700; }
        .step.active { color: var(--blue); }
        .step.done { color: var(--green); }
        .step-dot { width: 9px; height: 9px; margin: 0 auto .25rem; border-radius: 50%; background: #D7E3EA; }
        .step.active .step-dot { width: 11px; height: 11px; background: var(--blue); box-shadow: 0 0 0 4px var(--light-blue); }
        .step.done .step-dot { background: var(--green); }

        .eyebrow, .section-label { color: var(--blue); font-size: .72rem; letter-spacing: .12em; font-weight: 800; }
        .section-label { margin: 1.2rem 0 .65rem; }
        .page-title { color: var(--navy); font-size: 2.15rem; line-height: 1.1; letter-spacing: -.045em; margin: 0; }
        .page-subtitle { color: var(--muted); font-size: .96rem; margin: .4rem 0 0; }

        .tip-card { background: white; border: 1px solid #DCEBF3; border-radius: 14px; padding: .8rem 1rem; color: var(--text); font-size: .8rem; line-height: 1.4; box-shadow: 0 4px 14px rgba(0,59,112,.04); }
        .tip-icon { font-size: 1.15rem; margin-right: .25rem; }
        .food-card { background: white; border: 1px solid #DCEBF3; border-radius: 16px; padding: 1rem; min-height: 158px; box-shadow: 0 4px 13px rgba(0,59,112,.04); }
        .food-card:hover { border-color: #A9D6EC; box-shadow: 0 8px 18px rgba(0,59,112,.09); }
        .food-icon { font-size: 2rem; margin-bottom: .42rem; }
        .food-name { color: var(--navy); font-size: 1rem; font-weight: 800; }
        .food-category { color: var(--muted); font-size: .71rem; margin-top: .12rem; }
        .food-price { color: var(--blue); font-size: 1.05rem; font-weight: 800; margin-top: .42rem; }
        .rating { color: #B87500; font-size: .76rem; font-weight: 700; }
        .food-badge { display: inline-block; border-radius: 999px; padding: .18rem .46rem; margin-top: .45rem; font-size: .67rem; font-weight: 800; }
        .badge-veg { background: #E5F5EA; color: #16803C; }
        .badge-nonveg { background: #FCE6EA; color: #B4233F; }
        .badge-egg { background: #FFF1D6; color: #A76500; }

        .cart-heading { color: var(--navy); font-size: 1.3rem; font-weight: 800; }
        .cart-count { background: var(--blue); color: white; border-radius: 999px; padding: .18rem .5rem; font-size: .72rem; vertical-align: middle; }
        .cart-item { border-bottom: 1px solid #E4EEF3; padding: .6rem 0; }
        .cart-item-name { color: var(--text); font-size: .83rem; font-weight: 700; }
        .cart-item-price { color: var(--muted); font-size: .75rem; }
        .bill-box { background: var(--light-blue); border: 1px solid #C9E5F3; border-radius: 14px; padding: .8rem; margin-top: .8rem; }
        .bill-row { display: flex; justify-content: space-between; color: var(--muted); font-size: .78rem; margin: .28rem 0; }
        .bill-total { display: flex; justify-content: space-between; color: var(--navy); border-top: 1px solid #BBDDEC; padding-top: .6rem; margin-top: .55rem; font-size: 1.1rem; font-weight: 800; }
        .empty-cart { color: var(--muted); text-align: center; padding: 1.8rem .4rem; font-size: .83rem; line-height: 1.5; }
        .free-delivery { color: var(--green); font-weight: 700; }
        .app-footer { border-top: 1px solid #DCEBF3; color: var(--muted); font-size: .72rem; margin-top: 2rem; padding-top: .75rem; display: flex; justify-content: space-between; }

        .stButton > button { border-radius: 10px; min-height: 2.45rem; font-weight: 700; }
        .stTextInput input { border-radius: 10px; border-color: #C9DDE8; min-height: 2.45rem; }
        .stSelectbox [data-baseweb="select"] > div { border-radius: 10px; }
        .stRadio > div { gap: .35rem; }
        .stRadio label { background: white; border: 1px solid #DCEBF3; border-radius: 999px; padding: .38rem .68rem; }
        .stRadio label:has(input:checked) { background: var(--light-blue); border-color: var(--blue); }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header() -> None:
    st.markdown(
        """
        <div class="topbar">
            <div class="brand">
                <div class="brand-mark">🍴</div>
                <div><div class="brand-name">Food Lab</div><div class="brand-subtitle">A STEM Workshop application</div></div>
            </div>
            <div class="workshop-badge">STEM WORKSHOP</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_stepper() -> None:
    steps = ["Login", "Menu", "Pay", "Bank", "Receipt", "Delivery"]
    active = st.session_state.current_module
    active_index = steps.index(active.title()) if active.title() in steps else 1
    step_html = []
    for index, step in enumerate(steps):
        status = "done" if index < active_index else "active" if index == active_index else ""
        step_html.append(f"<div class='step {status}'><div class='step-dot'></div>{step}</div>")
    st.markdown(f"<div class='stepper'>{''.join(step_html)}</div>", unsafe_allow_html=True)


def render_placeholder(module_name: str) -> None:
    st.markdown(f"<h1 class='page-title'>{module_name} module</h1>", unsafe_allow_html=True)
    st.info(f"The {module_name.lower()} module will be integrated here.")
    if st.button("Back to menu", key="return_to_menu"):
        st.session_state.current_module = "menu"
        st.rerun()


inject_theme()
render_header()
render_stepper()

if st.session_state.current_module == "menu":
    render_menu()
else:
    render_placeholder(st.session_state.current_module.title())

st.markdown(
    "<div class='app-footer'><span>STEM Workshop</span><span>Educational simulation only</span></div>",
    unsafe_allow_html=True,
)
