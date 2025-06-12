# Agentic Memory: Your Memory

This repository chronicles the journey of building a robust, cross-application memory layer for AI agents. The goal is to create a service that allows AI systems (like those in Slack, Linear, or development environments) to share a consistent, persistent memory, enabling more powerful and context-aware agentic workflows.

## The Problem

Modern AI agents are powerful but forgetful. A conversation in one application is completely isolated from another. To build truly helpful agents that can automate complex tasks (e.g., "create a bug report from that Slack conversation and assign it to the right engineer"), we need a reliable memory layer that is:
- **Persistent:** Remembers information across sessions.
- **Contextually Isolated:** Can separate memories from different users, projects, or applications (e.g., `user_A`'s data should never leak into `user_B`'s queries).
- **Semantically Searchable:** Can retrieve information based on natural language and intent, not just keywords.

## Phase 1: Benchmarking `supermemory`

Our initial phase involved a deep, hands-on investigation of a commercial memory-as-a-service platform, [`supermemory`](https://supermemory.ai/). We developed a series of [industrial use-case simulations](use_cases/) to test its capabilities against our requirements.

### Key Findings & Conclusion

Our detailed findings are documented in [`supermemory_learnings.md`](supermemory_learnings.md). The executive summary is:

**`supermemory` is not a suitable backend for building reliable, multi-context agentic systems.**

While the service has a powerful semantic search engine, our tests revealed critical flaws in its API and SDK that prevent robust data isolation. We found that its filtering mechanisms act as weak "boosts" rather than strict partitions, leading to severe context pollution and data leakage between different users and sessions in our tests.

## Phase 2: Building `your-memory`

Armed with the hard-won insights from our research, we are now moving to Phase 2: **designing and building our own superior memory API.**

Our core design principles, directly addressing the failures we identified, are:
1.  **First-Class Contexts:** The concept of a "context" or "session" will be a primary, required parameter for all API calls.
2.  **Predictable & Strict Filtering:** Data will be strictly partitioned. A query in one context will **never** see data from another.
3.  **Developer-First Design:** The API and SDK will be consistent, well-documented, and intuitive from day one.

This repository will track the development of this new service.
