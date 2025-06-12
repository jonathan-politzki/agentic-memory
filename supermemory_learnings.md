# Supermemory: Conclusive Analysis & Learnings

This document outlines the key findings from our hands-on testing of the `supermemory` Python SDK (v3.0.0a1). Our conclusion has been updated based on a series of rigorous, industrial use-case simulations.

## Final Conclusion (Updated)

**`supermemory` is not a suitable backend for building reliable, multi-context agentic systems.**

While the service shows promise in semantic search, it fails on the most critical requirement for agentic workflows: **robust and predictable context isolation.** Our tests conclusively demonstrated that the filtering mechanisms (`user_id` and `containerTags`) do not create hard data partitions. Instead, they act as weak signals in a global search, resulting in severe context pollution from other users and sessions.

This architectural flaw, combined with a misleading and inconsistent Python SDK, makes the platform unreliable for any application requiring data privacy and predictable memory recall. We have validated the feedback from other developers, like Conner Pope, and can state with confidence that `supermemory`'s current implementation cannot support our vision.

---

## Key Failures & Evidence

1.  **Context Filtering is Unreliable:** The most critical failure. In our [Project Management Assistant test](use_cases/project_management_assistant.py), a search filtered for a unique project ID (`project:proj_ef1508`) returned a flood of completely unrelated data from other use cases and files, while failing to retrieve the actual project data. This demonstrates that `containerTags` do not provide reliable context isolation.
2.  **`user_id` Parameter is Not a Hard Filter:** In our [Customer Support Chatbot test](use_cases/customer_support_chatbot.py), providing a `user_id` correctly retrieved *some* information for that user but also returned polluted data from other users. This confirms the `user_id` acts as a search "boost," not a strict data partition, making it unsuitable for multi-tenant applications.
3.  **SDK vs. API Discrepancy:** Our initial tests failed repeatedly due to a severe mismatch between the Python SDK and the API documentation. We had to use direct code introspection (`inspect` module) to discover the correct method signatures and data structures, as the documentation was actively misleading.
    -   **`add()` method:** Does not accept a `user_id` parameter. User partitioning must be attempted by placing `user_id` in the `metadata` object.
    -   **`search()` method:** *Does* accept a `user_id` parameter, contradicting the `add()` method's structure.
    -   **Return Objects:** The search results are nested objects (`Result` -> `ResultChunk`) and the final text is stored in `ResultChunk.content`, a structure that is entirely undocumented.

## Path Forward: Build a Superior API

This investigation has been a success. We have not only saved ourselves from building on a flawed platform, but we have also generated a precise list of requirements for our own API. The `your-memory` API must be designed from the ground up to solve these problems.

Our core design principles will be:
-   **First-Class Contexts:** The concept of a "context" or "session" will be a primary, required parameter for all API calls.
-   **Predictable & Strict Filtering:** Data will be strictly partitioned. A query in one context will **never** see data from another.
-   **Developer-First Design:** The API and SDK will be consistent, well-documented, and intuitive from day one.

We are now ready to pivot from testing to building.

---

## Addendum: The Final Decisive Test

Based on feedback from another user suggesting that `containerTags` were effective for data partitioning, we designed one final, definitive test to validate this claim: [`use_cases/tag_partitioning_test.py`](use_cases/tag_partitioning_test.py).

This test created two unique organization tags and added a memory to each. It then performed a search for data while filtering for only **one** of those tags.

### Result: Catastrophic Failure

The test failed completely. The API call, despite being filtered for a specific `org:` tag, returned a flood of completely irrelevant data from the global memory pool and failed to retrieve the specific memory it was queried for.

**This result definitively proves that `containerTags` do not provide reliable context isolation.** It validates our previous findings and allows us to conclude with maximum confidence that `supermemory` is not a suitable platform for our needs.

The investigation phase is now closed.

---
*The original, more optimistic findings are archived below for historical reference.*

### Original Findings (Archived)

# Supermemory: Learnings & Analysis

This document outlines the key findings and insights gathered from our hands-on testing of the `supermemory` Python SDK (v3.0.0a1). The goal of this phase was to benchmark its capabilities against the requirements of a real-world, cross-application agentic workflow.

## Executive Summary

`supermemory` is a powerful and capable memory layer that successfully demonstrated core features essential for building agentic systems. It handled user-specific data partitioning and non-literal, semantic search queries effectively.

However, the Python SDK is let down by a significant discrepancy between its implementation and the official API documentation. Key features are non-obvious to use and required direct code introspection to understand. The service shows great promise, but developers should be prepared for a steep, undocumented learning curve.

## Key Findings

### 1. SDK and API Documentation are Mismatched

This was the most critical finding. Relying on the web-based API documentation and cURL examples led to repeated errors when using the Python SDK. The method signatures and expected parameters in Python are different from what the general documentation suggests.

**Conclusion:** For any developer using the Python SDK, the primary source of truth must be the code itself, not the documentation. Direct introspection using tools like Python's `inspect` module is mandatory.

### 2. Correct Data Partitioning (`user_id`)

-   **The Problem:** The documentation implies `userId` is a top-level parameter for adding and searching memories. The Python SDK's `add()` method, however, repeatedly threw an `unexpected keyword argument 'user_id'` error.
-   **The Solution (Discovered via Introspection):**
    -   When **adding** a memory, the `user_id` must be passed inside the `metadata` dictionary (e.g., `metadata={"user_id": "user_123"}`).
    -   When **searching**, you must build a `filters` object to query against that metadata field (e.g., `filters={"AND": [{"key": "metadata.user_id", "value": "user_123"}]}`).

### 3. Correct Search Result Data Structure

-   **The Problem:** Our initial assumption was that search results would be a list of dictionaries. This caused `'Result' object has no attribute 'get'` errors. Further guessing at attribute names like `.content` and `.document` also failed.
-   **The Solution (Discovered via Introspection):**
    -   The `search.execute()` method returns a list of `Result` objects.
    -   Each `Result` object contains a list of `ResultChunk` objects in its `.chunks` attribute.
    -   The actual text content of a memory is stored in the **`.content`** attribute of each `ResultChunk` object.
    -   The correct way to extract all text from a response is with a nested list comprehension: `[chunk.content for mem in response.results for chunk in mem.chunks]`.

### 4. Performance Analysis

-   **User Partitioning (✅ Pass):** Once we discovered the correct filtering method, the feature worked flawlessly. Searches for `conner_pope`'s data correctly excluded all data from `jonathan_p`. This is a huge success.
-   **Non-Literal Search (✅ Pass):** This was the most impressive result. The system successfully connected a vague, human-like query (`"any update on that sign-in problem?"`) to a specific, structured memory about a Linear ticket (`"I have created a ticket... The ticket ID is LIN-9662."`). This validates their claims of having a strong semantic search capability beyond simple keywords.
-   **Potential Issue - Result Duplication:** The search results often contained multiple identical chunks of the same memory. An application built on this would need to perform a de-duplication step on the results to avoid feeding redundant context to an LLM.

## Final Conclusion

`supermemory` is a viable and powerful tool for the agentic use cases we are targeting. It solved the core challenges of partitioned memory and semantic, cross-application context retrieval that we set out to test.

Our primary contribution in this phase has been **de-risking the technology and documenting its actual usage patterns.** We have effectively written the missing "how-to" guide for their Python SDK, which will be invaluable as we move into the next phase: designing and building our own API. We now have a clear benchmark to beat. 