import streamlit as st
import pandas as pd
import os
import time

def render_html(html):
    """Render HTML as HTML, never as escaped source text."""
    html = html.strip()
    if hasattr(st, "html"):
        st.html(html)
    else:
        st.markdown(html, unsafe_allow_html=True)


# Page Configuration with a clean centered layout and pizza tab icon

# Store all styling rules in a single source of truth variable
SHARED_CSS = """
<style>
    /* Completely hide left side menu panel, options buttons, and margins */
    [data-testid="stSidebar"], section[data-testid="stSidebarViewContainer"] {
        display: none !important;
        width: 0px !important;
    }
    [data-testid="stHeader"] {
        display: none !important;
    }
    
    /* Optimized: Reduced vertical padding to fit within standard height viewports without scrollbars */
    div.block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 0.5rem !important;
        min-height: calc(100vh - 1rem) !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 1400px !important;
        width: 100% !important;
        margin: 0 auto !important;
    }

    /* Global Typography matching Food Lab baseline styling */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #F8FAFC !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
    }
    
    /* Exact Food Lab Branding Header Bar Layout with minimized bottom margin */
    .brand-header {
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
        background: transparent !important;
        padding: 0.2rem 0 !important;
        margin-bottom: 0.6rem !important;
    }
    .brand-left {
        display: flex !important;
        align-items: center !important;
        gap: 0.8rem !important;
    }
    .brand-logo-icon {
        background-color: #0056B3 !important;
        width: 36px !important;
        height: 36px !important;
        border-radius: 8px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        color: white !important;
        font-size: 1.2rem !important;
        box-shadow: 0 4px 12px rgba(0, 86, 179, 0.1) !important;
    }
    .brand-text-title {
        color: #002D62 !important;
        font-weight: 800 !important;
        font-size: 1.4rem !important;
        line-height: 1.1 !important;
    }
    .brand-text-sub {
        color: #64748B !important;
        font-size: 0.75rem !important;
        margin-top: 0.1rem !important;
    }
    .brand-badge-button {
        border: 1px solid #D6E4F0 !important;
        background-color: #EBF3FA !important;
        color: #0056B3 !important;
        font-weight: 700 !important;
        font-size: 0.65rem !important;
        padding: 0.3rem 0.6rem !important;
        border-radius: 20px !important;
        letter-spacing: 0.05em !important;
        text-transform: uppercase !important;
    }
    
    /* Compact Stationary Page Header Card Container */
    .page-header-card {
        background: #FFFFFF !important;
        padding: 0.8rem 1.2rem !important;
        border-radius: 14px !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important;
        border: 1px solid #E2E8F0 !important;
        margin-bottom: 0.6rem !important;
    }
    
    /* Compact Dedicated Order Status Bar Card Container */
    .tracker-wrapper {
        width: 100% !important;
        box-sizing: border-box !important;
        background: #FFFFFF !important;
        padding: 0.8rem 1.2rem !important;
        border-radius: 14px !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important;
        border: 1px solid #E2E8F0 !important;
        margin-bottom: 0.6rem !important;
    }
    
    .progress-bar-container {
        display: flex !important;
        flex-direction: row !important;
        justify-content: space-between !important;
        align-items: center !important;
        position: relative !important;
        margin: 0 auto !important;
        padding: 1.8rem 0 1.8rem 0 !important;
        width: 100% !important;
    }
    
    /* Track lines layout values */
    .progress-line {
        position: absolute !important;
        top: 50% !important;
        left: 0 !important;
        right: 0 !important;
        height: 4px !important;
        background-color: #E2E8F0 !important;
        z-index: 1 !important;
        transform: translateY(-50%) !important;
    }
    
    .progress-line-fill {
        position: absolute !important;
        top: 50% !important;
        left: 0 !important;
        height: 4px !important;
        background-color: #0056B3 !important; 
        z-index: 2 !important;
        transform: translateY(-50%) !important;
        transition: width 0.4s ease !important;
    }
    
    .step-node {
        position: relative !important;
        z-index: 3 !important;
        background: #FFFFFF !important; 
        border: 3px solid #CBD5E1 !important;
        border-radius: 50% !important;
        width: 14px !important;
        height: 14px !important;
        transition: all 0.3s ease !important;
    }
    
    .step-node.dim-light {
        border-color: #CBD5E1 !important;
        background: #CBD5E1 !important;
    }
    
    .step-node.active-blue {
        border-color: #0056B3 !important;
        background: #0056B3 !important;
        box-shadow: 0 0 0 4px rgba(0, 86, 179, 0.2) !important;
    }
    
    /* Top-Float Delivery Icon Header Positions */
    .status-icon-header {
        position: absolute !important;
        top: -28px !important;
        left: 50% !important;
        transform: translateX(-50%) !important;
        font-size: 1.25rem !important;
        opacity: 0.3 !important;
        transition: all 0.3s ease !important;
    }
    
    .step-node.active-blue .status-icon-header {
        opacity: 1 !important;
        transform: translateX(-50%) scale(1.15) !important;
    }
    
    @keyframes stepPulse {
        0% { background-color: #0056B3; border-color: #0056B3; box-shadow: 0 0 0 0 rgba(0, 86, 179, 0.5); }
        50% { background-color: #3B82F6; border-color: #3B82F6; box-shadow: 0 0 0 6px rgba(0, 86, 179, 0.2); }
        100% { background-color: #0056B3; border-color: #0056B3; box-shadow: 0 0 0 0 rgba(0, 86, 179, 0); }
    }

    @keyframes alertPulse {
        0% { opacity: 1.0; transform: scale(1); box-shadow: 0 4px 12px rgba(0, 86, 179, 0.05); }
        50% { opacity: 0.95; transform: scale(1.002); box-shadow: 0 6px 14px rgba(0, 86, 179, 0.12); border-color: #0056B3 !important; }
        100% { opacity: 1.0; transform: scale(1); box-shadow: 0 4px 12px rgba(0, 86, 179, 0.05); }
    }

    .blinking-status {
        animation: alertPulse 2.5s infinite ease-in-out !important;
    }

    .step-node.active-highlight {
        animation: stepPulse 1.5s infinite ease-in-out !important;
    }
    
    .step-node.active-highlight .status-icon-header {
        opacity: 1 !important;
        transform: translateX(-50%) scale(1.15) !important;
    }
    
    .step-label {
        position: absolute !important;
        top: 22px !important;
        font-size: 0.8rem !important;
        font-weight: 600 !important;
        color: #94A3B8 !important; 
        white-space: nowrap !important;
        text-align: center !important;
        left: 50% !important;
        transform: translateX(-50%) !important;
    }
    
    .step-node.dim-light .step-label { color: #94A3B8 !important; }
    .step-node.active-blue .step-label { color: #0056B3 !important; font-weight: 700 !important; }
    .step-node.active-highlight .step-label { color: #0056B3 !important; font-weight: 700 !important; }

    /* Compact status alert banner padding rules */
    .status-alert {
        padding: 0.75rem 1rem !important;
        border-radius: 10px !important;
        font-size: 0.9rem !important;
        margin-top: 0.6rem !important;
        display: flex !important;
        align-items: center !important;
        gap: 0.6rem !important;
        transition: all 0.3s ease !important;
        line-height: 1.3 !important;
    }
    
    .status-state-active { 
        background-color: #EFF6FF !important; 
        color: #003366 !important; 
        border: 1px solid #93C5FD !important; 
        border-left: 5px solid #0056B3 !important;
    }
    
    .status-state-delivered {
        background-color: #F0FDF4 !important;
        color: #14532D !important;
        border: 1px solid #BBF7D0 !important;
        border-left: 5px solid #16A34A !important;
        font-weight: 700 !important;
    }
    
    .status-title-tag {
        font-weight: 800 !important;
        text-transform: uppercase !important;
        font-size: 0.7rem !important;
        letter-spacing: 0.05em !important;
        padding: 0.15rem 0.4rem !important;
        border-radius: 5px !important;
        margin-right: 0.2rem !important;
        display: inline-block !important;
    }
    
    .tag-blue { background-color: #DBEAFE !important; color: #1E40AF !important; }
    .tag-green { background-color: #DCFCE7 !important; color: #166534 !important; }

    /* Compact Profile Content Card Optimization Styles */
    .order-card {
        width: 100% !important;
        box-sizing: border-box !important;
        background: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 12px !important;
        padding: 1.2rem 1.5rem !important;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.01) !important;
    }
    
    .card-header-title {
        color: #002D62 !important; 
        margin-top: 0.1rem !important; 
        margin-bottom: 0.5rem !important;
        font-size: 1.6rem !important;
        font-weight: 800 !important;
        letter-spacing: -0.02em !important;
    }
    
    .card-section-label {
        color: #64748B !important; 
        font-weight: 700 !important; 
        font-size: 0.75rem !important; 
        text-transform: uppercase !important; 
        letter-spacing: 0.08em !important;
        display: block !important;
    }
    
    .item-badge {
        background-color: #EFF6FF !important;
        color: #0056B3 !important;
        font-weight: 500 !important;
        padding: 0.4rem 0.8rem !important;
        border-radius: 8px !important;
        display: inline-block !important;
        margin-right: 0.4rem !important;
        margin-top: 0.4rem !important;
        border: 1px solid #DBEAFE !important;
        font-size: 0.95rem !important;
        box-shadow: 0 1px 2px rgba(0, 86, 179, 0.05) !important;
    }
    
    .divider-line {
        border: 0 !important; 
        border-top: 1px solid #F1F5F9 !important; 
        margin-top: 0.6rem !important;
        margin-bottom: 0.6rem !important;
    }
</style>
"""

