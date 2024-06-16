import pandas as pd
from pymongo import MongoClient
import streamlit as st
from streamlit_folium import folium_static
import mysql.connector
import plotly.express as px
from streamlit_folium import folium_static
import folium


connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Taffy&0402",
        database="airbnb"
    )
cursor=connection.cursor(buffered=True)

tab1,tab2,tab3=st.tabs(["Visualization","Graph","Geo_visualization"])
with tab1:
    # Sidebar filters
    st.sidebar.header("Filters")
    room_type = st.sidebar.multiselect("Room_Type", ['Private room', 'Entire home/apt', 'Shared room'])
    accommodates = st.sidebar.slider("Accommodates", 1, 16, 1)
    bedrooms = st.sidebar.selectbox("Bedrooms", [1, 2, 3, 5, 4, 8, 6, 10, 0, 7, 15, 9, 14, 25, 13, 12, 11, 18, 16])
    beds = st.sidebar.selectbox("Beds", [1, 0, 3, 2, 4, 6, 5, 9, 7, 20, 10, 8, 15])
    bathrooms = st.sidebar.selectbox("Bathrooms", [1., 2., 1.5, 4., 2.5, 3., 3.5, 5., 6., 7., 0., 4.5, 8., 0.5, 16., 5.5, 9.])

    # Construct the SQL query with filters
    query = "SELECT _id, name, price FROM most WHERE 1=1"

    if room_type:
        room_type_str = "', '".join(room_type)
        query += f" AND room_type IN ('{room_type_str}')"

    query += f" AND accommodates = {accommodates}"
    query += f" AND bedrooms = {bedrooms}"
    query += f" AND beds = {beds}"
    query += f" AND bathrooms = {bathrooms}"

    # Execute the query
    cursor.execute(query)
    results = cursor.fetchall()

    # Convert the results to a DataFrame
    df = pd.DataFrame(results, columns=['ID', 'Name', 'Price'])

    # Display the dataframe
    st.write("### Airbnb Listings")
    st.dataframe(df)

    # Function to display additional info
    def display_info(selected_id):
        query = f"SELECT amenities, summary,notes,house_rules,price,name,security_deposit,cleaning_fee,extra_people,guests_included,host_name,host_location FROM most WHERE _id = {selected_id}"
        cursor.execute(query)
        details = cursor.fetchone()
        if details:
            amenities, summary, notes,house_rules,price,name,security_deposit,cleaning_fee,extra_people,guests_included,host_name,host_location = details
            st.header("Details : ")
            st.markdown(f":green-background[Name] : {name}")
            st.write(f":green-background[Price] : {price}")
            st.write(f":green-background[Amenities] : {amenities}")
            st.write(f":green-background[Summary] : {summary}")
            st.write(f":green-background[Notes] : {notes}")
            st.write(f":green-background[Security Deposit] : {security_deposit}")
            st.write(f":green-background[House Rules] : {house_rules}")
            st.write(f":green-background[Cleaning Fee] : {cleaning_fee}")
            st.write(f":green-background[Extra People] : {extra_people}")
            st.write(f":green-background[Guest Included] : {guests_included}")
            st.write(f":green-background[Host Name] : {host_name}")
            st.write(f":green-background[Host Location] : {host_location}")
        else:
            st.write("No additional information available.")

    
    def review_info(selected_id):
        query = f"""
            SELECT 
                review_scores_accuracy, review_scores_cleanliness, review_scores_checkin,
                review_scores_communication, review_scores_location, review_scores_value,
                review_scores_rating
            FROM 
                review_score
            WHERE 
                listing_id = {selected_id}
        """
        cursor.execute(query)
        review_details = cursor.fetchone()
        
        if review_details:
            (
                review_scores_accuracy, review_scores_cleanliness, review_scores_checkin,
                review_scores_communication, review_scores_location, review_scores_value,
                review_scores_rating
            ) = review_details
            
            st.header("Review Scores:")
            st.write(f":blue-background[Accuracy Score]: {review_scores_accuracy}")
            st.write(f":blue-background[Cleanliness Score]: {review_scores_cleanliness}")
            st.write(f":blue-background[Check-in Score]: {review_scores_checkin}")
            st.write(f":blue-background[Communication Score]: {review_scores_communication}")
            st.write(f":blue-background[Location Score]: {review_scores_location}")
            st.write(f":blue-background[Value Score]: {review_scores_value}")
            st.write(f":blue-background[Overall Rating]: {review_scores_rating}")
        else:
            st.write("No review information available for this listing.")
        # Fetch reviews for the listing
        review_query = f"""
            SELECT 
                reviewer_name, comments
            FROM 
                review
            WHERE 
                listing_id = {selected_id}
        """
        cursor.execute(review_query)
        reviews = cursor.fetchall()

        if reviews:
            st.header("Reviews:")
            for reviewer_name, comment in reviews:
                st.markdown(f":red-background[**{reviewer_name}**]:\n{comment}")
        else:
            st.write("No reviews available for this listing.")
    # Handle clicks on the ID
    selected_id = st.text_input("Enter the ID to get more details", "")
    if selected_id:
        display_info(selected_id)
        review_info(selected_id)
    
    # Function to display review information
    



