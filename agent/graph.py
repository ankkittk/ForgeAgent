from dotenv import load_dotenv
from langchain_groq import ChatGroq

#--------------------------------------------

load_dotenv()

llm = ChatGroq(model="openai/gpt-oss-120b")

#--------------------------------------------

data = """On April 15, the S&P 500 opened at 5,120.35 and closed at 5,125.60, marking a +0.10% daily gain. Intraday high reached 5,140.20, while the low touched 5,100.75, resulting in a trading range of 39.45 points (0.77%).

The CBOE Volatility Index (VIX) declined from 14.8 to 13.9, indicating reduced market volatility. Total market volume for the session was approximately 11.2 billion shares, compared to the 30-day average of 9.5 billion, reflecting elevated trading activity.

Liquidity conditions remained strong, with bid-ask spreads across large-cap equities averaging 0.02%, and order book depth remaining above normal thresholds throughout the session.

Market sentiment remained cautiously optimistic, supported by positive earnings reports and stable macroeconomic indicators. The short-term trend remains sideways, with the index trading within a narrow consolidation range over the past five sessions."""

request = " Based on the above market data, provide a concise analysis of the current market conditions, including key indicators such as price level, volatility, market sentiment, volume, liquidity, and trend."

structure = """ 
    Schema():
        price_level: float
        volatility: float
        market_sentiment: str
        volume: int
        liquidity: float
        trend: str

    Format = JSON
    """

constraint = " (Answer in as few tokens as possible.)"

prompt = data + request + structure + constraint

response = llm.invoke(prompt)

print(response.content)                                       