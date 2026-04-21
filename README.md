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
5.  **Environment Variables:** Some servers require environment variables (e.g., API keys, AWS profiles, Azure credentials). These are typically loaded from a `.env` file in the root of this project or directly in your environment. 

    **Template:** See `env.examples` for a complete template of all environment variables used across examples. Copy it to `.env` and fill in your actual values:
    ```bash
    cp env.examples .env
    # Then edit .env with your actual values
    ```

    For quick reference, here are the main environment variables:
    ```env
    # Example 4: API Key Auth
    ALPHAVANTAGE_API_KEY="YOUR_ALPHAVANTAGE_KEY"

    # Examples 5 & 6: AWS Services
    KNOWLEDGE_BASE_ID="YOUR_AWS_KB_ID"
    AWS_PROFILE="your-aws-sso-profile"
    AWS_REGION="your-aws-region"

    # Example 6: Local RAG with PostgreSQL
    # PGVECTOR_DB_NAME="vectordb"
    # PGVECTOR_DB_USER="your_db_user"
    # PGVECTOR_DB_PASSWORD="your_db_password"
    # PGVECTOR_DB_HOST="localhost"
    # PGVECTOR_DB_PORT="5432"

    # Example 7: Azure AI Search
    AZURE_SEARCH_ENDPOINT="https://your-service.search.windows.net"
    AZURE_SEARCH_INDEX="your-index-name"
    AZURE_SEARCH_KEY="your-api-key"  # Optional - omit to use DefaultAzureCredential

    # Example 8: Azure OAuth Remote Server
    ENABLE_OIDC="1"  # Set to "0" to disable OAuth
    AZURE_TENANT_ID="your-azure-tenant-id"
    OIDC_CLIENT_ID="your-azure-app-client-id"
    OIDC_CLIENT_SECRET="your-azure-app-client-secret"
    PUBLIC_BASE_URL="https://your-app-url.com"  # Must match Azure App registration
    OIDC_REDIRECT_PATH="/auth/callback"  # Optional, defaults to /auth/callback
    OIDC_ALLOWED_REDIRECT_URIS="http://localhost:*/*,http://127.0.0.1:*/*"  # Optional
    OIDC_REQUIRED_SCOPES="User.Read email openid profile offline_access"  # Optional
    ```

6. **AWS configuration:** Some of the servers make use of AWS services, like Bedrock Knowledge Bases or Embeddings. In order to use these you will need an AWS account, and you will need to use SSO to connect to AWS. The code examples uses the boto3 client.
You will need to create an SSO profile, and make sure you are logged in with
aws sso login --profile <your-profile-name>

aws configure sso is a one‑time wizard; afterwards only aws sso login is needed to renew the token.


7. **Local Vector Database** Example 06_local_rag_server illustrates an MCP server running on top of a local Postgresql server with PGVECTOR. Details on the server and RAG pipeline to set up this server is found in the separate RAG project.

## Running an Example Server

You can run any example server with the MCP Inspector directly using `mcp dev <servername.py>` from the `gritai-mcp-server-course` directory. For example, to run the motivational quotes server:

```bash
mcp dev examples/01_motivational_quotes/01_motivational_quotes_server.py
```

This will allow you to open the MCP Inspector at http://127.0.0.1:6274 🚀

## MCP Client Examples

This repository includes example MCP clients demonstrating how to connect to MCP servers over HTTP.

### `simple_client.py`

A basic FastMCP client that connects to a local HTTP MCP server. This example demonstrates:
- Connecting to an MCP server via HTTP
- Listing available tools, resources, and prompts
- Calling tools on the remote server

**Usage:**
```bash
# First, ensure your MCP server is running (e.g., on localhost:8000)
# Then run the client:
uv run simple_client.py
```

**File:** `simple_client.py`
- **Description:** Connects to `http://localhost:8000/mcp` and demonstrates basic client operations
- **Dependencies:** `fastmcp`

**Note:** For OAuth-authenticated servers, use `Client("http://localhost:8000/mcp", auth="oauth")`. See `simple_client_remote01.py` and `simple_client_remote02.py` for examples connecting to remote OAuth-protected servers.

## Integrating with Claude (or other MCP Host applications)

To use these example servers with an AI assistant like Claude or Cursor, that implements the MCP Client, you'll need to add a configuration to your LLM's tool settings. The `command` will typically be `uv`, and the `args` will point to the `uv run` command or `mcp run` for the specific server script.

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

