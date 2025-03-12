# test_api.py

import requests
import json
import sys

def test_process_endpoint(base_url, user_id, message):
    """
    Test the /api/process endpoint with the given parameters.
    
    Args:
        base_url: The base URL of the API
        user_id: User ID to use in the test
        message: Message to send in the test
    """
    # Ensure the URL has the correct format
    if not base_url.endswith('/'):
        base_url += '/'
    
    # Endpoint URL
    endpoint = f"{base_url}api/process"
    
    # Payload
    payload = {
        "user_id": user_id,
        "message": message
    }
    
    print(f"Testing endpoint: {endpoint}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        # Send POST request
        response = requests.post(
            endpoint,
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        # Print response details
        print(f"\nStatus code: {response.status_code}")
        print("Response headers:")
        for key, value in response.headers.items():
            print(f"  {key}: {value}")
        
        # Pretty print the JSON response if available
        try:
            response_json = response.json()
            print("\nResponse body:")
            print(json.dumps(response_json, indent=2))
        except json.JSONDecodeError:
            print("\nResponse body (not JSON):")
            print(response.text)
            
        # Indicate success or failure
        if response.status_code == 200:
            print("\n✅ Test successful!")
        else:
            print("\n❌ Test failed with status code:", response.status_code)
            
    except requests.RequestException as e:
        print(f"\n❌ Request failed: {e}")
        return False
        
    return response.status_code == 200

if __name__ == "__main__":
    # Default values
    default_url = "https://ai-orchestration-dashboardwar-325750143bf3.herokuapp.com"
    default_user = "test_user"
    default_message = "Hello, AI Orchestrator!"
    
    # Get command line arguments or use defaults
    base_url = sys.argv[1] if len(sys.argv) > 1 else default_url
    user_id = sys.argv[2] if len(sys.argv) > 2 else default_user
    message = sys.argv[3] if len(sys.argv) > 3 else default_message
    
    # Run the test
    test_process_endpoint(base_url, user_id, message)
