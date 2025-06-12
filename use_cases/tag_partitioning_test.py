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
print("Supermemory client initialized for Tag Partitioning Test.")

# --- HELPER FUNCTIONS ---
def add_memory(content, container_tags, metadata={}):
    print(f"\\n [+] Adding Memory with tags {container_tags}: '{content}'")
    try:
        # NOTE: We are NOT providing a user_id here, as we suspect it's a red herring.
        client.memories.add(content=content, metadata=metadata, container_tags=container_tags)
        print("     Success! Memory stored.")
    except Exception as e:
        print(f"     [!] Error adding memory: {e}")

def search_memories(query, container_tags=[]):
    print(f"\\n [?] Searching with query: '{query}'")
    print(f"     Filtering ONLY by tags: {container_tags}")
    
    filters = None
    if container_tags:
        # This is our best guess for the filter structure.
        filters = {"AND": [{"key": "containerTag", "value": tag} for tag in container_tags]}
    
    try:
        # NOTE: We are NOT providing a user_id here.
        response = client.search.execute(q=query, filters=filters)
        results = [chunk.content for mem in response.results for chunk in mem.chunks]
        print(f"     Success! Found {len(results)} results.")
        return results
    except Exception as e:
        print(f"     [!] Error searching memory: {e}")
        return []

# --- SIMULATION ---

def run_tag_partition_simulation():
    """
    Tests if `containerTags` can be used for hard data partitioning between organizations.
    """
    org1_tag = f"org:{uuid.uuid4().hex[:6]}"
    org2_tag = f"org:{uuid.uuid4().hex[:6]}"

    print(f"\\n--- STARTING TAG PARTITIONING SIMULATION ---")
    print(f"Organization 1 ID: {org1_tag}")
    print(f"Organization 2 ID: {org2_tag}")
    
    # --- Step 1: Add data to two separate "organizations" ---
    # Both orgs have a memory about "Project Chimera"
    add_memory(
        "For Project Chimera, we will use the Go programming language.",
        [org1_tag, "project:chimera"]
    )
    add_memory(
        "Stark Industries has decided that for Project Chimera, we will use Rust.",
        [org2_tag, "project:chimera"]
    )
    time.sleep(5) # Pause for processing

    # --- Step 2: Search within a single organization's partition ---
    # We query for "Project Chimera" but filter strictly for Organization 1.
    print("\\n" + "="*50)
    print("      MEMORY RECALL TEST (SHOULD ONLY SEE ORG 1 DATA)")
    print("="*50)

    results = search_memories("What language should we use for Project Chimera?", [org1_tag])
    
    print("\\n--- ANALYSIS ---")
    if not results:
        print("🔴 FAILED: The agent could not recall any information for the project.")
        return

    full_retrieved_text = " ".join(list(set(results)))
    print(f"\\nRetrieved Context for '{org1_tag}':\\n---\\n{full_retrieved_text}\\n---")
    
    # --- Verification ---
    # The results MUST contain Org 1's data and MUST NOT contain Org 2's data.
    contains_org1_data = "Go programming language" in full_retrieved_text
    contains_org2_data = "Rust" in full_retrieved_text

    print(f"Contained Org 1's Data ('Go'): {'✅' if contains_org1_data else '❌'}")
    print(f"Contained Org 2's Data ('Rust'): {'❌' if not contains_org2_data else '🔴 FAILED: Data leaked from another organization!'}")
    
    if contains_org1_data and not contains_org2_data:
        print("\\n✅ SUCCESS: `containerTags` successfully partitioned the data.")
    else:
        print("\\n🔴 FAILURE: `containerTags` did not provide a hard data partition.")

    print("\\n--- SIMULATION COMPLETE ---")


if __name__ == "__main__":
    run_tag_partition_simulation() 