# 🌟 DOUBLE INJECTION SAFEGUARD:
# Injecting the styles here at root handles the primary window and caching lifecycle.
st.markdown(SHARED_CSS, unsafe_allow_html=True)

# -------------------------------------------------
# ORDER DATA FROM PAYMENT PAGE
# -------------------------------------------------

def get_order_data():
    """Read the completed order directly from Payment page session state."""
    reference_no = st.session_state.get("reference_no", "")
    order_id = st.session_state.get("order_id", "") or reference_no or "PENDING"

    customer_name = (
        st.session_state.get("customer_name", "")
        or st.session_state.get("card_name", "")
        or "Guest"
    )

    return {
        "customer_name": customer_name,
        "order_id": order_id,
        "cart": st.session_state.get("cart", []),
        "subtotal": float(st.session_state.get("subtotal", 0)),
        "tax": float(st.session_state.get("tax", 0)),
        "grand_total": float(st.session_state.get("grand_total", 0)),
        "payment_method": st.session_state.get("payment_method", ""),
        "reference_no": reference_no,
    }


def render_order_summary(order):
    """Display the order received from the Payment page."""
    cart = order["cart"]

    if not cart:
        st.warning("⚠️ No order information is available from the Payment page.")
        return

    item_html = ""

    for item in cart:
        name = item.get("item", "Food Item")
        qty = int(item.get("qty", 1))
        price = float(item.get("price", 0))
        total = price * qty

        item_html += f"""
        <div style="
            display:flex;
            justify-content:space-between;
            align-items:center;
            gap:12px;
            padding:0.65rem 0;
            border-bottom:1px solid #F1F5F9;
        ">
            <div>
                <div style="color:#002D62;font-weight:700;font-size:0.9rem;">
                    🍕 {name}
                </div>
                <div style="color:#64748B;font-size:0.72rem;margin-top:0.15rem;">
                    Qty: {qty}
                </div>
            </div>
            <div style="
                color:#002D62;
                font-weight:800;
                font-size:0.85rem;
                white-space:nowrap;
            ">
                ₹ {total:.2f}
            </div>
        </div>
        """

    render_html(f"""
    <div class="order-card">
        <span class="card-section-label">Customer Profile</span>
        <h1 class="card-header-title">Hello, {order["customer_name"]}!</h1>

        <hr class="divider-line"/>

        <span class="card-section-label">
            Order Summary for #{order["order_id"]}
        </span>

        <div style="margin-top:0.55rem;">
            {item_html}
        </div>

        <div style="margin-top:0.7rem;">
            <div style="
                display:flex;
                justify-content:space-between;
                padding:0.3rem 0;
                color:#64748B;
                font-size:0.78rem;
            ">
                <span>Subtotal</span>
                <strong style="color:#002D62;">
                    ₹ {order["subtotal"]:.2f}
                </strong>
            </div>

            <div style="
                display:flex;
                justify-content:space-between;
                padding:0.3rem 0;
                color:#64748B;
                font-size:0.78rem;
            ">
                <span>Tax</span>
                <strong style="color:#002D62;">
                    ₹ {order["tax"]:.2f}
                </strong>
            </div>

            <div style="
                display:flex;
                justify-content:space-between;
                padding:0.3rem 0;
                color:#64748B;
                font-size:0.78rem;
            ">
                <span>Delivery</span>
                <strong style="color:#16A34A;">FREE</strong>
            </div>

            <div style="
                display:flex;
                justify-content:space-between;
                border-top:1px solid #E2E8F0;
                margin-top:0.45rem;
                padding-top:0.65rem;
                color:#002D62;
                font-size:1rem;
                font-weight:900;
            ">
                <span>Total</span>
                <span style="color:#0056B3;">
                    ₹ {order["grand_total"]:.2f}
                </span>
            </div>
        </div>

        <div style="
            margin-top:0.75rem;
            padding:0.55rem 0.7rem;
            background:#EFF6FF;
            border:1px solid #DBEAFE;
            border-radius:8px;
            color:#1E40AF;
            font-size:0.75rem;
        ">
            <strong>Payment:</strong>
            {order["payment_method"] or "Completed"}
        </div>
    </div>
    """)


