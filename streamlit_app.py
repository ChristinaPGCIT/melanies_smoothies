# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd

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
# Customer input: list of ingredients
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'),col('SEARCH_ON'))
# st.dataframe(data=my_dataframe, use_container_width=True)
# st.stop()

# Convert Snowpark DataFrame to a Panda Dataframe so we can use the LOC function
pd_df = my_dataframe.to_pandas()
st.dataframe(pd_df)
st.stop()

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

        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        #st.write('The search value for ', fruit_chosen,' is ', search_on, '.')
        
        st.subheader(fruit_chosen + 'Nutrition Information')
        fruityvice_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + search_on)
        fv_df=st.dataframe(data=fruityvice_response.json(),use_container_width=True)
        
    #st.write(ingredients_string)

    #Creates a SQL INSERT statement as a text string
    my_insert_stmt = """ insert into smoothies.public.orders(ingredients,name_on_order)
            values ('""" + ingredients_string +  """','""" + name_on_order + """')"""
    
    time_to_insert = st.button('Submit Order')      #Add a Submit button
    
    if time_to_insert:                              #Execute the insert when button clicked
        session.sql(my_insert_stmt).collect()
        st.success(f"Smoothie for {name_on_order} is ordered!", icon="✅")

#END-----------------------------------------------------------------------
#1. Pull fruit names from Snowflake.
#2. Show them as options in a multi-select.
#3. Let the user pick up to 5 fruits.
#4. Build a string of those fruits.
#5. When they click “Submit Order,” insert their name + chosen fruits into the orders table in Snowflake.
#6. Show a success message.
