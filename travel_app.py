import streamlit as st
import pandas as pd
from datetime import datetime
import requests  # Import requests for API calls
from openpyxl import load_workbook

# Page configuration for a better layout
st.set_page_config(page_title="GLOBO Travel - All Travel Plans Under One Roof", layout="wide")

# Function to load data from Excel
@st.cache_data
def load_data(url):
    try:
        data = pd.read_excel(url, engine='openpyxl')
        if data.empty:
            st.error("The Excel file is empty.")
            st.stop()
        return data
    except Exception as e:
        st.error(f"An error occurred while loading the data: {e}")
        st.stop()

# Update the URL to the raw link
url = 'https://raw.githubusercontent.com/rajeevdhoni/Globo-Travel/main/updated_travel_data.xlsx'

# Load the travel data
travel_data = load_data(url)

# Ensure necessary columns are present
required_columns = ['Travel Company', 'Trip Location', 'People per Trip', 'Fees', 'Other Details', 'Departure Date', 'Return Date', 'Star Rating', 'Amenities', 'Travel Type', 'Image URL']
for col in required_columns:
    if col not in travel_data.columns:
        st.error(f"Missing column: {col}")
        st.stop()

# Convert 'Departure Date' and 'Return Date' to datetime
travel_data['Departure Date'] = pd.to_datetime(travel_data['Departure Date'])
travel_data['Return Date'] = pd.to_datetime(travel_data['Return Date'])

# App title and description
st.title('🌍 GLOBO Travel')
st.subheader('All Travel Plans Under One Roof')
st.write('Discover global travel plans that suit everyone’s needs, from budget trips to luxury getaways.')
st.write('---')
st.write('Guided by Dr. PRANJALI GAJBHIYE')

# Sidebar filters
st.sidebar.header('Filter Your Trip')

# Location Filter
location_filter = st.sidebar.multiselect('Trip Location', options=sorted(travel_data['Trip Location'].unique()), default=sorted(travel_data['Trip Location'].unique()))

# People per Trip Filter
people_filter = st.sidebar.slider('People per Trip', min_value=1, max_value=int(travel_data['People per Trip'].max()), value=(1, int(travel_data['People per Trip'].max())))

# Fees Filter
fees_filter = st.sidebar.slider('Fees (₹)', min_value=int(travel_data['Fees'].min()), max_value=int(travel_data['Fees'].max()), value=(int(travel_data['Fees'].min()), int(travel_data['Fees'].max())))

# Departure Date Range Filter
departure_date_range = st.sidebar.date_input('Departure Date Range', value=[travel_data['Departure Date'].min().date(), travel_data['Departure Date'].max().date()])

# Return Date Range Filter
return_date_range = st.sidebar.date_input('Return Date Range', value=[travel_data['Return Date'].min().date(), travel_data['Return Date'].max().date()])

# Star Rating Filter
star_rating = st.sidebar.selectbox('Star Rating', options=[1, 2, 3, 4, 5], index=4)

# Amenities Filter
amenities_list = ['Parking', 'Swimming Pool', 'Free Wi-Fi', 'Restaurant', 'Gym']
selected_amenities = st.sidebar.multiselect('Amenities', options=amenities_list, default=amenities_list)

# Travel Type Filter
travel_type_list = ['Solo', 'Business', 'Leisure', 'Family']
travel_type_filter = st.sidebar.multiselect('Travel Type', options=travel_type_list, default=travel_type_list)

# Sort options
sort_by = st.sidebar.selectbox('Sort by', ['Fees', 'People per Trip', 'Trip Location'])

# Apply Filters button
apply_filters = st.sidebar.button('Apply Filters')

# Save Wish List in session state
if 'wish_list' not in st.session_state:
    st.session_state.wish_list = []

# Function to add trip to wish list
def add_to_wish_list(trip_location):
    if trip_location not in st.session_state.wish_list:
        st.session_state.wish_list.append(trip_location)
        st.success(f"{trip_location} added to your Wish List!")

