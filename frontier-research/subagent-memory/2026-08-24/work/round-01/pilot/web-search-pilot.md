# Web Search Pilot Snapshot

Search-engine result counts are not exposed and the returned lists are not exhaustive. These searches are discovery leads only; technical claims require reopening the primary paper, official documentation, or fixed repository version.

## Paper and repository terminology pilot

Executed around `2026-08-23T16:31Z`:

1. `site:arxiv.org multi-agent shared memory LLM agents 2025 2026`
2. `site:arxiv.org hierarchical multi-agent memory agent handoff 2025 2026`
3. `site:github.com multi-agent shared memory LLM agents`
4. `site:github.com subagent memory agent handoff shared state`

Material leads returned included:

- Governed Shared Memory for Multi-Agent LLM Systems — <https://arxiv.org/abs/2606.24535>
- Collaborative Memory — <https://arxiv.org/abs/2505.18279>
- Shared Selective Persistent Memory — <https://arxiv.org/abs/2607.09493>
- Intrinsic Memory Agents — <https://arxiv.org/abs/2508.08997>
- `plur-ai/plur` — <https://github.com/plur-ai/plur>
- `MehulG/memX` — <https://github.com/MehulG/memX>
- `ZenSystemAI/Zengram` — <https://github.com/ZenSystemAI/Zengram>
- `caura-ai/caura` — <https://github.com/caura-ai/caura>
- `skynetcmd/m3-memory` — <https://github.com/skynetcmd/m3-memory>
- `dan-calin/shared-agent-memory` — <https://github.com/dan-calin/shared-agent-memory>
- Microsoft UFO Blackboard documentation — <https://github.com/microsoft/UFO/blob/main/documents/docs/infrastructure/agents/design/memory.md>
- `raia-live/amfs` — <https://github.com/raia-live/amfs>

## Benchmark and runtime-state pilot

Executed around `2026-08-23T16:32Z`:

1. `site:arxiv.org multi-agent memory benchmark LLM agents shared memory`
2. `site:arxiv.org collective memory multi-agent LLM experience sharing`
3. `site:docs.langchain.com multi-agent subagent memory persistence store`
4. `site:openai.github.io/openai-agents-python handoffs sessions memory agents as tools`

Material leads returned included:

- GateMem — <https://arxiv.org/abs/2606.18829>
- GroupMemBench — <https://arxiv.org/abs/2605.14498>
- MIRIX — <https://arxiv.org/abs/2507.07957>
- OpenAI Agents SDK handoffs — <https://openai.github.io/openai-agents-python/handoffs/>
- OpenAI Agents SDK context management — <https://openai.github.io/openai-agents-python/context/>
- OpenAI Agents SDK sandbox memory — <https://openai.github.io/openai-agents-python/sandbox/memory/>

The OpenAI search exposed a mechanism distinction that changed the pilot map: a handoff may transfer filtered history while an agent-as-tool invocation may retain manager control and share application state unless explicitly isolated. Sandbox memory separately allows read-only internal agents that do not generate new long-term memories. These are leads for fixed-version repository inspection, not yet published findings.

## Official OpenAI-domain follow-up

Executed around `2026-08-23T16:35Z`:

- `subagent memory sandbox agents SDK site:developers.openai.com`

The official developer index exposed current multi-agent and sandbox-agent material but did not itself fully document the memory semantics found in the SDK reference. The OpenAI project slice therefore requires fixed-version inspection of `openai/openai-agents-python` plus official-domain status checks.
