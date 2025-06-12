import os
import uuid
import time
from dotenv import load_dotenv
from supermemory import Supermemory

# --- SETUP ---
load_dotenv()
api_key = os.getenv("SUPERMEMORY_API_KEY")
if not api_key:
    raise ValueError("SUPERMEMORY_API_KEY not found in .env file.")
client = Supermemory(api_key=api_key)
print("Supermemory client initialized for Customer Support Simulation.")

# --- HELPER FUNCTIONS (from previous use case) ---
def add_memory(user_id, content, metadata={}):
    print(f"\\n [+] Adding Memory for user '{user_id}': '{content}'")
    # Combine the user_id into the metadata for filtering
    metadata["user_id"] = user_id
    try:
        client.memories.add(content=content, metadata=metadata)
        print("     Success! Memory stored.")
    except Exception as e:
        print(f"     [!] Error adding memory: {e}")

def search_memories(user_id, query):
    print(f"\\n [?] Searching memories for user '{user_id}' with query: '{query}'")
    try:
        response = client.search.execute(q=query, user_id=user_id)
        results = [chunk.content for mem in response.results for chunk in mem.chunks]
        print(f"     Success! Found {len(results)} results.")
        return results
    except Exception as e:
        print(f"     [!] Error searching memory: {e}")
        return []

# --- SIMULATION ---

def run_chatbot_simulation():
    """
    Simulates a customer support chat to test memory recall over a conversation.
    """
    session_id = f"session_{uuid.uuid4().hex[:6]}"
    print(f"\\n--- STARTING CHATBOT SIMULATION (Session: {session_id}) ---")

    # The user is the same, but we use the session_id as the unique identifier
    # for this specific conversation.
    user_id = session_id 

    # 1. Conversation starts
    add_memory(user_id, "User: My name is Jane Doe and I'm having trouble with my new 'WizPro 5000' camera.", {"turn": 1})
    time.sleep(2)
    add_memory(user_id, "Agent: Hi Jane, I can help with that. What seems to be the issue with the WizPro 5000?", {"turn": 2})
    time.sleep(2)
    
    # 2. User describes the problem
    add_memory(user_id, "User: It's not turning on. I charged it overnight like the manual said, but the power light doesn't even blink.", {"turn": 3})
    time.sleep(2)
    
    # 3. Agent asks for more details, user provides them
    add_memory(user_id, "Agent: Okay, and just to be sure, you're using the power adapter that came in the box?", {"turn": 4})
    time.sleep(2)
    add_memory(user_id, "User: Yes, the original one. I even tried a different wall outlet.", {"turn": 5})
    time.sleep(2)

    # 4. A topic change / irrelevant question
    add_memory(user_id, "User: By the way, do you offer student discounts?", {"turn": 6})
    time.sleep(2)
    add_memory(user_id, "Agent: We do offer a 10% student discount, but let's get your camera working first.", {"turn": 7})
    time.sleep(5) # Longer pause for processing

    # 5. The "Memory Test"
    print("\\n" + "="*50)
    print("                MEMORY RECALL TEST")
    print("="*50)
    
    # The agent now needs to summarize the user's actual problem.
    # The query is intentionally a bit vague.
    final_summary_query = "Summarize the customer's primary technical issue."
    
    results = search_memories(user_id, final_summary_query)
    
    print("\\n--- ANALYSIS ---")
    if not results:
        print("🔴 FAILED: The agent could not recall any relevant information.")
        return

    # In a real app, you'd feed these results into an LLM to generate a clean summary.
    # For our test, we'll just check if the key concepts were retrieved.
    full_retrieved_text = " ".join(results)
    print(f"\\nRetrieved Context:\\n---\\n{full_retrieved_text}\\n---")
    
    # Check for key concepts
    recalled_name = "Jane Doe" in full_retrieved_text
    recalled_product = "WizPro 5000" in full_retrieved_text
    recalled_problem = "not turning on" in full_retrieved_text
    recalled_irrelevant = "student discount" in full_retrieved_text

    print(f"Recalled User's Name ('Jane Doe'): {'✅' if recalled_name else '❌'}")
    print(f"Recalled Product ('WizPro 5000'): {'✅' if recalled_product else '❌'}")
    print(f"Recalled Core Problem ('not turning on'): {'✅' if recalled_problem else '❌'}")
    print(f"Retrieved Irrelevant Details ('student discount'): {'⚠️ (Okay, but not ideal)' if recalled_irrelevant else '✅ (Good, it focused on the main topic)'}")
    
    print("\\n--- SIMULATION COMPLETE ---")


if __name__ == "__main__":
    run_chatbot_simulation() 