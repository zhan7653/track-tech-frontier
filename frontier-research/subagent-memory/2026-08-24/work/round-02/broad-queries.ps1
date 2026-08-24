$ErrorActionPreference = 'Stop'

$repo = 'D:\Code\track-tech-frontier'
$runRoot = Join-Path $repo 'frontier-research\subagent-memory\2026-08-24\work\round-02\broad'
$rawRoot = Join-Path $runRoot 'raw'
New-Item -ItemType Directory -Path $runRoot -Force | Out-Null
New-Item -ItemType Directory -Path $rawRoot -Force | Out-Null

$jobs = @(
    @{ QueryId='Q022'; Id='A01'; Provider='arxiv'; Query='(subagent OR "sub-agent") AND (memory OR context OR state OR inheritance)'; From='2023-01-01'; To='2026-08-24'; Limit=100; Pages=2; Lanes=@('paper'); Windows=@('W_PRE_FRONTIER','W_ROLLING_12M','W_ROLLING_90D'); Gain='Direct parent-child and spawn terminology.' },
    @{ QueryId='Q023'; Id='A02'; Provider='arxiv'; Query='("multi-agent" OR "multi agent") AND ("shared memory" OR "collective memory" OR "transactive memory" OR "collaborative memory") AND (LLM OR "language model")'; From='2023-01-01'; To='2026-08-24'; Limit=100; Pages=2; Lanes=@('paper'); Windows=@('W_PRE_FRONTIER','W_ROLLING_12M','W_ROLLING_90D'); Gain='Shared, collective, transactive and collaborative memory family recall.' },
    @{ QueryId='Q024'; Id='A03'; Provider='arxiv'; Query='(agent OR agentic) AND (handoff OR delegation OR spawn) AND (context OR memory OR state) AND (LLM OR "language model")'; From='2023-01-01'; To='2026-08-24'; Limit=100; Pages=2; Lanes=@('paper'); Windows=@('W_PRE_FRONTIER','W_ROLLING_12M','W_ROLLING_90D'); Gain='Delegation-state and handoff mechanisms.' },
    @{ QueryId='Q025'; Id='A04'; Provider='arxiv'; Query='"multi-agent" AND (blackboard OR "shared workspace" OR "shared state" OR "state synchronization") AND (LLM OR "language model")'; From='2023-01-01'; To='2026-08-24'; Limit=100; Pages=2; Lanes=@('paper'); Windows=@('W_PRE_FRONTIER','W_ROLLING_12M','W_ROLLING_90D'); Gain='Shared coordination substrates beyond memory-service wording.' },
    @{ QueryId='Q026'; Id='A05'; Provider='arxiv'; Query='"multi-agent" AND (trajectory OR experience OR skill) AND (sharing OR transfer OR reuse) AND (LLM OR "language model")'; From='2023-01-01'; To='2026-08-24'; Limit=100; Pages=2; Lanes=@('paper'); Windows=@('W_PRE_FRONTIER','W_ROLLING_12M','W_ROLLING_90D'); Gain='Population experience and skill-transfer mechanisms.' },
    @{ QueryId='Q027'; Id='A06'; Provider='arxiv'; Query='"multi-agent" AND (memory OR state) AND (conflict OR consistency OR transaction OR concurrency OR provenance) AND (LLM OR "language model")'; From='2023-01-01'; To='2026-08-24'; Limit=100; Pages=2; Lanes=@('paper'); Windows=@('W_PRE_FRONTIER','W_ROLLING_12M','W_ROLLING_90D'); Gain='Consistency, commit, conflict and provenance routes.' },
    @{ QueryId='Q028'; Id='A07'; Provider='arxiv'; Query='"multi-agent" AND memory AND (poisoning OR injection OR security OR privacy OR authorization OR leakage)'; From='2023-01-01'; To='2026-08-24'; Limit=100; Pages=2; Lanes=@('paper','negative'); Windows=@('W_PRE_FRONTIER','W_ROLLING_12M','W_ROLLING_90D'); Gain='Adversarial and governance evidence.' },
    @{ QueryId='Q029'; Id='A08'; Provider='arxiv'; Query='"multi-agent" AND memory AND (benchmark OR evaluation OR dataset)'; From='2023-01-01'; To='2026-08-24'; Limit=100; Pages=2; Lanes=@('paper','benchmark'); Windows=@('W_PRE_FRONTIER','W_ROLLING_12M','W_ROLLING_90D'); Gain='Benchmark and dataset coverage.' },
    @{ QueryId='Q030'; Id='A09'; Provider='arxiv'; Query='("coding agent" OR "research agent") AND (subagent OR "multi-agent") AND (memory OR state OR handoff OR workspace)'; From='2023-01-01'; To='2026-08-24'; Limit=100; Pages=2; Lanes=@('paper'); Windows=@('W_PRE_FRONTIER','W_ROLLING_12M','W_ROLLING_90D'); Gain='Coding and research agent scenario-specific state mechanisms.' },
    @{ QueryId='Q031'; Id='A10'; Provider='arxiv'; Query='("agent fleet" OR "agent population" OR "organizational memory") AND (memory OR knowledge OR experience)'; From='2023-01-01'; To='2026-08-24'; Limit=100; Pages=2; Lanes=@('paper'); Windows=@('W_PRE_FRONTIER','W_ROLLING_12M','W_ROLLING_90D'); Gain='Fleet and population-level memory.' },
    @{ QueryId='Q032'; Id='A11'; Provider='arxiv'; Query='("multi-party" OR "multi-user" OR "multi-principal") AND memory AND agent'; From='2023-01-01'; To='2026-08-24'; Limit=100; Pages=2; Lanes=@('paper','benchmark'); Windows=@('W_PRE_FRONTIER','W_ROLLING_12M','W_ROLLING_90D'); Gain='Multi-principal permissions and group-memory evaluation.' },
    @{ QueryId='Q033'; Id='A12'; Provider='arxiv'; Query='("decentralized memory" OR "federated memory") AND agent'; From='2023-01-01'; To='2026-08-24'; Limit=100; Pages=2; Lanes=@('paper'); Windows=@('W_PRE_FRONTIER','W_ROLLING_12M','W_ROLLING_90D'); Gain='Decentralized and federated topology alternatives.' },

    @{ QueryId='Q034'; Id='C01'; Provider='crossref'; Query='shared memory multi-agent large language model'; From='2025-08-25'; To='2026-08-24'; Limit=100; Pages=2; Lanes=@('paper'); Windows=@('W_ROLLING_12M'); Gain='Current DOI-indexed shared-memory papers.' },
    @{ QueryId='Q035'; Id='C02'; Provider='crossref'; Query='collaborative memory agents access control'; From='2023-01-01'; To='2026-08-24'; Limit=100; Pages=2; Lanes=@('paper','negative'); Windows=@('W_PRE_FRONTIER','W_ROLLING_12M','W_ROLLING_90D'); Gain='Permission and collaborative-memory terminology.' },
    @{ QueryId='Q036'; Id='C03'; Provider='crossref'; Query='transactive memory artificial intelligence agents'; From='2023-01-01'; To='2026-08-24'; Limit=100; Pages=2; Lanes=@('paper'); Windows=@('W_PRE_FRONTIER','W_ROLLING_12M','W_ROLLING_90D'); Gain='Transactive-memory roots and current agent work.' },
    @{ QueryId='Q037'; Id='C04'; Provider='crossref'; Query='blackboard multi-agent large language model'; From='2023-01-01'; To='2026-08-24'; Limit=100; Pages=2; Lanes=@('paper'); Windows=@('W_PRE_FRONTIER','W_ROLLING_12M','W_ROLLING_90D'); Gain='Blackboard and shared-state implementations in scholarly indexes.' },
    @{ QueryId='Q038'; Id='C05'; Provider='crossref'; Query='multi-agent experience sharing language models'; From='2023-01-01'; To='2026-08-24'; Limit=100; Pages=2; Lanes=@('paper'); Windows=@('W_PRE_FRONTIER','W_ROLLING_12M','W_ROLLING_90D'); Gain='Experience-transfer recall outside arXiv.' },
    @{ QueryId='Q039'; Id='C06'; Provider='crossref'; Query='multi-agent memory benchmark security'; From='2025-08-25'; To='2026-08-24'; Limit=100; Pages=2; Lanes=@('paper','benchmark','negative'); Windows=@('W_ROLLING_12M'); Gain='Current benchmark and security route.' },

    @{ QueryId='Q040'; Id='G01'; Provider='github-search'; Query='multi-agent memory'; Limit=100; Pages=2; Lanes=@('github','repository'); Windows=@('W_PRE_FRONTIER','W_ROLLING_12M','W_ROLLING_90D'); Gain='Broad implementation recall.' },
    @{ QueryId='Q041'; Id='G02'; Provider='github-search'; Query='shared memory ai agents'; Limit=100; Pages=2; Lanes=@('github','repository'); Windows=@('W_PRE_FRONTIER','W_ROLLING_12M','W_ROLLING_90D'); Gain='Cross-tool and fleet shared-memory implementations.' },
    @{ QueryId='Q042'; Id='G03'; Provider='github-search'; Query='subagent memory'; Limit=100; Pages=2; Lanes=@('github','repository'); Windows=@('W_PRE_FRONTIER','W_ROLLING_12M','W_ROLLING_90D'); Gain='Literal subagent-memory implementations.' },
    @{ QueryId='Q043'; Id='G04'; Provider='github-search'; Query='agent handoff context'; Limit=100; Pages=2; Lanes=@('github','repository'); Windows=@('W_PRE_FRONTIER','W_ROLLING_12M','W_ROLLING_90D'); Gain='Handoff and continuity artifacts.' },
    @{ QueryId='Q044'; Id='G05'; Provider='github-search'; Query='agent blackboard llm'; Limit=100; Pages=2; Lanes=@('github','repository'); Windows=@('W_PRE_FRONTIER','W_ROLLING_12M','W_ROLLING_90D'); Gain='Blackboard implementations.' },
    @{ QueryId='Q045'; Id='G06'; Provider='github-search'; Query='agent fleet memory'; Limit=100; Pages=2; Lanes=@('github','repository'); Windows=@('W_PRE_FRONTIER','W_ROLLING_12M','W_ROLLING_90D'); Gain='Fleet memory and governance.' },
    @{ QueryId='Q046'; Id='G07'; Provider='github-search'; Query='agent memory provenance'; Limit=100; Pages=2; Lanes=@('github','repository','negative'); Windows=@('W_PRE_FRONTIER','W_ROLLING_12M','W_ROLLING_90D'); Gain='Provenance-aware memory implementations.' },
    @{ QueryId='Q047'; Id='G08'; Provider='github-search'; Query='multi-agent state synchronization'; Limit=100; Pages=2; Lanes=@('github','repository'); Windows=@('W_PRE_FRONTIER','W_ROLLING_12M','W_ROLLING_90D'); Gain='Synchronization and shared-state candidates.' },
    @{ QueryId='Q048'; Id='G09'; Provider='github-search'; Query='multi-agent trajectory memory'; Limit=100; Pages=2; Lanes=@('github','repository'); Windows=@('W_PRE_FRONTIER','W_ROLLING_12M','W_ROLLING_90D'); Gain='Trajectory and population-memory code.' },
    @{ QueryId='Q049'; Id='G10'; Provider='github-search'; Query='coding agent shared memory'; Limit=100; Pages=2; Lanes=@('github','repository'); Windows=@('W_PRE_FRONTIER','W_ROLLING_12M','W_ROLLING_90D'); Gain='Coding-agent shared project state.' },
    @{ QueryId='Q050'; Id='G11'; Provider='github-search'; Query='research agent shared memory'; Limit=100; Pages=2; Lanes=@('github','repository'); Windows=@('W_PRE_FRONTIER','W_ROLLING_12M','W_ROLLING_90D'); Gain='Research-agent shared evidence and notes.' },
    @{ QueryId='Q051'; Id='G12'; Provider='github-search'; Query='mcp shared memory agents'; Limit=100; Pages=2; Lanes=@('github','repository'); Windows=@('W_PRE_FRONTIER','W_ROLLING_12M','W_ROLLING_90D'); Gain='MCP memory transport and cross-client stores.' },
    @{ QueryId='Q052'; Id='G13'; Provider='github-search'; Query='autogen memory agents'; Limit=100; Pages=2; Lanes=@('github','repository'); Windows=@('W_PRE_FRONTIER','W_ROLLING_12M','W_ROLLING_90D'); Gain='AutoGen-specific memory integrations.' },
    @{ QueryId='Q053'; Id='G14'; Provider='github-search'; Query='langgraph subagent memory'; Limit=100; Pages=2; Lanes=@('github','repository'); Windows=@('W_PRE_FRONTIER','W_ROLLING_12M','W_ROLLING_90D'); Gain='LangGraph subgraph, store and memory integrations.' },
    @{ QueryId='Q054'; Id='G15'; Provider='github-search'; Query='multi-agent memory'; From='2025-08-25'; To='2026-08-24'; DateField='created'; Limit=100; Pages=2; Lanes=@('github','repository'); Windows=@('W_ROLLING_12M'); Gain='Repositories created in the twelve-month frontier.' },
    @{ QueryId='Q055'; Id='G16'; Provider='github-search'; Query='subagent memory'; From='2025-08-25'; To='2026-08-24'; DateField='created'; Limit=100; Pages=2; Lanes=@('github','repository'); Windows=@('W_ROLLING_12M'); Gain='Recently created literal Subagent Memory projects.' },
    @{ QueryId='Q056'; Id='G17'; Provider='github-search'; Query='agent handoff memory'; From='2026-05-27'; To='2026-08-24'; DateField='created'; Limit=100; Pages=2; Lanes=@('github','repository'); Windows=@('W_ROLLING_90D'); Gain='New handoff-memory weak signals.' },
    @{ QueryId='Q057'; Id='G18'; Provider='github-search'; Query='shared memory ai agents'; From='2026-05-27'; To='2026-08-24'; DateField='pushed'; Limit=100; Pages=2; Lanes=@('github','repository'); Windows=@('W_ROLLING_90D'); Gain='Recently active shared-memory candidates.' },
    @{ QueryId='Q058'; Id='G19'; Provider='github-search'; Query='agent blackboard'; From='2026-05-27'; To='2026-08-24'; DateField='pushed'; Limit=100; Pages=2; Lanes=@('github','repository'); Windows=@('W_ROLLING_90D'); Gain='Recently active blackboard implementations.' },
    @{ QueryId='Q059'; Id='G20'; Provider='github-search'; Query='agent memory provenance'; From='2026-05-27'; To='2026-08-24'; DateField='pushed'; Limit=100; Pages=2; Lanes=@('github','repository','negative'); Windows=@('W_ROLLING_90D'); Gain='Recently active provenance-aware memory candidates.' }
)