### 7. Azure AI Search Server

-   **Directory:** `examples/07_azure_ai_search/`
-   **Server File:** `07_azure_ai_search_server.py`
-   **Description:** Demonstrates integration with Azure AI Search service. Showcases **dual authentication** support: API Key (simplest) or DefaultAzureCredential (most secure for production). Performs simple text search with configurable result count.
-   **Dependencies:** `azure-search-documents`, `azure-identity`
-   **Environment Variables:**
    -   `AZURE_SEARCH_ENDPOINT` (required) - Your Azure Search service endpoint
    -   `AZURE_SEARCH_INDEX` (required) - Name of the search index
    -   `AZURE_SEARCH_KEY` (optional) - API key for authentication. If not provided, uses DefaultAzureCredential (Azure CLI, Managed Identity, etc.)
-   **Claude Config (with API Key):**
    ```json
    "azure-ai-search": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/your/project/gritai-mcp-server-course",
        "run",
        "examples/07_azure_ai_search/07_azure_ai_search_server.py"
      ],
      "env": {
        "AZURE_SEARCH_ENDPOINT": "https://your-service.search.windows.net",
        "AZURE_SEARCH_INDEX": "your-index-name",
        "AZURE_SEARCH_KEY": "<your_api_key>"
      }
    }
    ```
-   **Claude Config (with DefaultAzureCredential):**
    ```json
    "azure-ai-search": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/your/project/gritai-mcp-server-course",
        "run",
        "examples/07_azure_ai_search/07_azure_ai_search_server.py"
      ],
      "env": {
        "AZURE_SEARCH_ENDPOINT": "https://your-service.search.windows.net",
        "AZURE_SEARCH_INDEX": "your-index-name"
      }
    }
    ```
    **Note:** When using DefaultAzureCredential, ensure you've run `az login` before starting Claude Desktop.

### 8. Azure OAuth Remote Server

-   **Directory:** `examples/08_azure_auth_remote_server/`
-   **Server File:** `app.py`
-   **Data File:** `motivational_quotes.json`
-   **Description:** An HTTP-based MCP server with Azure Entra ID (Azure AD) OAuth authentication. This server runs as an ASGI application suitable for deployment with Gunicorn/Uvicorn (e.g., on Azure App Service). Demonstrates OAuth-protected tools, user authentication, and remote HTTP server patterns. Includes tools for getting authenticated user info, random quotes, searching quotes, and fetching specific quotes.
-   **Dependencies:** `fastmcp`, `python-dotenv`, `starlette`
-   **Environment Variables:**
    -   `ENABLE_OIDC` (optional, default: "1") - Set to "0" to disable OAuth
    -   `AZURE_TENANT_ID` (required if OAuth enabled) - Your Azure Tenant ID
    -   `OIDC_CLIENT_ID` (required if OAuth enabled) - Your Azure App Registration Client ID
    -   `OIDC_CLIENT_SECRET` (required if OAuth enabled) - Your Azure App Registration Client Secret
    -   `PUBLIC_BASE_URL` (required if OAuth enabled) - Public URL of your deployed server (must match Azure App registration)
    -   `OIDC_REDIRECT_PATH` (optional, default: "/auth/callback") - OAuth callback path
    -   `OIDC_ALLOWED_REDIRECT_URIS` (optional) - Comma-separated list of allowed redirect URIs
    -   `OIDC_REQUIRED_SCOPES` (optional) - Space-separated list of required OAuth scopes
-   **Running the Server:**
    ```bash
    # Using Uvicorn (development)
    # From project root:
    uvicorn examples.08_azure_auth_remote_server.app:app --host 0.0.0.0 --port 8000
    
    # Or using Python module path:
    cd examples/08_azure_auth_remote_server
    uvicorn app:app --host 0.0.0.0 --port 8000

    # Using Gunicorn (production)
    gunicorn examples.08_azure_auth_remote_server.app:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
    ```
-   **Client Configuration:** This server exposes an HTTP endpoint at `/mcp`. Clients should connect to `https://your-server-url.com/mcp` with OAuth authentication. See `simple_client.py` and `simple_client_remote02.py` for client examples.
-   **Azure App Registration Setup:**
    1. Create an Azure App Registration in Azure Portal
    2. Configure redirect URIs: `https://your-app-url.com/auth/callback`
    3. Set API permissions (scopes): `User.Read`, `email`, `openid`, `profile`, `offline_access`
    4. Create a client secret and note the Client ID, Tenant ID, and Secret
    5. Update your `.env` file with these values

