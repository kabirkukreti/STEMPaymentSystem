"""
====================================================
Payment Module
Food Ordering Application

Entry function:
    render_payment()

Expected shared session state:
    cart
    subtotal
    tax
    grand_total

This module provides:
    - Order summary
    - Card validation
    - Demo OTP generation
    - OTP verification
    - UPI payment
    - Payment success screen

Keep this module free of st.set_page_config().
The main application owns page configuration/navigation.
"""

from pathlib import Path
import random
import string
from textwrap import dedent

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components


# -------------------------------------------------
# FILES
# -------------------------------------------------

APP_DIR = Path(__file__).resolve().parent
CARD_FILE = APP_DIR / "cards.csv"
OTP_COMPONENT_DIR = APP_DIR / "otp_component"


# -------------------------------------------------
# OTP COMPONENT
# -------------------------------------------------

_otp_component = components.declare_component(
    "food_lab_payment_otp",
    path=str(OTP_COMPONENT_DIR),
)


def otp_input(initial_value="", reset_token=0):
    return _otp_component(
        initial_value=initial_value,
        reset_token=reset_token,
        default=None,
        key="payment_otp_component",
    )


# -------------------------------------------------
# SESSION STATE
# -------------------------------------------------

def initialise_state():
    defaults = {
        "payment_status": "PENDING",
        "payment_method": "",
        "reference_no": "",
        "show_otp": False,
        "generated_otp": "",
        "otp_verified": False,
        "otp_reset_token": 0,
        "card_number": "",
        "card_name": "",
        "payment_success": False,
    }

    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


# -------------------------------------------------
# HTML / CSS HELPERS
# -------------------------------------------------

def render_html(html):
    html = dedent(html).strip()

    if hasattr(st, "html"):
        st.html(html)
    else:
        st.markdown(html, unsafe_allow_html=True)


