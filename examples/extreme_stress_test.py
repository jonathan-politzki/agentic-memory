import requests
import json
import os
import uuid
import time
import threading
import concurrent.futures
import random
import string
from datetime import datetime

# --- Configuration ---
API_KEY = os.environ.get("JEAN_API_KEY")
API_URL = "https://jean-memory-api.onrender.com/mcp/messages/"
EXTREME_TIMEOUT = 120  # 2 minutes for the most extreme tests

if not API_KEY:
    raise ValueError("JEAN_API_KEY environment variable not set!")

headers = {
    "X-Api-Key": API_KEY,
    "Content-Type": "application/json"
}

# --- Test Results Tracking ---
test_results = {
    "passed": 0,
    "failed": 0,
    "errors": [],
    "performance_metrics": []
}

def log_result(test_name, success, duration=None, error=None):
    """Log test results for analysis."""
    if success:
        test_results["passed"] += 1
        print(f"✅ {test_name} - PASSED" + (f" ({duration:.2f}s)" if duration else ""))
    else:
        test_results["failed"] += 1
        test_results["errors"].append(f"{test_name}: {error}")
        print(f"❌ {test_name} - FAILED: {error}")
    
    if duration:
        test_results["performance_metrics"].append({
            "test": test_name,
            "duration": duration,
            "timestamp": datetime.now().isoformat()
        })

def call_api_with_metrics(payload, timeout=30, test_name="Unknown"):
    """Call API and track performance metrics."""
    start_time = time.time()
    try:
        response = requests.post(API_URL, headers=headers, data=json.dumps(payload), timeout=timeout)
        response.raise_for_status()
        duration = time.time() - start_time
        return response.json(), duration, None
    except Exception as e:
        duration = time.time() - start_time
        return None, duration, str(e)

# --- EXTREME TEST SUITE ---

def test_1_massive_payload():
    """Test 1: Massive Memory Payload - Can we overwhelm the system?"""
    print("\n🔥 TEST 1: MASSIVE PAYLOAD STRESS TEST")
    
    # Generate a huge memory with lots of complex data
    massive_data = []
    for i in range(100):  # 100 complex memories
        memory = f"""
        STRESS TEST MEMORY #{i} - {uuid.uuid4()}
        
        Complex Data Structure:
        - Technical specs: {random.choice(['Python', 'JavaScript', 'Rust', 'Go'])} with {random.choice(['FastAPI', 'Express', 'Actix', 'Gin'])}
        - Performance metrics: {random.randint(100, 10000)}ms latency, {random.randint(1, 100)}% CPU usage
        - Random UUID chain: {' -> '.join([str(uuid.uuid4()) for _ in range(5)])}
        - Large text block: {''.join(random.choices(string.ascii_letters + string.digits + ' ', k=500))}
        - Nested JSON-like data: {{"key_{j}": "value_{j}_{random.randint(1000, 9999)}" for j in range(10)}}
        - Special characters: ñáéíóú çüß αβγδε 中文 日本語 العربية 🚀🔥💻⚡🎯
        """
        massive_data.append(memory.strip())
    
    payload = {
        "jsonrpc": "2.0", "id": 1, "method": "tools/call",
        "params": {
            "name": "add_memories",
            "arguments": {"text": "\n\n".join(massive_data)}
        }
    }
    
    result, duration, error = call_api_with_metrics(payload, timeout=60, test_name="Massive Payload")
    log_result("Massive Payload (100 complex memories)", result is not None, duration, error)
    
    return result is not None

def test_2_concurrent_bombardment():
    """Test 2: Concurrent API Bombardment - Multiple simultaneous requests"""
    print("\n🔥 TEST 2: CONCURRENT REQUEST BOMBARDMENT")
    
    def single_concurrent_call(thread_id):
        payload = {
            "jsonrpc": "2.0", "id": thread_id, "method": "tools/call",
            "params": {
                "name": "add_memories",
                "arguments": {"text": f"Concurrent test memory from thread {thread_id} at {datetime.now()}"}
            }
        }
        result, duration, error = call_api_with_metrics(payload, test_name=f"Concurrent-{thread_id}")
        return result is not None, duration, error
    
    # Launch 10 concurrent requests
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(single_concurrent_call, i) for i in range(10)]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]
    
    successful = sum(1 for success, _, _ in results if success)
    avg_duration = sum(duration for _, duration, _ in results) / len(results)
    
    log_result(f"Concurrent Bombardment ({successful}/10 successful)", successful >= 8, avg_duration)
    return successful >= 8

