"""
Mock test để kiểm tra logic của exercises mà không cần API key thực.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from exercises.exercise_2_tools import (
    search_legal_knowledge,
    check_statute_of_limitations,
    LEGAL_KNOWLEDGE,
)
from exercises.exercise_4_multiagent import (
    law_agent,
    tax_agent,
    compliance_agent,
    privacy_agent,
    check_routing,
    State,
)

print("=" * 70)
print("MOCK TEST: Kiểm tra logic các exercises")
print("=" * 70)

# =====================================================================
# TEST EXERCISE 2: TOOLS
# =====================================================================
print("\n✅ TEST 1: search_legal_knowledge tool")
print("-" * 70)

# Test 1a: Tìm knowledge base về breach
result = search_legal_knowledge.invoke({"query": "breach contract damages"})
print(f"Query: 'breach contract damages'")
print(f"Result: {result[:100]}...")
assert "breach" in result.lower() or "ucc" in result.lower(), "Không tìm thấy UCC breach info"
print("✓ Passed: Tìm được knowledge base UCC")

# Test 1b: Tìm knowledge base về labor
result = search_legal_knowledge.invoke({"query": "lao động sa thải"})
print(f"\nQuery: 'lao động sa thải'")
print(f"Result: {result[:100]}...")
assert "labor" in result.lower() or "việt nam" in result.lower(), "Không tìm thấy labor law"
print("✓ Passed: Tìm được Luật Lao Động Việt Nam")

print("\n✅ TEST 2: check_statute_of_limitations tool")
print("-" * 70)

# Test 2a: Contract
result = check_statute_of_limitations.invoke({"case_type": "contract"})
print(f"Case type: 'contract'")
print(f"Result: {result}")
assert "4 năm" in result or "4 years" in result, "Không có thời hiệu 4 năm"
print("✓ Passed: Thời hiệu contract = 4 năm")

# Test 2b: Labor
result = check_statute_of_limitations.invoke({"case_type": "labor"})
print(f"\nCase type: 'labor'")
print(f"Result: {result}")
assert "3 năm" in result, "Không có thời hiệu 3 năm cho labor"
print("✓ Passed: Thời hiệu labor = 3 năm")

print("\n✅ TEST 3: LEGAL_KNOWLEDGE entry")
print("-" * 70)
print(f"Số entry: {len(LEGAL_KNOWLEDGE)}")
assert len(LEGAL_KNOWLEDGE) >= 2, "Cần ít nhất 2 entries"
labor_entry = next((e for e in LEGAL_KNOWLEDGE if e["id"] == "labor_law"), None)
assert labor_entry is not None, "Không tìm thấy labor_law entry"
print(f"✓ Passed: labor_law entry có {len(labor_entry['keywords'])} keywords")

# =====================================================================
# TEST EXERCISE 4: MULTI-AGENT
# =====================================================================
print("\n" + "=" * 70)
print("✅ TEST 4: check_routing function")
print("-" * 70)

# Test 4a: Routing với keyword tax
test_state_tax: State = {
    "question": "Công ty phải trả bao nhiêu thuế?",
    "law_analysis": "",
    "tax_analysis": "",
    "compliance_analysis": "",
    "privacy_analysis": "",
    "final_response": "",
}
routes = check_routing(test_state_tax)
route_names = [r.node for r in routes]
print(f"Question: 'Công ty phải trả bao nhiêu thuế?'")
print(f"Routed to: {route_names}")
assert "tax_agent" in route_names, "Không route đến tax_agent"
print("✓ Passed: Route đến tax_agent")

# Test 4b: Routing với keyword privacy
test_state_privacy: State = {
    "question": "Nếu bị rò rỉ dữ liệu khách hàng thì sao?",
    "law_analysis": "",
    "tax_analysis": "",
    "compliance_analysis": "",
    "privacy_analysis": "",
    "final_response": "",
}
routes = check_routing(test_state_privacy)
route_names = [r.node for r in routes]
print(f"\nQuestion: 'Nếu bị rò rỉ dữ liệu khách hàng thì sao?'")
print(f"Routed to: {route_names}")
assert "privacy_agent" in route_names, "Không route đến privacy_agent"
print("✓ Passed: Route đến privacy_agent")

# Test 4c: Routing với keyword compliance
test_state_comp: State = {
    "question": "Cần tuân thủ quy định SEC nào?",
    "law_analysis": "",
    "tax_analysis": "",
    "compliance_analysis": "",
    "privacy_analysis": "",
    "final_response": "",
}
routes = check_routing(test_state_comp)
route_names = [r.node for r in routes]
print(f"\nQuestion: 'Cần tuân thủ quy định SEC nào?'")
print(f"Routed to: {route_names}")
assert "compliance_agent" in route_names, "Không route đến compliance_agent"
print("✓ Passed: Route đến compliance_agent")

# Test 4d: Routing khi không có keyword
test_state_none: State = {
    "question": "Xin chào",
    "law_analysis": "",
    "tax_analysis": "",
    "compliance_analysis": "",
    "privacy_analysis": "",
    "final_response": "",
}
routes = check_routing(test_state_none)
route_names = [r.node for r in routes]
print(f"\nQuestion: 'Xin chào'")
print(f"Routed to: {route_names}")
assert "aggregate_results" in route_names, "Không route đến aggregate_results"
print("✓ Passed: Route đến aggregate_results khi không có keyword")

print("\n✅ TEST 5: Kiểm tra các agent functions tồn tại")
print("-" * 70)
agents = {
    "law_agent": law_agent,
    "tax_agent": tax_agent,
    "compliance_agent": compliance_agent,
    "privacy_agent": privacy_agent,
}
for name, agent_func in agents.items():
    assert callable(agent_func), f"{name} không phải function"
    print(f"✓ {name} tồn tại và callable")

print("\n" + "=" * 70)
print("✅ TẤT CẢ TESTS PASSED!")
print("=" * 70)
print("\n📝 Ghi chú:")
print("- Các tools hoạt động đúng")
print("- Routing logic hoạt động đúng")
print("- Các agents được định nghĩa đúng")
print("- Khi có API key thực, chạy: python exercises/exercise_2_tools.py")
print("  hoặc: python exercises/exercise_4_multiagent.py")
print("=" * 70)
