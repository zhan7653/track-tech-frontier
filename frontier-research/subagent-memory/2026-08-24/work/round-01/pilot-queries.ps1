$ErrorActionPreference = 'Stop'

$repo = 'D:\Code\track-tech-frontier'
$runRoot = Join-Path $repo 'frontier-research\subagent-memory\2026-08-24\work\round-01\pilot'
$rawRoot = Join-Path $runRoot 'raw'
New-Item -ItemType Directory -Path $runRoot -Force | Out-Null
New-Item -ItemType Directory -Path $rawRoot -Force | Out-Null

$jobs = @(
    @{ Id = 'P01'; Provider = 'arxiv'; Query = '"multi-agent" AND memory AND (LLM OR "language model")'; From = '2025-08-25'; To = '2026-08-24'; Limit = 100; Pages = 2 },
    @{ Id = 'P02'; Provider = 'arxiv'; Query = '("shared memory" OR "collective memory" OR "collaborative memory") AND ("LLM agent" OR "language model agent")'; From = '2000-01-01'; To = '2026-08-24'; Limit = 100; Pages = 2 },
    @{ Id = 'P03'; Provider = 'semantic-scholar'; Query = 'multi-agent shared memory LLM agents'; From = '2025-08-25'; To = '2026-08-24'; Limit = 100; Pages = 1 },
    @{ Id = 'P04'; Provider = 'semantic-scholar'; Query = 'hierarchical agent memory handoff subagent'; From = '2000-01-01'; To = '2026-08-24'; Limit = 100; Pages = 1 },
    @{ Id = 'P05'; Provider = 'crossref'; Query = 'multi-agent shared memory large language model agents'; From = '2025-08-25'; To = '2026-08-24'; Limit = 100; Pages = 2 },
    @{ Id = 'P06'; Provider = 'crossref'; Query = 'collective memory collaborative agents language models'; From = '2000-01-01'; To = '2026-08-24'; Limit = 100; Pages = 2 },
    @{ Id = 'G01'; Provider = 'github-search'; Query = 'multi-agent memory llm'; Limit = 100; Pages = 2 },
    @{ Id = 'G02'; Provider = 'github-search'; Query = 'shared memory ai agents'; Limit = 100; Pages = 2 },
    @{ Id = 'G03'; Provider = 'github-search'; Query = 'subagent memory'; From = '2025-08-25'; To = '2026-08-24'; DateField = 'created'; Limit = 100; Pages = 2 },
    @{ Id = 'G04'; Provider = 'github-search'; Query = 'agent handoff memory'; From = '2026-05-27'; To = '2026-08-24'; DateField = 'pushed'; Limit = 100; Pages = 2 },
    @{ Id = 'G05'; Provider = 'github-search'; Query = 'blackboard llm agents'; Limit = 100; Pages = 2 },
    @{ Id = 'G06'; Provider = 'github-search'; Query = 'multi-agent memory'; From = '2026-05-27'; To = '2026-08-24'; DateField = 'created'; Limit = 100; Pages = 2 }
)

foreach ($job in $jobs) {
    $output = Join-Path $runRoot ($job.Id + '.jsonl')
    $metadata = Join-Path $runRoot ($job.Id + '-run.json')
    if ((Test-Path -LiteralPath $output) -and (Test-Path -LiteralPath $metadata)) {
        continue
    }
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
        '--retries', '4',
        '--backoff', '2'
    )
    if ($job.From) { $arguments += @('--from', $job.From) }
    if ($job.To) { $arguments += @('--to', $job.To) }
    if ($job.DateField) { $arguments += @('--github-date-field', $job.DateField) }

    & python @arguments
    if ($LASTEXITCODE -ne 0) {
        $failure = [ordered]@{
            job_id = $job.Id
            provider = $job.Provider
            query = $job.Query
            failed_at = (Get-Date -AsUTC -Format o)
            exit_code = $LASTEXITCODE
            note = 'Provider request failed after configured retries; preserved as a coverage limitation.'
        } | ConvertTo-Json -Compress
        Add-Content -LiteralPath (Join-Path $runRoot 'failures.jsonl') -Value $failure -Encoding utf8
        continue
    }
}
