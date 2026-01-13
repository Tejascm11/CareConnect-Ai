import streamlit as st
from utils.location import get_nearby_hospitals_by_city

st.title("🏥 Nearby Hospitals")

city = st.text_input("Enter your city")

if city and st.button("Find"):
    hospitals, _ = get_nearby_hospitals_by_city(city)
    for h in hospitals:
        st.write(h["name"])
