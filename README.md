# GritAI MCP Server Examples

This project provides a collection of example MCP (Model Context Protocol) servers built with **FastMCP 4**, designed to be educational and showcase different functionalities. All examples are based on a simple starter server, `base_server_template.py`.

Every server targets the **2026-07-28** protocol revision. FastMCP 4 serves both protocol eras from the same deployment and negotiates per connection, so these servers also work with hosts that still speak the older handshake protocol.

## Developing with Cursor

When using Cursor to develop MCP servers and clients, it is highly recommended to:

**Add Documentation to Cursor:**
  - It's recommended to add the MCP documentation to Cursor's knowledge base:
    - Add the MCP documentation (specifically for building with LLMs): https://modelcontextprotocol.io/llms-full.txt
    - Add the FastMCP documentation, which is what these examples are built on: https://gofastmcp.com/llms.txt
    - Add the current protocol revision so the model does not generate handshake-era code: https://modelcontextprotocol.io/specification/2026-07-28/changelog


**Wiring a server into Cursor:**
  - Copy `.cursor/mcp.json.example` to `.cursor/mcp.json` and replace `/absolute/path/to/gritai-mcp-server-course` with the path on your machine. The real `.cursor/mcp.json` is gitignored, since the path is machine-specific.

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
      'https://api.politiloggen.politiet.no/messages' \
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

- **`base_server_template.py`**: A minimal MCP server that acts as a template for creating new servers. It includes a basic "greeting" tool (stdio transport).
- **`base_server_template_http.py`**: The same server over HTTP. Previously this repo also carried `base_server_template_http_fastmcp2.py`; the two differed only by import, and now that everything is FastMCP 4 there is one HTTP template.
- **`examples/`**: This directory contains various example MCP servers, each in its own subdirectory.
    - Each example subdirectory (e.g., `01_motivational_quotes/`) contains the server script (e.g., `01_motivational_quotes_server.py`) and any related files (like data files or utility scripts).

## What changed in the 2026-07-28 protocol revision

This course was updated for the MCP specification revision released on 28 July 2026. It is not backward compatible, and it is worth understanding before reading the examples.

| Change | What it means in practice |
| --- | --- |
| **No sessions** | Protocol-level sessions and the `Mcp-Session-Id` header are gone from Streamable HTTP. A remote server can sit behind an ordinary round-robin load balancer - no session affinity. State that must survive across calls is passed as server-minted handles in ordinary tool arguments. |
| **No handshake** | `initialize` / `notifications/initialized` are gone. Every request carries its protocol version and client capabilities in `_meta`. Servers must implement `server/discover`, which clients may call up front to select a version. |
| **`ping` removed** | Along with `logging/setLevel` and `notifications/roots/list_changed`. This is why `simple_client.py` no longer calls `client.ping()`. |
| **Sampling, Roots and Logging deprecated** | Still functional, but new servers should not adopt them. Pass file paths as tool arguments instead of Roots, call an LLM provider directly instead of Sampling, and log to stderr or OpenTelemetry instead of Logging. |
| **Multi Round-Trip Requests (MRTR)** | Replaces server-initiated requests. Instead of the server calling back to the client, it returns an `InputRequiredResult` and the client retries the original request with `inputResponses`. Every result now carries a `resultType` of `"complete"` or `"input_required"`. |
| **Cacheable lists** | `tools/list`, `prompts/list`, `resources/list` and `resources/read` now carry `ttlMs` and `cacheScope`, so clients can cache them. FastMCP exposes these as the `cache_ttl` and `cache_scope` arguments on `FastMCP()`. |
| **HTTP+SSE deprecated** | Formally deprecated under the new feature-lifecycle policy, with a minimum twelve-month removal window. Use `transport="http"`. |
| **DCR deprecated** | OAuth Dynamic Client Registration gives way to Client ID Metadata Documents. See example 8 - FastMCP 4 enables CIMD by default. |
| **Extensions** | Optional capabilities now live outside the core protocol. Background tasks moved out to the `io.modelcontextprotocol/tasks` extension (`uv add "fastmcp[tasks]"` plus `mcp.add_extension(TasksExtension())`). |

Full changelog: https://modelcontextprotocol.io/specification/2026-07-28/changelog

