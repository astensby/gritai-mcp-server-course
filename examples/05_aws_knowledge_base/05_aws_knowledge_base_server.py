import json
import os
import sys

import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv
from fastmcp import FastMCP

load_dotenv()

mcp = FastMCP("aws-knowledgebase-test")


def get_bedrock_session(aws_region: str) -> boto3.Session:
    """Build a boto3 session.

    Uses AWS_PROFILE when set (the SSO profile from `aws configure sso`), and
    otherwise falls back to the default credential chain so the example also
    works with env credentials, an instance role, or a container role.
    """
    aws_profile = os.environ.get("AWS_PROFILE")
    if aws_profile:
        return boto3.Session(profile_name=aws_profile, region_name=aws_region)
    return boto3.Session(region_name=aws_region)


@mcp.tool()
def search_knowledge_base(query: str) -> str:
    """Search the AWS Bedrock knowledge base for the most relevant information."""
    knowledge_base_id = os.environ.get("KNOWLEDGE_BASE_ID")
    aws_region = os.environ.get("AWS_REGION")

    if not knowledge_base_id:
        return "Error: KNOWLEDGE_BASE_ID environment variable not set."
    if not aws_region:
        return "Error: AWS_REGION environment variable not set (required for Bedrock client)."

    try:
        session = get_bedrock_session(aws_region)
        bedrock_agent_runtime = session.client(service_name="bedrock-agent-runtime")

        response = bedrock_agent_runtime.retrieve(
            knowledgeBaseId=knowledge_base_id,
            retrievalQuery={"text": query},
        )

        results = response.get("retrievalResults", [])
        if not results:
            return "No relevant information found in the knowledge base."

        formatted_results = []
        for i, result in enumerate(results):
            content = result.get("content", {}).get("text", "N/A")
            score = result.get("score", "N/A")
            location = result.get("location", {})
            loc_str = json.dumps(location) if location else "N/A"
            formatted_results.append(
                f"Result {i + 1} (Score: {score}):\nContent: {content}\nLocation: {loc_str}\n---"
            )

        return "\n".join(formatted_results)

    except ClientError as e:
        return f"Error calling Bedrock Retrieve API: {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"


if __name__ == "__main__":
    required_vars = ["KNOWLEDGE_BASE_ID", "AWS_REGION"]
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    if missing_vars:
        # Print to stderr (stdout is the stdio transport) and stop - starting a
        # server that cannot answer a single call only hides the problem.
        print(
            f"Error: Missing required environment variables: {', '.join(missing_vars)}\n"
            "Please set them in .env or your environment before running the server.",
            file=sys.stderr,
        )
        sys.exit(1)

    mcp.run(transport="stdio")
