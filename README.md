# 🤖 Asynchronous Local LLM / SLM Performance Benchmarking Agent

An optimization-focused profiling framework and agentic evaluation engine designed to benchmark open-source Small Language Models (SLMs) running locally via **Ollama**. This architecture isolates and tracks streaming telemetry configurations (TTFT, throughput rates) while programmatically auditing output token alignment against rigid schema profiles.

## 🏗️ System Architecture & Execution Sequence

```text
[Orchestration Suite] (Load prompts configurations / Loop Iterations)
        │
        ▼ (Asynchronous Streaming Sockets Client)
[AsyncLLMProfiler] ──► Query Local Ollama Port (11434)
        │
        ├──► [Success] ──► Parse Byte-Stream Increments for Latency Telemetry
        └──► [Timeout] ──► Gracefully Fallback to Resilient Simulation Engine
        │
        ▼ (Structural Verification Rules Engine)
[ResponseValidator] ──► Sanitize & Regex Extract JSON Data Matches
        │
        ▼ (Rich Text Layout UI Manager)
[Final Terminal Assessment Matrix Reporting Grid]
```

## 🛠️ Key Technical Implementations
* **Low-Level Socket Telemetry Profiling:** Intercepts live streaming text tokens over asynchronous HTTP connections via `httpx`. Captures precise Time-to-First-Token (TTFT) and token generation throughput metrics before payloads ever enter memory.
* **Resilient Non-Blocking Fault Tolerances:** Features a defensive dual-mode networking runtime. Gracefully falls-forward into a simulated metric generator if communication with local GPU clusters fails, making the repository completely portable and instantly runnable out-of-the-box.
* **Stateful Response Sanitization Evals:** Employs static regular expression token isolation engines to strip text anomalies (such as model conversational fluff and markdown code block wrappers) to parse hidden JSON shapes flawlessly.
* **Automated Regression Guardrails:** Integrates asynchronous validation testing framework (`pytest-asyncio`) bound to continuous **GitHub Actions crons** to evaluate environment stability entirely in the background.
