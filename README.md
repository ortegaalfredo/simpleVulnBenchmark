# simpleVulnBenchmark: Vulnerability Benchmarking Utility

## Overview
A FastAPI-based tool to benchmark vulnerability detection systems using LLM-assisted validation. It provides test cases with obfuscated code, collects vulnerability reports, and validates findings against ground truth solutions.

## Setup
1. Install dependencies:
```bash
pip install -i requirements.txt
```
Run the server:

```bash
    python main.py --url [LLM_API_ENDPOINT] --api-key [YOUR_API_KEY]
```

Example:

```bash
    python main.py --url https://api.openai.com/v1/chat/completions --api-key sk-xxxx
```

Client example:

To automatically benchmark your agent, you must request testcases and send detected vulnerabilities to the benchmark.
This is an example client, you should choose a custom user_id for identification, and use the send_vulns() function to send your agents found testcase vulnerabilities.
The benchmark server.py will then return the score and also generate a HTML page with a ranking graph and a list of all tests made so far:


```python
# client.py
import requests

BASE_URL = "http://localhost:58000"

def start_session(user_id: str):
    response = requests.post(f"{BASE_URL}/startBenchmark/{user_id}")
    session_id = response.json()["sessionId"]
    print(f"Started session: {session_id}")
    return session_id

def get_test_case(session_id):
    url = f"{BASE_URL}/getTestCase/{session_id}"
    response = requests.get(url)
    if response.status_code == 404:
        detail = response.json().get("detail", "")
        if "No more test cases" in detail:
            return None, None
        else:
            raise Exception(f"Error getting test case: {detail}")
    data = response.json()
    return data["testCase"], data["testCaseID"]

def send_vulns(session_id, testcase_id, vulns):
    url = f"{BASE_URL}/sendVulns/{session_id}/{testcase_id}"
    response = requests.post(url, json=vulns)
    if response.status_code != 200:
        raise Exception(f"Failed to send vulns: {response.text}")

def finish_benchmark(session_id):
    url = f"{BASE_URL}/finishBenchmark/{session_id}"
    response = requests.post(url)
    if response.status_code != 200:
        raise Exception(f"Failed to finish benchmark: {response.text}")
    result = response.json()
    print(f"Benchmark finished. Correct: {result['correct']}, Total: {result['total']}")
    return result

def main():
    user_id = "user_123"  # Example user ID
    session_id = start_session(user_id)
    while True:
        test_case, testcase_id = get_test_case(session_id)
        if test_case is None:
            break
        print(f"Received test case: {len(test_case)} bytes")
        # Simulate sending vulnerabilities
        send_vulns(session_id, testcase_id, ["Attacker can use the flashloan function to manipulate the token value and mint unlimited tokens"])
    finish_benchmark(session_id)

if __name__ == "__main__":
    main()
```

