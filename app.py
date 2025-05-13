import streamlit as st
import asyncio
import yfinance as yf
from agents import Agent, Runner, function_tool
from dotenv import load_dotenv

load_dotenv()

@function_tool
def get_stock_data_tool(symbol: str) -> str:
    """
    Fetches key stock data for a given ticker symbol using yfinance.
    Returns a string with: name, current price, day's high/low, change, and market cap.
    If data is not found or an error occurs, it returns an error message.
    """
    try:
        ticker = yf.Ticker(symbol.upper())
        info = ticker.info

        if not info or info.get('regularMarketPrice') is None and info.get('currentPrice') is None:
            return f"Could not find valid market data for symbol: {symbol}."

        name = info.get("longName", info.get("shortName", symbol))
        current_price = info.get("currentPrice", info.get("regularMarketPrice"))
        day_high = info.get("dayHigh")
        day_low = info.get("dayLow")
        
        if current_price is None:
             return f"Could not retrieve current price for {name} ({symbol}). Data might be unavailable."

        response_parts = [f"Stock: {name} ({symbol})", f"Current Price: ${current_price:.2f}"]
        if day_high is not None and day_low is not None:
            response_parts.append(f"Day's Range: ${day_low:.2f} - ${day_high:.2f}")
        
        prev_close = info.get("previousClose")
        if prev_close is not None and current_price is not None:
            change = current_price - prev_close
            percent_change = (change / prev_close) * 100 if prev_close != 0 else 0
            response_parts.append(f"Change: ${change:.2f} ({percent_change:.2f}%)")
            
        market_cap = info.get("marketCap")
        if market_cap:
            response_parts.append(f"Market Cap: ${market_cap:,}")
            
        return ", ".join(response_parts)
    except Exception as e:
        print(f"Error in get_stock_data_tool for {symbol}: {e}")
        return f"Error fetching data for {symbol}. Please ensure the symbol is correct and try again."

stock_agent = Agent(
    name="Stock Agent",
    instructions="You are a financial assistant. Your primary role is to provide stock information for a given stock symbol using the 'get_stock_data_tool'. Present the information clearly. If a symbol is not provided or is unclear, ask for clarification. Only use the tool if a stock symbol is explicitly mentioned or strongly implied.",
    tools=[get_stock_data_tool],
)


spanish_agent = Agent(
    name="Spanish Agent",
    instructions="Eres un agente de IA útil que solo habla y responde en español. Si una consulta no está en español, indica cortésmente que solo entiendes español y no puedes procesar la solicitud. (You are a helpful AI agent that only speaks and responds in Spanish. If a query is not in Spanish, politely state that you only understand Spanish and cannot process the request.)",
)


triage_agent = Agent(
    name="Triage Agent",
    instructions="""Your role is to analyze the user's request and route it appropriately.
- If the request is clearly about stock prices, company financial data, or mentions a specific stock ticker symbol (e.g., MSFT, AAPL, GOOG, TSLA), handoff to the 'Stock Agent'.
- If the request is primarily in Spanish, or the user is attempting to communicate in Spanish (e.g., starts with 'Hola', contains '¿cómo estás?'), handoff to the 'Spanish Agent'.
- If the request does not clearly fall into the above categories, or if it's ambiguous, you should state that you are a Triage Agent and can route to a Stock Agent for financial data or a Spanish Agent for conversations in Spanish, then ask the user for clarification on how they'd like to proceed. Avoid making up answers for topics outside these areas.""",
    handoffs=[stock_agent, spanish_agent],
)


# Streamlit App
st.title("Multi-Agent AI Chat")
st.caption("Powered by Hakkoda")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello! How can I assist you today? I can fetch stock data (e.g., 'What's the price of GOOGL?') or chat in Spanish (e.g., 'Hola')."}]

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Ask about stocks or say 'hola'..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        with st.spinner("Agents are processing your request..."):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(Runner.run(triage_agent, prompt))
                response = result.final_output
                
            except Exception as e:
                st.error(f"An error occurred while running the agent: {str(e)}")
                response = "Sorry, I encountered an error processing your request."
            
            message_placeholder.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

st.sidebar.info("""
**About this app:**
This demo showcases a multi-agent system using the `agents` API:
- **Triage Agent**: Analyzes your query and routes it.
- **Stock Agent**: Uses the `get_stock_data_tool` to fetch financial data.
- **Spanish Agent**: Responds in Spanish.

Enter a query like "What's the stock price for AAPL?" or "Hola, ¿qué tal?"
""")
