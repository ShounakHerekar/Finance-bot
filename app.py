import streamlit as st
from backend import analyze_stock
# Page config
st.set_page_config(page_title="AI Stock Analyst", page_icon="📈", layout="wide")

# Title
st.title("📈 AI Stock Analyst Chatbot")

# Sidebar for stock input
st.sidebar.header("Stock Lookup")
ticker = st.sidebar.text_input("Enter Stock Symbol (e.g., AAPL, TSLA, INFY)", "AAPL")

# Main chat area
st.subheader("Chat with the AI Analyst")
user_question = st.text_area("Ask me anything about this stock:")

if st.button("Analyze"):
    with st.spinner("Fetching data and analyzing..."):

        print(ticker, user_question)  # Debugging line
        result, chart = analyze_stock(ticker, user_question)
        if chart:
            st.plotly_chart(chart, use_container_width=True)
        st.write(result)