# Anchor system startup run execution time to trace the 30-second phase states
if "start_time" not in st.session_state:
    st.session_state["start_time"] = time.time()

def render_payment_style_header():
    """Header matching the Payment page Food Lab branding."""
    render_html("""
    <div style="
        display:flex;
        justify-content:space-between;
        align-items:center;
        width:100%;
        padding:0.2rem 0 0.7rem 0;
        margin-bottom:0.35rem;
        box-sizing:border-box;
        font-family:Arial,sans-serif;
    ">
        <div style="
            display:flex;
            align-items:center;
            gap:0.8rem;
        ">
            <div style="
                width:36px;
                height:36px;
                border-radius:8px;
                background:#0056B3;
                display:flex;
                align-items:center;
                justify-content:center;
                color:#fff;
                font-size:1.2rem;
                box-shadow:0 4px 12px rgba(0,86,179,0.1);
            ">🍴</div>

            <div>
                <div style="
                    color:#002D62;
                    font-weight:800;
                    font-size:1.4rem;
                    line-height:1.1;
                ">Food Lab</div>

                <div style="
                    color:#64748B;
                    font-size:0.75rem;
                    margin-top:0.1rem;
                ">A STEM Workshop application</div>
            </div>
        </div>

        <div style="
            border:1px solid #D6E4F0;
            background:#EBF3FA;
            color:#0056B3;
            font-weight:700;
            font-size:0.65rem;
            padding:0.3rem 0.6rem;
            border-radius:20px;
            letter-spacing:0.05em;
        ">STEM WORKSHOP</div>
    </div>
    """)


