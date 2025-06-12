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
print("Supermemory client initialized for Project Management Simulation.")

# --- HELPER FUNCTIONS ---
def add_memory(user_id, content, container_tags, metadata={}):
    print(f"\\n [+] Adding Memory for user '{user_id}': '{content}'")
    print(f"     Tags: {container_tags}")
    metadata["user_id"] = user_id
    try:
        client.memories.add(content=content, metadata=metadata, container_tags=container_tags)
        print("     Success! Memory stored.")
    except Exception as e:
        print(f"     [!] Error adding memory: {e}")

def search_memories(user_id, query, container_tags=[]):
    print(f"\\n [?] Searching memories for user '{user_id}' with query: '{query}'")
    print(f"     Filtering by tags: {container_tags}")
    
    # Based on our learnings, build a proper filter for containerTags.
    filters = None
    if container_tags:
        filters = {"AND": [{"key": "containerTag", "value": tag} for tag in container_tags]}
    
    try:
        # Pass user_id directly, as discovered in the previous use case.
        response = client.search.execute(q=query, user_id=user_id, filters=filters)
        results = [chunk.content for mem in response.results for chunk in mem.chunks]
        print(f"     Success! Found {len(results)} results.")
        return results
    except Exception as e:
        print(f"     [!] Error searching memory: {e}")
        return []

# --- SIMULATION ---

def run_pm_simulation():
    """
    Simulates a project management workflow across multiple applications.
    """
    project_id = f"proj_{uuid.uuid4().hex[:6]}"
    user_id = "d CEO" # A single user context for this project
    print(f"\\n--- STARTING PROJECT MANAGEMENT SIMULATION (Project: {project_id}) ---")

    # --- Step 1: Initial brief in Slack ---
    slack_conversation = "We need to build a new feature: 'AI-powered code suggestions'. It should be integrated into the main editor by the end of the quarter."
    add_memory(
        user_id,
        slack_conversation,
        ["platform:slack", f"project:{project_id}", "type:feature_brief"]
    )
    time.sleep(3)

    # --- Step 2: Technical discussion in a GitHub Issue comment ---
    github_comment = "I've investigated the 'AI-powered code suggestions' feature. We'll need to use the new 'Cognitron-7' model from 'AI-Corp', which will require a new API key and a dedicated backend service."
    add_memory(
        user_id,
        github_comment,
        ["platform:github", "issue:123", f"project:{project_id}", "type:technical_spec"]
    )
    time.sleep(3)

    # --- Step 3: A decision is made in another Slack channel ---
    decision_message = "Decision: We are approved to get the 'Cognitron-7' model. Budget is locked in. Start integration work."
    add_memory(
        user_id,
        decision_message,
        ["platform:slack", "channel:C-exec-decisions", f"project:{project_id}", "type:decision_log"]
    )
    time.sleep(5) # Longer pause for processing

    # --- Step 4: The "Memory Test" ---
    # An agent needs to create a final Jira/Linear ticket with ALL the context.
    print("\\n" + "="*50)
    print("      PROJECT MANAGEMENT MEMORY RECALL TEST")
    print("="*50)

    # The query is broad, asking for all info on a specific project.
    final_task_query = "Create a summary of the 'AI-powered code suggestions' project for the final implementation ticket."
    
    # We will filter by the project_id tag to gather all related memories.
    results = search_memories(user_id, final_task_query, [f"project:{project_id}"])

    print("\\n--- ANALYSIS ---")
    if not results:
        print("🔴 FAILED: The agent could not recall any information for the project.")
        return

    full_retrieved_text = " ".join(list(set(results))) # Use set to de-duplicate
    print(f"\\nRetrieved Context for Project '{project_id}':\\n---\\n{full_retrieved_text}\\n---")
    
    # Check for key concepts from each source
    recalled_feature = "AI-powered code suggestions" in full_retrieved_text
    recalled_model = "Cognitron-7" in full_retrieved_text
    recalled_approval = "approved to get" in full_retrieved_text

    print(f"Recalled Feature Name (from Slack): {'✅' if recalled_feature else '❌'}")
    print(f"Recalled Technical Detail (from GitHub): {'✅' if recalled_model else '❌'}")
    print(f"Recalled Final Decision (from Slack #2): {'✅' if recalled_approval else '❌'}")
    
    print("\\n--- SIMULATION COMPLETE ---")

if __name__ == "__main__":
    run_pm_simulation() 