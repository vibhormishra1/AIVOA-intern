"""Final workflow node."""
from typing import Optional
def assemble_response(state):
    """Mark the graph complete and return its accumulated state."""
    return {**state, "processing_status": "complete"}
