"""Central integration entry point for the STEM Workshop application."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import streamlit as st

from module1.menu import render_menu
from module3.login import render_login
from PaymentModule.payment import render_payment

ROOT = Path(__file__).resolve().parent

st.set_page_config(
    page_title="Food Lab | STEM Workshop",
    page_icon="🍴",
    layout="wide",
    initial_sidebar_state="expanded",
)

DEFAULT_STATE = {
    "current_module": "menu",
    "user": "",
    "customer_name": "",
    "logged_in": False,
    "is_logged_in": False,
    "cart": [],
    "subtotal": 0.0,
    "tax": 0.0,
    "delivery_charge": 0.0,
    "total": 0.0,
    "grand_total": 0.0,
    "payment_status": "PENDING",
    "payment_method": "",
    "transaction_id": "",
    "reference_no": "",
    "payment_success": False,
    "order_id": "",
    "delivery_status": "Not started",
    "show_order_status": False,
}

for key, value in DEFAULT_STATE.items():
    st.session_state.setdefault(key, value)


def normalise_order_state() -> None:
    """Keep equivalent names/formats compatible across independent modules."""
    cart = st.session_state.get("cart", [])
    for item in cart:
        quantity = int(item.get("quantity", item.get("qty", 1)))
        item["quantity"] = quantity
        item["qty"] = quantity
    st.session_state["cart"] = cart

    subtotal = round(
    sum(
        float(item.get("price", 0))
        * int(item.get("quantity", item.get("qty", 1)))
        for item in cart
    ),
    2,
)

    tax = round(subtotal * 0.05, 2)
    delivery_charge = 0.0 if subtotal == 0 or subtotal >= 500 else 40.0
    grand_total = round(subtotal + tax + delivery_charge, 2)
    
    st.session_state["subtotal"] = subtotal
    st.session_state["tax"] = tax
    st.session_state["delivery_charge"] = delivery_charge
    st.session_state["total"] = grand_total
    st.session_state["grand_total"] = grand_total

    logged_in = bool(st.session_state.get("logged_in") or st.session_state.get("is_logged_in"))
    st.session_state["logged_in"] = logged_in
    st.session_state["is_logged_in"] = logged_in
    st.session_state["customer_name"] = st.session_state.get("customer_name") or st.session_state.get("user", "")
    if not st.session_state.get("order_id") and st.session_state.get("reference_no"):
        st.session_state["order_id"] = st.session_state["reference_no"]


def inject_theme() -> None:
    st.markdown(
        """
        <style>
        :root { --blue:#056DAE; --navy:#003B70; --light-blue:#EAF5FB; --background:#F6F9FC; --text:#17324D; --muted:#607D94; --green:#16803C; }
        .stApp { background:var(--background); color:var(--text); }
        [data-testid="stHeader"] { background:transparent; }
        .block-container { max-width:1200px; padding-top:1.25rem; padding-bottom:2rem; }
        [data-testid="stSidebar"] { background:white; border-right:1px solid #DCEBF3; }
        [data-testid="stSidebar"] .block-container { padding-top:1.25rem; }
        .topbar { display:flex; align-items:center; justify-content:space-between; margin-bottom:.9rem; }
        .brand { display:flex; align-items:center; gap:.7rem; }
        .brand-mark { width:40px; height:40px; display:grid; place-items:center; border-radius:13px; background:var(--blue); color:white; font-size:1.35rem; box-shadow:0 6px 16px rgba(5,109,174,.2); }
        .brand-name { color:var(--navy); font-size:1.2rem; line-height:1.1; font-weight:800; }
        .brand-subtitle { color:var(--muted); font-size:.72rem; margin-top:.18rem; }
        .workshop-badge { background:var(--light-blue); color:var(--blue); border:1px solid #C9E5F3; border-radius:999px; padding:.43rem .78rem; font-size:.72rem; font-weight:800; }
        .stepper { display:flex; align-items:center; gap:.25rem; background:white; border:1px solid #DCEBF3; border-radius:15px; padding:.65rem .8rem; margin-bottom:1.7rem; box-shadow:0 3px 12px rgba(0,59,112,.04); }
        .step { flex:1; color:#9AAEBC; text-align:center; font-size:.71rem; font-weight:700; }
        .step.active { color:var(--blue); }
        .step.done { color:var(--green); }
        .step-dot { width:9px; height:9px; margin:0 auto .25rem; border-radius:50%; background:#D7E3EA; }
        .step.active .step-dot { width:11px; height:11px; background:var(--blue); box-shadow:0 0 0 4px var(--light-blue); }
        .step.done .step-dot { background:var(--green); }
        .stButton > button { border-radius:10px; min-height:2.45rem; font-weight:700; }
        .stTextInput input { border-radius:10px; border-color:#C9DDE8; min-height:2.45rem; }
        .app-footer { border-top:1px solid #DCEBF3; color:var(--muted); font-size:.72rem; margin-top:2rem; padding-top:.75rem; display:flex; justify-content:space-between; }
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
    current = st.session_state.get("current_module", "menu")
    active = {"login": "Login", "menu": "Menu", "payment": "Pay", "delivery": "Delivery"}.get(current, "Menu")
    active_index = steps.index(active)
    step_html = []
    for index, label in enumerate(steps):
        status = "done" if index < active_index else "active" if index == active_index else ""
        step_html.append(f"<div class='step {status}'><div class='step-dot'></div>{label}</div>")
    st.markdown(f"<div class='stepper'>{''.join(step_html)}</div>", unsafe_allow_html=True)


def load_order_status_module():
    status_file = ROOT / "Order_Status" / "Order_Status.py"
    spec = spec_from_file_location("stem_order_status", status_file)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load {status_file}")
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def render_delivery() -> None:
    try:
        status_module = load_order_status_module()
        status_module.render_live_tracker_dashboard()
    except Exception as error:
        st.error("The delivery module could not be loaded.")
        st.exception(error)


normalise_order_state()
inject_theme()

# Payment's success screen sets this before rerunning. Route directly to
# Delivery so PaymentModule/payment.py does not use its legacy loader path.
if st.session_state.get("show_order_status", False):
    st.session_state["current_module"] = "delivery"

current_module = st.session_state.get("current_module", "menu")

if current_module in {"menu", "login"}:
    render_header()
    render_stepper()

if current_module == "menu":
    render_menu()
elif current_module == "login":
    render_login()
elif current_module == "payment":
    render_payment()
elif current_module == "delivery":
    render_delivery()
else:
    st.error(f"Unknown application module: {current_module}")

st.markdown(
    "<div class='app-footer'><span>STEM Workshop</span><span>Educational simulation only</span></div>",
    unsafe_allow_html=True,
)
