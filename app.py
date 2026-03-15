# app.py
import streamlit as st
import requests

st.title("📰 AI News Intelligence Agent")
st.write("Enter an event to search the web and generate an instant news briefing.")

event_query = st.text_input("Event Name (e.g., 'DeepSeek v3 release', 'India Budget')")

if st.button("Generate Briefing"):
    if event_query:
        with st.spinner(f"Agent is scraping news for '{event_query}'..."):
            try:
                # Call our local FastAPI endpoint
                response = requests.post(
                    "https://ai-news-test.onrender.com/research", 
                    json={"event_name": event_query}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    st.success("Briefing Generated!")
                    st.markdown(data["briefing"])
                else:
                    error_msg = response.json().get('detail', 'Unknown error occurred')
                    st.error(f"Error: {error_msg}")
            except requests.exceptions.ConnectionError:
                st.error("Failed to connect to the API. Make sure FastAPI (uvicorn) is running in the background!")
    else:
        st.warning("Please enter an event name.")

# Run with: streamlit run app.py