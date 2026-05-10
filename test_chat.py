import os, json, requests

BASE = "http://localhost:8000"

def chat(messages):
    r = requests.post(f"{BASE}/chat", json={"messages": messages}, timeout=30)
    r.raise_for_status()
    return r.json()

def run_tests():
    print("=" * 60)
    print("TEST 1: Health check")
    r = requests.get(f"{BASE}/health")
    print("Status:", r.json())

    print("\n" + "=" * 60)
    print("TEST 2: Vague query - should clarify, NOT recommend")
    resp = chat([{"role": "user", "content": "I need an assessment"}])
    print("Reply:", resp["reply"])
    print("Recommendations:", resp["recommendations"])
    assert resp["recommendations"] == [], "FAIL: Should not recommend on vague query"
    print("PASS: No premature recommendations")

    print("\n" + "=" * 60)
    print("TEST 3: Java developer - should recommend")
    resp = chat([
        {"role": "user", "content": "I am hiring a mid-level Java developer with 4 years experience who also works with stakeholders"},
        {"role": "assistant", "content": resp["reply"]},
        {"role": "user", "content": "Mid-level, around 4 years experience, needs to collaborate with business stakeholders"}
    ])
    print("Reply:", resp["reply"])
    print("Recommendations:")
    for r2 in resp["recommendations"]:
        print(f"  - {r2['name']} ({r2['test_type']}) -> {r2['url']}")
    assert len(resp["recommendations"]) >= 1, "FAIL: Should have recommendations"
    print(f"PASS: Got {len(resp['recommendations'])} recommendations")

    print("\n" + "=" * 60)
    print("TEST 4: Off-topic refusal")
    resp = chat([{"role": "user", "content": "What are the best interview questions to ask candidates?"}])
    print("Reply:", resp["reply"])
    print("Recommendations:", resp["recommendations"])
    print("(Should refuse general hiring advice)")

    print("\n" + "=" * 60)
    print("TEST 5: Comparison question")
    resp = chat([{"role": "user", "content": "What is the difference between OPQ32r and Global Skills Assessment?"}])
    print("Reply:", resp["reply"][:300])

    print("\n" + "=" * 60)
    print("TEST 6: Job description input")
    jd = """We are hiring a Senior Data Scientist. Requirements:
    - 5+ years Python experience
    - Machine learning expertise
    - Strong communication skills
    - Team collaboration"""
    resp = chat([{"role": "user", "content": f"Here is a job description: {jd}"}])
    print("Reply:", resp["reply"])
    print("Recommendations:")
    for r2 in resp["recommendations"]:
        print(f"  - {r2['name']} ({r2['test_type']})")

    print("\n" + "=" * 60)
    print("TEST 7: Refinement - add personality test")
    history = [
        {"role": "user", "content": "Hiring a Python developer, mid level"},
        {"role": "assistant", "content": "Here are some Python assessments for mid-level developers."},
        {"role": "user", "content": "Actually, also add personality tests to the shortlist"}
    ]
    resp = chat(history)
    print("Reply:", resp["reply"])
    types = [r2["test_type"] for r2 in resp["recommendations"]]
    print("Types in recommendations:", types)
    has_personality = any(t == "P" for t in types)
    print("Has personality:", has_personality)

    print("\n" + "=" * 60)
    print("ALL TESTS DONE")

if __name__ == "__main__":
    run_tests()
