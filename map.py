import streamlit as st
import openai
from streamlit_folium import st_folium
import folium
from geopy.geocoders import Nominatim

col1, col2 = st.columns([2, 3])

with col1:
    st.header("🗺️ Map")
    if "location" not in st.session_state:
        st.session_state["location"] = {"lat": 48.8566, "lon": 2.3522, "name": "Paris"}

    loc = st.session_state["location"]

    # Create the map centered at the location
    m = folium.Map(location=[loc["lat"], loc["lon"]], zoom_start=12)
    folium.Marker([loc["lat"], loc["lon"]], popup=loc["name"]).add_to(m)

    # Display the map
    st_folium(m, width=800, height=400)

with col2:
    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    st.header("💬 Chat locations")
    

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4o-mini"

if "message" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"]) 

if prompt := st.chat_input("what is up"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)


    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})

    


    location_text  = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content":  location_text })
    location_text = prompt

    
    geolocator = Nominatim(user_agent="map-app")
    location = geolocator.geocode(location_text)

    if location:
            st.success(f"Found location: {location.address}")
            # Update session state
            st.session_state["location"] = {
                "lat": location.latitude,
                "lon": location.longitude,
                "name": location_text
            }
    else:
        st.error("Sorry, location not found.")

