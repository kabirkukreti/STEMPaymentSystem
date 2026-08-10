"""Menu module for the STEM Workshop food-ordering application."""

from pathlib import Path
import csv

import streamlit as st


MENU_FILE = Path(__file__).resolve().parent / "menu.csv"
TAX_RATE = 0.05
DELIVERY_CHARGE = 40.0
FREE_DELIVERY_LIMIT = 500.0


@st.cache_data(show_spinner=False)
def load_menu() -> list[dict]:
    """Read menu.csv. Expected columns: item, price, emoji, category, type, rating."""
    with MENU_FILE.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        return [
            {
                "item": row["item"].strip(),
                "price": float(row["price"]),
                "emoji": row["emoji"].strip(),
                "category": row["category"].strip(),
                "type": row["type"].strip().lower(),
                "rating": float(row["rating"]),
            }
            for row in reader
        ]


def _item_key(item: dict) -> str:
    return item["item"].lower().replace(" ", "_").replace("'", "")


def _matches_search(item: dict, query: str) -> bool:
    searchable_text = " ".join(str(value) for value in item.values()).casefold()
    return query.casefold().strip() in searchable_text


def _filtered_items(menu: list[dict], selected_filter: str, search_query: str) -> list[dict]:
    filter_map = {
        "All Items": None,
        "Veg Only": "veg",
        "Non-Veg": "non-veg",
        "Egg Items": "egg",
    }
    selected_type = filter_map[selected_filter]
    return [
        item for item in menu
        if (selected_type is None or item["type"] == selected_type)
        and _matches_search(item, search_query)
    ]


def _cart_count() -> int:
    return sum(item["quantity"] for item in st.session_state.cart)


def _subtotal() -> float:
    return sum(item["price"] * item["quantity"] for item in st.session_state.cart)


def _add_item(item: dict) -> None:
    key = _item_key(item)
    for cart_item in st.session_state.cart:
        if cart_item["key"] == key:
            cart_item["quantity"] += 1
            break
    else:
        st.session_state.cart.append({
            "key": key,
            "item": item["item"],
            "price": item["price"],
            "quantity": 1,
        })


def _remove_item(key: str) -> None:
    for index, cart_item in enumerate(st.session_state.cart):
        if cart_item["key"] == key:
            if cart_item["quantity"] > 1:
                cart_item["quantity"] -= 1
            else:
                st.session_state.cart.pop(index)
            return


def _update_order_totals() -> None:
    subtotal = _subtotal()
    tax = subtotal * TAX_RATE
    delivery = 0.0 if subtotal >= FREE_DELIVERY_LIMIT or subtotal == 0 else DELIVERY_CHARGE
    st.session_state.subtotal = round(subtotal, 2)
    st.session_state.tax = round(tax, 2)
    st.session_state.delivery_charge = delivery
    st.session_state.total = round(subtotal + tax + delivery, 2)


def _type_badge(item_type: str) -> str:
    labels = {"veg": "VEG", "non-veg": "NON-VEG", "egg": "EGG"}
    css_class = {"veg": "badge-veg", "non-veg": "badge-nonveg", "egg": "badge-egg"}[item_type]
    return f"<span class='food-badge {css_class}'>{labels[item_type]}</span>"


