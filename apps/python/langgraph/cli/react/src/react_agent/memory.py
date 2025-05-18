from langgraph.checkpoint.redis import RedisSaver
from langgraph.checkpoint.memory import InMemorySaver

DB_URL="redis://localhost:6379/0"

# checkpointer = RedisSaver.from_conn_string(DB_URL)
checkpointer = InMemorySaver()