**Note:** This server is designed for HTTP deployment, not stdio-based MCP clients like Claude Desktop. For stdio-based integration, use the other example servers. This example is ideal for web-based MCP clients or API integrations.

### 9. FastMCP UI Apps (Prefab)

-   **Directory:** `examples/09_fastmcp_uiapp/`
-   **Description:** Four servers exploring FastMCP 3.0's UI App capabilities using [Prefab UI](https://gofastmcp.com/apps/prefab). All four share a common "10 years of random population data" theme and progressively demonstrate the UI App surface — from a plain tool, to a static chart, to an interactive form-driven app, to fully generative UI.
-   **Dependencies:** `fastmcp>=3.0.0`, `prefab-ui` (install via `uv add "fastmcp>=3.0" prefab-ui`)
-   **Servers:**
    -   **`09_population_server.py`** — Plain FastMCP 3 tool returning 10 years of randomized population data. Baseline for comparison with the UI variants.
    -   **`09_population_uiapp_server.py`** — Same data, rendered as a static Prefab `BarChart` via `@mcp.tool(app=True)`. Returns a `ToolResult` so the model also receives a text summary alongside the UI.
    -   **`09_population_fastmcpapp_server.py`** — Interactive app built with `FastMCPApp`. Uses the two-decorator pattern: `@app.ui()` exposes an entry point to the model, `@app.tool()` exposes a backend `regenerate_population` tool that the UI calls from a form submission. State is managed reactively with `Rx` and `SetState`. Demonstrates [Interactive Apps](https://gofastmcp.com/apps/interactive-apps).
    -   **`09_population_generative_server.py`** — [Generative UI](https://gofastmcp.com/apps/generative). Adds `mcp.add_provider(GenerativeUI())` which registers `generate_prefab_ui` and `search_prefab_components` tools, letting the LLM discover components and write Python code that renders in a Pyodide sandbox. Also exposes the raw data tool, so the model can fetch data and render any UI it chooses.
-   **Claude Config (example, repeat for each server):**
    ```json
    "population-uiapp": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/your/project/gritai-mcp-server-course",
        "run",
        "examples/09_fastmcp_uiapp/09_population_uiapp_server.py"
      ]
    }
    ```
-   **Testing locally — browser preview:**
    FastMCP 3 ships a built-in dev UI that renders Prefab views without needing an LLM host:
    ```bash
    fastmcp dev apps examples/09_fastmcp_uiapp/09_population_uiapp_server.py
    ```
    Opens a tool picker at `http://localhost:8080` where you can invoke the tool directly and see the rendered UI. Works for all four servers; for `09_population_generative_server.py` you'll need to paste Python code into the `code` argument yourself (useful for verifying the sandbox + renderer, but not the full LLM-driven flow).

-   **Testing with Claude Desktop:**
    Claude Desktop is the easiest way to exercise the full flow (LLM fetches data, optionally searches components, generates and invokes a Prefab UI). Prefer the `uv --directory` config pattern shown above over `fastmcp install claude-desktop` — the installer defaults to `uv run --with fastmcp ...` which creates an ephemeral env without `prefab-ui`, so any UI App server will crash at import with `ModuleNotFoundError: No module named 'prefab_ui'`. Using `--directory` resolves against this project's `pyproject.toml` / `uv.lock` where `prefab-ui` is already a dependency.

-   **Notes:**
    -   Requires FastMCP 3.x. Earlier 2.x releases do not support `@mcp.tool(app=True)`, `FastMCPApp`, or `GenerativeUI`.
    -   The generative server needs **Deno** on `PATH` for server-side Pyodide validation (auto-installed on first use). The sandbox only includes the Python standard library and Prefab components — no NumPy/pandas/requests.
    -   Host must support MCP UI resources for rendering (e.g. Claude Desktop with apps preview enabled).
    -   `FastMCPApp` form submissions do not auto-forward input values to backend tools. Wire them explicitly: `CallTool(fn, arguments={"country": Rx("form_country")})`.

---

This `README.md` should provide a good overview of your project and how to use the examples. Remember to replace `/path/to/your/project/gritai-mcp-server-course` in the Claude configurations with the actual path on your system.

