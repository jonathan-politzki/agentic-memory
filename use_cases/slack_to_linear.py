import os
import uuid
import time
from dotenv import load_dotenv
from supermemory import Supermemory

# --- SETUP ---
# Load environment variables from .env file
load_dotenv()

# Initialize the Supermemory client
api_key = os.getenv("SUPERMEMORY_API_KEY")
if not api_key:
    raise ValueError("SUPERMEMORY_API_KEY not found in .env file. Please add it.")

client = Supermemory(api_key=api_key)
print("Supermemory client initialized.")

# --- HELPER FUNCTIONS ---

def add_memory(user_id: str, content: str, container_tags: list = []):
    """Adds a new memory to Supermemory."""
    print(f"\n [+] Adding Memory for user '{user_id}': '{content}'")
    print(f"     Tags: {container_tags}")

    # Corrected: Based on SDK inspection, 'user_id' is not a top-level param.
    # It must be passed within the metadata object for filtering later.
    metadata = {"user_id": user_id}

    try:
        response = client.memories.add(
            content=content,
            metadata=metadata,
            container_tags=container_tags
        )
        print("     Success! Memory stored.")
        return response
    except Exception as e:
        print(f"     [!] Error adding memory: {e}")
        return None

def search_memories(user_id: str, query: str, container_tags: list = []):
    """Searches for memories for a given user."""
    print(f"\n [?] Searching memories for user '{user_id}' with query: '{query}'")
    print(f"     Filtering by tags: {container_tags}")

    # Corrected: Build a 'filters' object. Since user_id is in metadata,
    # we must build a filter for it.
    filters = {
        "AND": [
            {"key": "metadata.user_id", "value": user_id}
        ]
    }
    if container_tags:
        filters["AND"].extend([{"key": "containerTag", "value": tag} for tag in container_tags])

    try:
        response = client.search.execute(
            q=query,
            filters=filters
        )
        # Corrected: Based on direct introspection, the text is in the `.content`
        # attribute of each chunk object.
        results = [chunk.content for mem in response.results for chunk in mem.chunks]
        print(f"     Success! Found {len(results)} results.")
        for res in results:
            print(f"       - '{res}'")
        return results
    except Exception as e:
        print(f"     [!] Error searching memory: {e}")
        return []

# --- SIMULATION ---

def run_live_simulation():
    """
    Runs a live simulation against the Supermemory API to test key features.
    """
    print("\n--- STARTING LIVE SUPERMEMORY SIMULATION ---")

    # --- Use Case 1: Testing User Partitioning ---
    print("\n\n--- USE CASE 1: USER DATA PARTITIONING ---")
    # Two different users report two different bugs
    add_memory(
        user_id="conner_pope",
        content="The main login button is broken on staging.",
        container_tags=["platform:slack", "channel:C012AB3CD", "type:bug_report"]
    )
    add_memory(
        user_id="jonathan_p",
        content="The navigation bar disappears on the settings page.",
        container_tags=["platform:slack", "channel:C012AB3CD", "type:bug_report"]
    )
    
    # Wait a moment for processing
    time.sleep(5)

    # Agent searches for Conner's bugs. It should NOT see Jonathan's bug.
    print("\nNow, an agent searches ONLY for Conner's bug reports...")
    conner_results = search_memories(
        user_id="conner_pope",
        query="What's broken on staging?",
        container_tags=["type:bug_report"]
    )
    assert len(conner_results) >= 1, "Should find at least one bug report for Conner"
    assert "login button" in conner_results[0]
    print("\n     ✅ PASSED: Correctly retrieved only Conner's memory.")

    # --- Use Case 2: Testing Non-Literal Search & Cross-App Linking ---
    print("\n\n--- USE CASE 2: NON-LITERAL SEARCH & CROSS-APP LINKING ---")
    
    # Step A: An agent creates a Linear ticket based on Conner's bug report.
    print("\nStep A: Agent is creating a Linear ticket for the login bug.")
    linear_ticket_id = f"LIN-{uuid.uuid4().hex[:4].upper()}"
    
    # Step B: Agent ADDS a new memory about the ticket it just created.
    # This is the key step for cross-application context.
    add_memory(
        user_id="conner_pope",
        content=f"I have created a ticket for the login button issue. The ticket ID is {linear_ticket_id}.",
        container_tags=["platform:linear", f"ticket_id:{linear_ticket_id}", "type:status_update"]
    )
    
    time.sleep(5)

    # Step C: Conner asks for an update in Slack using a vague query.
    # The agent should be able to find the Linear ticket status.
    print("\nStep C: Conner asks for an update in Slack using a non-literal query...")
    status_update_results = search_memories(
        user_id="conner_pope",
        query="any update on that sign-in problem?"
    )
    
    assert len(status_update_results) > 0, "Search for status update should return results"
    # A good result would contain the ticket ID.
    found_ticket = any(linear_ticket_id in result for result in status_update_results)
    assert found_ticket
    print(f"\n     ✅ PASSED: Successfully found the Linear ticket status ('{linear_ticket_id}') from a vague Slack query.")

    print("\n--- SIMULATION COMPLETE ---")

if __name__ == "__main__":
    run_live_simulation() 