**What this means for these examples:** FastMCP 4 handles both eras for you, so none of the servers here need era-specific code. The client is where the difference shows: `Client(url, mode="auto")` (the default) speaks the modern protocol, and `mode="legacy"` forces the handshake era.

## General Setup

1.  **Clone the repository (if you haven't already).**
2.  **Ensure Python and `uv` are installed.**
    ```bash
    uv venv
    source .venv/bin/activate    
    ```    
Make sure uv is in your system PATH, or replace "command": "uv" with the full path to the uv executable.

3.  **Install the dependencies:**
    ```bash
    uv sync
    ```
    This installs the exact versions in the committed `uv.lock` (FastMCP 4.0.3, MCP SDK 2.2.0, Prefab 0.20.2) - everyone in the room gets the same environment. Do not use `uv add` for setup; it will resolve newer versions than the course was tested against.

Protocol documentation: https://modelcontextprotocol.io/introduction
FastMCP documentation: https://gofastmcp.com


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

You can run any example server with the MCP Inspector directly using `fastmcp dev <servername.py>` from the `gritai-mcp-server-course` directory. For example, to run the motivational quotes server:

```bash
fastmcp dev examples/01_motivational_quotes/01_motivational_quotes_server.py
```

(The old `mcp dev` command came from the `mcp[cli]` package. This course now uses the `fastmcp` CLI throughout - `fastmcp dev`, `fastmcp run`, `fastmcp inspect`, `fastmcp install`.)

This will allow you to open the MCP Inspector at http://127.0.0.1:6274 🚀

## Verifying every server at once

```bash
uv run tests/smoke_test.py
```

Starts each server for real and drives it through an MCP client: lists tools, resources and prompts, calls a tool where no third-party credential is needed, checks the HTTP transports and the `/health` route, and runs the full elicitation round trip from example 10. Exit code is 0 when everything passes.

Servers needing live credentials (04 Alpha Vantage, 05 Bedrock, 06 pgvector, 07 Azure Search) are only verified up to the point where the credential is needed - they must start and register their tools. Their retrieval path is yours to test against real credentials.

Run this after any dependency bump; it is what catches a protocol or FastMCP change breaking an example.

## MCP Client Examples

This repository includes example MCP clients demonstrating how to connect to MCP servers over HTTP.

### `simple_client.py`

A basic FastMCP client that connects to a local HTTP MCP server. This example demonstrates:
- Connecting to an MCP server via HTTP
- Listing available tools, resources, and prompts
- Calling tools on the remote server

**Usage:**
```bash
# Terminal 1 - start any HTTP server:
uv run base_server_template_http.py

# Terminal 2 - run the client:
uv run simple_client.py

# Or point it somewhere else:
MCP_SERVER_URL="https://your-server.example.com/mcp" uv run simple_client.py
```

**File:** `simple_client.py`
- **Description:** Connects to `MCP_SERVER_URL` (default `http://127.0.0.1:8000/mcp/`) and demonstrates basic client operations
- **Dependencies:** `fastmcp`

**Note:** For OAuth-authenticated servers, pass `auth="oauth"` - the client does this automatically for `https://` URLs.

### Remote Client (`simple_client_remote.py`)

The same client pointed at a deployed, OAuth-protected server. On first run FastMCP opens a browser for the OAuth flow and caches the token; later runs are silent. Point it at a server you control - example 8 is one you can deploy.

```bash
export MCP_SERVER_URL="https://<your-server>.fastmcp.app/mcp"
uv run simple_client_remote.py

# Call a tool rather than just listing them:
MCP_TOOL=random_quote uv run simple_client_remote.py
MCP_TOOL=echo_tool MCP_TOOL_ARGS='{"text": "Hello, world!"}' uv run simple_client_remote.py
```

**There is no `client.ping()` any more.** `ping` was removed from the protocol in the 2026-07-28 revision along with sessions and the `initialize` handshake. Calling it on a modern connection raises `MCPError: Method not found`; it only works if you force `Client(url, mode="legacy")`. Use `list_tools()` as your connectivity check.

## Integrating with Claude (or other MCP Host applications)

To use these example servers with an AI assistant like Claude or Cursor, that implements the MCP Client, you'll need to add a configuration to your LLM's tool settings. The `command` will typically be `uv`, and the `args` will point to the `uv run` command or `mcp run` for the specific server script.

**Important:** In the Claude configurations below, you **MUST** replace `"/path/to/your/project/gritai-mcp-server-course"` with the actual absolute path to the `gritai-mcp-server-course` directory on your system where `uv` will be executed.

On Windows, remember to use double backslash in your paths.


Alternatively, you can use `fastmcp install` - which will generate the config and add it to Claude for you.
```bash
fastmcp install claude-desktop examples/01_motivational_quotes/01_motivational_quotes_server.py
```

If you encounter issues with running your servers in Claude, try the `uv --directory` form below. It resolves against this project's `pyproject.toml` and `uv.lock`, so the server gets the dependencies it was tested with - the installer's ephemeral environment does not (this bites hardest on example 9, which needs `prefab-ui`).

As an example (applicable to all the below server examples):

    ```json
      "local-rag-server": {
      "command": "uv",
      "args": [
        "run",
        "--with",
        "fastmcp",
        "--with",
        "psycopg2-binary",
        "--with",
        "boto3",
        "fastmcp",
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

`base_server_template_http.py` is the same server over HTTP. Transport names for `mcp.run()` are `"stdio"`, `"http"` (Streamable HTTP) and `"sse"`. Use `"http"` for anything remote - `"sse"` is formally deprecated in the 2026-07-28 revision and scheduled for removal. Note that `host` and `port` are arguments to `run()`, not to the `FastMCP()` constructor.

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
-   **Environment Variables:** `KNOWLEDGE_BASE_ID`, `AWS_REGION`, `AWS_PROFILE` (optional - when set, that SSO profile is used; when unset, boto3's default credential chain applies)
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
-   **Utility Script:** `rag_retrieval_tools.py`
-   **Description:** A server that performs Retrieval Augmented Generation (RAG) by searching a local knowledge base (PostgreSQL with pgvector) using AWS Bedrock for embeddings. The `rag_retrieval_tools.py` script contains the core RAG logic.
-   **Dependencies:** `psycopg2-binary`, `boto3`
-   **Environment Variables (for `rag_retrieval_tools.py`):**
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
-   **Client Configuration:** This server exposes an HTTP endpoint at `/mcp`. Clients should connect to `https://your-server-url.com/mcp` with OAuth authentication. See `simple_client.py` and `simple_client_remote.py` for client examples.
-   **Azure App Registration Setup:**
    1. Create an Azure App Registration in Azure Portal
    2. Configure redirect URIs: `https://your-app-url.com/auth/callback`
    3. Set API permissions (scopes): `User.Read`, `email`, `openid`, `profile`, `offline_access`
    4. Create a client secret and note the Client ID, Tenant ID, and Secret
    5. Update your `.env` file with these values

**Note:** This server is designed for HTTP deployment, not stdio-based MCP clients like Claude Desktop. For stdio-based integration, use the other example servers. This example is ideal for web-based MCP clients or API integrations.

### 9. FastMCP UI Apps (Prefab)

-   **Directory:** `examples/09_fastmcp_uiapp/`
-   **Description:** Four servers exploring FastMCP 4's UI App capabilities using [Prefab UI](https://gofastmcp.com/apps/prefab). All four share a common "10 years of random population data" theme and progressively demonstrate the UI App surface — from a plain tool, to a static chart, to an interactive form-driven app, to fully generative UI.
-   **Dependencies:** `fastmcp>=4.0.3`, `prefab-ui` (already in `pyproject.toml`; just run `uv sync`)
-   **Servers:**
    -   **`09_population_server.py`** — Plain FastMCP tool returning 10 years of randomized population data. Baseline for comparison with the UI variants.
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
    FastMCP ships a built-in dev UI that renders Prefab views without needing an LLM host:
    ```bash
    fastmcp dev apps examples/09_fastmcp_uiapp/09_population_uiapp_server.py
    ```
    Opens a tool picker at `http://localhost:8080` where you can invoke the tool directly and see the rendered UI. Works for all four servers; for `09_population_generative_server.py` you'll need to paste Python code into the `code` argument yourself (useful for verifying the sandbox + renderer, but not the full LLM-driven flow).

-   **Testing with Claude Desktop:**
    Claude Desktop is the easiest way to exercise the full flow (LLM fetches data, optionally searches components, generates and invokes a Prefab UI). Prefer the `uv --directory` config pattern shown above over `fastmcp install claude-desktop` — the installer defaults to `uv run --with fastmcp ...` which creates an ephemeral env without `prefab-ui`, so any UI App server will crash at import with `ModuleNotFoundError: No module named 'prefab_ui'`. Using `--directory` resolves against this project's `pyproject.toml` / `uv.lock` where `prefab-ui` is already a dependency.

-   **Notes:**
    -   Requires FastMCP 4.x (this repo pins `fastmcp>=4.0.3,<5`). `prefab-ui` is pinned to `>=0.20.2,<0.21` deliberately: Prefab is pre-1.0 and ships breaking changes between minor versions.
    -   Chart arguments use snake_case (`x_axis=`). The camelCase form (`xAxis=`) still works as a Pydantic alias, but the examples now use one style throughout.
    -   The generative server needs **Deno** on `PATH` for server-side Pyodide validation (auto-installed on first use). The sandbox only includes the Python standard library and Prefab components — no NumPy/pandas/requests.
    -   Host must support MCP UI resources for rendering (e.g. Claude Desktop with apps preview enabled).
    -   `FastMCPApp` form submissions do not auto-forward input values to backend tools. Wire them explicitly: `CallTool(fn, arguments={"country": Rx("form_country")})`.

### 10. Elicitation & Multi Round-Trip Requests (MRTR)

-   **Directory:** `examples/10_elicitation_mrtr/`
-   **Server File:** `10_elicitation_mrtr_server.py`
-   **Client File:** `10_mrtr_client.py`
-   **Description:** The pattern that replaces server-initiated requests in the 2026-07-28 revision. The server asks the caller which municipality to fetch police incidents for - but because MCP is now stateless, it cannot interrupt its own response to ask. Instead it *returns* the question as the result of the call, and the client re-issues the same call with the answer attached. Builds on example 3, so it needs no credentials.
-   **Dependencies:** `requests` (already in `pyproject.toml`)
-   **The shape of it:**
    ```
    leg 1   client -> tools/call                     (no answer yet)
            server -> InputRequiredResult(...)       "which municipality?"
    leg 2   client -> tools/call + inputResponses    (same call, plus answers)
            server -> the real result
    ```
-   **Run it:**
    ```bash
    # Interactive - the client prompts you for the answer:
    uv run examples/10_elicitation_mrtr/10_mrtr_client.py

    # Or answer up front:
    MRTR_ANSWER=Bergen  uv run examples/10_elicitation_mrtr/10_mrtr_client.py
    MRTR_ANSWER=decline uv run examples/10_elicitation_mrtr/10_mrtr_client.py
    ```
    The client spawns the server itself, so you only need one terminal. Server diagnostics go to stderr and are interleaved with the client's output - watch for `[leg 1]` and `[leg 2]`.

-   **Teaching notes:**
    -   **The tool body runs once per leg, from the top.** Nothing is suspended and resumed. The example logs each leg so students can see one `call_tool()` produce two executions. Anything expensive or irreversible must happen *after* the answer arrives, never before the ask.
    -   **The original arguments are unchanged on leg 2.** `municipality` is still `None`; the answer arrives in `ctx.input_responses`, keyed by the name the server chose in `input_requests`.
    -   **`request_state` is the only continuity between legs**, and it travels through the client. Never put a secret in it, and validate what comes back.
    -   **Handle all three actions.** A user can `accept`, `decline` or `cancel`. The example returns a different message for each; try `MRTR_ANSWER=decline`.
    -   **Bound the rounds.** `Client(..., input_required_max_rounds=3)` stops a server that always asks and a client that always answers from looping forever.
    -   **The client must opt in.** A client with no `elicitation_handler` cannot complete the second leg. Host support varies - verify with your host before demoing.
    -   **Contrast with the old way:** calling `ctx.elicit()` on a modern connection raises `elicitation via server-initiated requests is unavailable on 2026-07-28 connections`. It still works under `Client(..., mode="legacy")`. Running both back to back is the fastest way to explain why MRTR exists.
    -   Sampling and Roots are deprecated (SEP-2577) and are deliberately **not** demonstrated here. Elicitation is not deprecated - it is the one of the three that survives, now expressed through MRTR.

---

---

This `README.md` should provide a good overview of your project and how to use the examples. Remember to replace `/path/to/your/project/gritai-mcp-server-course` in the Claude configurations with the actual path on your system.