def test_3_edge_case_inputs():
    """Test 3: Edge Case Inputs - Weird, malformed, and boundary data"""
    print("\n🔥 TEST 3: EDGE CASE INPUT TESTING")
    
    edge_cases = [
        "",  # Empty string
        " " * 10000,  # Just whitespace
        "A" * 50000,  # Very long single character
        "🚀" * 1000,  # Lots of emojis
        '{"malformed": json, "test": }',  # Malformed JSON-like string
        "SELECT * FROM users; DROP TABLE memories;",  # SQL injection attempt
        "<script>alert('xss')</script>",  # XSS attempt
        "\n\n\n\n\n" * 100,  # Lots of newlines
        "NULL\x00BYTE\x00TEST",  # Null bytes
        "Ω≈ç√∫˜µ≤≥÷åß∂ƒ©˙∆˚¬…æœ∑´®†¥¨ˆøπ\"'«",  # Special Unicode
    ]
    
    successful_edge_cases = 0
    for i, edge_case in enumerate(edge_cases):
        payload = {
            "jsonrpc": "2.0", "id": i, "method": "tools/call",
            "params": {
                "name": "add_memories",
                "arguments": {"text": f"Edge case test {i}: {edge_case}"}
            }
        }
        
        result, duration, error = call_api_with_metrics(payload, test_name=f"EdgeCase-{i}")
        if result is not None:
            successful_edge_cases += 1
    
    log_result(f"Edge Case Inputs ({successful_edge_cases}/{len(edge_cases)} handled)", 
               successful_edge_cases >= len(edge_cases) * 0.7)  # 70% success rate acceptable
    return successful_edge_cases >= len(edge_cases) * 0.7

def test_4_deep_query_stress():
    """Test 4: Deep Query Stress - Complex analytical queries"""
    print("\n🔥 TEST 4: DEEP QUERY STRESS TEST")
    
    complex_queries = [
        "Analyze all my technical preferences and create a comprehensive technology stack recommendation with detailed reasoning for each choice, including performance benchmarks and scalability considerations.",
        "Generate a detailed psychological profile based on my communication patterns, decision-making processes, and technical interests, then provide actionable insights for personal development.",
        "Create a comprehensive business strategy document based on my entrepreneurial interests, technical skills, and market observations, including a 5-year roadmap with specific milestones.",
        "Synthesize all my learning patterns and create a personalized curriculum for advanced AI/ML topics, including specific resources, timelines, and assessment criteria.",
    ]
    
    successful_deep_queries = 0
    for i, query in enumerate(complex_queries):
        payload = {
            "jsonrpc": "2.0", "id": i, "method": "tools/call",
            "params": {
                "name": "deep_memory_query",
                "arguments": {"search_query": query}
            }
        }
        
        print(f"   -> Executing complex query {i+1}/4...")
        result, duration, error = call_api_with_metrics(payload, timeout=EXTREME_TIMEOUT, test_name=f"DeepQuery-{i}")
        if result is not None:
            successful_deep_queries += 1
            # Check if we got substantial content
            if "result" in result and "content" in result["result"]:
                content_length = len(result["result"]["content"][0].get("text", ""))
                print(f"      Generated {content_length} characters of analysis")
    
    log_result(f"Deep Query Stress ({successful_deep_queries}/{len(complex_queries)} successful)", 
               successful_deep_queries >= 2)  # At least 50% success rate
    return successful_deep_queries >= 2

def test_5_rapid_fire_mixed_operations():
    """Test 5: Rapid Fire Mixed Operations - Quick succession of different API calls"""
    print("\n🔥 TEST 5: RAPID FIRE MIXED OPERATIONS")
    
    operations = [
        ("add_memories", {"text": f"Rapid fire test {i}"}) for i in range(5)
    ] + [
        ("search_memory", {"query": "rapid fire"}) for _ in range(3)
    ] + [
        ("ask_memory", {"question": "What do you know about rapid fire testing?"}) for _ in range(2)
    ] + [
        ("list_memories", {"limit": 3}) for _ in range(2)
    ]
    
    successful_ops = 0
    start_time = time.time()
    
    for i, (operation, args) in enumerate(operations):
        payload = {
            "jsonrpc": "2.0", "id": i, "method": "tools/call",
            "params": {"name": operation, "arguments": args}
        }
        
        result, duration, error = call_api_with_metrics(payload, test_name=f"RapidFire-{operation}-{i}")
        if result is not None:
            successful_ops += 1
        
        # Small delay to avoid overwhelming
        time.sleep(0.1)
    
    total_duration = time.time() - start_time
    ops_per_second = len(operations) / total_duration
    
    print(f"   -> Completed {successful_ops}/{len(operations)} operations in {total_duration:.2f}s ({ops_per_second:.2f} ops/sec)")
    log_result(f"Rapid Fire Mixed Ops ({successful_ops}/{len(operations)} successful)", 
               successful_ops >= len(operations) * 0.8)  # 80% success rate
    return successful_ops >= len(operations) * 0.8

