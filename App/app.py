import streamlit as st
from database import (
    add_food_item,
    get_all_food_items,
    get_expiring_items,
    delete_food_item,
)
from recipe_generator import generate_recipe

# Streamlit layout
st.set_page_config(page_title="Recipe Generator", layout="wide")

# Title
st.title("Recipe Generator")

# Initialize session state
if 'refresh' not in st.session_state:
    st.session_state.refresh = False

# Create two columns for layout
left_column, right_column = st.columns([1, 1])

# Left Column: All Items
with left_column:
    st.subheader("Your Items")

    try:
        all_items = get_all_food_items()
        for item in all_items:
            col1, col2 = st.columns([3, 1])
            col1.write(f"Item: {item['document']}, Expiry: {item['expiry']}")
            if col2.button(f"Delete {item['document']}", key=f"delete_{item['document']}"):
                delete_food_item(item['document'])
                st.session_state.refresh = True
    except Exception as e:
        st.error(f"Error fetching items: {str(e)}")

    # Add new item
    st.subheader("Add New Item")
    new_item = st.text_input("Item Name")
    expiry_days = st.number_input("Expiry (Days)", min_value=1, value=1)
    if st.button("Add Item"):
        try:
            add_food_item(new_item, f"{expiry_days} days")
            st.success(f"Added {new_item}")
            st.session_state.refresh = True
        except Exception as e:
            st.error(f"Error adding item: {str(e)}")

# Right Column: Expiring Soon and Recipe Generation
with right_column:
    st.subheader("Expiring Soon!!")

    try:
        expiring_items = get_expiring_items()
        for item in expiring_items:
            st.write(f"Expiring Item: {item['document']}, Expiry: {item['expiry']}")
    except Exception as e:
        st.error(f"Error fetching expiring items: {str(e)}")

    if st.button("Generate Recipe"):
        expiring_item_names = [item['document'] for item in expiring_items]
        recipe = generate_recipe(expiring_item_names, 1)
        st.write(recipe)

# Check if we need to refresh the page
if st.session_state.refresh:
    st.session_state.refresh = False
    st.rerun()