from langgraph.checkpoint.postgres import PostgresSaver
from core.state import UserProfile

POSTGRES_URI = "postgresql://postgres:postgres@localhost:5442/insuranceadvisor"

def get_checkpointer() -> PostgresSaver:
    """
    Short-Term Memory (STM) using Postgres.
    Stores graph state per thread_id.
    """    
    return PostgresSaver.from_conn_string(POSTGRES_URI)

# FOR LTM, WE'LL USE TWO DB'S
# 1. POSTGES   2. PINECONE 
# STM: PostgresSaver per thread_id
