$ErrorActionPreference = 'Stop'

$bundle = 'D:\Code\track-tech-frontier\frontier-research\subagent-memory\2026-08-24'
$inputPath = Join-Path $bundle 'discovery_results.jsonl'
$outputPath = Join-Path $bundle 'work\round-02\breadth-candidates.jsonl'
$summaryPath = Join-Path $bundle 'work\round-02\breadth-candidate-summary.json'

$clusterTerms = [ordered]@{
    'SM-C01' = @('subagent','sub-agent','spawn','handoff','delegation','inherit','context transfer','state transfer','agents as tools','manager agent')
    'SM-C02' = @('access control','permission','private memory','shared memory','scoped','scope','multi-tenant','multi-user','multi-principal','agent fleet','visibility','authorization')
    'SM-C03' = @('blackboard','shared workspace','shared state','memory service','shared memory','memory layer','filesystem','file-based','pub/sub','pubsub','event log','episode log')
    'SM-C04' = @('transaction','conflict','consistency','concurrency','json patch','patchboard','belief commit','version','supersed','stale','lattice','synchronization')
    'SM-C05' = @('consolidation','curator','critic','provenance','lineage','return','result envelope','summary','summariz','feedback','adjudicat')
    'SM-C06' = @('trajectory','experience sharing','skill sharing','skill transfer','transactive memory','decentralized memory','cross-model','procedural memory','replay','collective learning','self-evolving')
    'SM-C07' = @('retrieval','routing','search','rerank','context construction','context assembly','active navigation','who knows','subscription','inbox','action gate')
}

$strong = @(
    'subagent memory','sub-agent memory','multi-agent memory','multi agent memory',
    'shared memory','collaborative memory','transactive memory','decentralized memory',
    'hierarchical memory','memory collaboration','memory sharing','memory synchronization',
    'agent handoff','agent blackboard','shared agent memory','agent fleet memory'
)
$negative = @(
    'weak-memory isa','multiprocessor','neural architecture search','computer memory hierarchy',
    'memory allocation','out-of-memory','collective memory archive','historical memory',
    'cultural memory','social memory','holocaust memory','national memory'
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
    $proposed = [System.Collections.Generic.List[string]]::new()

    $hasAgent = $text -match 'agent|llm|language model'
    $hasMemoryState = $text -match 'memor|shared state|workspace|handoff|trajectory|experience|skill|provenance|blackboard'
    $hasMulti = $text -match 'multi-agent|multi agent|subagent|sub-agent|agent fleet|agent population|agent team|agent collaboration'
    if ($hasAgent) { $score += 2 }
    if ($hasMemoryState) { $score += 2 }
    if ($hasMulti) { $score += 3 }
    if ($hasAgent -and $hasMemoryState -and $hasMulti) { $score += 5 }

    foreach ($phrase in $strong) {
        if ($titleLower.Contains($phrase)) {
            $score += 10
            $signals.Add('title:' + $phrase)
        } elseif ($text.Contains($phrase)) {
            $score += 4
            $signals.Add('text:' + $phrase)
        }
    }
    foreach ($phrase in $negative) {
        if ($text.Contains($phrase) -and -not $hasMulti) {
            $score -= 15
            $signals.Add('negative:' + $phrase)
        }
    }

    foreach ($entry in $clusterTerms.GetEnumerator()) {
        $hits = 0
        foreach ($term in $entry.Value) {
            if ($text.Contains($term)) { $hits += 1 }
        }
        if ($hits -gt 0) {
            $proposed.Add([string]$entry.Key)
            $score += [Math]::Min(5, $hits)
        }
    }

    if ($score -ge 10) {
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
            proposed_clusters = @($proposed | Select-Object -Unique)
            signals = @($signals | Select-Object -Unique)
            discovery_ids = @($group.Group.discovery_id | Select-Object -Unique)
            query_ids = @($group.Group.query_id | Select-Object -Unique)
            abstract_or_description = if ($abstract) { $abstract } else { $description }
        }
    }
}

$ordered = @($candidates | Sort-Object -Property @{Expression={$_.score};Descending=$true}, @{Expression={$_.published_at};Descending=$true}, @{Expression={$_.title};Descending=$false})
$jsonLines = $ordered | ForEach-Object { $_ | ConvertTo-Json -Depth 10 -Compress }
$utf8 = [System.Text.UTF8Encoding]::new($false)
[System.IO.File]::WriteAllLines($outputPath, $jsonLines, $utf8)

$clusterCounts = [ordered]@{}
foreach ($clusterId in $clusterTerms.Keys) {
    $clusterCounts[$clusterId] = @($ordered | Where-Object { $_.proposed_clusters -contains $clusterId }).Count
}
$summary = [ordered]@{
    generated_at = (Get-Date -AsUTC -Format o)
    discovered_entities = $groups.Count
    breadth_candidates = $ordered.Count
    papers = @($ordered | Where-Object kind -eq 'paper').Count
    repositories = @($ordered | Where-Object kind -eq 'repository').Count
    score_bands = [ordered]@{
        score_35_plus = @($ordered | Where-Object score -ge 35).Count
        score_25_to_34 = @($ordered | Where-Object { $_.score -ge 25 -and $_.score -lt 35 }).Count
        score_18_to_24 = @($ordered | Where-Object { $_.score -ge 18 -and $_.score -lt 25 }).Count
        score_10_to_17 = @($ordered | Where-Object { $_.score -ge 10 -and $_.score -lt 18 }).Count
    }
    proposed_cluster_counts = $clusterCounts
    note = 'Heuristic breadth triage only. Scores and proposed clusters require manual inspection and are not relevance, quality, maturity, adoption, or final mapping judgments.'
}
[System.IO.File]::WriteAllText($summaryPath, ($summary | ConvertTo-Json -Depth 10), $utf8)
