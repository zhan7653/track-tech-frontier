$ErrorActionPreference = 'Stop'

$bundle = 'D:\Code\track-tech-frontier\frontier-research\subagent-memory\2026-08-24'
$inputPath = Join-Path $bundle 'discovery_results.jsonl'
$outputPath = Join-Path $bundle 'work\round-01\pilot-candidates.jsonl'
$summaryPath = Join-Path $bundle 'work\round-01\pilot-candidate-summary.json'

$strongPhrases = @(
    'subagent', 'sub-agent', 'multi-agent memory', 'multi agent memory',
    'shared memory', 'collaborative memory', 'collective memory',
    'transactive memory', 'decentralized memory', 'hierarchical memory',
    'memory collaboration', 'memory sharing', 'memory synchronization',
    'handoff memory', 'blackboard', 'state contamination', 'memory poisoning'
)
$mechanismPhrases = @(
    'handoff', 'provenance', 'conflict', 'transaction', 'concurren',
    'access control', 'permission', 'scope', 'shared state', 'knowledge sharing',
    'experience sharing', 'skill sharing', 'trajectory', 'workspace',
    'context transfer', 'state transfer', 'kv cache', 'agent fleet'
)
$negativePhrases = @(
    'weak-memory isa', 'multiprocessor', 'neural architecture search',
    'computer memory hierarchy', 'memory allocation', 'out-of-memory'
)

$groups = Get-Content -LiteralPath $inputPath | ForEach-Object { $_ | ConvertFrom-Json } | Group-Object identifier
$candidates = foreach ($group in $groups) {
    $first = $group.Group[0]
    $entity = $first.metadata.entity
    $title = [string]$entity.title
    $description = [string]$entity.description
    $abstract = [string]$entity.abstract
    $topics = (($entity.topics | ForEach-Object { [string]$_ }) -join ' ')
    $text = ($title + ' ' + $description + ' ' + $abstract + ' ' + $topics).ToLowerInvariant()
    $titleLower = $title.ToLowerInvariant()
    $score = 0
    $signals = [System.Collections.Generic.List[string]]::new()

    if ($text -match 'agent') { $score += 1 }
    if ($text -match 'memor|state|context|knowledge|experience|skill|handoff|blackboard') { $score += 1 }
    foreach ($phrase in $strongPhrases) {
        if ($titleLower.Contains($phrase)) {
            $score += 7
            $signals.Add('title:' + $phrase)
        } elseif ($text.Contains($phrase)) {
            $score += 3
            $signals.Add('text:' + $phrase)
        }
    }
    foreach ($phrase in $mechanismPhrases) {
        if ($titleLower.Contains($phrase)) {
            $score += 4
            $signals.Add('title:' + $phrase)
        } elseif ($text.Contains($phrase)) {
            $score += 1
            $signals.Add('text:' + $phrase)
        }
    }
    foreach ($phrase in $negativePhrases) {
        if ($text.Contains($phrase)) {
            $score -= 8
            $signals.Add('negative:' + $phrase)
        }
    }

    if ($score -ge 4) {
        [ordered]@{
            identifier = $first.identifier
            title = $title
            url = $first.url
            kind = $entity.kind
            published_at = $entity.published_at
            created_at = $entity.created_at
            pushed_at = $entity.pushed_at
            stars = $entity.stars
            score = $score
            signals = @($signals | Select-Object -Unique)
            discovery_ids = @($group.Group.discovery_id | Select-Object -Unique)
            query_ids = @($group.Group.query_id | Select-Object -Unique)
            abstract_or_description = if ($abstract) { $abstract } else { $description }
        }
    }
}

$ordered = @($candidates | Sort-Object @{ Expression = 'score'; Descending = $true }, @{ Expression = 'published_at'; Descending = $true }, title)
$jsonLines = $ordered | ForEach-Object { $_ | ConvertTo-Json -Depth 8 -Compress }
[System.IO.File]::WriteAllLines($outputPath, $jsonLines, [System.Text.UTF8Encoding]::new($false))

$summary = [ordered]@{
    generated_at = (Get-Date -AsUTC -Format o)
    discovered_entities = $groups.Count
    pilot_candidates = $ordered.Count
    papers = @($ordered | Where-Object kind -eq 'paper').Count
    repositories = @($ordered | Where-Object kind -eq 'repository').Count
    score_bands = [ordered]@{
        score_20_plus = @($ordered | Where-Object score -ge 20).Count
        score_12_to_19 = @($ordered | Where-Object { $_.score -ge 12 -and $_.score -lt 20 }).Count
        score_4_to_11 = @($ordered | Where-Object { $_.score -ge 4 -and $_.score -lt 12 }).Count
    }
    note = 'Heuristic pilot triage only. Scores guide manual mapping and are not quality, relevance, maturity, or adoption judgments.'
}
[System.IO.File]::WriteAllText($summaryPath, ($summary | ConvertTo-Json -Depth 8), [System.Text.UTF8Encoding]::new($false))
