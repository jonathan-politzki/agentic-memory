import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
from jean_api_sdk.client import JeanClient

# --- Configuration ---
load_dotenv()

# We will use a unique client_name for each test run to ensure isolation
SWARM_ID = f"swarm_{uuid.uuid4().hex[:6]}"
# Initialize the client, which will automatically pick up the JEAN_API_KEY
# from the .env file.
memory_client = JeanClient(client_name=SWARM_ID)

# --- Agent Definitions ---

class ResearcherAgent:
    def __init__(self, client: JeanClient, task_id: str, aspect: str):
        self.client = client
        self.task_id = task_id
        self.aspect = aspect

    def run(self, topic: str):
        """Researches a specific aspect of a topic and stores facts."""
        print(f"\\n[Researcher: {self.aspect}] Starting research on {topic}.")
        if self.aspect == "Technical Specs":
            facts = [
                "The new EV model features a 90kWh solid-state battery.",
                "It offers a dual-motor all-wheel-drive system with 600 horsepower.",
                "The chassis is a carbon-fiber monocoque for reduced weight.",
            ]
        else:  # Market Position
            facts = [
                "Competitor A's latest model has a longer range but slower charging.",
                "Competitor B is priced 15% lower but lacks performance features.",
                "The market shows a growing demand for premium, high-performance EVs.",
            ]
        
        for fact in facts:
            self.client.add_memory(f"Fact about {self.aspect}: {fact}")
        
        print(f"  ✅ [Researcher: {self.aspect}] Research complete. {len(facts)} facts stored.")
        return True

class AnalystAgent:
    def __init__(self, client: JeanClient, task_id: str):
        self.client = client
        self.task_id = task_id

    def run(self) -> str:
        """Waits for research and synthesizes it into a summary."""
        print("\\n[Analyst] Waiting for all research data...")
        time.sleep(2) 
        
        print("  - [Analyst] Listing all memories in the current context...")
        search_result = self.client.list_memories(limit=100)
        
        if not search_result or not search_result.get("results"):
            print("  - [Analyst] No memories found.")
            return "No analysis could be generated as no memories were found."

        facts = [
            res.get("memory", "") for res in search_result["results"]
            if "Fact about" in res.get("memory", "")
        ]
        if not facts:
            print("  - [Analyst] No 'Fact about' memories found in the list.")
            return "No analysis could be generated as no facts were found."
            
        print(f"  ✅ [Analyst] All research data found ({len(facts)} facts). Synthesizing analysis...")

        analysis = "## Competitive Analysis Summary\\n" + "\\n".join(f"- {fact}" for fact in facts)
        
        self.client.add_memory(f"ANALYSIS: {analysis}")
        print("  ✅ [Analyst] Analysis complete and stored.")
        return analysis

class ExecutiveAgent:
    def __init__(self, client: JeanClient, task_id: str):
        self.client = client
        self.task_id = task_id

    def run(self):
        """Waits for the analysis and makes a final decision."""
        print("\\n[Executive] Waiting for final analysis...")
        time.sleep(2)

        print("  - [Executive] Listing memories to find the final analysis...")
        search_result = self.client.list_memories(limit=100)
        
        if not search_result or not search_result.get("results"):
            print("  - [Executive] No analysis found. Cannot make a decision.")
            return "No decision could be made."

        analysis_list = [
            res.get("memory", "") for res in search_result["results"]
            if "ANALYSIS:" in res.get("memory", "")
        ]
        if not analysis_list:
            print("  - [Executive] No analysis found in memory list.")
            return "No decision could be made."

        analysis = analysis_list[0]
        print("  ✅ [Executive] Analysis received. Formulating final decision...")
        
        decision = f"Decision based on analysis: We will proceed with the project, focusing on our superior performance and fast-charging capabilities as key market differentiators."
        self.client.add_memory(f"FINAL DECISION: {decision}")
        print("  ✅ [Executive] Final decision stored.")
        return decision

# --- Orchestration ---

def simple_test():
    """A quick test to ensure the API is live and authentication works."""
    print("="*80)
    print("🔬 RUNNING SIMPLE CONNECTION TEST 🔬")
    print("="*80)
    client = JeanClient(client_name=f"simple-test-{uuid.uuid4().hex[:6]}")
    tools = client.list_tools()
    if tools and tools.get("tools"):
        print(f"✅ Simple Test PASSED. Found tools: {[t.get('name') for t in tools['tools']]}")
        return True
    else:
        print("❌ Simple Test FAILED. Could not list tools.")
        return False

def run_advanced_strategy_test():
    """Orchestrates the full agent swarm to produce a report."""
    swarm_id = f"swarm_{uuid.uuid4().hex[:6]}"
    swarm_client = JeanClient(client_name=swarm_id)

    print("\\n" + "="*80)
    print("🚀 STARTING ADVANCED AGENT SWARM TEST 🚀")
    print(f"(Using shared Client/Swarm ID: {swarm_id})")
    print("="*80)

    try:
        # Phase 1: Parallel Research
        with ThreadPoolExecutor(max_workers=2) as executor:
            research_futures = [
                executor.submit(ResearcherAgent(swarm_client, swarm_id, "Technical Specs").run, "Our New EV"),
                executor.submit(ResearcherAgent(swarm_client, swarm_id, "Market Position").run, "Our New EV")
            ]
            for future in as_completed(research_futures):
                future.result()
        
        # Phase 2: Analysis (depends on Phase 1)
        analysis = AnalystAgent(swarm_client, swarm_id).run()
        assert "Analysis" in analysis, "Analyst agent failed to produce an analysis."
        
        final_decision = ExecutiveAgent(swarm_client, swarm_id).run()
        assert "Decision" in final_decision, "Executive agent failed to make a decision."

        # Final validation using the robust list_memories method
        print("\\n" + "-"*80)
        print("🕵️ [Orchestrator] Validating final results from memory...")
        time.sleep(2) 
        all_memories = swarm_client.list_memories(limit=100)
        
        final_decision_from_memory_text = None
        if all_memories and all_memories.get('results'):
            for mem in all_memories['results']:
                if "FINAL DECISION:" in mem.get('memory', ''):
                    final_decision_from_memory_text = mem.get('memory', '')
                    break
        
        assert final_decision_from_memory_text, "Could not retrieve final decision from memory."
        assert "key market differentiators" in final_decision_from_memory_text, "Final decision content is incorrect."
        print(f"  - Retrieved Decision: '{final_decision_from_memory_text}'")
        
        print("\\n🏆🏆🏆 Advanced Strategy Test Successful! 🏆🏆🏆")

    except Exception as e:
        print(f"\\n❌❌❌ Test Failed: {e} ❌❌❌")

if __name__ == "__main__":
    if simple_test():
        run_advanced_strategy_test() 