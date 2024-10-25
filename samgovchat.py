import streamlit as st
import openai
import requests
from datetime import datetime, timedelta

# Set API keys from Streamlit secrets
openai.api_key = st.secrets["openai"]["api_key"]
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
    
    # Debug output to verify API request parameters
    st.write("API Request URL:", url)
    st.write("Request Parameters:", params)

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        st.write(f"Error: {response.status_code} - {response.text}")
        return None

# Function to ask further questions about an opportunity
def chat_about_opportunity(opportunity, question):
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an assistant that provides insights about government contract opportunities."},
            {"role": "assistant", "content": f"Here is a government contract opportunity: {opportunity}"},
            {"role": "user", "content": question}
        ]
    )
    return response.choices[0].message.content.strip()

# Streamlit UI
st.title("SAM.gov Opportunity Search with Chat")
st.write("Ask questions in natural language to find relevant government opportunities on SAM.gov and chat further about each opportunity.")

# Input field for natural language query
natural_query = st.text_input("Enter your search query:", "Looking for environmental services opportunities")

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

# Store results in session state to prevent reset
if "opportunities" not in st.session_state:
    st.session_state["opportunities"] = []

if st.button("Search"):
    st.write("Searching SAM.gov...")
    results = search_sam_gov(natural_query, ptype_code, posted_from, posted_to)
    if results and "opportunitiesData" in results:
        st.session_state["opportunities"] = results["opportunitiesData"]
    else:
        st.session_state["opportunities"] = []  # Clear if no results found
        st.write("No opportunities found or an error occurred.")

# Display results with chat option for each opportunity
for i, opportunity in enumerate(st.session_state["opportunities"]):
    with st.expander(opportunity.get("title", "No Title")):
        st.write("ID:", opportunity.get("noticeId", "N/A"))
        st.write("Type:", opportunity.get("type", "N/A"))
        st.write("Department:", opportunity.get("department", "N/A"))
        st.write("Posted Date:", opportunity.get("postedDate", "N/A"))
        st.write("Solicitation Number:", opportunity.get("solicitationNumber", "N/A"))
        st.write("Link:", opportunity.get("uiLink", "N/A"))
        
        # Input for follow-up questions on the opportunity, stored in session state
        question_key = f"question_{i}"
        if question_key not in st.session_state:
            st.session_state[question_key] = ""
        
        question = st.text_input(f"Ask about this opportunity (ID: {opportunity.get('noticeId', 'N/A')})", key=question_key)
        
        if st.button("Ask", key=f"ask_button_{i}"):
            if question:
                answer = chat_about_opportunity(opportunity, question)
                st.session_state[f"answer_{i}"] = answer  # Store answer to avoid reset
            else:
                st.write("Please enter a question.")
        
        # Display answer if available
        if f"answer_{i}" in st.session_state:
            st.write("Answer:", st.session_state[f"answer_{i}"])
