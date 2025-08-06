#for with confidence scoring and PDF input

import os
import requests
from typing import Dict, List, TypedDict
from langgraph.graph import StateGraph, END
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

#State Schema
class ResearchState(TypedDict, total=False):
    topic: str
    subquestions: List[str]
    findings: List[str]
    summary: str
    report: str
    citations: List[str]
    pdf_text: str
    attempted_replanning: bool
    confidence_scores: List[float]

#Planner Node
def planner_node(state: Dict) -> Dict:
    topic = state["topic"]
    prompt = f"Break down the research topic '{topic}' into 3-5 detailed sub-questions for research."
    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": "user", "content": prompt}]
    )
    questions = response.choices[0].message.content.split("\n")
    subquestions = [q.strip("- ").strip() for q in questions if q.strip()]
    return {"topic": topic, "subquestions": subquestions}

#Tavilyy Search
def tavily_search(query: str) -> List[Dict]:
    api_key = os.getenv("TAVILY_API_KEY")
    url = "https://api.tavily.com/search"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    body = {
        "query": query,
        "include_answers": True,
        "include_raw_content": False,
        "include_images": False,
        "max_results": 3
    }
    response = requests.post(url, headers=headers, json=body)
    data = response.json()
    results = []
    for item in data.get("results", []):
        results.append({
            "question": query,
            "title": item.get("title", ""),
            "url": item.get("url", ""),
            "content": item.get("content", "")
        })
    return results

#Gathering Node with Replanning
def gatherer_node(state: Dict) -> Dict:
    findings = []
    citations = []
    empty_results = 0

    for question in state["subquestions"]:
        search_results = tavily_search(question)
        if not search_results:
            empty_results += 1
            continue
        for item in search_results:
            findings.append(f"Q: {question}\nA: {item['content']}")
            citations.append(item["url"])

    if empty_results >= len(state["subquestions"]) // 2 and not state.get("attempted_replanning", False):
        return {
            "replan_needed": True,
            "topic": state["topic"],
            "attempted_replanning": True
        }

    return {
        "topic": state["topic"],
        "subquestions": state["subquestions"],
        "findings": findings,
        "citations": citations,
        "pdf_text": state.get("pdf_text", ""),
        "attempted_replanning": state.get("attempted_replanning", False)
    }

#Scoring
def rate_confidence(text:str)-> float:
    prompt = f"Rate your confidence (0-100) in the factual accuracy of the following answer. Respond with just a number:\n\n{text}"
    try:
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}]
        )
        rating = response.choices[0].message.content.strip()
        return float(rating)
    except:
        return 50.0

#Synthesizer Node
def summarize_text(text: str, topic: str) -> str:
    prompt = f"Summarize this research note on '{topic}':\n\n{text[:3000]}"
    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

def synthesizer_node(state: Dict) -> Dict:
    topic = state["topic"]
    partial_summaries = []
    confidence_scores = []

    pdf_context = state.get("pdf_text", "")
    if pdf_context:
        partial_summaries.append(f" Context from PDF:\n{pdf_context[:3000]}")

    for finding in state["findings"]:
        try:
            summary = summarize_text(finding, topic)
            partial_summaries.append(summary)
            confidence_scores.append(rate_confidence(summary))
        except Exception as e:
            partial_summaries.append(f"[Error summarizing one finding: {e}]")
            confidence_scores.append(50.0)

    combined = "\n\n".join(partial_summaries)[:6000]
    final_prompt = f"Based on the following summaries and any provided PDF context, provide a structured research report on '{topic}':\n\n{combined}"
    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": "user", "content": final_prompt}]
    )
    full_summary = response.choices[0].message.content.strip()

    return {
        "summary": full_summary,
        "report": full_summary,
        "citations": state.get("citations", []),
        "confidence_scores": confidence_scores
    }

#Orchestrator
def run_research_agent(topic: str, pdf_text: str = "") -> Dict:
    builder = StateGraph(ResearchState)

    builder.add_node("Planner", planner_node)
    builder.add_node("Gatherer", gatherer_node)
    builder.add_node("Synthesizer", synthesizer_node)

    builder.set_entry_point("Planner")
    builder.add_edge("Planner", "Gatherer")

    def gather_decision(state: Dict) -> str:
        return "Planner" if state.get("replan_needed") else "Synthesizer"

    builder.add_conditional_edges("Gatherer", gather_decision)
    builder.add_edge("Synthesizer", END)

    graph = builder.compile()
    result = graph.invoke({"topic": topic, "pdf_text": pdf_text})
    return result