with tab2:
    # Query for property_type, room_type, and price
    query1 = "SELECT property_type, room_type, price FROM most"
    cursor.execute(query1)
    results1 = cursor.fetchall()

    # Convert the results to a DataFrame
    df1 = pd.DataFrame(results1, columns=['Property_Type', 'Room_Type', 'Price'])

    # Multiselect widget for selecting property types with unique key
    property_types = st.multiselect("Select Property Types", df1['Property_Type'].unique(), key="property_types_selector")

    # Slider for setting price range
    price_range = st.slider("Select Price Range", min_value=0, max_value=48842, value=(0, 48842))

    # Filter DataFrame based on selected property types and price range
    filtered_df1 = df1[df1['Property_Type'].isin(property_types) & (df1['Price'] >= price_range[0]) & (df1['Price'] <= price_range[1])]

    # Display the filtered price variation graph
    st.write("### Price Variation by Property Type and Room Type")
    fig1 = px.box(filtered_df1, x='Property_Type', y='Price', color='Room_Type', title="Price Variation by Property Type and Room Type")
    st.plotly_chart(fig1)

    # Query to fetch price and country
    query = """
        SELECT m.price, a.country
        FROM most AS m
        INNER JOIN address AS a ON m._id = a.listing_id
    """
    cursor.execute(query)
    results = cursor.fetchall()

    # Convert results to a DataFrame
    df = pd.DataFrame(results, columns=['Price', 'Country'])

    # Calculate the average price of all listings
    overall_avg_price = df['Price'].mean()

    # Calculate the average price for each country
    country_avg_prices = df.groupby('Country')['Price'].mean().reset_index()
    country_avg_prices.columns = ['Country', 'Average_Price']

    # Display the average price of all listings
    st.write(f"### Overall Average Price: ${overall_avg_price:.2f}")

    # Display the average prices by country
    st.write("### Average Price by Country")

    # Create bar plot using Plotly Express
    fig = px.bar(country_avg_prices, x='Country', y='Average_Price', title='Average Price by Country')
    fig.update_layout(xaxis_title='Country', yaxis_title='Average Price')
    st.plotly_chart(fig)
    
    # Query to fetch country
    query = """
        SELECT a.country
        FROM address AS a
        INNER JOIN most AS m ON a.listing_id = m._id
    """
    cursor.execute(query)
    results = cursor.fetchall()

    # Convert results to a DataFrame
    df = pd.DataFrame(results, columns=['Country'])

    # Calculate the total number of listings for each country
    country_listing_counts = df['Country'].value_counts().reset_index()
    country_listing_counts.columns = ['Country', 'Total_Listings']

    # Display the total listings by country
    st.write("### Total Number of Listings by Country")

    # Create bar plot using Plotly Express
    fig = px.bar(country_listing_counts, x='Country', y='Total_Listings', title='Total Number of Listings by Country')
    fig.update_layout(xaxis_title='Country', yaxis_title='Total Listings')
    st.plotly_chart(fig)


with tab3:
    # Query to fetch latitude, longitude, country, suburb, and government area data
    query = "SELECT latitude, longitude, country, suburb, government_area FROM address"
    cursor.execute(query)
    results = cursor.fetchall()

    # Convert results to a DataFrame
    df = pd.DataFrame(results, columns=['Latitude', 'Longitude', 'Country', 'Suburb', 'Government_Area'])

    # Unique countries for dropdown selection
    countries = df['Country'].unique()

    st.header("Select Filters")
    selected_country = st.selectbox("Choose a country", countries)

    # Filter options based on selected country
    filtered_suburbs = df[df['Country'] == selected_country]['Suburb'].unique()
    selected_suburb = st.selectbox("Choose a suburb", filtered_suburbs)

    filtered_areas = df[df['Country'] == selected_country]['Government_Area'].unique()
    selected_area = st.selectbox("Choose a government area", filtered_areas)

    # Filter data based on selected country, suburb, and government area
    filtered_data = df[(df['Country'] == selected_country) & (df['Suburb'] == selected_suburb) & (df['Government_Area'] == selected_area)]

    # Create a Folium map centered on the selected country
    m = folium.Map(location=[filtered_data['Latitude'].mean(), filtered_data['Longitude'].mean()], zoom_start=6)

    # Add markers for latitude and longitude inside the selected country, suburb, and government area
    for index, row in filtered_data.iterrows():
        folium.Marker([row['Latitude'], row['Longitude']]).add_to(m)

    # Display the Folium map using streamlit-folium
    st.header("Map of Selected Locations")
    folium_static(m)