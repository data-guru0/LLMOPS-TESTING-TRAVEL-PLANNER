import streamlit as st
from src.core.planner import TravelPlanner

st.set_page_config(page_title="Travel Itinerary Planner", page_icon="🗺️")
st.title("🗺️ Travel Itinerary Planner")
st.write("Plan your day trip itinerary by entering a city and your interests!")

with st.form("planner_form"):
    city = st.text_input("Enter the city for your day trip")
    interests = st.text_input("Enter your interests (comma-separated)")
    submitted = st.form_submit_button("Generate Itinerary")

if submitted:
    if city and interests:
        planner = TravelPlanner()
        planner.set_city(city)
        planner.set_interests(interests)
        itinerary = planner.create_itinerary()

        st.subheader("📝 Your Itinerary")
        st.markdown(itinerary)
    else:
        st.warning("Please enter both city and interests.")
