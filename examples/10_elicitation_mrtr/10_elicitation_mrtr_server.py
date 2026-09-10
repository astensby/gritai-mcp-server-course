"""Example 10 - Multi Round-Trip Requests (MRTR) with elicitation.

The 2026-07-28 protocol revision made MCP stateless, which removed the
server-to-client back channel. A server can no longer interrupt its own
response to ask the client a question: `ctx.elicit()` raises
"elicitation via server-initiated requests is unavailable on 2026-07-28
connections" unless the client forces `mode="legacy"`.

MRTR (SEP-2322) replaces it. Instead of asking mid-call, the server *returns*
the question as the legitimate result of the call:

    leg 1   client -> tools/call                       (no answer yet)
            server -> InputRequiredResult(...)         "I need a municipality"
    leg 2   client -> tools/call + inputResponses      (same call, plus answers)
            server -> the real result

THE THING TO INTERNALISE: the tool body runs once per leg, from the top.
Nothing is suspended and resumed. Watch the [leg N] lines on stderr when you
run this - the body executes twice for one client-side call_tool().

Run it:
    fastmcp dev examples/10_elicitation_mrtr/10_elicitation_mrtr_server.py
    python examples/10_elicitation_mrtr/10_mrtr_client.py
"""

import logging
import sys
import time

import mcp.types as types
import requests
from fastmcp import Context, FastMCP

# stdout is the stdio transport - diagnostics always go to stderr.
logging.basicConfig(level=logging.INFO, format="%(message)s", stream=sys.stderr)
log = logging.getLogger("example10")

mcp = FastMCP("police-incidents-mrtr")

POLITILOGGEN_URL = "https://api.politiloggen.politiet.no/messages"

# A short pick-list keeps the elicitation form concrete. A real server would
# fetch this from the API or a config.
MUNICIPALITIES = ["Oslo", "Bergen", "Trondheim", "Stavanger", "Tromsø", "Arendal"]


def fetch_incidents(municipality: str | None = None) -> str:
    """Call the Politiloggen API, optionally filtered by municipality."""
    headers = {"accept": "text/plain"}
    params = {"Municipalities": municipality} if municipality else None
    try:
        response = requests.get(POLITILOGGEN_URL, headers=headers, params=params, timeout=15)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        return f"Error fetching incidents: {e}"


@mcp.tool()
def latest_incidents() -> str:
    """Get the latest police incidents from anywhere in Norway.

    No elicitation - this is the single-leg baseline to compare against.
    """
    log.info("[latest_incidents] single leg, no input needed")
    return fetch_incidents()


@mcp.tool()
def incidents_by_municipality(ctx: Context, municipality: str | None = None) -> str:
    """Get the latest police incidents for a municipality.

    If no municipality is given, the server asks the caller to pick one and the
    call completes on the next round trip.

    Args:
        municipality: Municipality to fetch incidents for. Optional - if it is
            missing, you will be asked to choose one.
    """
    answers = ctx.input_responses

    # ---------------------------------------------------------------- leg 1
    # No answers attached: this is the first leg. Ask, and return the ask.
    if not answers:
        if municipality:
            log.info("[leg 1] municipality supplied up front - no round trip needed")
            return fetch_incidents(municipality)

        log.info("[leg 1] no municipality - returning an InputRequiredResult")
        return types.InputRequiredResult(
            input_requests={
                # The key is yours to choose. It is how you find this answer
                # again on the next leg, when several asks are in flight.
                "municipality": types.ElicitRequest(
                    params=types.ElicitRequestFormParams(
                        message="Which municipality do you want police incidents for?",
                        requested_schema={
                            "type": "object",
                            "properties": {
                                "municipality": {
                                    "type": "string",
                                    "title": "Municipality",
                                    "enum": MUNICIPALITIES,
                                }
                            },
                            "required": ["municipality"],
                        },
                    )
                )
            },
            # request_state is the only continuity between legs. It travels
            # through the client, so treat it as untrusted on the way back and
            # never put a secret in it.
            request_state=f"incidents:{int(time.time())}",
        )

    # ---------------------------------------------------------------- leg 2
    # The client re-issued the same call with the answers attached. Note that
    # `municipality` is still None here - the argument was never modified. The
    # answer lives in ctx.input_responses.
    log.info("[leg 2] answers received, request_state=%r", ctx.request_state)
    # Look the answer up by the key chosen on leg 1. It arrives via the client,
    # so do not assume it is there - .get(), not [].
    reply = answers.get("municipality")
    if reply is None:
        return "No answer came back for 'municipality'."

    # A user can refuse. Handle all three actions - "accept" is not a given.
    if reply.action == "decline":
        return "No municipality chosen, so no incidents were fetched."
    if reply.action == "cancel":
        return "The request was cancelled before a municipality was chosen."

    chosen = (reply.content or {}).get("municipality")
    if chosen not in MUNICIPALITIES:
        # The answer came back through the client - validate it like any other
        # client-supplied input.
        return f"'{chosen}' is not one of the municipalities offered."

    log.info("[leg 2] fetching incidents for %s", chosen)
    return fetch_incidents(chosen)


if __name__ == "__main__":
    mcp.run(transport="stdio")
