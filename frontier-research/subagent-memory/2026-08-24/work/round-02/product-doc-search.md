# Product and Runtime Documentation Search

Searches were executed on 2026-08-23 UTC. Result counts are not exhaustive. Reader-facing product facts require opening the exact page and, where consequential, fixed-version repository inspection.

## Query set 1

1. `site:docs.anthropic.com Claude Code subagents memory`
2. `site:docs.langchain.com langgraph subagents memory store persistence`
3. `site:microsoft.github.io/autogen memory multi-agent state save load`
4. `site:google.github.io/adk-docs multi-agent memory session state`

High-value results:

- AutoGen managing state — <https://microsoft.github.io/autogen/dev/user-guide/agentchat-user-guide/tutorial/state.html>
- AutoGen Memory and RAG — <https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/memory.html>
- LangGraph persistence — <https://docs.langchain.com/oss/python/langgraph/persistence>
- LangGraph subgraph persistence — <https://docs.langchain.com/oss/python/langgraph/use-subgraphs>

The Anthropic-domain variant and Google ADK query did not surface an adequate direct result in this call, so alternate canonical domains were searched next.

## Query set 2

1. `site:code.claude.com/docs subagents memory Claude Code`
2. `site:google.github.io/adk-docs sessions memory multi-agent state`
3. `site:docs.crewai.com memory multi-agent flows shared state`
4. `site:docs.langchain.com deepagents subagents memory context namespacing`

High-value results:

- Claude Code custom subagents — <https://code.claude.com/docs/en/sub-agents>
- Claude Code worktrees — <https://code.claude.com/docs/en/worktrees>
- Claude Code memory — <https://code.claude.com/docs/en/memory>
- Deep Agents context engineering — <https://docs.langchain.com/oss/python/deepagents/context-engineering>
- Deep Agents memory — <https://docs.langchain.com/oss/python/deepagents/memory>

Claude Code documentation exposes fresh isolated subagent context, delegation summaries, inherited project memory/instructions, per-subagent persistent memory scopes (`user`, `project`, `local`), parent permission precedence and optional worktree isolation. Deep Agents exposes parent runtime-context propagation, per-subagent namespacing, filesystem-mediated result transfer and backend-routed long-term memory.

## Query set 3

1. `site:google.github.io/adk-docs "Memory Service" agents session state`
2. `site:docs.crewai.com "Memory" agents crew shared state`
3. `site:openai.github.io/openai-agents-python/sandbox/memory subagents memory generate`
4. `site:docs.langchain.com/oss/python/deepagents subagents context memory`

High-value results:

- OpenAI Agents SDK sandbox memory — <https://openai.github.io/openai-agents-python/sandbox/memory/>
- Deep Agents subagents — <https://docs.langchain.com/oss/python/deepagents/subagents>
- LangChain supervisor-style subagents — <https://docs.langchain.com/oss/python/langchain/multi-agent/subagents>

OpenAI's current SDK documentation distinguishes conversation Session from sandbox memory, supports memory layouts independent of agent name, and allows internal agents/subagents to read but not generate memory. LangChain's supervisor pattern documents stateless subagents with the main agent holding conversation memory, while LangGraph subgraphs separately expose per-invocation, per-thread and stateless persistence modes.

## Map impact

The product evidence created a new first-order branch: **Subagent-local persistence and identity**. Spawn-time inheritance does not determine whether a named Subagent retains state across invocations, threads, sessions, projects or users. That retention choice changes concurrency, privacy, reuse and cleanup independently of delegation packet construction.