def render_css(css):
    css = dedent(css).strip()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def inject_styles():
    render_css(
        """
        /* ---------- Application shell ---------- */

        [data-testid="stHeader"],
        [data-testid="stToolbar"],
        [data-testid="stDecoration"] {
            display: none !important;
        }

        .stApp {
            background: #F6F9FC;
        }

        [data-testid="stMainBlockContainer"],
        .block-container {
            max-width: 1320px !important;
            padding-top: 0.55rem !important;
            padding-bottom: 1.2rem !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }

        /* ---------- Header ---------- */

        .food-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
            padding: 8px 10px 7px;
        }

        .food-brand {
            display: flex;
            align-items: center;
            gap: 11px;
        }

        .food-logo {
            width: 42px;
            height: 42px;
            border-radius: 8px;
            background: #EAF5FB;
            color: #056DAE;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 22px;
            flex-shrink: 0;
        }

        .food-title {
            color: #003B70;
            font-size: 22px;
            line-height: 23px;
            font-weight: 800;
        }

        .food-subtitle {
            color: #718096;
            font-size: 11px;
            margin-top: 2px;
        }

        .workshop-badge {
            border: 1px solid #BFDDEB;
            background: #F3FAFD;
            color: #056DAE;
            border-radius: 22px;
            padding: 8px 16px;
            font-size: 11px;
            font-weight: 800;
            letter-spacing: .02em;
        }

        /* ---------- Six-step progress ---------- */

        .progress-shell {
            background: #FFFFFF;
            border: 1px solid #E1E5EA;
            border-radius: 22px;
            padding: 10px 20px;
            margin: 3px 0 20px;
            box-shadow: 0 3px 12px rgba(0, 59, 112, .04);
        }

        .progress-container {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 6px;
        }

        .progress-step {
            display: flex;
            align-items: center;
            gap: 7px;
            color: #9AA5B1;
            font-size: 12px;
            font-weight: 600;
            white-space: nowrap;
        }

        .progress-step.completed {
            color: #056DAE;
        }

        .progress-step.active {
            color: #056DAE;
            font-weight: 900;
        }

        .progress-circle {
            width: 18px;
            height: 18px;
            border-radius: 50%;
            background: #E1E7EC;
            color: #8D98A4;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 9px;
            font-weight: 800;
        }

        .progress-circle.completed {
            background: #16803C;
            color: #FFFFFF;
        }

        .progress-circle.active {
            background: #056DAE;
            color: #FFFFFF;
            box-shadow: 0 0 0 4px #EAF5FB;
        }

        .progress-line {
            flex: 1;
            min-width: 18px;
            height: 1px;
            background: #DCE2E8;
        }

        /* ---------- Page headings ---------- */

        .page-kicker {
            color: #056DAE;
            font-size: 11px;
            font-weight: 900;
            letter-spacing: .16em;
            text-transform: uppercase;
            margin-bottom: 3px;
        }

        .page-title {
            color: #003B70;
            font-size: 31px;
            line-height: 34px;
            font-weight: 800;
            letter-spacing: -.02em;
            margin-bottom: 4px;
        }

        .page-description {
            color: #718096;
            font-size: 13px;
            margin-bottom: 14px;
        }

        /* ---------- Cards ---------- */

        .food-card {
            background: #FFFFFF;
            border: 1px solid #E0E5EA;
            border-radius: 15px;
            padding: 15px 17px;
            box-shadow: 0 5px 18px rgba(0, 59, 112, .045);
            margin-bottom: 12px;
        }

        .section-title {
            color: #003B70;
            font-size: 16px;
            font-weight: 800;
            margin-bottom: 11px;
        }

        .section-title-blue {
            color: #056DAE;
            font-size: 14px;
            font-weight: 900;
            letter-spacing: .01em;
            margin-bottom: 10px;
        }

        /* ---------- Order ---------- */

        .order-item {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
            padding: 9px 0;
            border-bottom: 1px solid #EEF1F4;
        }

        .order-item:last-child {
            border-bottom: none;
        }

        .order-name {
            color: #003B70;
            font-size: 13px;
            font-weight: 700;
        }

        .order-qty {
            color: #718096;
            font-size: 10px;
            margin-top: 2px;
        }

        .order-price {
            color: #003B70;
            font-size: 13px;
            font-weight: 800;
            white-space: nowrap;
        }

        /* ---------- Total card ---------- */

        .bill-card {
            background: #EAF5FB;
            border: 1px solid #CDE8F3;
            border-radius: 14px;
            padding: 14px 16px;
        }

        .bill-row {
            display: flex;
            justify-content: space-between;
            padding: 5px 0;
            color: #718096;
            font-size: 12px;
        }

        .bill-row strong {
            color: #003B70;
        }

        .grand-total {
            display: flex;
            justify-content: space-between;
            border-top: 1px solid #C7DFEA;
            margin-top: 7px;
            padding-top: 10px;
            color: #003B70;
            font-size: 17px;
            font-weight: 900;
        }

        .grand-total-value {
            color: #056DAE;
        }

        /* ---------- Payment controls ---------- */

        .payment-info {
            background: #EAF5FB;
            border-radius: 9px;
            padding: 9px 11px;
            margin: 8px 0 12px;
            color: #003B70;
            font-size: 11px;
        }

        .payment-label {
            color: #003B70;
            font-size: 12px;
            font-weight: 800;
            margin-bottom: 4px;
        }

        div[data-testid="stTextInput"] {
            margin-bottom: 7px;
        }

        div[data-testid="stTextInput"] input {
            min-height: 42px;
            height: 42px;
            border-radius: 9px;
            border-color: #D6DDE4;
            font-size: 13px;
        }

        div[data-testid="stTextInput"] input:focus {
            border-color: #056DAE;
            box-shadow: 0 0 0 3px #056DAE18;
        }

        div[data-testid="stButton"] {
            margin-top: 5px;
        }

        div[data-testid="stButton"] > button {
            min-height: 42px;
            height: 42px;
            border-radius: 9px;
            font-size: 13px;
            font-weight: 800;
        }

        div[data-testid="stButton"] > button[kind="primary"] {
            background: #056DAE;
            border-color: #056DAE;
            color: #FFFFFF;
        }

        div[data-testid="stButton"] > button[kind="primary"]:hover {
            background: #045A91;
            border-color: #045A91;
        }

        div[data-testid="stRadio"] {
            margin-bottom: 7px;
        }

        div[data-testid="stRadio"] label {
            font-size: 12px;
            font-weight: 700;
        }

        /* ---------- OTP ---------- */

        .otp-heading {
            color: #003B70;
            font-size: 20px;
            font-weight: 900;
            margin: 3px 0 5px;
        }

        .otp-description {
            color: #718096;
            font-size: 12px;
            margin-bottom: 10px;
        }

        /* ---------- Mobile ---------- */

        .mobile-card {
            min-height: 100%;
        }

        .phone-wrapper {
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 4px 0 7px;
        }

        .phone {
            width: 205px;
            height: 320px;
            background: #111827;
            border-radius: 31px;
            padding: 7px;
            box-shadow: 0 14px 30px rgba(0, 0, 0, .18);
        }

        .phone-screen {
            background: #FFFFFF;
            border-radius: 25px;
            height: 306px;
            overflow: hidden;
        }

        .phone-notch {
            width: 74px;
            height: 16px;
            background: #111827;
            border-radius: 0 0 11px 11px;
            margin: 0 auto;
        }

        .phone-header {
            display: flex;
            align-items: center;
            gap: 7px;
            padding: 8px 11px;
            border-bottom: 1px solid #ECEFF2;
            color: #003B70;
            font-size: 11px;
            font-weight: 800;
        }

        .phone-icon {
            width: 24px;
            height: 24px;
            border-radius: 50%;
            background: #056DAE;
            color: #FFFFFF;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 11px;
        }

        .message-area {
            padding: 10px;
        }

        .message-time {
            text-align: center;
            color: #8A95A2;
            font-size: 8px;
            margin-bottom: 8px;
        }

        .message-bubble {
            background: #EAF5FB;
            border-radius: 14px 14px 14px 4px;
            padding: 12px;
            color: #003B70;
        }

        .message-brand {
            color: #056DAE;
            font-size: 12px;
            font-weight: 900;
            margin-bottom: 7px;
        }

        .message-text {
            font-size: 9px;
            line-height: 1.45;
        }

        .otp-display {
            color: #E31837;
            font-size: 20px;
            font-weight: 900;
            letter-spacing: 3px;
            margin: 9px 0;
            white-space: nowrap;
        }

        .message-small {
            color: #657080;
            font-size: 8px;
            line-height: 1.35;
            margin-top: 8px;
        }

        .waiting-card {
            background: #F8FAFC;
            border: 1px dashed #C8D4DE;
            border-radius: 12px;
            padding: 20px 14px;
            text-align: center;
            color: #718096;
            font-size: 12px;
            line-height: 1.5;
        }

        .waiting-icon {
            font-size: 30px;
            margin-bottom: 6px;
        }

        /* ---------- Success ---------- */

        .success-card {
            background: #F0FAF4;
            border: 1px solid #B7E4C7;
            border-radius: 17px;
            padding: 30px 24px;
            text-align: center;
        }

        .success-icon {
            font-size: 42px;
        }

        .success-title {
            color: #16803C;
            font-size: 27px;
            font-weight: 900;
            margin-top: 3px;
        }

        .success-text {
            color: #587062;
            font-size: 13px;
            margin-top: 5px;
        }

        .reference {
            max-width: 380px;
            margin: 15px auto 0;
            background: #FFFFFF;
            border-radius: 9px;
            padding: 10px;
            color: #003B70;
            font-size: 12px;
            font-weight: 800;
        }

        /* ---------- Alerts ---------- */

        div[data-testid="stAlert"] {
            border-radius: 9px;
            font-size: 12px;
        }

        hr {
            margin: 8px 0 !important;
        }


        /* ---------- Three-Column Payment Layout ---------- */

        .horizontal-order-card,
        .horizontal-bill-card,
        .payment-action-card {
            height: 100%;
            margin-bottom: 0;
        }

        .horizontal-bill-card {
            min-height: 100%;
        }

        .horizontal-order-card .order-item {
            padding: 10px 0;
        }

        .horizontal-bill-card .section-title {
            margin-bottom: 14px;
        }

        .horizontal-bill-card .bill-row {
            padding: 8px 0;
        }

        /* OTP and mobile preview remain horizontally aligned. */
        .payment-action-card {
            min-height: 100%;
        }


        /* ---------- Compact horizontal payment layout ---------- */

        .compact-card {
            margin-bottom: 0;
            min-height: 100%;
        }

        .compact-order-item {
            padding: 8px 0;
        }

        .compact-card .section-title {
            font-size: 14px;
            margin-bottom: 8px;
        }

        .compact-card .order-name {
            font-size: 12px;
        }

        .compact-card .order-qty {
            font-size: 9px;
        }

        .compact-card .order-price {
            font-size: 11px;
        }

        .compact-card .bill-row {
            font-size: 10px;
            padding: 5px 0;
            gap: 5px;
        }

        .compact-card .grand-total {
            font-size: 14px;
            padding-top: 8px;
        }

        .payment-section-title {
            color: #056DAE;
            font-size: 15px;
            font-weight: 900;
            background: #FFFFFF;
            border: 1px solid #E0E5EA;
            border-radius: 14px;
            padding: 12px 14px;
            margin-bottom: 10px;
            box-shadow: 0 5px 18px rgba(0, 59, 112, .045);
        }

        @media (max-width: 1250px) {
            .compact-card .order-price {
                font-size: 10px;
            }

            .compact-card .bill-row {
                font-size: 9px;
            }
        }

        /* ---------- Responsive ---------- */



        @media (max-width: 900px) {
            .progress-shell {
                overflow-x: auto;
            }

            .progress-container {
                min-width: 720px;
            }

            .food-title {
                font-size: 19px;
            }

            .page-title {
                font-size: 27px;
            }
        }
        """
    )