$failuresPath = Join-Path $runRoot 'failures.jsonl'
foreach ($job in $jobs) {
    $output = Join-Path $runRoot ($job.Id + '.jsonl')
    $metadata = Join-Path $runRoot ($job.Id + '-run.json')
    if ((Test-Path -LiteralPath $output) -and (Test-Path -LiteralPath $metadata)) { continue }

    $rawDir = Join-Path $rawRoot $job.Id
    $arguments = @(
        'scripts\discover_frontier.py', $job.Provider,
        '--query', $job.Query,
        '--limit', [string]$job.Limit,
        '--pages', [string]$job.Pages,
        '--raw-dir', $rawDir,
        '--output', $output,
        '--metadata', $metadata,
        '--sleep', '0.35',
        '--retries', '3',
        '--backoff', '2'
    )
    if ($job.From) { $arguments += @('--from', $job.From) }
    if ($job.To) { $arguments += @('--to', $job.To) }
    if ($job.DateField) { $arguments += @('--github-date-field', $job.DateField) }

    & python @arguments
    if ($LASTEXITCODE -ne 0) {
        $failure = [ordered]@{
            query_id = $job.QueryId
            job_id = $job.Id
            provider = $job.Provider
            query = $job.Query
            failed_at = (Get-Date -AsUTC -Format o)
            exit_code = $LASTEXITCODE
            note = 'Provider request failed after configured retries; preserved as a coverage limitation.'
        } | ConvertTo-Json -Compress
        Add-Content -LiteralPath $failuresPath -Value $failure -Encoding utf8
    }
}

$specQueries = foreach ($job in $jobs) {
    $output = Join-Path $runRoot ($job.Id + '.jsonl')
    $metadata = Join-Path $runRoot ($job.Id + '-run.json')
    if (-not ((Test-Path -LiteralPath $output) -and (Test-Path -LiteralPath $metadata))) { continue }
    [ordered]@{
        query_id = $job.QueryId
        occurrence_jsonl = [System.IO.Path]::GetFileName($output)
        run_metadata = [System.IO.Path]::GetFileName($metadata)
        stage = 'discover'
        lanes = $job.Lanes
        windows = $job.Windows
        parents = @()
        gaps = @()
        information_gain = $job.Gain
    }
}

$spec = [ordered]@{ queries = @($specQueries) }
[System.IO.File]::WriteAllText((Join-Path $runRoot 'import-spec.json'), ($spec | ConvertTo-Json -Depth 10), [System.Text.UTF8Encoding]::new($false))
