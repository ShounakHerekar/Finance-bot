import os
from dotenv import load_dotenv
from yahooquery import Ticker
import plotly.express as px
from mistralai import Mistral

# Load environment variables
load_dotenv()
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

# Initialize Mistral client
client = Mistral(api_key=MISTRAL_API_KEY)
# mistral-large-latest open-mistral-7b
def call_mistral(prompt: str, model: str = "open-mistral-7b"):
    response = client.chat.complete(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


def analyze_stock(ticker: str, question: str):
    """
    Fetch stock data via YahooQuery, create a chart, and generate AI-powered analysis.
    Returns: (answer_text, plotly_chart)
    """
    try:
        # Fetch stock data
        stock = Ticker(ticker)
        hist = stock.history(period="6mo")
        summary = stock.summary_detail
        key_stats = stock.key_stats

        if hist.empty:
            return f"⚠️ No data found for {ticker}. Please check the symbol.", None

        # YahooQuery returns multi-index; reset it
        hist = hist.reset_index()
        if "close" not in hist.columns:
            return f"⚠️ Could not find price data for {ticker}.", None

        # Create chart
        fig = px.line(
            hist,
            x="date",
            y="close",
            title=f"{ticker} Closing Price (Last 6 Months)"
        )

        # Extract details safely
        info = summary.get(ticker, {})
        stats = key_stats.get(ticker, {})

        current_price = hist["close"].iloc[-1]
        high_52 = info.get("fiftyTwoWeekHigh")
        low_52 = info.get("fiftyTwoWeekLow")
        market_cap = info.get("marketCap") or stats.get("marketCap")
        pe_ratio = stats.get("trailingPE") or info.get("trailingPE")
        dividend_yield = info.get("dividendYield")

        # Build AI prompt
        prompt = f"""
        The user asked: "{question}"
        Stock: {ticker}
        Current Price: {current_price:.2f}
        52-week High: {high_52}
        52-week Low: {low_52}
        Market Cap: {market_cap}
        P/E Ratio: {pe_ratio}
        Dividend Yield: {dividend_yield}

        Based on the above data and the historical price chart,if possible provide insights, trends, and answer the user's question.
        Please summarize this information clearly and concisely in plain English.
        """

        # Call Mistral
        answer = call_mistral(prompt)
        return answer, fig

    except Exception as e:
        fallback_prompt = f"""
        The user asked about {ticker}, but stock data could not be fetched.
        The error was: {str(e)}.
        Please explain to the user in simple, polite English why the data might be unavailable
        (e.g., rate limits, invalid ticker, or temporary outage),
        and suggest trying again later or with another stock.
        """
        answer = call_mistral(fallback_prompt)
        return answer, None