# -------------------------------------------------
# DATA
# -------------------------------------------------

def load_cards():
    if CARD_FILE.exists():
        return pd.read_csv(
            CARD_FILE,
            dtype={"card_number": str},
        )

    return pd.DataFrame(
        columns=["card_number", "card_name", "balance"]
    )


def save_cards(df):
    df.to_csv(CARD_FILE, index=False)


def deduct_balance(card_number, amount):
    cards = load_cards()

    if cards.empty:
        return (
            False,
            "Card database not found. Create cards.csv beside payment.py.",
        )

    row = cards[
        cards["card_number"].astype(str) == str(card_number)
    ]

    if row.empty:
        return False, "Invalid card."

    index = row.index[0]
    balance = float(cards.loc[index, "balance"])

    if balance < amount:
        return False, "Insufficient balance."

    cards.loc[index, "balance"] = balance - amount
    save_cards(cards)

    return True, "Payment Successful"


def generate_otp():
    otp = "".join(
        random.choices(string.digits, k=6)
    )

    st.session_state.generated_otp = otp
    return otp


def clear_otp():
    st.session_state.generated_otp = ""
    st.session_state.otp_reset_token += 1


# -------------------------------------------------
# SHARED DESIGN
# -------------------------------------------------

def render_header():
    render_html(
        """
        <div class="food-header">
            <div class="food-brand">
                <div class="food-logo">🍴</div>
                <div>
                    <div class="food-title">Food Lab</div>
                    <div class="food-subtitle">
                        A STEM Workshop application
                    </div>
                </div>
            </div>

            <div class="workshop-badge">
                STEM WORKSHOP
            </div>
        </div>
        """
    )


