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