def _render_sidebar_cart() -> None:
    with st.sidebar:
        st.markdown(
            f"<div class='cart-heading'>Your cart <span class='cart-count'>{_cart_count()}</span></div>",
            unsafe_allow_html=True,
        )
        st.caption("Your selections stay saved as you move through the application.")

        if not st.session_state.cart:
            st.markdown("<div class='empty-cart'>🛒<br/><b>Your cart is empty</b><br/>Add something from the menu.</div>", unsafe_allow_html=True)
        else:
            for cart_item in list(st.session_state.cart):
                item_col, quantity_col, remove_col = st.columns([3.3, 1.1, .8])
                with item_col:
                    st.markdown(
                        f"<div class='cart-item'><div class='cart-item-name'>{cart_item['item']}</div>"
                        f"<div class='cart-item-price'>₹{cart_item['price']:.0f} each</div></div>",
                        unsafe_allow_html=True,
                    )
                with quantity_col:
                    st.markdown(f"<div style='padding-top:.8rem;text-align:center;font-weight:700;'>×{cart_item['quantity']}</div>", unsafe_allow_html=True)
                with remove_col:
                    if st.button("−", key=f"remove_{cart_item['key']}", help="Remove one"):
                        _remove_item(cart_item["key"])
                        _update_order_totals()
                        st.rerun()

            if st.button("Clear all", use_container_width=True, key="clear_cart"):
                st.session_state.cart = []
                _update_order_totals()
                st.rerun()

        _update_order_totals()
        subtotal = st.session_state.subtotal
        tax = st.session_state.tax
        delivery = st.session_state.delivery_charge
        total = st.session_state.total
        delivery_text = "FREE" if delivery == 0 and subtotal >= FREE_DELIVERY_LIMIT else f"₹{delivery:.0f}"
        delivery_class = "free-delivery" if delivery_text == "FREE" else ""
        st.markdown(
            f"<div class='bill-box'><div class='bill-row'><span>Subtotal</span><span>₹{subtotal:.0f}</span></div>"
            f"<div class='bill-row'><span>Tax (5%)</span><span>₹{tax:.0f}</span></div>"
            f"<div class='bill-row'><span>Delivery</span><span class='{delivery_class}'>{delivery_text}</span></div>"
            f"<div class='bill-total'><span>Total</span><span>₹{total:.0f}</span></div></div>",
            unsafe_allow_html=True,
        )

        if st.button("Proceed to login  →", type="primary", use_container_width=True, disabled=not st.session_state.cart, key="proceed_to_login"):
            st.session_state.current_module = "login"
            st.rerun()


def render_menu() -> None:
    """Render the Menu module. The main app calls this function."""
    try:
        menu = load_menu()
    except (FileNotFoundError, KeyError, ValueError, csv.Error) as error:
        st.error("The menu could not be loaded. Please check menu.csv and its column names.")
        st.caption(f"Development detail: {error}")
        return

    _render_sidebar_cart()

    title_col, tip_col = st.columns([2.1, 1])
    with title_col:
        st.markdown("<div class='eyebrow'>WELCOME TO THE FOOD LAB</div>", unsafe_allow_html=True)
        st.markdown("<h1 class='page-title'>Pick your favourites</h1>", unsafe_allow_html=True)
        st.markdown("<p class='page-subtitle'>Explore the menu, search for a dish and build your order.</p>", unsafe_allow_html=True)
    with tip_col:
        st.markdown("<div class='tip-card'><span class='tip-icon'>✨</span><b>Quick tip</b><br/>Orders above ₹500 get free delivery.</div>", unsafe_allow_html=True)

    filter_col, search_col = st.columns([1.45, 1])
    with filter_col:
        selected_filter = st.radio(
            "Filter menu",
            ["All Items", "Veg Only", "Non-Veg", "Egg Items"],
            horizontal=True,
            label_visibility="collapsed",
            key="menu_filter",
        )
    with search_col:
        search_query = st.text_input("Search menu", placeholder="Search by dish, category or type...", label_visibility="collapsed", key="menu_search")

    visible_items = _filtered_items(menu, selected_filter, search_query)
    st.markdown(f"<div class='section-label'>{len(visible_items)} ITEMS AVAILABLE</div>", unsafe_allow_html=True)

    if not visible_items:
        st.info("No matching items found. Try a different search or filter.")
    else:
        for start in range(0, len(visible_items), 3):
            row_items = visible_items[start:start + 3]
            columns = st.columns(3)
            for column, item in zip(columns, row_items):
                with column:
                    st.markdown(
                        f"<div class='food-card'><div class='food-icon'>{item['emoji']}</div>"
                        f"<div class='food-name'>{item['item']}</div><div class='food-category'>{item['category']}</div>"
                        f"<div class='rating'>★ {item['rating']:.1f}</div>{_type_badge(item['type'])}"
                        f"<div class='food-price'>₹{item['price']:.0f}</div></div>",
                        unsafe_allow_html=True,
                    )
                    if st.button("Add to cart", use_container_width=True, key=f"add_{_item_key(item)}"):
                        _add_item(item)
                        _update_order_totals()
                        st.rerun()
