import pytest
from langgraph_graph import planner_node, gatherer_node, synthesizer_node

# Mock state input
mock_state = {"topic": "Impact of AI on education"}

def test_planner_node():
    result = planner_node(mock_state)
    assert "subquestions" in result
    assert isinstance(result["subquestions"], list)
    assert len(result["subquestions"]) >= 2

def test_gatherer_node():
    plan = planner_node(mock_state)
    state = {
        "topic": mock_state["topic"],
        "subquestions": plan["subquestions"]
    }
    result = gatherer_node(state)
    assert "findings" in result
    assert isinstance(result["findings"], list)
    assert len(result["findings"]) > 0

def test_synthesizer_node():
    findings = ["AI is helping automate grading.", "AI can provide personalized learning plans."]
    state = {
        "topic": mock_state["topic"],
        "findings": findings
    }
    result = synthesizer_node(state)
    assert "summary" in result
    assert isinstance(result["summary"], str)
    assert len(result["summary"]) > 20
