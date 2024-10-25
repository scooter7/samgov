import streamlit as st
import requests

# Set API keys from Streamlit secrets
samgov_api_key = st.secrets["samgov"]["api_key"]

# SAM.gov API search function
def search_sam_gov(query):
    url = "https://api.sam.gov/prod/opportunities/v1/search"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {samgov_api_key}"
    }
    params = {
        "q": query,
        "page": 1,
        "size": 10
    }
    response = requests.get(url, headers=headers, params=params)
    return response.json()

# Streamlit UI
st.title("SAM.gov Opportunity Search")
st.write("Enter your search query in natural language to find relevant government opportunities on SAM.gov.")

# Input field for natural language query
natural_query = st.text_input("Enter your query:", "environmental services")

if st.button("Search"):
    if natural_query:
        st.write("Searching SAM.gov...")
        results = search_sam_gov(natural_query)

        # Display results
        if "opportunities" in results:
            opportunity_list = results["opportunities"]
            if opportunity_list:
                for i, opportunity in enumerate(opportunity_list):
                    with st.expander(opportunity.get("title", "No Title")):
                        st.write("ID:", opportunity.get("noticeId", "N/A"))
                        st.write("Type:", opportunity.get("type", "N/A"))
                        st.write("Location:", opportunity.get("location", "N/A"))
                        st.write("Details:", opportunity.get("url", "N/A"))
            else:
                st.write("No opportunities found.")
        else:
            st.write("No opportunities found.")
    else:
        st.write("Please enter a query to search.")
