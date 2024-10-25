import streamlit as st
import openai
import requests

# Set API keys from Streamlit secrets
openai.api_key = st.secrets["openai"]["api_key"]
samgov_api_key = st.secrets["samgov"]["api_key"]

# GPT-4o-mini API call function to convert natural language to SAM.gov query
def get_structured_query(natural_query):
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an assistant that helps format queries for government contract opportunities."},
            {"role": "user", "content": f"Translate this natural language query into a structured query for SAM.gov: {natural_query}"}
        ]
    )
    return response.choices[0].message.content.strip()

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

# Function to generate response from GPT about specific opportunities
def chat_about_opportunity(opportunity, question):
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an assistant that helps users understand government contract opportunities."},
            {"role": "user", "content": f"Here is a government contract opportunity: {opportunity}. The user has a question about it: {question}"}
        ]
    )
    return response.choices[0].message.content.strip()

# Streamlit UI
st.title("SAM.gov Opportunity Search")
st.write("Enter your search query in natural language to find relevant government opportunities on SAM.gov.")

# Input field for natural language query
natural_query = st.text_input("Enter your query:", "Looking for IT support contracts in California")

if st.button("Search"):
    if natural_query:
        st.write("Generating structured query...")
        structured_query = get_structured_query(natural_query)
        st.write("Structured query:", structured_query)

        st.write("Searching SAM.gov...")
        results = search_sam_gov(structured_query)

        # Display results
        if "opportunities" in results:
            opportunity_list = results["opportunities"]
            for i, opportunity in enumerate(opportunity_list):
                with st.expander(opportunity.get("title", "No Title")):
                    st.write("ID:", opportunity.get("noticeId", "N/A"))
                    st.write("Type:", opportunity.get("type", "N/A"))
                    st.write("Location:", opportunity.get("location", "N/A"))
                    st.write("Details:", opportunity.get("url", "N/A"))
                    
                    # Input for follow-up questions on the opportunity
                    question = st.text_input(f"Ask about this opportunity (ID: {opportunity.get('noticeId', 'N/A')})", key=f"question_{i}")
                    if st.button("Ask", key=f"ask_button_{i}"):
                        if question:
                            answer = chat_about_opportunity(opportunity, question)
                            st.write("Answer:", answer)
                        else:
                            st.write("Please enter a question.")
        else:
            st.write("No opportunities found.")
    else:
        st.write("Please enter a query to search.")