def render_progress():
    # Pay is active while payment is in progress.
    # Once payment succeeds, Pay becomes a completed green step
    # with a check mark, matching Login and Menu.
    payment_completed = st.session_state.get(
        "payment_success",
        False,
    )

    pay_class = (
        "completed"
        if payment_completed
        else "active"
    )

    pay_circle = (
        "✓"
        if payment_completed
        else "3"
    )

    pay_step_html = f"""
                <div class="progress-step {pay_class}">
                    <div class="progress-circle {pay_class}">
                        {pay_circle}
                    </div>
                    Pay
                </div>
    """

    render_html(
        f"""
        <div class="progress-shell">
            <div class="progress-container">

                <div class="progress-step completed">
                    <div class="progress-circle completed">✓</div>
                    Login
                </div>

                <div class="progress-line"></div>

                <div class="progress-step completed">
                    <div class="progress-circle completed">✓</div>
                    Menu
                </div>

                <div class="progress-line"></div>

                {pay_step_html}

                <div class="progress-line"></div>

                <div class="progress-step">
                    <div class="progress-circle">4</div>
                    Bank
                </div>

                <div class="progress-line"></div>

                <div class="progress-step">
                    <div class="progress-circle">5</div>
                    Receipt
                </div>

                <div class="progress-line"></div>

                <div class="progress-step">
                    <div class="progress-circle">6</div>
                    Delivery
                </div>

            </div>
        </div>
        """
    )