def test_6_malformed_requests():
    """Test 6: Malformed Request Handling - Test API's error handling"""
    print("\n🔥 TEST 6: MALFORMED REQUEST HANDLING")
    
    malformed_requests = [
        {"invalid": "json structure"},  # Missing required fields
        {"jsonrpc": "1.0", "method": "invalid_method", "id": 1},  # Wrong JSON-RPC version
        {"jsonrpc": "2.0", "method": "tools/call", "params": {"name": "nonexistent_tool"}, "id": 1},  # Invalid tool
        {"jsonrpc": "2.0", "method": "tools/call", "params": {"name": "add_memories"}, "id": 1},  # Missing arguments
        {"jsonrpc": "2.0", "method": "tools/call", "params": {"name": "add_memories", "arguments": {"wrong_param": "test"}}, "id": 1},  # Wrong parameter
    ]
    
    handled_gracefully = 0
    for i, malformed_payload in enumerate(malformed_requests):
        try:
            response = requests.post(API_URL, headers=headers, data=json.dumps(malformed_payload), timeout=30)
            # We expect these to fail, but gracefully (not 500 errors)
            if response.status_code in [400, 422]:  # Bad request or validation error
                handled_gracefully += 1
                print(f"   -> Malformed request {i+1} handled gracefully (HTTP {response.status_code})")
            elif response.status_code == 500:
                print(f"   -> Malformed request {i+1} caused server error (HTTP 500)")
            else:
                print(f"   -> Malformed request {i+1} unexpected response (HTTP {response.status_code})")
        except Exception as e:
            print(f"   -> Malformed request {i+1} caused exception: {e}")
    
    log_result(f"Malformed Request Handling ({handled_gracefully}/{len(malformed_requests)} handled gracefully)", 
               handled_gracefully >= len(malformed_requests) * 0.6)  # 60% graceful handling acceptable
    return handled_gracefully >= len(malformed_requests) * 0.6

def run_extreme_stress_tests():
    """Execute the complete extreme stress test suite."""
    print("🚀🔥 EXTREME STRESS TEST SUITE - GOING HAM ON THE JEAN MEMORY API 🔥🚀")
    print("=" * 80)
    
    start_time = time.time()
    
    # Run all stress tests
    tests = [
        test_1_massive_payload,
        test_2_concurrent_bombardment,
        test_3_edge_case_inputs,
        test_4_deep_query_stress,
        test_5_rapid_fire_mixed_operations,
        test_6_malformed_requests,
    ]
    
    for test_func in tests:
        try:
            test_func()
        except Exception as e:
            log_result(test_func.__name__, False, error=str(e))
        print("-" * 40)
    
    total_duration = time.time() - start_time
    
    # Final Results
    print("\n" + "=" * 80)
    print("🏁 EXTREME STRESS TEST RESULTS")
    print("=" * 80)
    print(f"Total Tests: {test_results['passed'] + test_results['failed']}")
    print(f"✅ Passed: {test_results['passed']}")
    print(f"❌ Failed: {test_results['failed']}")
    print(f"⏱️  Total Duration: {total_duration:.2f} seconds")
    
    if test_results['performance_metrics']:
        avg_response_time = sum(m['duration'] for m in test_results['performance_metrics']) / len(test_results['performance_metrics'])
        max_response_time = max(m['duration'] for m in test_results['performance_metrics'])
        print(f"📊 Avg Response Time: {avg_response_time:.2f}s")
        print(f"📊 Max Response Time: {max_response_time:.2f}s")
    
    if test_results['errors']:
        print(f"\n🚨 ERRORS ENCOUNTERED:")
        for error in test_results['errors']:
            print(f"   - {error}")
    
    success_rate = test_results['passed'] / (test_results['passed'] + test_results['failed']) * 100
    print(f"\n🎯 Overall Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("🏆 VERDICT: API SURVIVED THE EXTREME STRESS TEST! 🏆")
    elif success_rate >= 60:
        print("⚠️  VERDICT: API showed resilience but has some weaknesses")
    else:
        print("💥 VERDICT: API struggled under extreme conditions")

if __name__ == "__main__":
    run_extreme_stress_tests() 