def render_payment_style_progress():
    """Payment-page-style 6-step progress with Delivery active."""
    render_html("""
    <div style="
        background:#FFFFFF;
        padding:0.65rem 1rem;
        border-radius:14px;
        border:1px solid #E2E8F0;
        box-shadow:0 1px 3px rgba(0,0,0,0.04);
        margin-bottom:0.8rem;
        font-family:Arial,sans-serif;
        overflow-x:auto;
    ">
        <div style="
            display:flex;
            align-items:center;
            justify-content:center;
            min-width:650px;
            gap:8px;
            color:#64748B;
            font-size:0.72rem;
            font-weight:700;
        ">
            <div style="text-align:center;color:#16A34A;min-width:55px;">
                <div style="
                    width:24px;height:24px;border-radius:50%;
                    margin:0 auto 4px auto;
                    background:#DCFCE7;color:#16A34A;
                    display:flex;align-items:center;justify-content:center;
                ">✓</div>
                Login
            </div>

            <div style="height:2px;width:38px;background:#86EFAC;"></div>

            <div style="text-align:center;color:#16A34A;min-width:55px;">
                <div style="
                    width:24px;height:24px;border-radius:50%;
                    margin:0 auto 4px auto;
                    background:#DCFCE7;color:#16A34A;
                    display:flex;align-items:center;justify-content:center;
                ">✓</div>
                Menu
            </div>

            <div style="height:2px;width:38px;background:#86EFAC;"></div>

            <div style="text-align:center;color:#16A34A;min-width:55px;">
                <div style="
                    width:24px;height:24px;border-radius:50%;
                    margin:0 auto 4px auto;
                    background:#DCFCE7;color:#16A34A;
                    display:flex;align-items:center;justify-content:center;
                ">✓</div>
                Pay
            </div>

            <div style="height:2px;width:38px;background:#86EFAC;"></div>

            <div style="text-align:center;color:#64748B;min-width:55px;">
                <div style="
                    width:24px;height:24px;border-radius:50%;
                    margin:0 auto 4px auto;
                    background:#F1F5F9;color:#64748B;
                    display:flex;align-items:center;justify-content:center;
                ">4</div>
                Bank
            </div>

            <div style="height:2px;width:38px;background:#E2E8F0;"></div>

            <div style="text-align:center;color:#64748B;min-width:55px;">
                <div style="
                    width:24px;height:24px;border-radius:50%;
                    margin:0 auto 4px auto;
                    background:#F1F5F9;color:#64748B;
                    display:flex;align-items:center;justify-content:center;
                ">5</div>
                Receipt
            </div>

            <div style="height:2px;width:38px;background:#0056B3;"></div>

            <div style="text-align:center;color:#0056B3;min-width:65px;">
                <div style="
                    width:24px;height:24px;border-radius:50%;
                    margin:0 auto 4px auto;
                    background:#DBEAFE;color:#0056B3;
                    display:flex;align-items:center;justify-content:center;
                ">6</div>
                Delivery
            </div>
        </div>
    </div>
    """)