def render_page_heading():
    render_html(
        """
        <div class="page-kicker">PAYMENT</div>
        <div class="page-title">
            Complete your payment
        </div>
        <div class="page-description">
            Choose your preferred payment method and complete your order securely.
        </div>
        """
    )


def render_order_summary(cart, subtotal, tax, grand_total):
    html = """
        <div class="food-card">
            <div class="section-title">
                Your order
            </div>
    """

    for item in cart:
        name = item.get("item", "Food Item")
        qty = int(item.get("qty", 1))
        price = float(item.get("price", 0))

        html += f"""
            <div class="order-item">
                <div>
                    <div class="order-name">{name}</div>
                    <div class="order-qty">Qty: {qty}</div>
                </div>

                <div class="order-price">
                    ₹ {price * qty:.2f}
                </div>
            </div>
        """

    html += """
        </div>
    """

    render_html(html)

    render_html(
        f"""
        <div class="bill-card">
            <div class="bill-row">
                <span>Subtotal</span>
                <strong>₹ {subtotal:.2f}</strong>
            </div>

            <div class="bill-row">
                <span>Tax (5%)</span>
                <strong>₹ {tax:.2f}</strong>
            </div>

            <div class="bill-row">
                <span>Delivery</span>
                <strong style="color:#16803C;">FREE</strong>
            </div>

            <div class="grand-total">
                <span>Total</span>
                <span class="grand-total-value">
                    ₹ {grand_total:.2f}
                </span>
            </div>
        </div>
        """
    )


def render_quick_tip():
    render_html(
        """
        <div class="food-card">
            <div class="section-title">
                ✨ Quick tip
            </div>

            <div style="
                color:#4A5568;
                font-size:12px;
                line-height:1.5;
            ">
                Keep your card details ready. A one-time OTP
                will be generated for this transaction.
            </div>
        </div>
        """
    )


def render_mobile_otp():
    otp = st.session_state.get("generated_otp", "")
    display_otp = otp if otp else "------"

    render_html(
        f"""
        <div class="food-card mobile-card">

            <div class="section-title-blue">
                📱 Mobile Verification
            </div>

            <div class="phone-wrapper">

                <div class="phone">

                    <div class="phone-screen">

                        <div class="phone-notch"></div>

                        <div class="phone-header">
                            <div class="phone-icon">💬</div>
                            Code Café
                        </div>

                        <div class="message-area">

                            <div class="message-time">
                                Today, 9:42 AM
                            </div>

                            <div class="message-bubble">

                                <div class="message-brand">
                                    Code Café
                                </div>

                                <div class="message-text">
                                    Your payment OTP is
                                </div>

                                <div class="otp-display">
                                    {display_otp}
                                </div>

                                <div class="message-text">
                                    Valid for this transaction only.
                                </div>

                                <div class="message-small">
                                    Do not share this code with anyone.
                                </div>

                            </div>

                        </div>

                    </div>

                </div>

            </div>
        </div>
        """
    )


def render_waiting_mobile():
    render_html(
        """
        <div class="food-card mobile-card">
            <div class="section-title-blue">
                📱 Mobile Verification
            </div>

            <div class="waiting-card">
                <div class="waiting-icon">📱</div>
                <strong style="color:#003B70;">
                    OTP will appear here
                </strong>
                <br>
                Generate an OTP to display the
                payment message on the mobile screen.
            </div>
        </div>
        """
    )


# -------------------------------------------------
# CARD PAYMENT
# -------------------------------------------------

