"""Smoke test for every server in this course repo.

Starts each server for real and drives it through an MCP client: lists tools,
resources and prompts, and where no third-party credential is needed, calls a
tool and checks the response. Also exercises the HTTP transports, the ASGI/auth
example, and the full elicitation round trip in example 10.

Run it:
    uv run tests/smoke_test.py
    uv run tests/smoke_test.py -v     # tracebacks on failure

Exit code is 0 when everything passes, 1 otherwise.

Servers that need live credentials (04 Alpha Vantage, 05 Bedrock, 06 pgvector,
07 Azure Search) are verified up to the point where the credential is needed:
they must start and register their tools. Their actual retrieval path is not
covered here - only a run against real credentials proves that.
"""

import asyncio
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

from fastmcp import Client
from fastmcp.client.elicitation import ElicitResult
from fastmcp.client.transports import PythonStdioTransport

ROOT = Path(__file__).resolve().parents[1]
VERBOSE = "-v" in sys.argv

# (label, script, optional (tool_name, args) to actually call)
STDIO_TARGETS = [
    ("base template (stdio)", "base_server_template.py", ("hello", {})),
    ("01 quotes", "examples/01_motivational_quotes/01_motivational_quotes_server.py",
     ("random_quote", {})),
    ("02 finance", "examples/02_dummy_finance_tools/02_finance_tools_server.py",
     ("calculate_cagr", {"symbol": "NVDA", "years": 5, "start_price": 10.0, "end_price": 100.0})),
    ("03 police API", "examples/03_public_api_server/03_public_api_server.py",
     ("latest_incidents", {})),
    ("04 alpha vantage", "examples/04_apikey_auth/04_apikey_auth_server.py", None),
    ("05 aws kb", "examples/05_aws_knowledge_base/05_aws_knowledge_base_server.py", None),
    ("06 local rag", "examples/06_local_rag/06_local_rag_server.py", None),
    ("07 azure search", "examples/07_azure_ai_search/07_azure_ai_search_server.py", None),
    ("09a plain tool", "examples/09_fastmcp_uiapp/09_population_server.py",
     ("get_population_history", {"country": "Norway"})),
    ("09b static UI app", "examples/09_fastmcp_uiapp/09_population_uiapp_server.py",
     ("get_population_history", {"country": "Norway"})),
    ("09c interactive app", "examples/09_fastmcp_uiapp/09_population_fastmcpapp_server.py",
     ("population_viewer", {"country": "Norway"})),
    ("09d generative UI", "examples/09_fastmcp_uiapp/09_population_generative_server.py",
     ("get_population_history", {"country": "Norway"})),
    ("10 mrtr elicitation", "examples/10_elicitation_mrtr/10_elicitation_mrtr_server.py",
     ("incidents_by_municipality", {"municipality": "Oslo"})),
]

HTTP_TARGETS = [
    ("base template (http)", "base_server_template_http.py", 8091, False),
    ("01 remote (http+health)",
     "examples/01_motivational_quotes/01_motivational_quotes_server_remote.py", 8092, True),
]


def ok(label, detail):
    print(f"  PASS  {label:24} {detail}")
    return True


def bad(label, detail):
    print(f"  FAIL  {label:24} {detail}")
    return False


def text_of(result):
    if getattr(result, "content", None):
        return (getattr(result.content[0], "text", "") or "").replace("\n", " ")
    return ""


async def check_stdio(label, script, call):
    transport = PythonStdioTransport(script_path=ROOT / script, cwd=str(ROOT))
    try:
        async with Client(transport) as client:
            tools = await client.list_tools()
            try:
                resources = await client.list_resources()
            except Exception:
                resources = []
            try:
                prompts = await client.list_prompts()
            except Exception:
                prompts = []

            called = "not called (needs credentials)"
            if call:
                name, args = call
                called = f"{name} -> {text_of(await client.call_tool(name, args))[:44]}"
            return ok(label, f"tools={len(tools)} res={len(resources)} "
                             f"prompts={len(prompts)} | {called}")
    except Exception as e:
        if VERBOSE:
            import traceback
            traceback.print_exc()
        return bad(label, f"{type(e).__name__}: {str(e)[:200]}")


def http_probe(port, path):
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}{path}", timeout=3) as r:
            return r.status, r.read().decode()[:20]
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception:
        return None, ""