# Apply filters and sorting once the button is clicked
if apply_filters:
    # Filter data based on selections
    filtered_data = travel_data[
        (travel_data['Trip Location'].isin(location_filter)) &
        (travel_data['People per Trip'].between(people_filter[0], people_filter[1])) &
        (travel_data['Fees'].between(fees_filter[0], fees_filter[1])) &
        (travel_data['Star Rating'] >= star_rating) &
        (travel_data['Departure Date'].between(pd.to_datetime(departure_date_range[0]), pd.to_datetime(departure_date_range[1]))) &
        (travel_data['Return Date'].between(pd.to_datetime(return_date_range[0]), pd.to_datetime(return_date_range[1]))) &
        (travel_data['Travel Type'].str.contains('|'.join(travel_type_filter), case=False, na=False)) &
        (travel_data['Amenities'].str.contains('|'.join(selected_amenities), case=False, na=False))
    ].sort_values(by=sort_by, ascending=True)

    # Display filtered results
    if filtered_data.empty:
        st.write("No trips match your criteria.")
    else:
        st.subheader('Filtered Travel Plans')

        # Display each filtered trip with details
        for index, row in filtered_data.iterrows():
            st.write('---')
            col1, col2 = st.columns([2, 1])  # Create two columns (left for info, right for image)

            # Left column for trip information
            with col1:
                st.markdown(f"### {row['Travel Company']}")
                st.markdown(f"**Trip Location:** {row['Trip Location']}")
                st.markdown(f"**People per Trip:** {row['People per Trip']}")
                st.markdown(f"**Fees:** ₹{row['Fees']}")
                st.markdown(f"**Details:** {row['Other Details']}")
                st.markdown(f"**Departure Date:** {row['Departure Date'].strftime('%Y-%m-%d')}")
                st.markdown(f"**Return Date:** {row['Return Date'].strftime('%Y-%m-%d')}")
                st.markdown(f"**Star Rating:** {row['Star Rating']} stars")
                st.markdown(f"**Amenities:** {row['Amenities']}")
                st.markdown(f"**Travel Type:** {row['Travel Type']}")
                st.markdown(f"**Travel ID:** {row['Travel ID']}")

               

                

                # Book your trip
                st.markdown("[👆 to Book Your Adventure](https://forms.office.com/Pages/ResponsePage.aspx?id=DQSIkWdsW0yxEjajBLZtrQAAAAAAAAAAAAMAACcqb-tUMERWUEY3OUlESTdCQ05ZWTVNUVpVRDdLVy4u)", unsafe_allow_html=True)

                # Live chat button for assistance
                st.markdown("[💬 Chat for Assistance](https://chat.whatsapp.com/KjisiRz5L0yE51e7EWoriw)", unsafe_allow_html=True)

                # Add a review button with form link
                st.markdown(f"[📝 Add a Review Here](https://forms.office.com/Pages/ResponsePage.aspx?id=DQSIkWdsW0yxEjajBLZtrQAAAAAAAAAAAAMAACcqb-tUMFg3UE1SUVFQRVJMT002TDJXTkFMMEFZSS4u)", unsafe_allow_html=True)

                # Social sharing buttons with dynamic trip details
                trip_info = f"Check out this trip to {row['Trip Location']} with {row['Travel Company']}. Fees: ₹{row['Fees']}! Departure: {row['Departure Date'].strftime('%Y-%m-%d')}"
                
                st.write("**Share this trip:**")
                st.markdown(f"""
                <div style="display: inline-block; vertical-align: middle; margin: 10px 0;">
                    <a href="https://www.facebook.com/sharer/sharer.php?u=https://example.com&quote={trip_info}" target="_blank" style="margin-right: 10px;">
                        <img src="https://upload.wikimedia.org/wikipedia/commons/5/51/Facebook_f_logo_%282019%29.svg" alt="Facebook" style="width: 24px; height: 24px;">
                    </a>
                    <a href="https://api.whatsapp.com/send?text={trip_info}" target="_blank" style="margin-right: 10px;">
                        <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" alt="WhatsApp" style="width: 24px; height: 24px;">
                    </a>
                    <a href="https://www.instagram.com/" target="_blank">
                        <img src="https://upload.wikimedia.org/wikipedia/commons/a/a5/Instagram_icon.png" alt="Instagram" style="width: 24px; height: 24px;">
                    </a>
                </div>
                """, unsafe_allow_html=True)

            # Right column for image
            with col2:
                if pd.notna(row['Image URL']):
                    st.image(row['Image URL'], caption=f"{row['Trip Location']}", use_container_width=True)

        st.write('---')


# Wit.ai integration
st.sidebar.header("Ask Travel-Related Questions")

# Input box for user questions
question = st.sidebar.text_input("Type your question here...")

# Define your Wit.ai access token
WIT_AI_TOKEN = 'SBQCSPDLJPIIW54D6VEYQTON5C5KD3OW'  # Replace with your actual token

# Call Wit.ai API when the user asks a question
if question:
    url = f'https://api.wit.ai/message?v=20240101&q={question}'  # Use a valid date format for versioning
    headers = {
        'Authorization': f'Bearer {WIT_AI_TOKEN}'
    }
    
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        wit_response = response.json()
        
        # Extracting the message or relevant information
        if 'intents' in wit_response and wit_response['intents']:
            intent = wit_response['intents'][0]
            # Replace underscores with spaces in the intent name
            intent_name = intent['name'].replace('_', ' ')
            confidence = intent['confidence']
            answer = f"{intent_name}"
        else:
            answer = "I'm not sure how to help with that."

        # Display the answer
        st.markdown(f"### Answer:")
        st.markdown(f"> {answer}")
    else:
        st.error(f"Error fetching response from Wit.ai: {response.status_code} - {response.text}")




# Footer
st.write('---')
st.markdown('<div style="text-align: center; font-size: small;">© 2024 GLOBO Travel. All rights reserved.</div>', unsafe_allow_html=True)

