import os
import json
import requests
import uuid
from dotenv import load_dotenv

# --- Configuration ---
load_dotenv()
API_KEY = os.getenv("JEAN_API_KEY")
API_URL = "https://jean-memory-api.onrender.com/agent/v1/mcp/messages/"

if not API_KEY:
    raise ValueError("JEAN_API_KEY environment variable not set!")

# --- Helper Function to Call the API ---
def call_jean_api(payload):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(API_URL, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API call failed: {e}")
        return None

# --- Simulation ---
def run_cross_app_test():
    print("--- Running Cross-Application Agent Test ---")
    
    # Use a unique ID for this test run to ensure isolation
    ticket_id = f"JIRA-{uuid.uuid4().hex[:4].upper()}"
    user_report = f"User 'dave' reported in #bugs: 'Can't reset my password for ticket {ticket_id}, the link is broken.'"

    # --- Step 1: A 'Slack Monitor' agent captures a user report ---
    print("\\nStep 1: Ingesting memory from Slack...")
    slack_payload = {
        "jsonrpc": "2.0", "id": 1, "method": "tools/call",
        "params": {
            "name": "add_memories",
            "arguments": {
                "text": user_report,
                "source_app": "slack",
                "metadata": {"channel": "#bugs", "status": "reported", "ticket_id": ticket_id}
            }
        }
    }
    add_slack_result = call_jean_api(slack_payload)
    assert add_slack_result is not None, "Failed to add Slack memory"
    print("✅ Slack memory added.")

    # --- Step 2: A 'Jira Monitor' agent creates a ticket ---
    print("\\nStep 2: Ingesting memory from Jira...")
    jira_payload = {
        "jsonrpc": "2.0", "id": 2, "method": "tools/call",
        "params": {
            "name": "add_memories",
            "arguments": {
                "text": f"Jira Ticket {ticket_id} created: 'Password reset link broken'",
                "source_app": "jira",
                "metadata": {"ticket_id": ticket_id, "status": "open"}
            }
        }
    }
    add_jira_result = call_jean_api(jira_payload)
    assert add_jira_result is not None, "Failed to add Jira memory"
    print("✅ Jira memory added.")

    # --- Step 3: A developer's agent seeks context on the ticket ---
    print(f"\\nStep 3: A developer's agent searches for context on '{ticket_id}'...")
    search_payload = {
        "jsonrpc": "2.0", "id": 3, "method": "tools/call",
        "params": {
            "name": "search_memories",
            "arguments": {
                "query": ticket_id,
                "source_app": "slack,jira" # Filter by both apps
            }
        }
    }
    search_results = call_jean_api(search_payload)

    # --- Step 4: Verification ---
    print("\\nStep 4: Verifying the results...")
    assert search_results is not None, "Search API call failed."
    
    results = search_results.get('result', {}).get('results', [])
    assert len(results) >= 2, f"Expected at least 2 memories, but found {len(results)}"
    
    found_slack = any(res.get('metadata', {}).get('source_app') == 'slack' for res in results)
    found_jira = any(res.get('metadata', {}).get('source_app') == 'jira' for res in results)

    assert found_slack, "Did not find the memory from Slack."
    assert found_jira, "Did not find the memory from Jira."

    print("✅ Slack memory successfully retrieved.")
    print("✅ Jira memory successfully retrieved.")
    print("\\n🏆🏆🏆 Cross-Application Agent Test Successful! 🏆🏆🏆")
    print("The agent successfully retrieved linked memories from multiple sources.")

if __name__ == "__main__":
    run_cross_app_test() 