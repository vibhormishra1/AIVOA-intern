"""Complaint AI workflow orchestration using LangGraph."""
from typing import Optional
from langgraph.graph import StateGraph, START, END
from .state import ComplaintState
from .nodes.parse_document import parse_document
from .nodes.validate import validate_completeness
from .nodes.classify_risk import classify_risk
from .nodes.check_duplicates import check_duplicates
from .nodes.generate_capa import generate_capa
from .nodes.assemble import assemble_response

# Build the LangGraph workflow
workflow = StateGraph(ComplaintState)

workflow.add_node("parse_document", parse_document)
workflow.add_node("validate_completeness", validate_completeness)
workflow.add_node("classify_risk", classify_risk)
workflow.add_node("check_duplicates", check_duplicates)
workflow.add_node("generate_capa", generate_capa)
workflow.add_node("assemble", assemble_response)

workflow.add_edge(START, "parse_document")
workflow.add_edge("parse_document", "validate_completeness")
workflow.add_edge("validate_completeness", "classify_risk")
workflow.add_edge("classify_risk", "check_duplicates")
workflow.add_edge("check_duplicates", "generate_capa")
workflow.add_edge("generate_capa", "assemble")
workflow.add_edge("assemble", END)

complaint_app = workflow.compile()

async def run_complaint_graph(raw_text: str, file_type: str = "txt", existing=None):
    """Run the LangGraph pipeline from start to finish."""
    initial_state = {
        "raw_text": raw_text,
        "file_type": file_type,
        "errors": [],
        "existing_records": existing or []
    }
    
    # Run the graph asynchronously
    final_state = await complaint_app.ainvoke(initial_state)
    return final_state
