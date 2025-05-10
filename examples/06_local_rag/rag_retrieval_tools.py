import os
import json
import logging
from typing import List, Dict, Any
import boto3
import psycopg2
from psycopg2 import sql

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

AWS_REGION_NAME = os.environ.get("AWS_REGION", "eu-west-1")
AWS_EMBEDDING_MODEL_ID = "amazon.titan-embed-text-v2:0"
AWS_PROFILE_NAME = "my-mcp-server-profile"
try:
    session = boto3.Session(profile_name=AWS_PROFILE_NAME, region_name=AWS_REGION_NAME)
    bedrock_runtime = session.client(service_name='bedrock-runtime')
    aws_available = True
    logging.info(f"Successfully initialized AWS Bedrock runtime client in region '{AWS_REGION_NAME}'.")
except Exception as e:
    logging.warning(f"Failed to initialize AWS Bedrock runtime client. AWS embeddings unavailable. Error: {e}")
    bedrock_runtime = None
    aws_available = False

DB_NAME = os.environ.get("PGVECTOR_DB_NAME", "vectordb")
DB_USER = os.environ.get("PGVECTOR_DB_USER", "my_username")
DB_PASSWORD = os.environ.get("PGVECTOR_DB_PASSWORD", "my_password")
DB_HOST = os.environ.get("PGVECTOR_DB_HOST", "localhost")
DB_PORT = os.environ.get("PGVECTOR_DB_PORT", "5432")
DB_SCHEMA = "embeddings"
DB_TABLE = "documents"

def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        logging.info(f"Successfully connected to database '{DB_NAME}' on {DB_HOST}:{DB_PORT}.")
        return conn
    except psycopg2.OperationalError as e:
        logging.error(f"Database connection failed: {e}")
        return None
    except Exception as e:
        logging.error(f"An unexpected error occurred during database connection: {e}")
        return None

def retrieve_chunks(
    query: str,
    top_n: int = 5,
    aws_model_id: str = AWS_EMBEDDING_MODEL_ID
) -> List[Dict[str, Any]]:
    if not query:
        logging.warning("Query is empty. Cannot retrieve chunks.")
        return []
    if not aws_available or not bedrock_runtime:
        logging.error("AWS Bedrock client not available for query embedding.")
        return []

    query_embedding_list = None
    try:
        logging.info(f"Creating query embedding using AWS Bedrock model: {aws_model_id}")
        request_body = json.dumps({"inputText": query})
        response = bedrock_runtime.invoke_model(
            body=request_body, modelId=aws_model_id, accept='application/json', contentType='application/json'
        )
        response_body = json.loads(response.get('body').read())
        query_embedding_list = response_body.get('embedding')

        if query_embedding_list is None:
             logging.error("Failed to create query embedding with AWS Bedrock.")
             return []
        logging.info("Successfully created embedding for query using AWS.")

        conn = get_db_connection()
        if not conn:
            logging.error("Failed to get database connection for retrieval.")
            return []

        results = []
        try:
            with conn.cursor() as cur:
                retrieve_sql = sql.SQL("""
                    SELECT chunk_id, filename, content, embedding <=> %s::vector AS distance
                    FROM {}.{}
                    ORDER BY distance ASC
                    LIMIT %s;
                """).format(sql.Identifier(DB_SCHEMA), sql.Identifier(DB_TABLE))

                cur.execute(retrieve_sql, (query_embedding_list, top_n))
                db_results = cur.fetchall()

                for row in db_results:
                    chunk_id, filename, content, distance = row
                    similarity_score = 1.0 - distance
                    results.append({
                        'score': max(0.0, similarity_score),
                        'chunk': {
                            'chunk_id': chunk_id,
                            'filename': filename,
                            'content': content,
                        }
                    })
                logging.info(f"Retrieved top {len(results)} chunks from database.")

        except psycopg2.Error as e:
            logging.error(f"Database error during retrieval: {e}")
            conn.rollback()
        except Exception as e:
            logging.error(f"An unexpected error occurred during retrieval: {e}")
            conn.rollback()
        finally:
            if conn:
                conn.close()
                logging.info("Database connection closed after retrieval.")

        return results

    except Exception as e:
        logging.error(f"Failed to retrieve chunks: {e}")
        return []

def rerank_chunks(query: str, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    logging.info("Skipping re-ranking step (placeholder).")
    return results

def answer_query(query: str, top_n: int = 5):
    logging.info(f"Answering query: '{query}' using AWS embeddings and PostgreSQL")
    retrieved = retrieve_chunks(query, top_n=top_n)
    if not retrieved:
        logging.warning("No chunks retrieved for the query.")
        return []

    reranked = rerank_chunks(query, retrieved)
    return reranked

# Main execution example removed as this is now a library module 