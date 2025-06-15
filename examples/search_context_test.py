import os
import uuid
import time
from dotenv import load_dotenv
from jean_api_sdk.client import JeanClient

# --- Configuration ---
load_dotenv()

def run_search_context_test():
    """
    A targeted test to determine if `search_memories` correctly
    respects the X-Client-Name header for context isolation.
    """
    # 1. Create two unique, isolated client contexts
    context_a_id = f"context-a-{uuid.uuid4().hex[:6]}"
    context_b_id = f"context-b-{uuid.uuid4().hex[:6]}"
    
    client_a = JeanClient(client_name=context_a_id)
    client_b = JeanClient(client_name=context_b_id)

    print("="*80)
    print("🔬 RUNNING SEARCH CONTEXT ISOLATION TEST 🔬")
    print(f"  - Context A: {context_a_id}")
    print(f"  - Context B: {context_b_id}")
    print("="*80)

    # 2. Add a specific, unique memory to each context
    secret_a = "The code for the Alpha launch is 'fidelio'."
    secret_b = "The password for the Beta server is 'orpheus'."

    print(f"\\n-> Adding secret to Context A...")
    client_a.add_memory(secret_a)
    
    print(f"\\n-> Adding secret to Context B...")
    client_b.add_memory(secret_b)

    # Give the server a moment to index the new memories
    print("\\nWaiting for search index to update...")
    time.sleep(5)

    # 3. Search for Secret A, but ONLY within Context A
    print(f"\\n-> Searching for '{secret_a.split()[-1]}' ONLY in Context A...")
    search_result = client_a.search_memories(query="fidelio")

    # 4. Verification
    print("\\n--- ANALYSIS ---")
    assert search_result is not None, "Search API call failed."
    
    results = search_result.get('results', [])
    assert len(results) > 0, f"❌ FAILURE: Search in Context A returned no results."
    
    retrieved_text = " ".join([res.get('memory', '') for res in results])
    print(f"  - Retrieved memories: {retrieved_text}")

    contains_secret_a = "fidelio" in retrieved_text
    contains_secret_b = "orpheus" in retrieved_text

    assert contains_secret_a, "❌ FAILURE: Did not find the correct secret in Context A."
    assert not contains_secret_b, f"❌ CRITICAL FAILURE: Data from Context B ('{secret_b}') leaked into Context A's search results!"

    print("\\n🏆 SUCCESS: `search_memories` correctly isolates context.")
    print("   It found the correct secret and did not show data from other contexts.")


if __name__ == "__main__":
    run_search_context_test() 