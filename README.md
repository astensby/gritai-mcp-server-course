# GritAI MCP Server Examples

This project provides a collection of example MCP (Model Context Protocol) servers built with the Python SDK and specifically FastMCP, designed to be educational and showcase different functionalities. All examples are based on a simple starter server, `base_server_template.py`.

## Developing with Cursor

When using Cursor to develop MCP servers and clients, it is highly recommended to:

**Add Documentation to Cursor:**
  - It's recommended to add the MCP documentation to Cursor's knowledge base:
    - Add the MCP documentation (specifically for building with LLMs): https://modelcontextprotocol.io/llms-full.txt
    - Add the Python SDK documentation to assist with server development and understanding the SDK: https://github.com/modelcontextprotocol/python-sdk/blob/main/README.md


**Prompting:**
  - Prompt Cursor to create your MCP server
    ```text
      Build an MCP server in Python using @MCPPythonDocs that:
      Exposes a tool method that returns a random motivational quote from our file-based JSON database @motivational_quotes.json 
    ```

  - You can then iterate and ask Cursor to add more tool calls, even wrap API calls like this:
    ```text
      Help me implement the get_latest_incidents() function that will make use of the open external API that I can access here:
      curl -X 'GET' \
      'https://api.politiet.no/politiloggen/v1/messages' \
      -H 'accept: text/plain'
    ```

**Best practices:**
- Break down complex servers into smaller pieces
- Test each component thoroughly before moving on
- Keep security in mind - validate inputs and limit access appropriately
- Document your code well for future maintenance
- Follow MCP protocol specifications carefully

If you’re pulling data from APIs or databases, consider making your tools async using async def.


## Project Structure

- **`base_server_template.py`**: A minimal MCP server that acts as a template for creating new servers. It includes a basic "greeting" tool.
- **`examples/`**: This directory contains various example MCP servers, each in its own subdirectory.
    - Each example subdirectory (e.g., `01_motivational_quotes/`) contains the server script (e.g., `01_motivational_quotes_server.py`) and any related files (like data files or utility scripts).

## General Setup

