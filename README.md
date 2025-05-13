# Multi-Agent Streamlit Application with OpenAI Agents

This project demonstrates how to build a multi-agent application using the `openai-agents` Python library, presented through a Streamlit web interface. The application features a Triage Agent that routes user queries to specialized agents: a Stock Agent for financial data and a Spanish Agent for conversations in Spanish.

## Core Concepts of the `openai-agents` Library

The `openai-agents` library provides a framework for creating and orchestrating sophisticated AI agents. Here are some of the core concepts used in this example:

1.  **`Agent`**:
    *   An `Agent` is an AI entity powered by a language model (e.g., from OpenAI).
    *   It is defined with a `name`, `instructions` (which guide its behavior and responses), and optionally, `tools` it can use and `handoffs` to other agents.
    *   **Example (`app.py`)**:
        *   `stock_agent`: Instructed to provide stock information and uses the `get_stock_data_tool`.
        *   `spanish_agent`: Instructed to converse only in Spanish.
        *   `triage_agent`: Instructed to analyze user input and route to either the `stock_agent` or `spanish_agent`.

2.  **`@function_tool`**:
    *   This decorator is used to make regular Python functions available as "tools" that an `Agent` can decide to use.
    *   The agent's underlying language model is made aware of these tools (their names, descriptions, and input schemas) and can decide when and how to call them based on its instructions and the user's query.
    *   **Example (`app.py`)**:
        *   The `get_stock_data_tool(symbol: str) -> str` function uses `yfinance` to fetch stock data. It's decorated with `@function_tool`, allowing the `stock_agent` to utilize it.

3.  **`handoffs`**:
    *   An `Agent` can be configured with a list of other agents it can "handoff" a conversation or task to.
    *   The agent's instructions should guide it on when and how to decide to initiate a handoff. This allows for creating sophisticated workflows where different agents handle different parts of a user's request.
    *   **Example (`app.py`)**:
        *   The `triage_agent` has `stock_agent` and `spanish_agent` in its `handoffs` list. Its instructions tell it to route queries based on content (stock-related or Spanish language).

4.  **`Runner`**:
    *   The `Runner` is responsible for executing an agent or a chain of agents.
    *   The `Runner.run(agent, input_string)` method takes an initial agent and the user's input. It manages the interaction with the language model, tool execution (if the agent decides to use one), and handoffs between agents.
    *   It returns a result object, from which `result.final_output` can be extracted.
    *   **Example (`app.py`)**:
        *   When a user submits a query in the Streamlit app, `Runner.run(triage_agent, prompt)` is called to start the agent interaction.

## Structure of `app.py`

The `app.py` file in this project is structured as follows:

1.  **Imports**: Necessary libraries like `streamlit`, `asyncio`, `yfinance`, and components from the `agents` library (`Agent`, `Runner`, `function_tool`). It also uses `dotenv` for managing API keys.
2.  **Tool Definition**:
    *   `get_stock_data_tool()`: A Python function decorated with `@function_tool` to make it available to agents.
3.  **Agent Definitions**:
    *   `stock_agent`: Configured with specific instructions to use the stock tool and its name.
    *   `spanish_agent`: Configured with instructions to only speak Spanish.
    *   `triage_agent`: Configured with instructions to analyze input and handoff to the appropriate specialist agent (`stock_agent` or `spanish_agent`).
4.  **Streamlit UI**:
    *   Sets up the page title and caption.
    *   Manages and displays a chat history using `st.session_state`.
    *   Provides a chat input field for users.
5.  **Asyncio Event Loop Handling**:
    *   When user input is received, it explicitly creates and sets a new `asyncio` event loop to run the `Runner.run()` coroutine. This is important for integrating asyncio-based libraries like `openai-agents` with Streamlit.
6.  **Agent Execution**:
    *   `loop.run_until_complete(Runner.run(triage_agent, prompt))` is the core call that initiates the agent processing pipeline starting with the `triage_agent`.
    *   The final output from the agent interaction is then displayed in the chat.

## Setup and Running the Application

To run this application on your local machine, follow these steps:

1.  **Clone the Repository (if applicable) or Create Project Files**:
    Ensure you have `app.py` and this `README.md`.

2.  **Create a Virtual Environment (Recommended)**:
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

3.  **Install Dependencies**:
    You'll need `streamlit`, `yfinance`, the `openai-agents` library, and `python-dotenv`. Create a `requirements.txt` file with the following content:
    ```
    streamlit
    yfinance
    openai-agents
    python-dotenv
    ```
    Then install them:
    ```bash
    pip install -r requirements.txt
    ```
    *Note: The `openai-agents` library might have its own specific installation instructions or extras (e.g., for OpenAI models); refer to its official documentation.*

4.  **Set Up Environment Variables**:
    The `openai-agents` library will likely require an API key for the underlying language model provider (e.g., OpenAI). Create a `.env` file in the root of your project directory:
    ```env
    OPENAI_API_KEY="your_openai_api_key_here"
    ```
    Replace `"your_openai_api_key_here"` with your actual API key. `app.py` uses `load_dotenv()` to load this key.

5.  **Run the Streamlit Application**:
    ```bash
    streamlit run app.py
    ```
    This will start the Streamlit server, and you can access the application in your web browser (usually at `http://localhost:8501`).

## Customizing and Further Development

This example provides a basic framework. You can extend it in many ways:

*   **Add More Agents**: Define new `Agent` instances with different instructions, tools, or handoff capabilities for more specialized tasks.
*   **Create New Tools**: Write new Python functions for specific actions (e.g., database lookups, calling other APIs, performing calculations) and decorate them with `@function_tool` to make them available to your agents.
*   **Modify Agent Instructions**: Experiment with different phrasings and levels of detail in agent instructions to fine-tune their behavior, decision-making for tool use, and handoff logic.
*   **Implement More Complex Workflows**: Design intricate chains of handoffs between multiple agents to handle multi-step processes.
*   **Explore Advanced `openai-agents` Features**: The library offers features like streaming, guardrails, different model configurations, and more, which you can explore in its official documentation.

This application serves as a starting point for understanding and building powerful applications with the `openai-agents` library.
 
