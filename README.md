# simpleVulnBenchmark: Vulnerability Benchmarking Utility

## Overview
A FastAPI-based tool to benchmark vulnerability detection systems using LLM-assisted validation. It provides test cases with obfuscated code, collects vulnerability reports, and validates findings against ground truth solutions.

## Server Setup
1. Install dependencies:
```bash
pip install -r requirements.txt
```
Run the server:

```bash
    python main.py --url [LLM_API_ENDPOINT] --api-key [YOUR_API_KEY]
```

Example:

```bash
    python main.py --url https://api.openai.com/v1/chat/completions --api-key sk-xxxx
```

## Client

The benchmark consists of 3 API calls to request test cases and submit potential vulnerabilities:

1. Identification: Choose a unique user_id to identify your agent during the benchmarking process.
2. Request test cases: Start by retrieving the test cases from the benchmark server.
3. Submit vulnerabilities: Use the send_vulns() function to report any vulnerabilities detected by your agent.
4. Call finish_benchmark() to calculate results.

The ranking and scoring are fully automated. Once submitted, the benchmark server (server.py) will:

1. Calculate and return your agent's performance score.
2. Generate a detailed HTML report containing:
3. A ranking graph to visualize your agent’s performance relative to others.
4. A comprehensive list of all tests conducted so far.

The test cases are simple: a single file per test, with only one critical vulnerability per file. Some files contain no critical vulnerabilities. A mis-reported vulnerability counts as a false positive.


## Example client code:

Currently, this benchmark is running on neuroengine.ai, with 43 test-cases.
This example will run the benchmark and send results to the instance running at neuroengine.ai. No registration required.
Results will be available at: https://www.neuroengine.ai/67267476912310299493/reports/benchReport.html

```python
from client import start_session, get_test_case, send_vulns, finish_benchmark

BASE_URL = "http://www.neuroengine.ai:58000"

def main():
    """
    Example of how to run a full benchmark session.
    """
    user_id = "user_123"  # Example user ID
    session_id = start_session(BASE_URL, user_id)

    while True:
        test_case_data = get_test_case(BASE_URL, session_id)
        if test_case_data is None:
            print("No more test cases.")
            break
        
        test_case, testcase_id = test_case_data
        print(f"Received test case '{testcase_id}' ({len(test_case)} bytes)")

        # TODO: Implement your vulnerability detection logic here
        # For example, you could analyze the `test_case` content
        vulnerabilities = ["Attacker can use the flashloan function to manipulate the token value and mint unlimited tokens"]
        
        print(f"Sending {len(vulnerabilities)} detected vulnerabilities...")
        send_vulns(BASE_URL, session_id, testcase_id, vulnerabilities)

    print("Finishing benchmark...")
    finish_benchmark(BASE_URL, session_id)

if __name__ == "__main__":
    main() 
```

