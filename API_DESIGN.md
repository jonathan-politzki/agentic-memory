# Agentic Memory API - Design Document v1

This document outlines the initial design for a robust, developer-first Agentic Memory API. The design is heavily influenced by the limitations and shortcomings discovered during our evaluation of the `supermemory` API.

## Core Philosophy

1.  **Context is King:** The API's primary function is to manage memories *within specific contexts*. A context can be a user, a project, a Slack thread, or any other partition the developer defines. Global, context-less memories should not be the default.
2.  **Developer Experience is Paramount:** The API and its accompanying SDKs must be intuitive, consistent, and well-documented. Common operations should be simple, and complex operations should be possible without ambiguity. "Failing silently" is not acceptable.
3.  **Predictable & Transparent:** The structure of requests and responses should be consistent across the API. The developer should never have to guess where a piece of data is located in a response object.

---

## 1. Core Objects

### 1.1. `Memory`
The fundamental unit of data.

*   `id`: Unique identifier for the memory.
*   `content`: The text or data of the memory.
*   `context_id`: **(Required)** The ID of the context this memory belongs to.
*   `metadata`: A simple key-value store for additional, filterable data.
*   `created_at`: Timestamp.

### 1.2. `Context`
A logical partition for memories. This is the core concept that was missing from `supermemory`.

*   `id`: Unique identifier for the context (e.g., "user-123", "project-abc").
*   `owner_id`: The user or entity that owns this context.
*   `name`: A human-readable name for the context (e.g., "Slack Thread #general").
*   `created_at`: Timestamp.

---

## 2. API Endpoints

The base URL will be `/api/v1`.

### 2.1. Memories

#### `POST /memories`
Adds a new memory.

**Request Body:**
```json
{
  "content": "This is a new memory.",
  "context_id": "user-123" // Required
  "metadata": {
    "source": "slack",
    "channel": "#random"
  }
}
```

**Response:** `201 Created` with the full `Memory` object.

#### `POST /search`
Searches for memories, but always within a specific context.

**Request Body:**
```json
{
  "query": "What did we talk about?",
  "context_id": "user-123", // Required
  "filters": { // Optional, simple filters
    "source": "slack"
  }
}
```
**Response:** `200 OK` with a list of `Memory` objects.

### 2.2. Contexts

#### `POST /contexts`
Creates a new context (e.g., when a new user signs up).

**Request Body:**
```json
{
  "id": "user-456", // Optional, can be provided by user or generated
  "name": "New User's Memory Space"
}
```
**Response:** `201 Created` with the full `Context` object.

#### `GET /contexts/{context_id}`
Retrieves information about a specific context.

**Response:** `200 OK` with the `Context` object.

---

## 3. Key Improvements Over `supermemory`

*   **First-Class Contexts:** The `context_id` is a required, top-level parameter for all memory operations, making partitioning explicit and reliable.
*   **Simplified Filtering:** Metadata filters are simple key-value pairs, not complex JSON strings.
*   **Consistent SDK:** The official Python SDK will be a 1:1 match for the API. If a parameter is in the API, it will be a named argument in the SDK function. No more guessing.
*   **No Silent Failures:** If a required parameter is missing or an invalid one is provided, the API will return a descriptive `4xx` error.

This initial design directly addresses the major pain points we discovered. We can now begin to flesh out the details of the implementation, starting with the server framework and database schema. 