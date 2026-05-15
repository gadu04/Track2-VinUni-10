"""Bài Tập 4: Thêm Privacy Agent vào Multi-Agent System

Hoàn thành các TODO để thêm privacy agent và conditional routing.
"""

import asyncio
import os
import sys
from typing import Annotated, TypedDict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langgraph.graph import END, START, StateGraph
from langgraph.types import Send

from common.llm import get_llm


def _last_wins(left: str | None, right: str | None) -> str:
    """Reducer: giá trị mới ghi đè giá trị cũ."""
    return right if right is not None else (left or "")


class State(TypedDict):
    question: str
    law_analysis: Annotated[str, _last_wins]
    tax_analysis: Annotated[str, _last_wins]
    compliance_analysis: Annotated[str, _last_wins]
    privacy_analysis: Annotated[str, _last_wins]  # TODO: Thêm field mới
    final_response: str
    routing_tax: bool
    routing_compliance: bool
    routing_privacy: bool


def law_agent(state: State) -> dict:
    """Agent phân tích pháp lý tổng quát."""
    llm = get_llm()
    prompt = f"""Bạn là chuyên gia pháp lý. Phân tích câu hỏi sau:

{state['question']}

Tập trung vào: hợp đồng, trách nhiệm dân sự, quyền và nghĩa vụ pháp lý."""
    
    response = llm.invoke([HumanMessage(content=prompt)])
    return {"law_analysis": response.content}


def check_routing(state: State) -> dict:
    """Quyết định gọi agents nào dựa trên nội dung câu hỏi."""
    question_lower = state["question"].lower()
    
    # Kiểm tra keywords để xác định agents cần gọi
    needs_tax = any(kw in question_lower for kw in ["tax", "irs", "thuế"])
    needs_compliance = any(kw in question_lower for kw in ["compliance", "sec", "regulation"])
    needs_privacy = any(kw in question_lower for kw in ["data", "privacy", "gdpr", "dữ liệu", "rò rỉ"])
    
    # Cập nhật state với routing info
    return {
        "routing_tax": needs_tax,
        "routing_compliance": needs_compliance,
        "routing_privacy": needs_privacy
    }


def tax_agent(state: State) -> dict:
    """Agent chuyên về thuế."""
    llm = get_llm()
    prompt = f"""Bạn là chuyên gia thuế. Phân tích khía cạnh thuế trong câu hỏi:

Câu hỏi: {state['question']}
Phân tích pháp lý: {state.get('law_analysis', 'N/A')}

Tập trung: IRS, tax evasion, penalties, FBAR, FATCA."""
    
    response = llm.invoke([HumanMessage(content=prompt)])
    return {"tax_analysis": response.content}


def compliance_agent(state: State) -> dict:
    """Agent chuyên về compliance."""
    llm = get_llm()
    prompt = f"""Bạn là chuyên gia compliance. Phân tích khía cạnh tuân thủ:

Câu hỏi: {state['question']}
Phân tích pháp lý: {state.get('law_analysis', 'N/A')}

Tập trung: SEC, SOX, FCPA, AML, regulatory violations."""
    
    response = llm.invoke([HumanMessage(content=prompt)])
    return {"compliance_analysis": response.content}


# TODO: Implement privacy_agent
def privacy_agent(state: State) -> dict:
    """Agent chuyên về bảo vệ dữ liệu cá nhân và GDPR."""
    llm = get_llm()
    prompt = f"""Bạn là chuyên gia về bảo vệ dữ liệu cá nhân và GDPR. Phân tích khía cạnh privacy:

Câu hỏi: {state['question']}
Phân tích pháp lý: {state.get('law_analysis', 'N/A')}

Tập trung: GDPR, data protection, privacy rights, data breach notification, liability for data loss."""
    
    response = llm.invoke([HumanMessage(content=prompt)])
    return {"privacy_analysis": response.content}


def aggregate_results(state: State) -> dict:
    """Tổng hợp kết quả từ tất cả agents."""
    llm = get_llm()
    
    sections = []
    if state.get("law_analysis"):
        sections.append(f"📋 PHÂN TÍCH PHÁP LÝ:\n{state['law_analysis']}")
    if state.get("tax_analysis"):
        sections.append(f"💰 PHÂN TÍCH THUẾ:\n{state['tax_analysis']}")
    if state.get("compliance_analysis"):
        sections.append(f"✅ PHÂN TÍCH TUÂN THỰ:\n{state['compliance_analysis']}")
    if state.get("privacy_analysis"):
        sections.append(f"🔒 PHÂN TÍCH PRIVACY:\n{state['privacy_analysis']}")
    
    combined = "\n\n".join(sections)
    
    prompt = f"""Tổng hợp các phân tích sau thành một báo cáo pháp lý hoàn chỉnh:

{combined}

Câu hỏi gốc: {state['question']}

Hãy tạo một báo cáo ngắn gọn, có cấu trúc rõ ràng."""
    
    response = llm.invoke([HumanMessage(content=prompt)])
    return {"final_response": response.content}


def build_graph() -> StateGraph:
    """Xây dựng multi-agent graph."""
    graph = StateGraph(State)
    
    # Add nodes
    graph.add_node("law_agent", law_agent)
    graph.add_node("check_routing", check_routing)
    graph.add_node("tax_agent", tax_agent)
    graph.add_node("compliance_agent", compliance_agent)
    graph.add_node("privacy_agent", privacy_agent)
    graph.add_node("aggregate_results", aggregate_results)
    
    # Define edges
    graph.add_edge(START, "law_agent")
    graph.add_edge("law_agent", "check_routing")
    
    # Conditional edges từ check_routing đến các agents
    def routing_function(state):
        """Route to agents dựa trên routing flags."""
        next_nodes = []
        if state.get("routing_tax"):
            next_nodes.append("tax_agent")
        if state.get("routing_compliance"):
            next_nodes.append("compliance_agent")
        if state.get("routing_privacy"):
            next_nodes.append("privacy_agent")
        return next_nodes if next_nodes else ["aggregate_results"]
    
    graph.add_conditional_edges("check_routing", routing_function)
    
    # Các agents đều chuyển đến aggregate_results
    graph.add_edge("tax_agent", "aggregate_results")
    graph.add_edge("compliance_agent", "aggregate_results")
    graph.add_edge("privacy_agent", "aggregate_results")
    graph.add_edge("aggregate_results", END)
    
    return graph.compile()


async def main():
    load_dotenv()
    
    # Test với câu hỏi có liên quan đến privacy
    question = "Nếu công ty bị rò rỉ dữ liệu khách hàng, hậu quả pháp lý và thuế là gì?"
    
    print("=" * 70)
    print("MULTI-AGENT SYSTEM với Privacy Agent")
    print("=" * 70)
    print(f"\nCâu hỏi: {question}\n")
    print("Đang xử lý qua các agents...\n")
    
    graph = build_graph()
    
    result = await graph.ainvoke({
        "question": question,
        "law_analysis": "",
        "tax_analysis": "",
        "compliance_analysis": "",
        "privacy_analysis": "",
        "final_response": "",
        "routing_tax": False,
        "routing_compliance": False,
        "routing_privacy": False,
    })
    
    print("\n" + "=" * 70)
    print("KẾT QUẢ CUỐI CÙNG")
    print("=" * 70)
    print(result["final_response"])
    print("\n" + "=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
