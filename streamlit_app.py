# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col

#-----------------------------------------------------------------------
# Title and Intro
st.title(f":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

#-----------------------------------------------------------------------
# Customer input: Name
name_on_order = st.text_input('Name on Smoothie')
st.write('The name on your Smoothie will be: ',name_on_order)

# Create a connection + session
cnx = st.connection("snowflake", type="snowflake")
session = cnx.session()

# -------------------------------------
# --- TEMP: connection sanity check ---
st.write(session.sql("select current_account(), current_role(), current_warehouse(), current_database(), current_schema()").collect())
#-----------------------------------------------------------------------
# Customer input: list of ingredients

my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))

#Show the fruit options rendered in the fruit_option table fruit_name column.
#st.dataframe(data=my_dataframe, use_container_width=True)

#Let the user pick ingredients
# ingredients_list = st.multiselect(
#     "Choose up to 5 ingredients: ",
#     my_dataframe
#     #default=["Apples", "Blueberries"],
# )

# Convert Snowpark DataFrame to a simple Python list of fruit names
fruit_options = [row["FRUIT_NAME"] for row in my_dataframe.collect()]

ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_options,
    max_selections=5)

#-----------------------------------------------------------------------
#Build a string of chosen ingredients.
#If the user picked anything, this loops through each fruit and builds one long string, separated by spaces.
if ingredients_list:
    ingredients_string=""
    
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        
    st.write(ingredients_string)


    #Creates a SQL INSERT statement as a text string
    my_insert_stmt = """ insert into smoothies.public.orders(ingredients,name_on_order)
            values ('""" + ingredients_string +  """','""" + name_on_order + """')"""
    
    time_to_insert = st.button('Submit Order')      #Add a Submit button
    
    if time_to_insert:                              #Execute the insert when button clicked
        session.sql(my_insert_stmt).collect()

        
        #st.success('Your Smoothie is ordered!', icon="✅")

        st.success(f"Smoothie for {name_on_order} is ordered!", icon="✅")
#-----------------------------------------------------------------------
# New section to display smoothiefroot nutrition info
import requests
smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
#st.text(smoothiefroot_response.json())
sf_df=st.dataframe(data=smoothiefroot_response.json(),use_container_width=True)


#END-----------------------------------------------------------------------
#1. Pull fruit names from Snowflake.
#2. Show them as options in a multi-select.
#3. Let the user pick up to 5 fruits.
#4. Build a string of those fruits.
#5. When they click “Submit Order,” insert their name + chosen fruits into the orders table in Snowflake.
#6. Show a success message.
