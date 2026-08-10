# Query log

| ID | Stage | Provider | Time (UTC) | Results | Lanes | Exact query |
|---|---|---|---|---:|---|---|
| Q0001 | pilot | arxiv | 2026-08-10T03:37:18Z | 100 | paper, mechanism | "agent memory" OR "LLM agent memory" OR "long-term memory agents" |
| Q0002 | pilot | semantic-scholar | 2026-08-10T03:37:18Z | 0 | paper | agent memory \| long-term memory LLM agent |
| Q0003 | pilot | crossref | 2026-08-10T03:37:57Z | 100 | paper, history | agent memory large language model |
| Q0004 | pilot | github-search | 2026-08-10T03:43:40Z | 100 | github, product | agent memory in:name,description,readme stars:>=5 archived:false |
| Q0005 | discover | arxiv | 2026-08-10T03:51:01Z | 100 | paper, mechanism | "agent memory" OR "LLM agent memory" OR "long-term memory agents" |
| Q0006 | discover | arxiv | 2026-08-10T03:51:08Z | 100 | paper, mechanism | memory AND ("large language model" OR LLM) AND (agent OR agentic) |
| Q0007 | discover | arxiv | 2026-08-10T03:51:16Z | 100 | paper, mechanism, cost | memory AND (write OR storage OR consolidate OR consolidation OR forgetting OR update) AND (agent OR LLM) |
| Q0008 | discover | arxiv | 2026-08-10T03:51:24Z | 100 | paper, mechanism, history | ("episodic memory" OR "semantic memory" OR "procedural memory" OR "experience memory" OR "skill memory") AND (agent OR LLM) |
| Q0009 | discover | arxiv | 2026-08-10T03:51:46Z | 100 | paper, mechanism | memory AND (graph OR temporal OR structured OR hierarchy OR knowledge) AND (agent OR LLM) |
| Q0010 | discover | arxiv | 2026-08-10T03:51:52Z | 100 | paper, benchmark | (benchmark OR evaluation) AND memory AND (agent OR LLM) |
| Q0011 | discover | arxiv | 2026-08-10T03:51:59Z | 100 | paper, mechanism | ("multi-agent" OR multiagent OR "shared memory") AND memory AND (LLM OR agent) |
| Q0012 | discover | arxiv | 2026-08-10T03:52:10Z | 100 | paper, mechanism | (tool OR action OR embodied OR web) AND agent AND memory AND (LLM OR "large language model") |
| Q0013 | discover | arxiv | 2026-08-10T03:52:51Z | 100 | paper, security, negative | (poisoning OR privacy OR extraction OR stale OR deletion OR conflict OR security) AND memory AND (agent OR LLM) |
| Q0014 | discover | arxiv | 2026-08-10T03:52:58Z | 100 | paper, mechanism, cost | ("memory system" OR "memory OS" OR "memory architecture" OR "memory management") AND (agent OR LLM) |
| Q0015 | discover | arxiv | 2026-08-10T03:53:05Z | 100 | paper, mechanism | memory AND (agent OR agentic) AND (LLM OR "large language model") |
| Q0016 | discover | arxiv | 2026-08-10T03:53:12Z | 100 | paper, negative, mechanism | ("long context" OR stateless OR RAG OR retrieval) AND (agent OR LLM) AND memory |
| Q0017 | discover | arxiv | 2026-08-10T03:53:33Z | 100 | paper, mechanism, product | (personalization OR conversational OR assistant) AND "long-term memory" AND (LLM OR agent) |
| Q0018 | discover | arxiv | 2026-08-10T03:53:41Z | 100 | paper, mechanism | (multimodal OR embodied OR vision) AND agent AND memory AND (LLM OR "large language model") |
| Q0019 | discover | arxiv | 2026-08-10T03:53:49Z | 100 | paper, mechanism, history | (reflection OR self-improving OR "self-evolving" OR learning) AND agent AND memory AND (LLM OR "large language model") |
| Q0020 | discover | arxiv | 2026-08-10T03:53:56Z | 100 | paper, mechanism | ("world model" OR state) AND agent AND memory AND (LLM OR "large language model") |
| Q0021 | discover | github-search | 2026-08-10T03:55:00Z | 100 | github | "agent memory" in:name,description stars:>=5 archived:false |
| Q0022 | discover | github-search | 2026-08-10T03:55:00Z | 100 | github | memory in:name,description topic:ai-agents stars:>=5 archived:false |
| Q0023 | discover | github-search | 2026-08-10T03:55:00Z | 100 | github | memory in:name,description topic:llm stars:>=5 archived:false |
| Q0024 | discover | github-search | 2026-08-10T03:55:03Z | 100 | github | "long-term memory" in:name,description stars:>=5 archived:false |
| Q0025 | discover | github-search | 2026-08-10T03:55:01Z | 100 | github | memory in:name,description stars:>=1000 archived:false |
| Q0026 | discover | github-search | 2026-08-10T03:55:22Z | 100 | github | memory in:name,description stars:>=100 archived:false |
| Q0027 | discover | github-search | 2026-08-10T03:55:23Z | 100 | github | memory in:name,description stars:>=10 archived:false |
| Q0028 | discover | github-search | 2026-08-10T03:55:23Z | 100 | github | agentmemory in:name,description,readme stars:>=5 archived:false |
| Q0029 | discover | github-search | 2026-08-10T03:55:24Z | 100 | github, mechanism | "episodic memory" in:name,description,readme archived:false |
| Q0030 | discover | github-search | 2026-08-10T03:55:23Z | 100 | github, mechanism | "semantic memory" in:name,description,readme archived:false |
| Q0031 | discover | github-search | 2026-08-10T03:55:43Z | 100 | github, mechanism | "procedural memory" in:name,description,readme archived:false |
| Q0032 | discover | github-search | 2026-08-10T03:55:41Z | 100 | github, benchmark | "memory benchmark" agent in:name,description,readme archived:false |
| Q0033 | discover | github-search | 2026-08-10T03:55:41Z | 100 | github, mechanism | memory graph agent in:name,description stars:>=5 archived:false |
| Q0034 | discover | github-search | 2026-08-10T03:55:41Z | 100 | github, mechanism | memory mcp agent in:name,description stars:>=5 archived:false |
| Q0035 | discover | github-search | 2026-08-10T03:55:42Z | 100 | github, mechanism | memory ai-agent in:name,description stars:>=5 archived:false |
| Q0036 | discover | github-search | 2026-08-10T03:56:03Z | 100 | github, security, negative | memory poisoning agent in:name,description,readme archived:false |
| Q0037 | discover | github-search | 2026-08-10T03:56:02Z | 100 | github, mechanism | memory multi-agent in:name,description,readme archived:false |
| Q0038 | discover | github-search | 2026-08-10T03:56:04Z | 100 | github, mechanism | memory multimodal agent in:name,description,readme archived:false |
| Q0039 | discover | github-search | 2026-08-10T03:56:02Z | 100 | github, mechanism | memory rag agent in:name,description stars:>=10 archived:false |
| Q0040 | discover | github-search | 2026-08-10T03:55:59Z | 15 | github, product, mechanism | "context engine" memory in:name,description stars:>=10 archived:false |
| Q0041 | discover | crossref | 2026-08-10T03:56:27Z | 100 | paper, mechanism | episodic semantic procedural memory LLM agent |
| Q0042 | discover | crossref | 2026-08-10T03:56:28Z | 100 | paper, history | long term memory large language model agent |
| Q0043 | discover | crossref | 2026-08-10T03:56:30Z | 100 | paper, benchmark | memory benchmark autonomous agent |
| Q0044 | discover | crossref | 2026-08-10T03:56:28Z | 100 | paper, mechanism, cost | memory management LLM agent |
| Q0045 | discover | crossref | 2026-08-10T03:56:31Z | 100 | paper, security, negative | memory poisoning AI agent |
| Q0046 | discover | arxiv | 2026-08-10T03:56:54Z | 100 | paper, mechanism | memory AND ("large language model" OR LLM) AND (agent OR agentic) |
| Q0047 | discover | arxiv | 2026-08-10T03:56:55Z | 100 | paper, mechanism | memory AND (graph OR temporal OR structured OR hierarchy OR knowledge) AND (agent OR LLM) |
| Q0048 | discover | github-search | 2026-08-10T03:56:55Z | 100 | github, mechanism, product | "memory layer" agent in:name,description stars:>=5 archived:false |
| Q0049 | discover | arxiv | 2026-08-10T03:57:40Z | 100 | paper, history, mechanism | memory AND (agent OR "large language model" OR LLM OR "generative agents") |
| Q0050 | discover | arxiv | 2026-08-10T03:57:40Z | 100 | paper, history, mechanism | "generative agents" OR Reflexion OR MemGPT OR Voyager OR "episodic memory" |
| Q0051 | discover | arxiv | 2026-08-10T03:57:40Z | 100 | paper, history, mechanism | memory AND (agent OR agentic) AND (LLM OR "large language model") |
| Q0052 | discover | arxiv | 2026-08-10T03:57:39Z | 100 | paper, benchmark | (benchmark OR evaluation) AND memory AND (agent OR LLM) |
| Q0053 | discover | arxiv | 2026-08-10T03:57:59Z | 100 | paper, mechanism | memory AND (graph OR temporal OR structured OR knowledge) AND (agent OR LLM) |
| Q0054 | discover | arxiv | 2026-08-10T03:58:07Z | 100 | paper, mechanism, history | (reflection OR experience OR self-improving OR learning) AND memory AND (agent OR LLM) |
| Q0055 | discover | arxiv | 2026-08-10T03:58:13Z | 100 | paper, mechanism | memory AND (agent OR agentic) AND (LLM OR "large language model") |
| Q0056 | discover | arxiv | 2026-08-10T03:58:20Z | 100 | paper, benchmark, security, negative | (benchmark OR poisoning OR privacy OR stale OR deletion OR security) AND memory AND (agent OR LLM) |
| Q0057 | gap-fill | arxiv | 2026-08-10T05:03:48Z | 82 | paper, mechanism, cost | ("agent memory" OR "LLM agent memory") AND (database OR storage OR index OR transaction OR bitemporal) |
| Q0058 | gap-fill | arxiv | 2026-08-10T05:03:56Z | 4 | paper, mechanism, benchmark | ("coding agent" OR "software agent") AND ("project memory" OR "session memory" OR "decision log" OR "repository memory") |
| Q0059 | gap-fill | arxiv | 2026-08-10T05:04:04Z | 164 | paper, benchmark, negative, cost | ("agent memory" OR "LLM memory") AND (benchmark OR evaluation) AND (update OR forgetting OR action OR temporal OR contamination OR cost) |
| Q0060 | gap-fill | arxiv | 2026-08-10T05:04:15Z | 160 | paper, mechanism, negative, security, cost | ("agent memory" OR "long-term memory") AND (admission OR consolidation OR forgetting OR revoke OR rollback OR contradiction OR stale) |
| Q0061 | gap-fill | arxiv | 2026-08-10T05:04:26Z | 123 | paper, security, negative | ("agent memory" OR "persistent memory") AND (poisoning OR provenance OR authority OR leakage OR deletion OR repair) |
| Q0062 | gap-fill | arxiv | 2026-08-10T05:04:38Z | 154 | paper, mechanism, cost | ("agent memory" OR "LLM agent memory") AND (latency OR token OR storage OR cost OR energy OR "write amplification") |
| Q0063 | gap-fill | github-search | 2026-08-10T05:04:48Z | 67 | github, mechanism, product | agent memory graph temporal |
| Q0064 | gap-fill | github-search | 2026-08-10T05:04:57Z | 200 | github, mechanism, product | coding agent project memory |
| Q0065 | gap-fill | github-search | 2026-08-10T05:05:09Z | 5 | github, benchmark, security, negative | agent memory security benchmark |
| Q0066 | gap-fill | github-search | 2026-08-10T05:05:15Z | 6 | github, standards, product | agent memory protocol portable MCP |
| Q0067 | deep-focus | arxiv | 2026-08-10T05:05:25Z | 190 | paper, mechanism, negative, cost | ("agent memory" OR "long-term memory") AND ("active retrieval" OR navigation OR ranking OR selection) |
| Q0068 | deep-focus | arxiv | 2026-08-10T05:05:35Z | 56 | paper, mechanism, security | ("multi-agent" OR "multi agent") AND ("shared memory" OR "distributed memory" OR "memory protocol") |
| Q0069 | deep-focus | github-search | 2026-08-10T05:05:43Z | 200 | github, product | "agent memory" |
| Q0070 | verify | crossref | 2026-08-10T05:06:45Z | 200 | paper, benchmark | agent memory benchmark long-term memory agents |
| Q0071 | verify | arxiv | 2026-08-10T05:06:54Z | 200 | paper, history, mechanism | ("MemGPT" OR "MemoryBank" OR "Generative Agents" OR "Voyager" OR "Reflexion" OR "Think-in-Memory" OR "Memory Gym") |
| Q0072 | adversarial | arxiv | 2026-08-10T05:07:11Z | 200 | paper, negative, benchmark, mechanism | ("agent memory" OR "LLM memory") AND ("no memory" OR "long context" OR BM25 OR failure OR degradation OR ablation) |
| Q0073 | adversarial | arxiv | 2026-08-10T05:07:23Z | 107 | paper, security, negative | ("agent memory" OR "persistent memory") AND (attack OR poisoning OR backdoor OR privacy OR deletion OR leakage) |
| Q0074 | adversarial | github-search | 2026-08-10T05:07:30Z | 2 | github, benchmark, security, negative | agent memory poisoning attack benchmark |
| STD-Q001 | adversarial | web-search | 2026-08-10T05:45:00Z | None | adoption | "Universal Memory Protocol" production deployment case study |
| STD-Q002 | adversarial | web-search | 2026-08-10T05:45:00Z | None | adoption | "Open Memory Protocol" production deployment case study AI |
| STD-Q003 | adversarial | web-search | 2026-08-10T05:45:00Z | None | adoption | "Agent Memory Protocol" independent implementation deployment |
| STD-Q004 | adversarial | web-search | 2026-08-10T05:45:00Z | None | adoption | "MemTools" independent reproduction agent memory |
| STD-Q005 | verify | GitHub Search API | 2026-08-10T05:46:23Z | 103 | standards | "agent memory protocol" in:name,description,readme |
| STD-Q006 | verify | GitHub Search API | 2026-08-10T05:46:25Z | 18 | standards | "open memory protocol" in:name,description,readme |
| STD-Q007 | adversarial | GitHub Code Search API | 2026-08-10T05:46:27Z | 4 | adoption | "agentmemoryprotocol.io" -repo:agentmemoryprotocol/agentmemoryprotocol |
| STD-Q008 | adversarial | GitHub Code Search API | 2026-08-10T05:46:28Z | 2 | adoption | "smriti-memcore/amp" -repo:smriti-memcore/amp |
| STD-Q009 | adversarial | GitHub Code Search API | 2026-08-10T05:46:29Z | 0 | adoption | "amp.batch_encode" -repo:smriti-memcore/amp |
| STD-Q010 | adversarial | GitHub Code Search API | 2026-08-10T05:46:31Z | 0 | adoption | "openmemoryprotocol.com" -repo:EB-DevTech/Open-Memory-Protocol |
| STD-Q011 | adversarial | GitHub Code Search API | 2026-08-10T05:46:33Z | 52 | adoption | "github.com/SMJAI/open-memory-protocol" -repo:SMJAI/open-memory-protocol |
| STD-Q012 | adversarial | GitHub Code Search API | 2026-08-10T05:46:37Z | 3 | adoption | "@universalmemoryprotocol/core" -repo:edihasaj/universal-memory-protocol |
| STD-Q013 | adversarial | GitHub Code Search API | 2026-08-10T05:46:38Z | 3 | adoption | "@saihm/mcp-server" -repo:SAIHM-Admin/saihm-mcp |
| STD-Q014 | verify | GitHub REST API | 2026-08-10T04:45:00Z | 9 | standards | GET repos/{owner}/{repo}; commits/{ref}; contributors; releases; tags for selected protocol repositories |
| STD-Q015 | adversarial | npm registry API | 2026-08-10T04:45:00Z | 2 | adoption | @universalmemoryprotocol/core and @saihm/mcp-server metadata; point last-week downloads 2026-08-02..2026-08-08 |
| STD-Q016 | verify | direct primary-source open | 2026-08-10T05:45:00Z | 4 | standards | Open W3C AI Agent Memory Interoperability CG home, charter/status posts, IETF datatracker, SAIHM standards page |
| STD-Q017 | verify | direct primary-source open | 2026-08-10T05:45:00Z | 5 | standards | Open MCP 2026-07-28 release, architecture, server primitives, extensions overview and official memory-server source |
| STD-Q018 | verify | direct primary-source open | 2026-08-10T05:45:00Z | 2 | standards | Open arXiv:2607.21404 HTML and JJJAYYYZhao/MemTools-public pinned repository |
| QDV-0af624e3fd0583b7 | verify | direct-open | 2026-08-10T05:42:00Z | 1 | paper, github, benchmark, negative, cost | Open and verify canonical primary source: ai-hyz/MemoryAgentBench dataset |
| QDV-0b3b58f0fa540628 | verify | direct-open | 2026-08-10T05:20:00Z | 1 | paper, github, standards, product, adoption | Open and verify canonical primary source: SAIHM MCP reference implementation |
| QDV-97e40777d253967e | verify | direct-open | 2026-08-10T04:59:08Z | 1 | paper, github, mechanism, negative, cost | Open and verify canonical primary source: REP selection metadata |
| QDV-1267ef16bfbeabae | verify | direct-open | 2026-08-10T05:16:00Z | 1 | paper, github, security, negative, product | Open and verify canonical primary source: Google Cloud Memory Bank docs |
| QDV-1418f84b18358859 | verify | direct-open | 2026-08-10T05:41:00Z | 1 | paper, github, benchmark, negative, cost | Open and verify canonical primary source: Ethan-Bei/Mem-Gallery dataset |
| QDV-1479f16fea091e4a | verify | direct-open | 2026-08-10T05:45:00Z | 1 | paper, github, standards, product, adoption | Open and verify canonical primary source: The 2026-07-28 MCP Specification |
| QDV-147eb673155c806d | verify | direct-open | 2026-08-10T04:57:32Z | 1 | paper, history, mechanism, github | Open and verify canonical primary source: noahshinn/reflexion README |
| QDV-180d8ef43eeef670 | verify | direct-open | 2026-08-10T04:59:08Z | 1 | paper, github, mechanism, negative, cost | Open and verify canonical primary source: SimpleMem: Efficient Lifelong Memory for LLM Agents |
| QDV-1df60a1d4afe4bf0 | verify | direct-open | 2026-08-10T04:57:32Z | 1 | paper, history, mechanism, github | Open and verify canonical primary source: Reflexion: Language Agents with Verbal Reinforcement Learning |
| QDV-2253a3ab27b96074 | verify | direct-open | 2026-08-10T05:30:00Z | 1 | paper, github, benchmark, negative, cost | Open and verify canonical primary source: MemoryArena official project and dataset |
| QDV-23b05f50a2961ba0 | verify | direct-open | 2026-08-10T05:45:00Z | 1 | paper, github, standards, product, adoption | Open and verify canonical primary source: MCP Server Features Overview |
| QDV-2727d7645491e246 | verify | direct-open | 2026-08-10T05:16:00Z | 1 | paper, github, security, negative, product | Open and verify canonical primary source: Microsoft Foundry Agent Service Memory docs |
| QDV-2ceb76e49532ff8a | verify | direct-open | 2026-08-10T04:58:06Z | 1 | paper, github, mechanism, security, negative | Open and verify canonical primary source: XSkill: Continual Learning from Experience and Skills in Multimodal Agents |
| QDV-327a7c3f55ca5581 | verify | direct-open | 2026-08-10T05:45:00Z | 1 | paper, github, standards, product, adoption | Open and verify canonical primary source: AI Agent Memory Interoperability CG charter and status posts |
| QDV-3376facecc0c141f | verify | direct-open | 2026-08-10T05:45:00Z | 1 | paper, github, standards, product, adoption | Open and verify canonical primary source: draft-saihm-memory-protocol-01 — datatracker |
| QDV-353a23a80f837f17 | verify | direct-open | 2026-08-10T05:45:00Z | 1 | paper, github, standards, product, adoption | Open and verify canonical primary source: Agent-Memory Protocol: A Privacy-Focused Protocol for LLM Agents and User Memory Interaction |
| QDV-4300c6489d63a70e | verify | direct-open | 2026-08-10T05:20:00Z | 1 | paper, github, standards, product, adoption | Open and verify canonical primary source: Agent Memory Protocol v0.1 |
| QDV-ef105f50a5eb52a2 | verify | direct-open | 2026-08-10T04:59:08Z | 1 | paper, github, mechanism, negative, cost | Open and verify canonical primary source: v09 mapped corpus exact-name scan |
| QDV-4c77518fbf11f7a6 | verify | direct-open | 2026-08-10T05:46:38Z | 1 | paper, github, standards, product, adoption | Open and verify canonical primary source: External @saihm/mcp-server references research log |
| QDV-69017d8d08774bc6 | verify | direct-open | 2026-08-10T05:32:00Z | 1 | paper, github, benchmark, negative, cost | Open and verify canonical primary source: xiaowu0162/LongMemEval |
| QDV-694d92dca4ceea20 | verify | direct-open | 2026-08-10T04:57:32Z | 1 | paper, history, mechanism, github | Open and verify canonical primary source: ericjiang18/MemCon README |
| QDV-6d0d8dd47d71c479 | verify | direct-open | 2026-08-10T04:58:06Z | 1 | paper, github, mechanism, security, negative | Open and verify canonical primary source: XSkill-Agent/XSkill README and repository metadata |
| QDV-778e2d9726e789db | verify | direct-open | 2026-08-10T05:21:00Z | 1 | paper, github, benchmark, negative, cost | Open and verify canonical primary source: EMemBench |
| QDV-7b9d0f177a059902 | verify | direct-open | 2026-08-10T05:18:00Z | 1 | paper, github, benchmark, negative, cost | Open and verify canonical primary source: HaluMem: Evaluating Hallucinations in Memory Systems of Agents |
| QDV-7d8bb2e98eb1cf17 | verify | direct-open | 2026-08-10T05:14:00Z | 1 | paper, github, benchmark, negative, cost | Open and verify canonical primary source: LongMemEval: Benchmarking Chat Assistants on Long-Term Interactive Memory |
| QDV-7db8bdcf51f377a3 | verify | direct-open | 2026-08-10T04:57:32Z | 1 | paper, history, mechanism, github | Open and verify canonical primary source: joonspk-research/generative_agents README |
| QDV-8942e3ccf604231b | verify | direct-open | 2026-08-10T05:46:37Z | 1 | paper, github, standards, product, adoption | Open and verify canonical primary source: External @universalmemoryprotocol/core references research log |
| QDV-8a51d1e1605f8ffe | verify | direct-open | 2026-08-10T05:45:00Z | 1 | paper, github, standards, product, adoption | Open and verify canonical primary source: MCP Extensions Overview |
| QDV-8dbbd736ce37feda | verify | direct-open | 2026-08-10T05:34:00Z | 1 | paper, github, benchmark, negative, cost | Open and verify canonical primary source: import-myself/Membench |
| QDV-9135e682a19653f5 | verify | direct-open | 2026-08-10T05:45:00Z | 1 | paper, github, standards, product, adoption | Open and verify canonical primary source: SAIHM Standards status |
| QDV-98589758e85a1228 | verify | direct-open | 2026-08-10T04:58:06Z | 1 | paper, github, mechanism, security, negative | Open and verify canonical primary source: INMS: Memory Sharing for Large Language Model based Agents |
| QDV-a55cdee21963ed9b | verify | direct-open | 2026-08-10T05:35:00Z | 1 | paper, github, benchmark, negative, cost | Open and verify canonical primary source: xiaowu0162/LongMemEval-V2 |
| QDV-ab2735ae2d71cd24 | verify | direct-open | 2026-08-10T05:45:00Z | 1 | paper, github, standards, product, adoption | Open and verify canonical primary source: AI Agent Memory Interoperability Community Group |
| QDV-aca01102857fbc12 | verify | direct-open | 2026-08-10T05:20:00Z | 1 | paper, github, standards, product, adoption | Open and verify canonical primary source: Smriti AMP specification |
| QDV-ae493eafc368b7c9 | verify | direct-open | 2026-08-10T05:16:00Z | 1 | paper, github, security, negative, product | Open and verify canonical primary source: Amazon Bedrock Agents Classic memory docs |
| QDV-bd5638a89b2f2e3d | verify | direct-open | 2026-08-10T05:31:00Z | 1 | paper, github, benchmark, negative, cost | Open and verify canonical primary source: snap-research/locomo |
| QDV-bd7d291e9f53708a | verify | direct-open | 2026-08-10T05:46:37Z | 1 | paper, github, standards, product, adoption | Open and verify canonical primary source: UMP npm registry metadata |
| QDV-cb8f252ccaaf10b0 | verify | direct-open | 2026-08-10T05:20:00Z | 1 | paper, github, standards, product, adoption | Open and verify canonical primary source: Knowledge Graph Memory Server |
| QDV-d3e5cdce41792693 | verify | direct-open | 2026-08-10T05:25:00Z | 1 | paper, github, standards, product, adoption | Open and verify canonical primary source: Independent discussion of Smriti AMP |
| QDV-d8e1090f71ef8891 | verify | direct-open | 2026-08-10T05:26:00Z | 1 | paper, github, benchmark, negative, cost | Open and verify canonical primary source: ImplicitMemBench |
| QDV-da9e733d9c09306d | verify | direct-open | 2026-08-10T05:20:00Z | 1 | paper, github, standards, product, adoption | Open and verify canonical primary source: MemTools-public |
| QDV-e11f76377b468755 | verify | direct-open | 2026-08-10T05:25:00Z | 1 | paper, github, standards, product, adoption | Open and verify canonical primary source: Open Memory Protocol v2.0 Specification |
| QDV-e3ab85f7cd9d62eb | verify | direct-open | 2026-08-10T05:20:00Z | 1 | paper, github, standards, product, adoption | Open and verify canonical primary source: EB-DevTech Open Memory Protocol repository |
| QDV-e94011411190c327 | verify | direct-open | 2026-08-10T05:16:00Z | 1 | paper, github, security, negative, product | Open and verify canonical primary source: AgentPoison |
| QDV-eee6cbbccab20c09 | verify | direct-open | 2026-08-10T05:45:00Z | 1 | paper, github, standards, product, adoption | Open and verify canonical primary source: MCP Architecture |
| QDV-efc9ff30e0690f22 | verify | direct-open | 2026-08-10T04:57:32Z | 1 | paper, history, mechanism, github | Open and verify canonical primary source: Generative Agents: Interactive Simulacra of Human Behavior |
| QDV-c71a66fb28a56956 | verify | direct-open | 2026-08-10T05:46:38Z | 1 | paper, github, standards, product, adoption | Open and verify canonical primary source: External adoption-probe research log |
| QDV-3b863c2f5152a754 | verify | direct-open | 2026-08-10T05:46:25Z | 1 | paper, github, standards, product, adoption | Open and verify canonical primary source: Protocol-name collision research log |
| QGR-A01 | verify | github-code-search | 2026-08-10T05:21:10Z | 2784 | github, adoption | "mem0ai" filename:requirements.txt |
| QGR-A02 | verify | github-code-search | 2026-08-10T05:21:26Z | 104 | github, adoption | "letta-client" filename:pyproject.toml |
| QGR-A03 | verify | github-code-search | 2026-08-10T05:21:46Z | 294 | github, adoption | "cognee" filename:requirements.txt |
| QGR-A04 | verify | github-code-search | 2026-08-10T05:22:00Z | 438 | github, adoption | "supermemory" filename:package.json |
| QGR-A05 | verify | github-code-search | 2026-08-10T05:22:12Z | 48 | github, adoption | "memvid" filename:requirements.txt |
| QGR-A06 | verify | github-code-search | 2026-08-10T05:22:27Z | 9 | github, adoption | "basic-memory" filename:pyproject.toml |
| QGR-A07 | verify | github-code-search | 2026-08-10T05:22:46Z | 838 | github, adoption | "Microsoft.KernelMemory" extension:csproj |
| QGR-A08 | verify | github-code-search | 2026-08-10T05:23:01Z | 250 | github, adoption | "hindsight-client" filename:pyproject.toml |
| QGR-A09 | verify | github-code-search | 2026-08-10T05:23:13Z | 5 | github, adoption | "lightmem" filename:requirements.txt |
| QGR-A10 | verify | github-code-search | 2026-08-10T05:23:28Z | 65 | github, adoption | "MemoryOS" filename:requirements.txt |
| QGR-P01 | verify | github-repository-search | 2026-08-10T05:26:10Z | 0 | github, adoption | "A Glimpse into Long-term Physical Coexistence with Intelligent Robots" |
| QGR-P02 | verify | github-repository-search | 2026-08-10T05:26:13Z | 0 | github, adoption | PHILIA robot gateway Astribot |
| QGR-P03 | verify | github-repository-search | 2026-08-10T05:26:15Z | 0 | github, adoption | 2607.11377 |
| QGR-PAPER | verify | direct-open | 2026-08-10T05:26:15Z | 1 | paper, github, adoption | Open and verify PHILIA paper identity and repository links |
| QC09-001 | deep-focus | direct-open | 2026-08-10T06:55:01Z | 1 | paper, benchmark, mechanism | Open and verify arXiv 2606.22417 and its code/data link |
| QC09-002 | verify | github-direct-open | 2026-08-10T06:55:10Z | 1 | github, benchmark, mechanism | Verify TransformerOptimus/supercoder-eval at fixed commit 89e4156ba11538a8be0e2343d215bdff778550ed |
| QC09-003 | deep-focus | direct-open | 2026-08-10T06:55:20Z | 1 | paper, mechanism | Open and verify arXiv 2606.12329 PROJECTMEM |
| QC09-004 | verify | github-direct-open | 2026-08-10T06:55:30Z | 1 | github, mechanism, security | Verify riponcm/projectmem at fixed commit 3d8e3f379913d49585ba126d090f5501de9c079d |
| QC09-005 | adversarial | direct-open | 2026-08-10T06:55:40Z | 1 | paper, negative, benchmark | Open and verify arXiv 2602.11988 repository context-file counterevidence |
| QC09-006 | deep-focus | direct-open | 2026-08-10T06:55:50Z | 1 | paper, mechanism, security, benchmark | Open and verify arXiv 2605.01567 safety-gated RL developer memory |
| SAT11-C01-OA | verify | OpenAlex Works API | 2026-08-10T09:40:55Z | 10 | paper, mechanism, history | LLM agent memory service runtime checkpoint rollback API |
| SAT11-C02-OA | verify | OpenAlex Works API | 2026-08-10T09:43:49Z | 1 | paper, mechanism, cost | LLM agent memory storage indexing durability reindex cost |
| SAT11-C03-OA | verify | OpenAlex Works API | 2026-08-10T09:44:36Z | 0 | paper, mechanism, history | LLM agent memory temporal knowledge graph bitemporal version conflict provenance |
| SAT11-C04-OA | verify | OpenAlex Works API | 2026-08-10T09:41:08Z | 5 | paper, mechanism, negative | LLM agent memory retrieval ranking active navigation stale inappropriate |
| SAT11-C05-OA | verify | OpenAlex Works API | 2026-08-10T09:41:12Z | 1 | paper, mechanism, negative | LLM agent memory consolidation forgetting supersede revoke purge rollback |
| SAT11-C06-OA | verify | OpenAlex Works API | 2026-08-10T09:44:42Z | 10 | paper, mechanism, negative | LLM agent procedural memory reusable skill experience failure transfer |
| SAT11-C07-OA | verify | OpenAlex Works API | 2026-08-10T09:44:47Z | 10 | paper, mechanism, cost, negative | LLM agent memory context compression token budget latency cost raw evidence |
| SAT11-C08-OA | verify | OpenAlex Works API | 2026-08-10T09:44:53Z | 10 | paper, mechanism, security, negative | LLM agent memory personalization user profile identity correction consent stale preference |
| SAT11-C10-OA | verify | OpenAlex Works API | 2026-08-10T09:44:59Z | 10 | paper, benchmark, mechanism | LLM agent memory embodied multimodal world state partial observability benchmark |
| SAT11-C11-OA | verify | OpenAlex Works API | 2026-08-10T09:45:04Z | 10 | paper, mechanism, security | multi-agent shared memory distributed portable private authority revocation |
| SAT11-C12-OA | verify | OpenAlex Works API | 2026-08-10T09:45:09Z | 10 | paper, security, negative, mechanism | LLM agent memory poisoning privacy integrity provenance deletion security |
| SAT11-C13-OA | verify | OpenAlex Works API | 2026-08-10T09:41:42Z | 10 | paper, benchmark, negative, cost | LLM agent memory longitudinal benchmark ablation comparability |
| SAT11-FOUNDATION-OA | verify | OpenAlex Works API | 2026-08-10T09:41:48Z | 10 | paper, history, mechanism | LLM agent memory long-term memory architecture history benchmark |
| SAT11-FUTURE-OA | verify | OpenAlex Works API | 2026-08-10T09:41:52Z | 0 | paper, history, negative | LLM agent memory persistent memory benchmark security |
| SAT11-GH-C01C02 | verify | GitHub REST Search API | 2026-08-10T09:36:30Z | 10 | github, mechanism | "agent memory" MCP server created:>=2025-08-10 |
| SAT11-GH-C03C04 | verify | GitHub REST Search API | 2026-08-10T09:36:39Z | 10 | github, mechanism | "agent memory" graph temporal created:>=2025-08-10 |
| SAT11-GH-C05C06 | verify | GitHub REST Search API | 2026-08-10T09:36:49Z | 2 | github, mechanism | "agent memory" forgetting skill created:>=2025-08-10 |
| SAT11-GH-C07C08 | verify | GitHub REST Search API | 2026-08-10T09:36:57Z | 5 | github, mechanism | "agent memory" context profile created:>=2025-08-10 |
| SAT11-GH-C10C11 | verify | GitHub REST Search API | 2026-08-10T09:37:07Z | 1 | github, mechanism | "agent memory" multimodal shared created:>=2025-08-10 |
| SAT11-GH-C12C13 | verify | GitHub REST Search API | 2026-08-10T09:37:16Z | 1 | github, mechanism | "agent memory" security benchmark created:>=2025-08-10 |
| SAT12-C01-ARXIV | verify | arXiv Atom API | 2026-08-10T09:37:19Z | 10 | paper, mechanism, history | persistent stateful LLM agent Letta Mem0 MemOS API transaction checkpoint recovery |
| SAT12-C02-ARXIV | verify | arXiv Atom API | 2026-08-10T09:37:23Z | 10 | paper, mechanism, cost | long-term agent memory Zep Cognee MemMachine storage index crash consistency deletion cost |
| SAT12-C03-ARXIV | verify | arXiv Atom API | 2026-08-10T09:37:28Z | 10 | paper, mechanism, history | LLM agent memory Graphiti Zep A-MEM temporal knowledge graph bitemporal conflict provenance |
| SAT12-C04-ARXIV | verify | arXiv Atom API | 2026-08-10T09:37:34Z | 0 | paper, mechanism, negative | long-term memory agents LightMem HippoRAG hybrid retrieval graph traversal reranker hard filter budget abstention |
| SAT12-C05-ARXIV | verify | arXiv Atom API | 2026-08-10T09:37:38Z | 10 | paper, mechanism, negative | LLM agent memory ForgetEval MemCon MemTxn selective forgetting consolidation supersession delete restore |
| SAT12-C06-ARXIV | verify | arXiv Atom API | 2026-08-10T09:37:44Z | 10 | paper, mechanism, negative | LLM agents Reflexion Voyager MemSkill XSkill procedural memory skill library experience failure transfer |
| SAT12-C07-ARXIV | verify | arXiv Atom API | 2026-08-10T09:37:49Z | 6 | paper, mechanism, cost, negative | LLM agent memory SimpleMem MemGPT LightMem context compression virtualization budgeted consolidation latency token cost |
| SAT12-C08-ARXIV | verify | arXiv Atom API | 2026-08-10T09:37:54Z | 3 | paper, benchmark, security, negative | LLM agent memory MemoryBank Memora STALE LoCoMo user profile correction consent stale preference benchmark |
| SAT12-C10-ARXIV | verify | arXiv Atom API | 2026-08-10T09:37:58Z | 10 | paper, benchmark, mechanism | multimodal embodied agent memory AriGraph WorldLines WorldMemArena MeMento world state partial observability benchmark |
| SAT12-C11-ARXIV | verify | arXiv Atom API | 2026-08-10T09:38:03Z | 1 | paper, mechanism, security | multi-agent memory Collaborative Memory INMS UMP shared distributed portable private fragments authority revocation |
| SAT12-C12-ARXIV | verify | arXiv Atom API | 2026-08-10T09:38:10Z | 10 | paper, security, negative, mechanism | persistent agent memory MINJA MemSecBench Memory Guard poisoning privacy provenance deletion write retrieve execute forget |
| SAT12-C13-ARXIV | verify | arXiv Atom API | 2026-08-10T09:38:14Z | 10 | paper, benchmark, negative, cost | longitudinal agent memory benchmark MemoryAgentBench LoCoMo LongMemEval MemoryArena MemSecBench no-memory ablation |
| SAT12-FOUNDATION-ARXIV | verify | arXiv Atom API | 2026-08-10T09:38:19Z | 10 | paper, history, mechanism | Generative Agents MemGPT Reflexion Voyager MemoryBank foundational agent memory history |
| SAT12-FUTURE-CROSSREF | verify | Crossref REST API | 2026-08-10T09:38:21Z | 10 | paper, history, negative | LLM agent memory persistent memory benchmark security |
| SAT12-GH-C01C02 | verify | GitHub REST Search API | 2026-08-10T09:38:24Z | 10 | github, mechanism | "persistent memory" agent MCP created:>=2026-05-12 |
| SAT12-GH-C03C04 | verify | GitHub REST Search API | 2026-08-10T09:38:35Z | 6 | github, mechanism | "temporal memory" agent graph created:>=2026-05-12 |
| SAT12-GH-C05C06 | verify | GitHub REST Search API | 2026-08-10T09:38:45Z | 10 | github, mechanism | "agent skill" memory created:>=2026-05-12 |
| SAT12-GH-C07C08 | verify | GitHub REST Search API | 2026-08-10T09:38:55Z | 10 | github, mechanism | "personal AI memory" created:>=2026-05-12 |
| SAT12-GH-C10C11 | verify | GitHub REST Search API | 2026-08-10T09:39:04Z | 8 | github, mechanism | "multi-agent memory" shared created:>=2026-05-12 |
| SAT12-GH-C12C13 | verify | GitHub REST Search API | 2026-08-10T09:39:14Z | 10 | github, mechanism | "agent memory" poisoning created:>=2026-05-12 |
| SAT13-C06C12C13-OA | verify | OpenAlex Works API | 2026-08-10T09:54:42Z | 10 | paper, security, benchmark, negative, mechanism | trajectory poisoning self-evolving agent skill persistent memory security benchmark defense provenance |
| SAT13-C06C12C13-12M-OA | verify | OpenAlex Works API | 2026-08-10T09:57:26Z | 10 | paper, security, benchmark, negative, mechanism | self-evolving agent skill backdoor trajectory evidence promotion security evaluation |
| SAT13-GH-C06C12C13 | verify | GitHub REST Search API | 2026-08-10T09:54:46Z | 1 | github, mechanism | "agent skill" poisoning memory created:>=2026-05-12 |
| SAT09-C09-PAPER-OA | verify | OpenAlex Works API | 2026-08-10T08:43:36Z | 25 | paper, history, mechanism | "coding agent" project memory repository memory session memory decision log |
| SAT09-C09-GITHUB | verify | GitHub REST Search API | 2026-08-10T08:43:40Z | 20 | github, mechanism | "project memory" "coding agent" created:>=2026-05-12 |
| SAT09-C09-COUNTER-OA | verify | OpenAlex Works API | 2026-08-10T08:43:45Z | 25 | benchmark, negative, cost, security | coding agent project memory benchmark failure stale security cost handoff |
| SAT09-C14-PAPER-OA | verify | OpenAlex Works API | 2026-08-10T08:43:49Z | 25 | paper, history, mechanism | agent memory taxonomy survey architecture theory stateful agents |
| SAT09-C14-BOUNDARY-OA | verify | OpenAlex Works API | 2026-08-10T08:43:52Z | 25 | paper, mechanism, negative, cost, security | LLM agent memory external parametric latent model-native boundary long context |
| SAT09-C14-GITHUB | verify | GitHub REST Search API | 2026-08-10T08:43:56Z | 20 | github, history, mechanism | "agent memory" architecture created:>=2025-08-10 |
| SAT10-C09-PAPER-CROSSREF | verify | Crossref REST API | 2026-08-10T08:44:00Z | 25 | paper, history, mechanism | coding agent project memory repository memory session handoff |
| SAT10-C09-PAPER-ARXIV | verify | arXiv Atom API | 2026-08-10T08:44:03Z | 4 | paper, benchmark, negative, mechanism | ("coding agent" OR "software agent") AND ("project memory" OR "repository memory" OR "session memory") |
| SAT10-C09-GITHUB | verify | GitHub REST Search API | 2026-08-10T08:44:14Z | 20 | github, mechanism, negative, security, cost | "Claude Code" memory handoff created:>=2026-05-12 |
| SAT10-C14-PAPER-CROSSREF | verify | Crossref REST API | 2026-08-10T08:44:18Z | 25 | paper, history, mechanism | agentic memory survey taxonomy external memory model-native parametric memory |
| SAT10-C14-PAPER-ARXIV | verify | arXiv Atom API | 2026-08-10T08:44:21Z | 25 | paper, history, mechanism, negative | "agent memory" AND (survey OR taxonomy OR "external memory" OR "latent memory" OR "parametric memory") |
| SAT10-C14-GITHUB | verify | GitHub REST Search API | 2026-08-10T08:44:25Z | 20 | github, history, mechanism, benchmark | "agentic memory" architecture created:>=2025-08-10 |
| SAT-STD-Q001 | verify | W3C API | 2026-08-10T09:37:20Z | 1 | standards | group shortname ai-agent-memory-interop |
| SAT-STD-Q002 | verify | W3C API | 2026-08-10T09:37:20Z | 17 | adoption | users of ai-agent-memory-interop |
| SAT-STD-Q003 | verify | W3C API | 2026-08-10T09:37:20Z | 0 | standards | specifications route for ai-agent-memory-interop |
| SAT-STD-Q004 | verify | IETF Datatracker API | 2026-08-10T09:37:20Z | 1 | standards | draft-saihm-memory-protocol |
| SAT-STD-Q005 | verify | IETF Datatracker API | 2026-08-10T09:37:20Z | 15 | standards | events for draft-saihm-memory-protocol |
| SAT-STD-Q006 | verify | MCP official docs | 2026-08-10T09:37:20Z | 3 | standards | official extension families at cutoff |
| SAT-STD-Q007 | verify | MCP official docs | 2026-08-10T09:37:20Z | 1 | product | MCP Tasks scope |
| SAT-STD-Q008 | verify | GitHub Code Search API | 2026-08-10T09:37:41Z | 13 | adoption | "github.com/SAIHM-Admin/saihm-mcp" -repo:SAIHM-Admin/saihm-mcp |
| SAT-STD-Q009 | verify | GitHub Code Search API | 2026-08-10T09:37:41Z | 6 | adoption | "github.com/agentmemoryprotocol/agentmemoryprotocol" -repo:agentmemoryprotocol/agentmemoryprotocol |
| SAT-STD-Q010 | verify | GitHub Code Search API | 2026-08-10T09:37:41Z | 2 | adoption | "github.com/smriti-memcore/amp" -repo:smriti-memcore/amp |
| SAT-STD-Q011 | verify | GitHub Code Search API | 2026-08-10T09:37:41Z | 0 | adoption | "github.com/EB-DevTech/Open-Memory-Protocol" -repo:EB-DevTech/Open-Memory-Protocol |
| SAT-STD-Q012 | verify | GitHub Code Search API | 2026-08-10T09:37:41Z | 52 | adoption | "github.com/SMJAI/open-memory-protocol" -repo:SMJAI/open-memory-protocol |
| SAT-STD-Q013 | verify | GitHub Code Search API | 2026-08-10T09:37:41Z | 6 | adoption | "github.com/edihasaj/universal-memory-protocol" -repo:edihasaj/universal-memory-protocol |
| SAT-STD-Q014 | verify | GitHub Code Search API | 2026-08-10T09:37:41Z | 0 | adoption | "github.com/JJJAYYYZhao/MemTools-public" -repo:JJJAYYYZhao/MemTools-public |
| SAT-STD-Q015 | verify | GitHub Contents API | 2026-08-10T09:38:00Z | 1 | standards | UMP adapter implementation |
| SAT-STD-Q016 | verify | GitHub Contents API | 2026-08-10T09:38:00Z | 1 | standards | UMP adapter tests |
| SAT-STD-Q017 | verify | GitHub Actions API | 2026-08-10T09:38:00Z | 2 | standards | workflow runs for pinned AMH commit |
| SAT-STD-Q018 | verify | GitHub Contents API | 2026-08-10T09:38:00Z | 1 | standards | UMP 1.0 record schema |
| SAT-STD-Q019 | verify | OpenAlex Works API | 2026-08-10T08:55:00Z | 3 | standards | "Universal Memory Protocol" |
| SAT-STD-Q020 | verify | OpenAlex Works API | 2026-08-10T08:55:00Z | 4 | standards | "Agent Memory Protocol" |
| SAT-STD-Q021 | verify | OpenAlex Works API | 2026-08-10T08:55:00Z | 1 | standards | "Open Memory Protocol" |
| SAT-STD-Q022 | verify | OpenAlex Works API | 2026-08-10T08:55:00Z | 0 | standards | "AI Agent Memory Interoperability" |
| SAT-STD-Q023 | verify | OpenAlex Works API | 2026-08-10T08:55:00Z | 0 | standards | "draft-saihm-memory-protocol" |
| SAT-STD-Q024 | verify | GitHub REST API | 2026-08-10T08:55:00Z | 1 | standards | santhoshravindran7/portable-agent-memory |
| SAT-STD-Q025 | verify | arXiv | 2026-08-10T08:55:00Z | 1 | standards | arXiv:2605.11032 |
| SAT-STD-Q026 | verify | GitHub REST API | 2026-08-10T08:55:00Z | 1 | adoption | antonio-amore-akiki/amore |
| SAT-STD-Q027 | verify | GitHub REST API | 2026-08-10T08:55:00Z | 1 | standards | engramspec/spec |
| SAT-STD-Q028 | verify | DOI resolver / SSRN | 2026-08-10T08:55:00Z | 1 | standards | 10.2139/ssrn.6878038 |
| SAT-STD-Q029 | verify | Zenodo DOI landing | 2026-08-10T08:55:00Z | 1 | standards | 10.5281/zenodo.19423177 |
| SAT-STD-Q030 | verify | GitHub Code Search API | 2026-08-10T08:55:00Z | 0 | adoption | ("engramspec.org" OR "engram_version") -repo:engramspec/spec |
| SAT-STD-Q031 | verify | GitHub Repository Search API | 2026-08-10T09:38:28Z | 382 | standards | "memory protocol" agent in:readme created:>=2026-04-01 pushed:>=2026-07-01 |
| SAT-STD-Q032 | verify | GitHub Repository Search API | 2026-08-10T09:38:28Z | 29 | standards | "portable agent memory" in:readme created:>=2026-04-01 pushed:>=2026-07-01 |
| SAT-STD-Q033 | verify | GitHub Repository Search API | 2026-08-10T09:38:28Z | 4 | standards | "memory interoperability" agent in:readme created:>=2026-04-01 pushed:>=2026-07-01 |
| SAT-STD-Q034 | verify | GitHub Repository Search API | 2026-08-10T09:38:28Z | 9 | standards | "memory conformance" agent in:readme created:>=2026-04-01 pushed:>=2026-07-01 |
| SAT-STD-Q035 | verify | GitHub Repository Search API | 2026-08-10T09:38:28Z | 49 | standards | "memory portability" MCP in:readme created:>=2026-04-01 pushed:>=2026-07-01 |
| SAT-STD-Q036 | verify | GitHub REST/Contents API | 2026-08-10T09:38:28Z | 1 | standards | HKUDS/MGP |
| SAT-STD-Q037 | verify | GitHub REST/Contents API | 2026-08-10T09:38:28Z | 1 | standards | tinqiao-oss/engramory |
| SAT-STD-Q038 | verify | GitHub REST/Contents API | 2026-08-10T09:38:28Z | 1 | standards | Vortx-AI/emem |
| SAT-STD-Q039 | verify | GitHub REST/Contents API | 2026-08-10T09:38:28Z | 1 | standards | aquifer-labs/ocf |
| SAT-STD-Q040 | verify | GitHub REST/Contents API | 2026-08-10T09:38:28Z | 1 | standards | glatinone/agent-memory-protocol |
| SAT-STD-Q041 | verify | GitHub Code Search API | 2026-08-10T09:39:00Z | 0 | adoption | "github.com/HKUDS/MGP" -repo:HKUDS/MGP |
| SAT-STD-Q042 | verify | GitHub Code Search API | 2026-08-10T09:39:00Z | 7 | adoption | "github.com/tinqiao-oss/engramory" -repo:tinqiao-oss/engramory |
| SAT-STD-Q043 | verify | GitHub Code Search API | 2026-08-10T09:39:00Z | 53 | adoption | "github.com/Vortx-AI/emem" -repo:Vortx-AI/emem |
| SAT-STD-Q044 | verify | GitHub Code Search API | 2026-08-10T09:39:00Z | 7 | adoption | "github.com/aquifer-labs/ocf" -repo:aquifer-labs/ocf |
| SAT-STD-Q045 | verify | GitHub Code Search API | 2026-08-10T09:39:00Z | 0 | adoption | "github.com/glatinone/agent-memory-protocol" -repo:glatinone/agent-memory-protocol |
| SAT-STD-Q046 | verify | GitHub Contents API | 2026-08-10T09:39:00Z | 1 | adoption | syh5285126-ops/agent-team Engramory bootstrap |
| SAT-STD-Q047 | verify | Crossref REST API | 2026-08-10T09:39:21Z | 1896965 | adoption | Memory Governance Protocol AI agent |
| SAT-STD-Q048 | verify | Crossref REST API | 2026-08-10T09:39:21Z | 1271848 | adoption | Engramory AI agent memory |
| SAT-STD-Q049 | verify | Crossref REST API | 2026-08-10T09:39:21Z | 2425309 | adoption | Open Cognitive Format AI agent |
| SAT-STD-Q050 | verify | Crossref REST API | 2026-08-10T09:39:21Z | 1652314 | adoption | emem verifiable memory protocol AI agents |
| SAT-STD-Q051 | verify | Crossref REST API | 2026-08-10T09:39:21Z | 9126910 | standards | RFC AMP 001 agent memory protocol |
| SAT-STD-Q052 | verify | Crossref REST API | 2026-08-10T09:39:21Z | 1077130 | standards | Agent Memory Hall portability |
| SAT-STD-Q053 | verify | DataCite REST API | 2026-08-10T09:39:58Z | 0 | standards | titles.title:"Memory Governance Protocol" |
| SAT-STD-Q054 | verify | DataCite REST API | 2026-08-10T09:39:58Z | 0 | standards | titles.title:"Engramory" |
| SAT-STD-Q055 | verify | DataCite REST API | 2026-08-10T09:39:58Z | 0 | standards | titles.title:"Open Cognitive Format" |
| SAT-STD-Q056 | verify | DataCite REST API | 2026-08-10T09:39:58Z | 0 | standards | titles.title:"emem verifiable memory" |
| SAT-STD-Q057 | verify | DataCite REST API | 2026-08-10T09:39:58Z | 0 | standards | titles.title:"Agent Memory Hall" |
| SAT-STD-Q058 | verify | DataCite REST API | 2026-08-10T09:39:58Z | 0 | standards | titles.title:"RFC-AMP-001" |
| SAT-STD-Q059 | verify | GitHub Code Search API | 2026-08-10T10:05:21Z | 0 | adoption | "from mgp_client" -repo:HKUDS/MGP |
| SAT-STD-Q060 | verify | GitHub Code Search API | 2026-08-10T10:05:21Z | 0 | adoption | "@vortxai/emem" -repo:Vortx-AI/emem |
| SAT-STD-Q061 | verify | GitHub Code Search API | 2026-08-10T10:05:21Z | 1 | adoption | "rules-snippet.md" "engramory" -repo:tinqiao-oss/engramory |
| SAT-STD-Q062 | verify | GitHub Code Search API | 2026-08-10T10:05:21Z | 21 | adoption | "ocf_version" "0.2" -repo:aquifer-labs/ocf |
| SAT-STD-Q063 | verify | W3C Community Group site | 2026-08-10T10:05:21Z | 0 | standards | current AI Agent Memory Interoperability CG publication/status surface |
| SAT-STD-Q064 | verify | IETF Internet-Draft archive | 2026-08-10T10:05:21Z | 0 | standards | draft-saihm-memory-protocol-01 |
| SAT-STD-Q065 | verify | MCP official specification | 2026-08-10T10:05:21Z | 3 | product | MCP server primitives |
| SAT-STD-Q066 | verify | MCP official specification | 2026-08-10T10:05:21Z | 1 | product | MCP state boundary |
| SAT-STD-Q067 | verify | Bing web search | 2026-08-10T10:07:05Z | 10 | adoption | "Vortx-AI/emem" deployment |
| SAT-STD-Q068 | verify | Bing web search | 2026-08-10T10:07:05Z | 10 | adoption | "HKUDS/MGP" production |
| SAT-STD-Q069 | verify | Bing web search | 2026-08-10T10:07:05Z | 10 | adoption | "tinqiao-oss/engramory" deployment |
| SAT-STD-Q070 | verify | Bing web search | 2026-08-10T10:07:05Z | 7 | standards | "AI Agent Memory Interoperability Community Group" specification |
| SAT-STD-Q071 | verify | Bing web search | 2026-08-10T10:07:05Z | 10 | standards | "draft-saihm-memory-protocol-01" standard |
| SAT-STD-Q072 | verify | Bing web search | 2026-08-10T10:07:05Z | 10 | product | "MCP Tasks" memory |
| SAT-STD-Q073 | verify | Bing web search | 2026-08-10T10:07:05Z | 0 | product | site:modelcontextprotocol.io "Prompts" "Resources" "Tools" memory |
| SAT-STD-Q074 | verify | W3C Community Group charter | 2026-08-10T10:07:50Z | 0 | standards | current charter status and deliverables |
| SAT-STD-Q075 | verify | IETF Datatracker HTML | 2026-08-10T10:07:50Z | 0 | standards | current draft-saihm-memory-protocol status |
| SAT-STD-Q076 | verify | MCP official docs | 2026-08-10T10:07:50Z | 3 | product | current extension families |
| SAT-STD-Q077 | verify | MCP official docs | 2026-08-10T10:07:50Z | 1 | product | MCP Tasks scope |
