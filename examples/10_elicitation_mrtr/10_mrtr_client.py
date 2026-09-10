"""Client for example 10 - the other half of a Multi Round-Trip Request.

A client only takes part in MRTR if it provides an elicitation_handler. When
the server answers with `resultType: "input_required"`, FastMCP calls the
handler and then re-issues the original request with the answer attached.

From here it looks like ONE call_tool(). On the server it is two legs - run the
server's stderr alongside this and you will see [leg 1] and [leg 2].

Run it:
    python examples/10_elicitation_mrtr/10_mrtr_client.py            # asks you
    MRTR_ANSWER=Bergen python examples/10_elicitation_mrtr/10_mrtr_client.py
    MRTR_ANSWER=decline python examples/10_elicitation_mrtr/10_mrtr_client.py
"""

import asyncio
import os
import sys
from pathlib import Path

from fastmcp import Client
from fastmcp.client.elicitation import ElicitResult
from fastmcp.client.transports import PythonStdioTransport

SERVER = Path(__file__).parent / "10_elicitation_mrtr_server.py"


async def elicitation_handler(message, response_type, params, context):
    """Answer the server's question.

    Return a dict (or a response_type instance) to accept, or an ElicitResult
    with action="decline"/"cancel" to refuse. A host application would show a
    dialog here; Claude Desktop and other hosts render the requested_schema as
    a form.
    """
    options = (params.requested_schema or {}).get("properties", {}).get("municipality", {}).get("enum", [])
    print(f"\n  [server asks] {message}")
    print(f"  [options]     {', '.join(options)}")

    answer = os.getenv("MRTR_ANSWER")
    if answer is None and sys.stdin.isatty():
        # input() blocks, so keep it off the event loop.
        answer = await asyncio.to_thread(input, "  your answer (or 'decline'): ")
    answer = (answer or "Oslo").strip()

    if answer.lower() in {"decline", "no", "q"}:
        print("  [client] declining\n")
        return ElicitResult(action="decline")

    print(f"  [client] answering {answer!r}\n")
    return {"municipality": answer}


async def main():
    # input_required_max_rounds bounds the ping-pong: a server that always asks
    # and a client that always answers would otherwise loop forever.
    client = Client(
        PythonStdioTransport(script_path=SERVER),
        elicitation_handler=elicitation_handler,
        input_required_max_rounds=3,
        mode="auto",  # the 2026-07-28 sessionless protocol
    )

    async with client:
        print("Calling incidents_by_municipality() with NO municipality...")
        result = await client.call_tool("incidents_by_municipality", {})
        text = result.content[0].text if result.content else ""
        print(f"  [result] {text[:220]}...\n")

        print("Calling it again WITH a municipality (no round trip needed)...")
        result = await client.call_tool("incidents_by_municipality", {"municipality": "Bergen"})
        text = result.content[0].text if result.content else ""
        print(f"  [result] {text[:220]}...")


asyncio.run(main())
