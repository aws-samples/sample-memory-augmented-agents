# Agents That Remember: Context Windows, Summaries, and Persistent Sessions

*Give agents short-term and long-term memory so they stay coherent across a conversation and recall you between sessions*

---

This is the eighth post in our series on [AWS Prescriptive Guidance for Agentic AI Patterns](https://docs.aws.amazon.com/prescriptive-guidance/latest/agentic-ai-patterns/). Each post focuses on the concepts and patterns behind a single agent type, paired with a [hands-on sample on GitHub](README.md).

## Introduction

By default, a large language model has no memory with each request being independent. The reason a chatbot *seems* to remember earlier turns is that the application quietly re-sends the conversation history with every message. That works until the history gets too big, and it disappears entirely the moment the session ends.

A memory-augmented agent treats memory as a first-class concern. It carries recent context forward, decides what older context to keep when space runs short, and can persist what it learns across sessions. That shift, from a reactive tool to something that accumulates context, is what makes an agent feel like a collaborator rather than a vending machine.

By the end of this post, you'll understand:
- Why LLMs are stateless and what that forces applications to do
- The difference between short-term and long-term memory
- Three memory strategies: sliding window, summarization, and persistent sessions
- When each kind of memory is worth its cost

---

## The Road to Agent Memory: A Brief History

### The stateless prompt

Early LLM applications had exactly one place to put context: the prompt. To make a model "remember," you concatenated the whole conversation and re-sent it every turn. Simple, but bounded by the **context window**, the maximum number of tokens the model can read at once. Exceed it and the request fails, so long or open-ended conversations needed a strategy for what to keep.

### Managing the window

That pressure produced the first real memory techniques, all about fitting the right context into a finite window. A **sliding window** keeps the most recent messages and drops the oldest. **Summarization** compresses old turns into a short recap so their key facts survive without their full token cost. Both buy coherence within a single session by being deliberate about what the model sees.

### Long-term and retrievable memory

Keeping context across *sessions* required storing it outside the prompt entirely. Two different jobs emerged: durably persisting raw state that you fetch by key, and semantic recall. Those map to different primitives. On AWS, [Amazon DynamoDB](https://aws.amazon.com/dynamodb/) is a common fit for durable state, while semantic recall is typically backed by a vector index. Sitting on top of these primitives, [Amazon Bedrock AgentCore Memory](https://aws.amazon.com/blogs/machine-learning/amazon-bedrock-agentcore-memory-building-context-aware-agents/) packages the whole pattern into a managed service: it stores raw events, extracts long-term facts and preferences, and serves them back via semantic retrieval, so you're not wiring those pieces together yourself.

--- 
## Short-Term vs. Long-Term Memory

<img src="images/memory-augmented-agents.png" width="600" alt="Diagram of a memory-augmented agent: input triggers retrieval of short-term and long-term memory, the LLM reasons with that context to produce output, and new information is written back to memory." />

Memory-augmented agents draw the same distinction people do.

**Short-term memory** is the working context of the current session, i.e. the recent dialogue and task state. It lives close to the model (in or near the prompt) and is fast to access, but bounded by the context window. Sliding windows and summarization are short-term strategies and don't solve the problem of persistence.

**Long-term memory** persists beyond the session. It lives in external storage and is retrieved when relevant, then injected into the prompt. It's how an agent greets you by name on day thirty, not just within one chat.

A capable agent uses both: short-term memory for the thread of the current conversation, long-term memory for everything it should carry across sessions. The two also interact, a long conversation's summary might be promoted into long-term storage when the session ends. Deciding what graduates from short-term to long-term is itself a design choice. Store too much and retrieval gets noisy and expensive; store too little and the agent forgets things that mattered.

---

## Three Strategies


| Strategy | Scope | Keeps | Trade-off |
|----------|-------|-------|-----------|
| **Sliding window** | Short-term | The most recent N messages | Forgets anything older |
| **Summarization** | Short-term | A compressed recap + recent messages | Extra model calls; loses verbatim detail |
| **Persistent sessions** | Long-term | Full state saved across restarts | Needs external storage |

A **sliding window** is the simplest: cap the history at the last N messages and let the rest fall off. Perfect when only recent context matters, which covers most chat. **Summarization** is smarter about the past. Instead of dropping old turns, it folds them into a running summary, so an early fact survives a long conversation at the cost of the model calls that produce the summary. **Persistent sessions** step outside the run entirely: state is written to storage under a session ID and reloaded next time, so the agent remembers across restarts and even across days.

These three can be used together. A production assistant might run a sliding window for the live exchange, summarize older turns as they age out, and persist the running summary to a database keyed by user. The good news for builders is that a framework like the [Strands Agents SDK](https://strandsagents.com/) treats each as a swappable component: you choose a conversation manager for the in-session strategy and a session manager for persistence, and the agent code barely changes. That makes it cheap to start with a sliding window and graduate to persistent, retrievable memory only when the use case demands it.

---

## When to Use Memory-Augmented Agents

Add memory when continuity, personalization, or learning from the past matters.

| Use Case | Example |
|----------|---------|
| **Conversational copilots** | Assistants that remember a user's preferences |
| **Coding agents** | Tracking changes across a codebase over time |
| **Adaptive workflows** | Agents that adjust based on task history |
| **Digital twins** | Systems that evolve as they accumulate knowledge |
| **Research agents** | Avoiding redundant retrievals by remembering what's been seen |

### Memory Isn't Free

Memory isn't free. It adds storage, retrieval latency, and a real privacy question. You're now persisting user data, which carries handling and retention obligations. For one-shot work like classification, translation, or a self-contained question, a stateless agent is simpler, cheaper, and has nothing to protect.

---

## What's Next

You now understand why LLMs are stateless, the difference between short-term and long-term memory, and the three strategies for giving an agent continuity. The natural next step is to see them run. The **[companion sample](README.md)** builds sliding-window, summarizing, and persistent-session agents.

Memory rounds out the capabilities we've given an agent. Thus far, we've enabled reasoning, tools, voice, and now state. The remaining question is how to be confident in what we've built before letting it loose. In the [next post](https://github.com/aws-samples/sample-simulation-testbed-agents/blob/main/Practice%20Worlds%20-%20Simulation%20and%20Test-Bed%20Agents.md), we'll put agents in simulated environments using sandboxes and test-beds where they can act, and fail, without consequence.

---

## Resources

- [Companion sample: Memory-Augmented Agents](README.md)
- [AWS Prescriptive Guidance - Memory-augmented agents](https://docs.aws.amazon.com/prescriptive-guidance/latest/agentic-ai-patterns/memory-augmented-agents.html)
- [Amazon Bedrock AgentCore Memory](https://aws.amazon.com/blogs/machine-learning/amazon-bedrock-agentcore-memory-building-context-aware-agents/)
- [Strands Agents Documentation](https://strandsagents.com/)
- [Amazon Bedrock User Guide](https://docs.aws.amazon.com/bedrock/latest/userguide/what-is-bedrock.html)

---

**Tim Sitze** is a Solutions Architect at Amazon Web Services, where he works with cybersecurity ISVs to design and scale their products on AWS. He specializes in security, AI/ML, IoT and data platform architectures, and has partnered on workloads spanning identity threat intelligence, agentic AI, and cloud-native security operations. Tim is based in the Washington, D.C. area.  
