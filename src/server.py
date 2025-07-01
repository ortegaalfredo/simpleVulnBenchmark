# main.py
import os
import uuid
from fastapi import FastAPI, HTTPException
from typing import List
import argparse
import requests
import time
import random
from reporter import generate_html_report

app = FastAPI()

# Globals for LLM config
LLM_URL = None
API_KEY = None

# Directory containing test cases
TEST_CASE_DIR = "testcases/vulnerable"

# In-memory storage for sessions
sessions = {}

@app.post("/startBenchmark/{user_id}")
def start_benchmark(user_id: str):
    session_id = str(uuid.uuid4())
    test_cases = []
    for filename in os.listdir(TEST_CASE_DIR):
        if not filename.endswith(".solution"):
            # Repeat each test-case 3 times.
            test_cases.append(filename)
    test_cases.sort()
    sessions[session_id] = {
        "user_id": user_id,
        "start_time": time.time(),
        "test_cases": test_cases,
        "current_index": 0,
        "vulns": {},
        "positive": 0,
        "false_positive": 0
    }
    return {"sessionId": session_id}

@app.get("/getTestCase/{session_id}")
def get_test_case(session_id: str):
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    test_cases = session["test_cases"]
    current_index = session["current_index"]
    if current_index >= len(test_cases):
        raise HTTPException(status_code=404, detail="No more test cases")
    test_case = test_cases[current_index]
    session["current_index"] = current_index + 1
    test_case_path = os.path.join(TEST_CASE_DIR, test_case)
    try:
        with open(test_case_path, "r") as f:
            test_case_content = f.read()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read test case: {e}")
    test_case_id = test_case
    test_case_content = obfuscate_code_with_llm(test_case_content)
    return {"testCase": test_case_content, "testCaseID": test_case_id}

def check_vuln_with_llm(vuln: str, code: str, solution: str) -> bool:
    if not LLM_URL or not API_KEY:
        print("Warning: LLM URL or API Key not configured. Skipping check.")
        return False

    prompt = f"""You are a security auditor. You are given a piece of code, a reported vulnerability, and the true vulnerability description. Your task is to determine if the reported vulnerability matches the true vulnerability.

Code:
---
{code}
---

Reported Vulnerability:
---
{vuln}
---

True Vulnerability Description (Solution):
---
{solution}
---

Does the "Reported Vulnerability" accurately and uniquely describe the issue explained in the "True Vulnerability Description" for the given "Code"? Answer with only "yes" or "no". 
"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 8192,
        "temperature": 0.8
    }

    try:
        response = requests.post(LLM_URL, headers=headers, json=data, timeout=600)
        response.raise_for_status()
        llm_response = response.json()
        raw_content = llm_response['choices'][0]['message']['content'].strip()
        if "</think>" in raw_content:
            raw_content = raw_content.split("</think>", 1)[1].strip()
        answer = raw_content.lower()
        print(f"LLM says: {answer}")
        return "yes" in answer
    except Exception as e:
        print(f"Error calling LLM: {e}")
        return False

def obfuscate_code_with_llm(code: str) -> str:
    """
    Uses an LLM to modify the given source code by changing variable names,
    while maintaining the original logic, inputs, and outputs.
    """
    if not LLM_URL or not API_KEY:
        print("Warning: LLM URL or API Key not configured. Returning original code.")
        return code

    prompt = f"""You are a code refactorer. You are given a piece of source code.
Your task is to modify the code by changing the names of all variables, functions, and classes
to different names. The logic, inputs, and outputs of the code must remain exactly the same.
Do not add, remove, or change any other part of the code.

Original Code:
---
{code}
---

Return only the modified code.
/no_think
"""
    # Generate a random seed for this request
    seed = random.randint(0, 2**31-1)

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 8192,  # Increased for code generation
        "temperature": 0.8,
        "seed": seed
    }

    try:
        response = requests.post(LLM_URL, headers=headers, json=data, timeout=600)
        response.raise_for_status()
        llm_response = response.json()
        modified_code = llm_response['choices'][0]['message']['content'].strip()
        if "</think>" in modified_code:
            modified_code = modified_code.split("</think>", 1)[1].strip()
        # The LLM might wrap the code in markdown, so we remove it
        if modified_code.startswith("```") and modified_code.endswith("```"):
            modified_code = modified_code[modified_code.find('\n')+1:-3].strip()
        print("Code obfuscated successfully.")
        return modified_code
    except Exception as e:
        print(f"Error during code obfuscation: {e}")
        return code  # Return original code on error

@app.post("/sendVulns/{session_id}/{testcase_id}")
def send_vulns(session_id: str, testcase_id: str, vuln: str):
    """
    testcase_id is the test case file name. vuln is a single vulnerability string.
    """
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    # Security: Prevent path traversal and only allow known test cases
    if (".." in testcase_id or "/" in testcase_id or "\\" in testcase_id or
        testcase_id not in session["test_cases"]):
        raise HTTPException(status_code=400, detail="Invalid testcase_id")
    if "vulns" not in session:
        session["vulns"] = {}
    if testcase_id not in session["vulns"]:
        session["vulns"][testcase_id] = []
    session["vulns"][testcase_id].append(vuln)
    print(f"Received vuln for {testcase_id}: {vuln}")
    print("Checking if vuln is found...")
    test_case_path = os.path.join(TEST_CASE_DIR, testcase_id)
    test_case_solution_path = os.path.join(TEST_CASE_DIR, testcase_id)+".solution"
    try:
        with open(test_case_path, "r") as f:
            test_case_content = f.read()
        with open(test_case_solution_path, "r") as f:
            test_case_solution_content = f.read()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Test case or solution not found for {testcase_id}")
    
    is_correct = check_vuln_with_llm(vuln, test_case_content, test_case_solution_content)
    if is_correct:
        session["positive"] += 1
        print("Vuln matched solution. Score: +1 positive")
    else:
        session["false_positive"] += 1
        print("Vuln did not match solution. Score: +1 false_positive")

    return {"status": "success"}

@app.post("/finishBenchmark/{session_id}")
def finish_benchmark(session_id: str):
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    end_time = time.time()
    elapsed_time = end_time - session["start_time"]
    result_line = f"{int(end_time)},{session['user_id']},{session['positive']},{session['false_positive']},{elapsed_time}\n"
    
    with open("results.txt", "a") as f:
        f.write(result_line)

    generate_html_report()

    return {
        "correct": session["positive"], 
        "total": len(session["test_cases"]),
        "false_positive": session["false_positive"],
        "time_taken": elapsed_time
    }

if __name__ == "__main__":
    import uvicorn
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True, help="LLM API endpoint URL for OpenAI-compatible API.", default="https://api.openai.com/v1/chat/completions")
    parser.add_argument("--api-key", dest="api_key", required=True, help="LLM API key.", default="asdf")
    args = parser.parse_args()

    LLM_URL = args.url
    API_KEY = args.api_key
    
    uvicorn.run(app, host="0.0.0.0", port=58000)