def render_card_payment():
    render_html(
        """
        <div class="section-title">
            💳 Card Payment
        </div>
        """
    )

    card_number = st.text_input(
        "Card Number",
        max_chars=16,
        placeholder="Enter 16-digit card number",
        key="payment_card_number",
    )

    card_name = st.text_input(
        "Card Holder Name",
        placeholder="Enter card holder name",
        key="payment_card_name",
    )

    render_html(
        """
        <div class="payment-info">
            🛡️ An OTP will be generated for this transaction.
        </div>
        """
    )

    if st.button(
        "Generate OTP  →",
        type="primary",
        use_container_width=True,
        key="payment_generate_otp",
    ):
        if not card_number.strip():
            st.error("Card Number is required.")
            return

        if not card_number.isdigit():
            st.error("Card Number should contain digits only.")
            return

        if len(card_number) != 16:
            st.error(
                "Card Number must contain exactly 16 digits."
            )
            return

        if not card_name.strip():
            st.error("Card Holder Name is required.")
            return

        cards = load_cards()

        if cards.empty:
            st.error(
                "Card database not found. Create cards.csv beside payment.py."
            )
            return

        if cards[
            cards["card_number"].astype(str) == str(card_number)
        ].empty:
            st.error("Invalid card number.")
            return

        otp = generate_otp()

        st.session_state.card_number = card_number
        st.session_state.card_name = card_name
        st.session_state.show_otp = True
        st.session_state.otp_verified = False
        st.session_state.otp_reset_token += 1

        # Demo only: show OTP in the UI toast as well as on the mobile mock-up.
        st.toast(f"Demo OTP: {otp}")

        st.rerun()


# -------------------------------------------------
# OTP VERIFICATION
# -------------------------------------------------

def render_otp_verification(grand_total):
    render_html(
        """
        <div class="otp-heading">
            🔐 Verify your payment
        </div>

        <div class="otp-description">
            Enter the 6-digit OTP displayed on the mobile screen.
        </div>
        """
    )

    entered = otp_input(
        reset_token=st.session_state.get(
            "otp_reset_token",
            0,
        )
    )

    entered = "" if entered is None else str(entered)

    verify_col, back_col = st.columns([3, 1])

    with verify_col:
        verify = st.button(
            "✓ Verify Payment",
            type="primary",
            use_container_width=True,
            key="verify_otp_button",
        )

    with back_col:
        back = st.button(
            "← Back",
            use_container_width=True,
            key="back_otp_button",
        )

    if back:
        clear_otp()

        st.session_state.show_otp = False
        st.session_state.card_number = ""
        st.session_state.card_name = ""

        st.rerun()

    if not verify:
        return

    if len(entered) != 6 or not entered.isdigit():
        st.error("Please enter all 6 OTP digits.")
        return

    stored = st.session_state.get(
        "generated_otp",
        "",
    )

    if not stored:
        st.error(
            "OTP is no longer available. Generate a new OTP."
        )
        return

    if entered != stored:
        st.error("Invalid OTP.")
        return

    success, message = deduct_balance(
        st.session_state.card_number,
        grand_total,
    )

    if not success:
        st.error(message)
        return

    st.session_state.payment_status = "SUCCESS"
    st.session_state.payment_method = "Card"
    st.session_state.reference_no = (
        f"CAFE-{random.randint(100000, 999999)}"
    )
    st.session_state.otp_verified = True
    st.session_state.payment_success = True

    clear_otp()

    st.session_state.show_otp = False

    st.rerun()


# -------------------------------------------------
# UPI PAYMENT
# -------------------------------------------------

def render_upi_payment():
    render_html(
        """
        <div class="section-title">
            📱 UPI Payment
        </div>
        """
    )

    upi = st.text_input(
        "UPI ID",
        placeholder="example@upi",
        key="payment_upi_id",
    )

    render_html(
        """
        <div class="payment-info">
            🔒 Enter your UPI ID to complete the payment.
        </div>
        """
    )

    if st.button(
        "Pay Now  →",
        type="primary",
        use_container_width=True,
        key="upi_pay_button",
    ):
        if not upi.strip():
            st.error("UPI ID is required.")
            return

        if "@" not in upi:
            st.error("Please enter a valid UPI ID.")
            return

        st.session_state.payment_status = "SUCCESS"
        st.session_state.payment_method = "UPI"
        st.session_state.reference_no = (
            f"CAFE-{random.randint(100000, 999999)}"
        )
        st.session_state.payment_success = True

        st.rerun()


