import streamlit as st
from apscheduler.schedulers.background import BackgroundScheduler
from database import (
    add_food_item,
    get_all_food_items,
    get_expiring_items,
    delete_food_item,
)
from recipe_generator import generate_recipe
from auth import login_signup_page, send_email, get_user_email

# Function to check for expiring items
def check_expiring_items():
    expiring_items = get_expiring_items()
    for item in expiring_items:
        # Check if item is expiring soon (e.g., 3 days or less)
        expiry_value, expiry_unit = item["expiry"].split()
        expiry_value = int(expiry_value)
        if expiry_value <= 3 and expiry_unit == "days":
            subject = "Warning: Your food is about to spoil!"
            body = f"⚠ Warning: {item['document']} is expiring in {expiry_value} day(s)."
            user_email = get_user_email(st.session_state.username)
            if user_email:
                send_email(subject, body, user_email)

# Set up the background scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(check_expiring_items, "interval", days=1)  # Run every day
scheduler.start()

# Main app logic
def main_app():
    st.title("🍳 SmartBite")

    left_column, right_column = st.columns([1, 1])

    # Left Column: All Items
    with left_column:
        st.subheader("🥕 Your Pantry")

        # Add Item button
        if st.button("➕ Add New Item"):
            st.session_state.show_add_item = True

        # Display all items
        all_items = get_all_food_items()
        if all_items:
            for item in all_items:
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(
                        f"""
                        <div class="item-card">
                            <h4>{item['document']}</h4>
                            <p>Expires in: {item['expiry']}</p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                with col2:
                    if st.button("🗑", key=f"delete_{item['document']}"):
                        delete_food_item(item["document"])
                        st.experimental_rerun()
        else:
            st.info("Your pantry is empty. Add some items!")

    # Add Item Popup (Left Sidebar)
    if st.session_state.get('show_add_item', False):
        with st.sidebar:
            st.subheader("Add New Item")
            with st.form("add_item_form"):
                new_item = st.text_input("Item Name")
                col1, col2 = st.columns(2)
                with col1:
                    expiry_value = st.number_input("Expiry Value", min_value=1, value=1)
                with col2:
                    expiry_unit = st.selectbox("Expiry Unit", ["Days", "Months"])

                if st.form_submit_button("Add to Pantry"):
                    if new_item:
                        expiry = f"{expiry_value} {expiry_unit.lower()}"
                        add_food_item(new_item, expiry)
                        st.success(f"Added {new_item} to your pantry!")
                        st.session_state.show_add_item = False
                        st.experimental_rerun()
                    else:
                        st.error("Please enter an item name.")

            if st.button("Cancel"):
                st.session_state.show_add_item = False
                st.experimental_rerun()

    # Right Column: Expiring Soon and Recipe Generation
    with right_column:
        if not st.session_state.get('show_recipe', False):
            st.subheader("🚨 Expiring Soon")

            expiring_items = get_expiring_items()
            if expiring_items:
                for item in expiring_items:
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.markdown(
                            f"""
                            <div class="item-card expiring-card">
                                <h4>{item['document']}</h4>
                                <p>Expires in: {item['expiry']}</p>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                    with col2:
                        if st.checkbox(
                            "Use",
                            key=f"select_{item['document']}",
                            value=item["document"] in st.session_state.get('selected_items', []),
                        ):
                            if 'selected_items' not in st.session_state:
                                st.session_state.selected_items = []
                            if item["document"] not in st.session_state.selected_items:
                                st.session_state.selected_items.append(item["document"])
                        else:
                            if 'selected_items' in st.session_state and item["document"] in st.session_state.selected_items:
                                st.session_state.selected_items.remove(item["document"])

                if st.button("🎨 Generate Recipe", type="primary"):
                    st.session_state.show_recipe = True
                    st.session_state.recipe = None  # Reset recipe status
                    st.experimental_rerun()
            else:
                st.info("No items expiring soon.")
        else:
            st.subheader("🍽 Generated Recipe")
            if st.session_state.get('selected_items', []):
                if st.session_state.get('recipe') is None:
                    with st.spinner("Generating your recipe..."):
                        st.session_state.recipe = generate_recipe(
                            st.session_state.selected_items
                        )

                # Display the current recipe
                st.markdown(
                    f"""
                    <div class="recipe-card">
                        <h3>Recipe using {', '.join(st.session_state.selected_items)}</h3>
                        <p>{st.session_state.recipe}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # Add button to generate another recipe
                if st.button("🔄 Generate Another Recipe"):
                    with st.spinner("Generating another recipe..."):
                        st.session_state.recipe = generate_recipe(
                            st.session_state.selected_items
                        )  # Generate new recipe

                # Show close button when a recipe is generated
                if st.button("Close Recipe"):
                    st.session_state.show_recipe = False
                    st.session_state.selected_items = []
                    st.session_state.recipe = None  # Reset recipe on close
                    st.experimental_rerun()
            else:
                st.warning(
                    "No items were selected. Please select expiring items to generate a recipe."
                )

                # Show close button when no items are selected
                if st.button("Close"):
                    st.session_state.show_recipe = False
                    st.session_state.selected_items = []
                    st.session_state.recipe = None  # Reset recipe on close
                    st.experimental_rerun()

def main():
    # Set page config
    st.set_page_config(page_title="SmartBite", layout="wide")

    # Custom CSS for styling
    st.markdown(
        """
        <style>
        .main {
            padding: 1rem;
        }
        .stButton>button {
            width: 100%;
        }
        .item-card {
            background-color: #1E1E1E;
            padding: 1rem;
            border-radius: 0.5rem;
            margin-bottom: 0.75rem;
            color: white;
        }
        .expiring-card {
            background-color: #793de0;
        }
        .scrollable-section {
            max-height: 400px;
            overflow-y: auto;
            padding: 1rem;
            border: 1px solid #444;
            border-radius: 0.5rem;
            background-color: #0E1117;
        }
        .right-popup {
            position: fixed;
            top: 0;
            right: 0;
            width: 40%;
            height: 100vh;
            background-color: #262730;
            padding: 2rem;
            z-index: 999;
            overflow-y: auto;
            box-shadow: -5px 0 15px rgba(0,0,0,0.3);
        }
        .close-button {
            position: relative;
            top: 1rem;
            right: 1rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Initialize session states
    if "show_add_item" not in st.session_state:
        st.session_state.show_add_item = False
    if "show_recipe" not in st.session_state:
        st.session_state.show_recipe = False
    if "selected_items" not in st.session_state:
        st.session_state.selected_items = []
    if "recipe" not in st.session_state:
        st.session_state.recipe = None

    login_signup_page()
    
    if st.session_state.username:
        main_app()

if __name__ == '__main__':
    main()