1.  **Clone the repository (if you haven't already).**
2.  **Ensure Python and `uv` are installed.**
    ```bash
    uv venv
    source .venv/bin/activate    
    ```    
Make sure uv is in your system PATH, or replace "command": "uv" with the full path to the uv executable.

3.  **Install MCP CLI:**
    ```bash
    uv add "mcp[cli]"
    ```

Full documentation here: https://modelcontextprotocol.io/introduction


4.  **Navigate to the project directory:**
    ```bash
    cd /path/to/your/project/gritai-mcp-server-course
    ```
5.  **Environment Variables:** Some servers require environment variables (e.g., API keys, AWS profiles). These are typically loaded from a `.env` file in the root of this project or directly in your environment. Create a `.env` file if needed. For example:
    ```env
    ALPHAVANTAGE_API_KEY="YOUR_ALPHAVANTAGE_KEY"
    KNOWLEDGE_BASE_ID="YOUR_AWS_KB_ID"
    AWS_PROFILE="your-aws-sso-profile"
    AWS_REGION="your-aws-region"
    # For rag_pipeline.py (used by 07_local_rag_server)
    # PGVECTOR_DB_NAME="vectordb"
    # PGVECTOR_DB_USER="your_db_user"
    # PGVECTOR_DB_PASSWORD="your_db_password"
    # PGVECTOR_DB_HOST="localhost"
    # PGVECTOR_DB_PORT="5432"
    ```

6. **AWS configuration:** Some of the servers make use of AWS services, like Bedrock Knowledge Bases or Embeddings. In order to use these you will need an AWS account, and you will need to use SSO to connect to AWS. The code examples uses the boto3 client.
You will need to create an SSO profile, and make sure you are logged in with
aws sso login --profile <your-profile-name>

aws configure sso is a one‑time wizard; afterwards only aws sso login is needed to renew the token.


7. **Local Vector Database** Example 07_local_rag_server illustrates an MCP server running on top of a local Postgresql server with PGVECTOR. Details on the server and RAG pipeline to set up this server is found in the separate RAG project.

## Running an Example Server

You can run any example server with the MCP Inspector directly using `mcp dev <servername.py>` from the `gritai-mcp-server-course` directory. For example, to run the motivational quotes server:

```bash
mcp dev examples/01_motivational_quotes/01_motivational_quotes_server.py
```

This will allow you to open the MCP Inspector at http://127.0.0.1:6274 🚀


## Integrating with Claude

To use these example servers with an LLM like Claude, you'll need to add a configuration to your LLM's tool settings. The `command` will typically be `uv`, and the `args` will point to the `uv run` command or `mcp run` for the specific server script.

**Important:** In the Claude configurations below, you **MUST** replace `"/path/to/your/project/gritai-mcp-server-course"` with the actual absolute path to the `gritai-mcp-server-course` directory on your system where `uv` will be executed.

On Windows, remember to use double backslash in your paths.


Alternatively, you can use the `mcp install` function - which will generate the config and add it to Claude for you. 
```bash
mcp install examples/01_motivational_quotes/01_motivational_quotes_server.py
```

If you encounter issues with running your servers in Claude, you might try changing from the uv run approach to the mcp run approach, in particular if you get errors because of missing dependencies.

As an example (applicable to all the below server examples):

    ```json
      "local-rag-server": {
      "command": "uv",
      "args": [
        "run",
        "--with",
        "mcp[cli]",
        "--with",
        "psycopg2-binary",
        "--with",
        "boto3",
        "mcp",
        "run",
        "/path/to/your/project/gritai-mcp-server-course/examples/06_local_rag/06_local_rag_server.py"
      ],
      "env": {
        <variables goes here...>
      }
    }
    ```

---

## Base Server Template

### `base_server_template.py`

A very basic server with a `hello` tool. Serves as a boiler plate for any MCP server.

-   **File:** `base_server_template.py`
-   **Description:** Greets the user and demonstrates a minimal tool setup.
-   **Claude Config:**
    ```json
    "greeting-server": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/your/project/gritai-mcp-server-course", 
        "run",
        "base_server_template.py"
      ]
    }
    ```

---

## Example Servers

### 1. Motivational Quotes Server

-   **Directory:** `examples/01_motivational_quotes/`
-   **Server File:** `01_motivational_quotes_server.py`
-   **Data File:** `motivational_quotes.json`
-   **Description:** Provides a tool to fetch random motivational quotes and a prompt to make a quote funny. Reads quotes from the local `motivational_quotes.json` file.
-   **Claude Config:**
    ```json
    "motivational-quotes": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/your/project/gritai-mcp-server-course",
        "run",
        "examples/01_motivational_quotes/01_motivational_quotes_server.py"
      ]
    }
    ```


### 2. Dummy Finance Tools Server

This server demonstrates MCP Tools, Prompts and Resources.

-   **Directory:** `examples/02_dummy_finance_tools/`
-   **Server File:** `02_finance_tools_server.py`
-   **Description:** Provides basic dummy finance-related tools and resources, such as fetching (mock) earnings for a stock, getting latest NVIDIA earnings (mock), summarizing earnings (prompt), and calculating CAGR.
-   **Claude Config:**
    ```json
    "basic-finance-server": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/your/project/gritai-mcp-server-course",
        "run",
        "examples/02_dummy_finance_tools/02_finance_tools_server.py"
      ]
    }
    ```


### 3. Connect to Public API (police-incidents) Server

-   **Directory:** `examples/03_public_api_server/`
-   **Server File:** `03_public_api_server.py`
-   **Description:** Fetches the latest police incidents from the Norwegian Police API. Includes tools to get all latest incidents or incidents by municipality.
-   **Dependencies:** `requests`
-   **Claude Config:**
    ```json
    "police-incidents": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/your/project/gritai-mcp-server-course",
        "run",
        "examples/03_public_api_server/03_public_api_server.py"
      ]
    }
    ```

### 4. API Key Auth (Investment Data) Server

-   **Directory:** `examples/04_apikey_auth/`
-   **Server File:** `04_apikey_auth_server.py`
-   **Description:** Searches for stock tickers using the Alpha Vantage API, which requires an API key set via the `ALPHAVANTAGE_API_KEY` environment variable.
-   **Dependencies:** `requests`
-   **Environment Variables:** `ALPHAVANTAGE_API_KEY`
-   **Claude Config:**
    ```json
    "investment-data": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/your/project/gritai-mcp-server-course",
        "run",
        "examples/04_apikey_auth/04_apikey_auth_server.py"
      ],
      "env": {
        "ALPHAVANTAGE_API_KEY": "<your_key_here>"
      }
    }
    ```    

### 5. AWS Knowledge Base Server

-   **Directory:** `examples/05_aws_knowledge_base/`
-   **Server File:** `05_aws_knowledge_base_server.py`
-   **Description:** Searches an AWS Bedrock knowledge base. Requires AWS credentials (e.g., via an AWS profile specified in `AWS_PROFILE`) and `KNOWLEDGE_BASE_ID` and `AWS_REGION` environment variables.
-   **Dependencies:** `boto3`, `python-dotenv`
-   **Environment Variables:** `KNOWLEDGE_BASE_ID`, `AWS_REGION`, `AWS_PROFILE` (used internally by `boto3`)
-   **Claude Config:**
    ```json
    "aws-knowledgebase-test": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/your/project/gritai-mcp-server-course",
        "run",
        "examples/05_aws_knowledge_base/05_aws_knowledge_base_server.py"
      ],
      "env": {
        "KNOWLEDGE_BASE_ID": "<your_knowledge_base_id",
        "AWS_REGION": "<your_aws_region>", 
        "AWS_PROFILE": "<your_aws_profile>"
      }
    }
    ```

In order to gracefully handle SSO token expiry, you will need to add logic to catch token expiry and can then trigger the SSO login flow by for instance calling:
  ```python
    subprocess.run(["aws", "sso", "login", "--profile", PROFILE], check=True)  
  ```

### 6. Local RAG Server

-   **Directory:** `examples/06_local_rag/`
-   **Server File:** `06_local_rag_server.py`
-   **Utility Script:** `rag_pipeline.py`
-   **Description:** A server that performs Retrieval Augmented Generation (RAG) by searching a local knowledge base (PostgreSQL with pgvector) using AWS Bedrock for embeddings. The `rag_pipeline.py` script contains the core RAG logic.
-   **Dependencies:** `psycopg2-binary`, `boto3`
-   **Environment Variables (for `rag_pipeline.py`):**
    -   `AWS_REGION`, `AWS_PROFILE` (for Bedrock embeddings)
    -   `PGVECTOR_DB_NAME`, `PGVECTOR_DB_USER`, `PGVECTOR_DB_PASSWORD`, `PGVECTOR_DB_HOST`, `PGVECTOR_DB_PORT` (for database connection)
-   **Claude Config:**
    ```json
    "local-rag-server": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/your/project/gritai-mcp-server-course",
        "run",
        "examples/06_local_rag/06_local_rag_server.py"
      ],
      "env": {
        "KNOWLEDGE_BASE_ID": "<your_knowledge_base_id",
        "AWS_REGION": "<your_aws_region>", 
        "AWS_PROFILE": "<your_aws_profile>",
        "PGVECTOR_DB_NAME": "",
        "PGVECTOR_DB_PASSWORD": "",
        "PGVECTOR_DB_USER": "",
        "PGVECTOR_DB_HOST": "",
        "PGVECTOR_DB_PORT": ""
      }
       
    }
    ```

---

This `README.md` should provide a good overview of your project and how to use the examples. Remember to replace `/path/to/your/project/gritai-mcp-server-course` in the Claude configurations with the actual path on your system.