@st.fragment(run_every="2s")
def render_live_tracker_dashboard():
    order = get_order_data()

    # Keep the same application header and workflow progress used by Payment.
    render_payment_style_header()
    render_payment_style_progress()

    # Two-column layout:
    # Left  = order details from Payment page
    # Right = live delivery tracking
    left_col, right_col = st.columns([0.85, 1.65], gap="large")

    with left_col:
        render_order_summary(order)

    with right_col:
        elapsed_seconds = time.time() - st.session_state["start_time"]

        node1_class = "step-node"
        node2_class = "step-node"
        node3_class = "step-node"

        if elapsed_seconds <= 60:
            line_fill_width = f"{min((elapsed_seconds / 60.0) * 100, 100.0):.1f}%"
        else:
            line_fill_width = "100%"

        if elapsed_seconds <= 30:
            status = "cooking"
            sec_left = 30 - elapsed_seconds

            node1_class = "step-node active-blue"

            status_msg = (
                "Baking your order items fresh in the oven! "
                f"Next phase in <b>{sec_left:.0f}s</b>"
            )

            alert_style_class = (
                "status-alert status-state-active blinking-status"
            )

            title_badge = (
                '<span class="status-title-tag tag-blue">Cooking</span>'
            )

        elif elapsed_seconds <= 60:
            status = "on the way"
            sec_left = 60 - elapsed_seconds

            node2_class = "step-node active-blue"

            status_msg = (
                "Your package is in transit with our delivery pilot! "
                f"Next phase in <b>{sec_left:.0f}s</b>"
            )

            alert_style_class = (
                "status-alert status-state-active blinking-status"
            )

            title_badge = (
                '<span class="status-title-tag tag-blue">In Transit</span>'
            )

        else:
            status = "delivered"
            node3_class = "step-node active-blue"

            status_msg = (
                "Your hot meal has successfully arrived. Enjoy your food!"
            )

            alert_style_class = "status-alert status-state-delivered"

            title_badge = (
                '<span class="status-title-tag tag-green">Delivered</span>'
            )

        # Use st.html() instead of st.markdown() for the tracker.
        # This prevents Streamlit from displaying the HTML source as text.
        tracker_html = f"""
        <style>
            .live-tracker {{
                width: 100%;
                box-sizing: border-box;
                padding: 18px 22px 20px 22px;
                font-family: Arial, sans-serif;
                background: #FFFFFF;
                border-radius: 12px;
            }}

            .tracker-row {{
                display: grid;
                grid-template-columns: 88px minmax(70px, 1fr) 88px minmax(70px, 1fr) 88px;
                align-items: center;
                width: 100%;
                box-sizing: border-box;
                min-height: 105px;
            }}

            .tracker-node {{
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                text-align: center;
                min-width: 0;
                z-index: 3;
            }}

            .tracker-icon {{
                width: 52px;
                height: 52px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                background: #F1F5F9;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                font-size: 25px;
                line-height: 1;
                margin-bottom: 7px;
                box-sizing: border-box;
            }}

            .tracker-node.active .tracker-icon {{
                background: #DBEAFE;
                box-shadow: 0 0 0 5px #EFF6FF;
            }}

            .tracker-label {{
                color: #64748B;
                font-size: 12px;
                font-weight: 700;
                white-space: nowrap;
            }}

            .tracker-node.active .tracker-label {{
                color: #0056B3;
            }}

            .tracker-connector {{
                height: 5px;
                width: 100%;
                border-radius: 8px;
                background: #E2E8F0;
                position: relative;
                overflow: hidden;
            }}

            .tracker-connector-fill {{
                position: absolute;
                inset: 0 auto 0 0;
                width: {line_fill_width};
                background: #0056B3;
                border-radius: 8px;
                transition: width 0.5s ease;
            }}

            .tracker-message {{
                width: 100%;
                box-sizing: border-box;
                margin-top: 18px;
                padding: 14px 18px;
                border-radius: 10px;
                text-align: center;
                font-size: 14px;
                line-height: 1.45;
            }}

            .tracker-message.active {{
                background: #EFF6FF;
                border: 1px solid #BFDBFE;
                border-left: 5px solid #0056B3;
                color: #1E40AF;
            }}

            .tracker-message.delivered {{
                background: #F0FDF4;
                border: 1px solid #BBF7D0;
                border-left: 5px solid #16A34A;
                color: #166534;
            }}

            .tracker-badge {{
                display: inline-block;
                margin-right: 8px;
                padding: 3px 8px;
                border-radius: 4px;
                background: #DBEAFE;
                color: #0056B3;
                font-weight: 800;
                font-size: 12px;
            }}

            .tracker-badge.delivered {{
                background: #DCFCE7;
                color: #16A34A;
            }}

            @media (max-width: 700px) {{
                .live-tracker {{
                    padding: 14px 8px;
                }}

                .tracker-row {{
                    grid-template-columns: 62px minmax(35px, 1fr) 62px minmax(35px, 1fr) 62px;
                    min-height: 95px;
                }}

                .tracker-icon {{
                    width: 44px;
                    height: 44px;
                    font-size: 21px;
                }}

                .tracker-label {{
                    font-size: 10px;
                }}
            }}
        </style>

        <div class="live-tracker">
            <div class="tracker-row">

                <div class="tracker-node {"active" if status == "cooking" else ""}">
                    <div class="tracker-icon">👩‍🍳</div>
                    <div class="tracker-label">Cooking</div>
                </div>

                <div class="tracker-connector">
                    <div class="tracker-connector-fill"
                         style="width:{line_fill_width};"></div>
                </div>

                <div class="tracker-node {"active" if status == "on the way" else ""}">
                    <div class="tracker-icon">🛵</div>
                    <div class="tracker-label">On The Way</div>
                </div>

                <div class="tracker-connector">
                    <div class="tracker-connector-fill"
                         style="width:{"100%" if status == "delivered" else "0%"};"></div>
                </div>

                <div class="tracker-node {"active" if status == "delivered" else ""}">
                    <div class="tracker-icon">🎁</div>
                    <div class="tracker-label">Delivered</div>
                </div>

            </div>

            <div class="tracker-message {"delivered" if status == "delivered" else "active"}">
                {title_badge}
                <span>{status_msg}</span>
            </div>
        </div>
        """

        st.html(tracker_html)

        # No balloons on the Order Status page; keep the tracker unobstructed.



# Run the automated single-page dashboard tracking routine
if __name__ == "__main__":
    render_live_tracker_dashboard()
