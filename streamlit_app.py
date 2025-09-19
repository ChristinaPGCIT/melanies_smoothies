# streamlit_app.py

# -----------------------------------------------------------------------
# Import python packages
import streamlit as st
import pandas as pd

# -----------------------------------------------------------------------
# Snowflake connection (reads from [connections.snowflake] in Secrets)
cnx = st.connection("snowflake", type="snowflake")

# Optional: sanity check (shows account, role, etc.)
with cnx.cursor() as cur:
    cur.execute("""
        SELECT current_account(), current_role(), current_warehouse(),
               current_database(), current_schema()
    """)
    st.write(cur.fetchone())

# -----------------------------------------------------------------------
# Title and Intro
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# -----------------------------------------------------------------------
# Customer input: Name
name_on_order = st.text_input("Name on Smoothie")
st.write("The name on your Smoothie will be:", name_on_order)

# -----------------------------------------------------------------------
# Customer input: list of ingredients
df_fruits = pd.read_sql(
    "SELECT FRUIT_NAME FROM SMOOTHIES.PUBLIC.FRUIT_OPTIONS ORDER BY FRUIT_NAME",
    cnx
)

# Convert to a Python list
fruit_options = df_fruits["FRUIT_NAME"].tolist()

ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_options,
    max_selections=5
)

# -----------------------------------------------------------------------
# Build string of chosen ingredients and insert into Snowflake
if ingredients_list:
    ingredients_string = " ".join(ingredients_list)
    st.write(ingredients_string)

    if st.button("Submit Order"):
        with cnx.cursor() as cur:
            cur.execute(
                "INSERT INTO SMOOTHIES.PUBLIC.ORDERS (INGREDIENTS, NAME_ON_ORDER) VALUES (%s, %s)",
                (ingredients_string.strip(), name_on_order.strip())
            )
        st.success(f"Smoothie for {name_on_order} is ordered!", icon="✅")

# -----------------------------------------------------------------------
# Notes:
# 1. Reads credentials from Streamlit Secrets ([connections.snowflake]).
# 2. Uses connector + pandas instead of Snowpark.
# 3. Safe f
