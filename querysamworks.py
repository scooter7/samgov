import streamlit as st
import requests
from datetime import datetime, timedelta

# Set API key from Streamlit secrets
samgov_api_key = st.secrets["samgov"]["api_key"]

# SAM.gov API search function with required parameters
def search_sam_gov(query, ptype, posted_from, posted_to):
    url = "https://api.sam.gov/prod/opportunities/v2/search"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {samgov_api_key}"
    }
    params = {
        "api_key": samgov_api_key,
        "keywords": query,
        "ptype": ptype,
        "postedFrom": posted_from,
        "postedTo": posted_to,
        "limit": 10,
        "offset": 0,
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        st.write(f"Error: {response.status_code} - {response.text}")
        return None

# Streamlit UI
st.title("SAM.gov Opportunity Search")
st.write("Enter your search criteria to find relevant government opportunities on SAM.gov.")

# Input fields for search parameters
natural_query = st.text_input("Enter keywords:", "environmental services")

# Required parameter: Procurement Type
procurement_types = {
    "Justification (J&A)": "u",
    "Pre-solicitation": "p",
    "Award Notice": "a",
    "Sources Sought": "r",
    "Special Notice": "s",
    "Solicitation": "o",
    "Sale of Surplus Property": "g",
    "Combined Synopsis/Solicitation": "k",
    "Intent to Bundle Requirements (DoD-Funded)": "i",
}
ptype = st.selectbox("Select Procurement Type", options=list(procurement_types.keys()))
ptype_code = procurement_types[ptype]

# Required date fields
today = datetime.today()
default_posted_from = (today - timedelta(days=30)).strftime("%m/%d/%Y")
posted_from = st.text_input("Posted Date From (MM/DD/YYYY):", default_posted_from)
posted_to = st.text_input("Posted Date To (MM/DD/YYYY):", today.strftime("%m/%d/%Y"))

if st.button("Search"):
    if natural_query:
        st.write("Searching SAM.gov...")
        results = search_sam_gov(natural_query, ptype_code, posted_from, posted_to)

        # Display results
        if results and "opportunitiesData" in results:
            opportunities = results["opportunitiesData"]
            if opportunities:
                for i, opportunity in enumerate(opportunities):
                    with st.expander(opportunity.get("title", "No Title")):
                        st.write("ID:", opportunity.get("noticeId", "N/A"))
                        st.write("Type:", opportunity.get("type", "N/A"))
                        st.write("Department:", opportunity.get("department", "N/A"))
                        st.write("Posted Date:", opportunity.get("postedDate", "N/A"))
                        st.write("Solicitation Number:", opportunity.get("solicitationNumber", "N/A"))
                        st.write("Link:", opportunity.get("uiLink", "N/A"))
            else:
                st.write("No opportunities found.")
        else:
            st.write("No opportunities found or an error occurred.")
    else:
        st.write("Please enter keywords to search.")
