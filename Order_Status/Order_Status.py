import streamlit as st
import pandas as pd
import os
import time

# Page Configuration with a clean centered layout and pizza tab icon
st.set_page_config(page_title="Food Lab Tracker", page_icon="🍕", layout="centered")

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
        padding-bottom: 0px !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 700px !important;
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

# Target directory path configuration
CSV_FILE = "C:/Pizza_App_Files/orders.csv"

def load_order_data():
    if not os.path.exists(CSV_FILE):
        st.error(f"❌ File Not Found: Please ensure your tracking file is placed in `{CSV_FILE}`")
        return None
    try:
        st.cache_data.clear()
        return pd.read_csv(CSV_FILE, dtype={"order_id": str})
    except Exception as e:
        st.error(f"Error reading file: {e}")
        return None

# Anchor system startup run execution time to trace the 30-second phase states
if "start_time" not in st.session_state:
    st.session_state["start_time"] = time.time()

# --- Continuous Display Tracker Fragment Container Loop ---
@st.fragment(run_every="2s")
def render_live_tracker_dashboard():
    # 🌟 FIXED DESIGN PATTERN:
    # Reinjecting the stylesheet at the very first line of the fragment ensures that 
    # second browser tabs or freshly opened pages render instantly without layout breaks or 4s lag gaps!
    st.markdown(SHARED_CSS, unsafe_allow_html=True)
    
    # Render Brand Layout Title Top Section Header Row
    st.markdown("""
<div class="brand-header">
    <div class="brand-left">
        <div class="brand-logo-icon">🍕</div>
        <div>
            <div class="brand-text-title">Food Lab</div>
            <div class="brand-text-sub">A STEM Workshop application</div>
        </div>
    </div>
    <div class="brand-badge-button">
        Stem Workshop
    </div>
</div>
""", unsafe_allow_html=True)

    # Render Stationary 6-Step Layout Page Header Card (No line connections between node checkpoints)
    st.markdown("""
<div class="page-header-card">
    <div class="progress-bar-container" style="max-width: 540px; padding: 0.3rem 0 1rem 0;">
        <div class="step-node dim-light" style="background-color: #16A34A !important; border-color: #16A34A !important;"><div class="step-label" style="color: #16A34A !important;">Login</div></div>
        <div class="step-node dim-light"><div class="step-label">Menu</div></div>
        <div class="step-node dim-light"><div class="step-label">Pay</div></div>
        <div class="step-node dim-light"><div class="step-label">Bank</div></div>
        <div class="step-node dim-light"><div class="step-label">Receipt</div></div>
        <div class="step-node active-highlight"><div class="step-label">Delivery</div></div>
    </div>
</div>
""", unsafe_allow_html=True)

    df_orders = load_order_data()
    
    if df_orders is not None and not df_orders.empty:
        customer = df_orders['customer_name'].iloc[0]
        order_id = df_orders['order_id'].iloc[0]
        pizza_list = df_orders['pizza_details'].tolist()
        
        # Calculate exactly how many seconds have ticked past since app execution launched
        start_time = st.session_state.get("start_time")

        if start_time is not None:
            elapsed_seconds = time.time() - start_time
        else:
            elapsed_seconds = 0.0
        
        # Setup layout dynamic progress variables for Cooking -> On The Way -> Delivered tracking bar
        node1_class = "step-node"
        node2_class = "step-node"
        node3_class = "step-node"
        line_fill_width = "0%"
        status_msg = ""
        status = "cooking"
        
        # ⏱️ DYNAMIC STATUS TIMER LOGIC - SMOOTH PROGRESS ENHANCEMENT
        if elapsed_seconds <= 60:
            fluid_percentage = (elapsed_seconds / 60.0) * 100
            line_fill_width = f"{min(fluid_percentage, 100.0):.1f}%"
        else:
            line_fill_width = "100%"

        if elapsed_seconds <= 30:
            status = "cooking"
            sec_left = 30 - elapsed_seconds
            node1_class = "step-node active-blue"
            status_msg = f"Baking your order items fresh in the oven! Next phase in <b>{sec_left:.0f}s</b>"
            alert_style_class = "status-alert status-state-active blinking-status"
            title_badge = '<span class="status-title-tag tag-blue">Cooking</span>'
        elif elapsed_seconds <= 60:
            status = "on the way"
            sec_left = 60 - elapsed_seconds
            node1_class = "step-node dim-light"
            node2_class = "step-node active-blue"
            status_msg = f"Your package is in transit with our delivery pilot! Next phase in <b>{sec_left:.0f}s</b>"
            alert_style_class = "status-alert status-state-active blinking-status"
            title_badge = '<span class="status-title-tag tag-blue">In Transit</span>'
        else:
            status = "delivered"
            node1_class = "step-node dim-light"
            node2_class = "step-node dim-light"
            node3_class = "step-node active-blue"
            status_msg = "Your hot meal has successfully arrived. Enjoy your food!"
            alert_style_class = "status-alert status-state-delivered"
            title_badge = '<span class="status-title-tag tag-green">Delivered</span>'

        # Wrap the template layout call inside a structural layout column to force HTML compilation
        dashboard_row = st.columns(1)
        
        with dashboard_row[0]:
            # Render DEDICATED SEPARATE 3-Step Delivery Progress Tracker Card Row
            st.markdown(f"""
<div class="tracker-wrapper">
<div class="progress-bar-container" style="max-width: 400px; padding: 1.4rem 0 1.4rem 0 !important;">
<div class="progress-line"></div>
<div class="progress-line-fill" style="width: {line_fill_width};"></div>
<div class="{node1_class}">
<div class="status-icon-header">👩‍🍳</div>
<div class="step-label">Cooking</div>
</div>
<div class="{node2_class}">
<div class="status-icon-header">🛵</div>
<div class="step-label">On The Way</div>
</div>
<div class="{node3_class}">
<div class="status-icon-header">🎁</div>
<div class="step-label">Delivered</div>
</div>
</div>
<div>
<div class="{alert_style_class}">
    {title_badge} <span>{status_msg}</span>
</div>
</div>
</div>
""", unsafe_allow_html=True)

            # Build list pills string elements sequentially with enhanced sizing styles
            pills_html = "".join([f'<span class="item-badge">🍕 {pizza}</span>' for pizza in pizza_list])

            # Details Summary Sheet Card Layout - Beautifully nested and scaled up
            st.markdown(f"""
<div class="order-card">
<span class="card-section-label">Customer Profile</span>
<h1 class="card-header-title">Hello, {customer}!</h1>
<hr class="divider-line"/>
<span class="card-section-label">Order Summary for #{order_id}</span>
<div style="margin-top: 0.4rem; margin-bottom: 0.1rem; display: block;">
{pills_html}
</div>
</div>
""", unsafe_allow_html=True)

        # Fire balloon celebration upon delivery milestone landing completion
        if status == "delivered":
            st.balloons()
    else:
        st.warning("⚠️ No active customer records found inside the tracking file database.")

# Run the automated single-page dashboard tracking routine
if __name__ == "__main__":
    render_live_tracker_dashboard()
