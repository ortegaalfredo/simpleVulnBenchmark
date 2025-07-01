import requests
from typing import List, Tuple, Optional

def start_session(base_url: str, user_id: str) -> str:
    """Starts a new benchmark session for the given user."""
    response = requests.post(f"{base_url}/startBenchmark/{user_id}")
    response.raise_for_status()
    session_id = response.json()["sessionId"]
    print(f"Started session: {session_id}")
    return session_id

def get_test_case(base_url: str, session_id: str) -> Optional[Tuple[str, str]]:
    """Retrieves the next test case for the given session."""
    url = f"{base_url}/getTestCase/{session_id}"
    response = requests.get(url)
    if response.status_code == 404:
        detail = response.json().get("detail", "")
        if "No more test cases" in detail:
            return None
        else:
            raise Exception(f"Error getting test case: {detail}")
    response.raise_for_status()
    data = response.json()
    return data["testCase"], data["testCaseID"]

def send_vulns(base_url: str, session_id: str, testcase_id: str, vulns: List[str]) -> None:
    """Sends a list of found vulnerabilities for a specific test case, one by one."""
    url = f"{base_url}/sendVulns/{session_id}/{testcase_id}"
    for vuln in vulns:
        response = requests.post(url, params={"vuln": vuln})
        response.raise_for_status()

def finish_benchmark(base_url: str, session_id: str) -> dict:
    """Finishes the benchmark session and gets the results."""
    url = f"{base_url}/finishBenchmark/{session_id}"
    response = requests.post(url)
    response.raise_for_status()
    result = response.json()
    print(f"Benchmark finished. Correct: {result['correct']}, Total: {result['total']}, False Positives: {result['false_positive']}")
    return result 