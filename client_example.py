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