# -------------------------------------------------
# SUCCESS
# -------------------------------------------------

def render_success(grand_total):
    render_html(
        f"""
        <div class="food-card">

            <div class="success-card">

                <div class="success-icon">
                    🎉
                </div>

                <div class="success-title">
                    Payment Successful
                </div>

                <div class="success-text">
                    Your payment has been completed successfully.
                </div>

                <div class="reference">
                    Reference Number
                    <br><br>
                    {st.session_state.reference_no}
                </div>

            </div>

        </div>
        """
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            "Amount Paid",
            f"₹ {grand_total:.2f}",
        )

    with c2:
        st.metric(
            "Payment Method",
            st.session_state.payment_method,
        )

    with c3:
        if st.session_state.payment_method == "Card":
            st.metric(
                "Card",
                "**** " + st.session_state.card_number[-4:],
            )
        else:
            st.metric(
                "Status",
                "PAID",
            )


# -------------------------------------------------
# MAIN ENTRY POINT
# -------------------------------------------------

def render_payment():
    initialise_state()
    inject_styles()

    cart = st.session_state.get("cart", [])
    subtotal = float(st.session_state.get("subtotal", 0))
    tax = float(st.session_state.get("tax", 0))
    grand_total = float(st.session_state.get("grand_total", 0))

    render_header()
    render_progress()

    if st.session_state.get("payment_success", False):
        render_success(grand_total)
        return

    render_page_heading()

    if not cart:
        st.info("Cart is empty.")
        return

    # =========================================================
    # COMPACT FOUR-COLUMN PAYMENT LAYOUT
    #
    # Initial payment:
    #   Order | Bill | Payment | Quick Tip
    #
    # OTP:
    #   Order | Bill | OTP Input | Mobile
    #
    # This keeps every section narrow, distinct and horizontally
    # aligned across the page.
    # =========================================================

    if st.session_state.get("show_otp", False):

        order_col, bill_col, otp_col, mobile_col = st.columns(
            [0.92, 0.72, 1.08, 0.72],
            gap="small",
        )

        # -----------------------------------------------------
        # ORDER
        # -----------------------------------------------------
        with order_col:
            order_html = """
            <div class="food-card compact-card">
                <div class="section-title">Your order</div>
            """

            for item in cart:
                name = item.get("item", "Food Item")
                qty = int(item.get("qty", 1))
                price = float(item.get("price", 0))

                order_html += f"""
                    <div class="order-item compact-order-item">
                        <div>
                            <div class="order-name">{name}</div>
                            <div class="order-qty">Qty: {qty}</div>
                        </div>
                        <div class="order-price">
                            ₹ {price * qty:.2f}
                        </div>
                    </div>
                """

            order_html += "</div>"
            render_html(order_html)

        # -----------------------------------------------------
        # BILL
        # -----------------------------------------------------
        with bill_col:
            render_html(
                f"""
                <div class="bill-card compact-card">

                    <div class="section-title">
                        Bill details
                    </div>

                    <div class="bill-row">
                        <span>Subtotal</span>
                        <strong>₹ {subtotal:.2f}</strong>
                    </div>

                    <div class="bill-row">
                        <span>Tax (5%)</span>
                        <strong>₹ {tax:.2f}</strong>
                    </div>

                    <div class="bill-row">
                        <span>Delivery</span>
                        <strong style="color:#16803C;">FREE</strong>
                    </div>

                    <div class="grand-total">
                        <span>Total</span>
                        <span class="grand-total-value">
                            ₹ {grand_total:.2f}
                        </span>
                    </div>

                </div>
                """
            )

        # -----------------------------------------------------
        # OTP INPUT
        # -----------------------------------------------------
        with otp_col:
            render_html(
                """
                <div class="food-card compact-card">
                    <div class="section-title-blue">
                        🔐 OTP Verification
                    </div>

                    <div class="otp-heading">
                        Verify your payment
                    </div>

                    <div class="otp-description">
                        Enter the 6-digit OTP shown on your mobile.
                    </div>
                """
            )

            entered = otp_input(
                reset_token=st.session_state.get(
                    "otp_reset_token",
                    0,
                )
            )

            entered = "" if entered is None else str(entered)

            verify = st.button(
                "✓ Verify Payment",
                type="primary",
                use_container_width=True,
                key="verify_otp_button",
            )

            back = st.button(
                "← Back",
                use_container_width=True,
                key="back_otp_button",
            )

            render_html("</div>")

            if back:
                clear_otp()
                st.session_state.show_otp = False
                st.session_state.card_number = ""
                st.session_state.card_name = ""
                st.rerun()

            if verify:
                if len(entered) != 6 or not entered.isdigit():
                    st.error("Please enter all 6 OTP digits.")
                else:
                    stored = st.session_state.get(
                        "generated_otp",
                        "",
                    )

                    if not stored:
                        st.error(
                            "OTP is no longer available. "
                            "Please generate a new OTP."
                        )
                    elif entered != stored:
                        st.error("Invalid OTP.")
                    else:
                        success, message = deduct_balance(
                            st.session_state.card_number,
                            grand_total,
                        )

                        if not success:
                            st.error(message)
                        else:
                            st.session_state.payment_status = "SUCCESS"
                            st.session_state.payment_method = "Card"
                            st.session_state.reference_no = (
                                f"CAFE-{random.randint(100000, 999999)}"
                            )
                            st.session_state.otp_verified = True
                            st.session_state.payment_success = True
                            clear_otp()
                            st.session_state.show_otp = False
                            st.rerun()

        # -----------------------------------------------------
        # MOBILE
        # -----------------------------------------------------
        with mobile_col:
            render_mobile_otp()

    else:

        order_col, bill_col, payment_col, tip_col = st.columns(
            [0.92, 0.72, 1.18, 0.55],
            gap="small",
        )

        # -----------------------------------------------------
        # ORDER
        # -----------------------------------------------------
        with order_col:
            order_html = """
            <div class="food-card compact-card">
                <div class="section-title">Your order</div>
            """

            for item in cart:
                name = item.get("item", "Food Item")
                qty = int(item.get("qty", 1))
                price = float(item.get("price", 0))

                order_html += f"""
                    <div class="order-item compact-order-item">
                        <div>
                            <div class="order-name">{name}</div>
                            <div class="order-qty">Qty: {qty}</div>
                        </div>
                        <div class="order-price">
                            ₹ {price * qty:.2f}
                        </div>
                    </div>
                """

            order_html += "</div>"
            render_html(order_html)

        # -----------------------------------------------------
        # BILL
        # -----------------------------------------------------
        with bill_col:
            render_html(
                f"""
                <div class="bill-card compact-card">

                    <div class="section-title">
                        Bill details
                    </div>

                    <div class="bill-row">
                        <span>Subtotal</span>
                        <strong>₹ {subtotal:.2f}</strong>
                    </div>

                    <div class="bill-row">
                        <span>Tax (5%)</span>
                        <strong>₹ {tax:.2f}</strong>
                    </div>

                    <div class="bill-row">
                        <span>Delivery</span>
                        <strong style="color:#16803C;">FREE</strong>
                    </div>

                    <div class="grand-total">
                        <span>Total</span>
                        <span class="grand-total-value">
                            ₹ {grand_total:.2f}
                        </span>
                    </div>

                </div>
                """
            )

        # -----------------------------------------------------
        # PAYMENT
        # -----------------------------------------------------
        with payment_col:
            st.markdown(
                '<div class="payment-section-title">💳 Payment</div>',
                unsafe_allow_html=True,
            )

            payment_mode = st.radio(
                "Choose Payment Method",
                ["Card", "UPI"],
                horizontal=True,
                key="payment_mode_selector",
                label_visibility="collapsed",
            )

            if payment_mode == "Card":
                render_card_payment()
            else:
                render_upi_payment()

        # -----------------------------------------------------
        # QUICK TIP
        # -----------------------------------------------------
        with tip_col:
            render_quick_tip()