async def check_http(label, script, port, health):
    env = dict(os.environ, PORT=str(port))
    proc = subprocess.Popen([sys.executable, str(ROOT / script)], cwd=str(ROOT), env=env,
                            stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    try:
        deadline = time.time() + 30
        while time.time() < deadline:
            if http_probe(port, "/mcp/")[0] is not None:
                break
            if proc.poll() is not None:
                err = proc.stderr.read().decode()[-300:] if proc.stderr else ""
                return bad(label, f"server exited. {err}")
            time.sleep(0.4)
        else:
            return bad(label, "server never came up")

        health_note = ""
        if health:
            status, body = http_probe(port, "/health")
            if status != 200:
                return bad(label, f"/health returned {status}, expected 200")
            health_note = f" | /health={status} {body!r}"

        async with Client(f"http://127.0.0.1:{port}/mcp/") as client:
            tools = await client.list_tools()
            name = tools[0].name
            result = await client.call_tool(name, {})
        return ok(label, f"tools={len(tools)} | {name} -> {text_of(result)[:36]}{health_note}")
    except Exception as e:
        return bad(label, f"{type(e).__name__}: {str(e)[:200]}")
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=8)
        except subprocess.TimeoutExpired:
            proc.kill()


async def check_asgi_auth_example():
    """Example 08 exposes an ASGI app rather than run() - talk to it in-memory."""
    label = "08 azure (OIDC off)"
    os.environ["ENABLE_OIDC"] = "0"
    sys.path.insert(0, str(ROOT / "examples/08_azure_auth_remote_server"))
    try:
        import app as ex08
        async with Client(ex08.mcp) as client:
            tools = await client.list_tools()
            result = await client.call_tool("random_quote", {})
        names = ",".join(sorted(t.name for t in tools))
        return ok(label, f"tools=[{names}] | asgi={type(ex08.app).__name__} "
                         f"-> {text_of(result)[:30]}")
    except Exception as e:
        return bad(label, f"{type(e).__name__}: {str(e)[:200]}")


async def check_mrtr_roundtrip():
    """Example 10: the tool body must run twice, once per leg."""
    label = "10 MRTR round trip"
    legs = {"asked": False}

    async def handler(message, response_type, params, context):
        legs["asked"] = True
        return {"municipality": "Bergen"}

    script = ROOT / "examples/10_elicitation_mrtr/10_elicitation_mrtr_server.py"

    def fresh_transport():
        # A new transport per client: keep_alive would reuse the previous
        # session, and with it the previous elicitation handler.
        return PythonStdioTransport(script_path=script, cwd=str(ROOT), keep_alive=False)

    try:
        async with Client(fresh_transport(), elicitation_handler=handler,
                          input_required_max_rounds=3) as client:
            # No municipality -> the server must ask, then complete on leg 2.
            result = await client.call_tool("incidents_by_municipality", {})
            if not legs["asked"]:
                return bad(label, "server never asked - no elicitation happened")
            if "messages" not in text_of(result):
                return bad(label, f"unexpected leg-2 result: {text_of(result)[:120]}")


        # And the refusal path must be handled too.
        async def decline(message, response_type, params, context):
            return ElicitResult(action="decline")

        async with Client(fresh_transport(), elicitation_handler=decline,
                          input_required_max_rounds=3) as client:
            declined = text_of(await client.call_tool("incidents_by_municipality", {}))
            if "No municipality chosen" not in declined:
                return bad(label, f"decline path returned: {declined[:120]}")

        return ok(label, "leg 1 asked, leg 2 completed | decline path handled")
    except Exception as e:
        if VERBOSE:
            import traceback
            traceback.print_exc()
        return bad(label, f"{type(e).__name__}: {str(e)[:200]}")


async def main():
    import fastmcp
    print(f"Smoke test - FastMCP {fastmcp.__version__}, Python {sys.version.split()[0]}")
    print("=" * 78)

    results = []
    print("\nstdio servers")
    for label, script, call in STDIO_TARGETS:
        results.append(await check_stdio(label, script, call))

    print("\nHTTP servers")
    for label, script, port, health in HTTP_TARGETS:
        results.append(await check_http(label, script, port, health))

    print("\nASGI / auth / protocol")
    results.append(await check_asgi_auth_example())
    results.append(await check_mrtr_roundtrip())

    print("=" * 78)
    passed = sum(results)
    print(f"{passed}/{len(results)} passed")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
