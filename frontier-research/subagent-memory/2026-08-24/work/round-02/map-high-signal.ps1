$ErrorActionPreference = 'Stop'

$bundle = 'D:\Code\track-tech-frontier\frontier-research\subagent-memory\2026-08-24'
$candidatePath = Join-Path $bundle 'work\round-02\breadth-candidates.jsonl'
$checkedAt = '2026-08-23T17:20:00Z'
$excludeTitles = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
@(
    'Long Context Scaling: Divide and Conquer via Multi-Agent Question-driven Collaboration',
    'LLM Agent Swarm for Hypothesis-Driven Drug Discovery',
    'Chow-Liu Ordering for Long-Context Reasoning in Chain-of-Agents'
) | ForEach-Object { [void]$excludeTitles.Add($_) }

$candidates = Get-Content -LiteralPath $candidatePath | ForEach-Object { $_ | ConvertFrom-Json }
$eligible = foreach ($candidate in $candidates) {
    if ($candidate.score -lt 18) { continue }
    $text = ($candidate.title + ' ' + $candidate.abstract_or_description).ToLowerInvariant()
    $title = $candidate.title.ToLowerInvariant()
    if ($candidate.kind -eq 'paper') {
        $centralTitle = $title -match 'memor|state|context|handoff|blackboard|provenance|trajectory|skill|inherit|coordination|communication|trust|security|privacy|jailbreak|protocol|persistence|agent network|agent swarm'
        $multiAgent = $text -match 'multi-agent|multi agent|subagent|agent team|agent population'
        if (-not ($centralTitle -and $multiAgent)) { continue }
    } else {
        $memoryMechanism = $text -match 'memor|blackboard|handoff|shared state|shared workspace|provenance'
        $multiAgent = $text -match 'multi-agent|multi agent|subagent|agent fleet|agent team|agent collaboration|shared memory'
        if (-not ($memoryMechanism -and $multiAgent)) { continue }
    }
    $candidate
}

$entityPath = Join-Path $bundle 'entities.jsonl'
$entities = @(Get-Content -LiteralPath $entityPath | ForEach-Object { $_ | ConvertFrom-Json })
$entityByIdentifier = @{}
foreach ($entity in $entities) { $entityByIdentifier[[string]$entity.identifier] = $entity }

$screeningPath = Join-Path $bundle 'screening.jsonl'
$screeningLines = if (Test-Path -LiteralPath $screeningPath) { @(Get-Content -LiteralPath $screeningPath) } else { @() }
$screeningIds = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::Ordinal)
$screeningLines | ForEach-Object { [void]$screeningIds.Add([string](($_ | ConvertFrom-Json).screening_id)) }

$stagePath = Join-Path $bundle 'stage_events.jsonl'
$stageLines = if (Test-Path -LiteralPath $stagePath) { @(Get-Content -LiteralPath $stagePath) } else { @() }
$stageIds = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::Ordinal)
$stageLines | ForEach-Object { [void]$stageIds.Add([string](($_ | ConvertFrom-Json).event_id)) }

$assignmentPath = Join-Path $bundle 'cluster_assignments.jsonl'
$assignmentLines = if (Test-Path -LiteralPath $assignmentPath) { @(Get-Content -LiteralPath $assignmentPath) } else { @() }
$assignmentIds = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::Ordinal)
$assignmentLines | ForEach-Object { [void]$assignmentIds.Add([string](($_ | ConvertFrom-Json).assignment_id)) }

$newScreening = [System.Collections.Generic.List[string]]::new()
$newStage = [System.Collections.Generic.List[string]]::new()
$newAssignments = [System.Collections.Generic.List[string]]::new()
$promoted = 0
$mappedCandidates = 0
$deferredCandidates = 0

foreach ($candidate in $eligible) {
    $entity = $entityByIdentifier[[string]$candidate.identifier]
    if ($null -eq $entity) { continue }
    $isExcluded = $excludeTitles.Contains([string]$candidate.title)
    $decision = if ($isExcluded) { 'defer' } else { 'map' }
    $reason = if ($isExcluded) {
        'High-recall query collision: multi-agent context/security relevance is adjacent, but the item does not yet establish a core Subagent Memory lifecycle mechanism.'
    } else {
        'High-signal breadth candidate passed manual rule and stratified-sample review; identity, date and direct cross-agent memory/state relevance are sufficient for map-stage use only.'
    }

    foreach ($discoveryId in $entity.discovery_ids) {
        $screeningId = 'SC-R2-' + ([string]$discoveryId).Substring(2)
        if ($screeningIds.Contains($screeningId)) { continue }
        $row = [ordered]@{
            screening_id = $screeningId
            discovery_id = $discoveryId
            decision = $decision
            reason = $reason
            checked_at = $checkedAt
        } | ConvertTo-Json -Depth 8 -Compress
        $newScreening.Add($row)
        [void]$screeningIds.Add($screeningId)
    }

    if ($isExcluded) {
        $deferredCandidates += 1
        continue
    }
    $mappedCandidates += 1

    if ($entity.stage -eq 'discovered') {
        $entity.stage = 'mapped'
        $eventId = 'SE-R2-' + ([string]$entity.entity_id).Substring(2)
        if (-not $stageIds.Contains($eventId)) {
            $row = [ordered]@{
                event_id = $eventId
                entity_id = $entity.entity_id
                from_stage = 'discovered'
                to_stage = 'mapped'
                occurred_at = $checkedAt
                rationale = 'Round 02 high-signal breadth mapping after manual rule and stratified-sample review; deep verification remains separate.'
            } | ConvertTo-Json -Depth 8 -Compress
            $newStage.Add($row)
            [void]$stageIds.Add($eventId)
        }
        $promoted += 1
    }

    $clusters = [System.Collections.Generic.List[string]]::new()
    foreach ($clusterId in $candidate.proposed_clusters) {
        if (-not $clusters.Contains([string]$clusterId)) { $clusters.Add([string]$clusterId) }
    }
    $text = ($candidate.title + ' ' + $candidate.abstract_or_description).ToLowerInvariant()
    if ($text -match 'subagent|sub-agent' -and $text -match 'persist|memor|checkpoint|session|cross-project|cross-session') {
        if (-not $clusters.Contains('SM-C08')) { $clusters.Insert(0, 'SM-C08') }
    }
    if ($clusters.Count -eq 0) { $clusters.Add('SM-C03') }

    $position = 0
    foreach ($clusterId in @($clusters | Select-Object -First 3)) {
        $assignmentId = 'A-R2-' + ([string]$entity.entity_id).Substring(2) + '-' + $clusterId.Substring(3)
        if ($assignmentIds.Contains($assignmentId)) { continue }
        $row = [ordered]@{
            assignment_id = $assignmentId
            cluster_id = $clusterId
            confidence = if ($candidate.score -ge 25) { 'medium' } else { 'low' }
            entity_id = $entity.entity_id
            membership = if ($position -eq 0) { 'primary' } else { 'secondary' }
            method = 'heuristic breadth mapping after manual rule and stratified-sample review'
            rationale = "Candidate score $($candidate.score) and mechanism terms support map-stage membership; this is not a quality or deep-evidence judgment."
            time = $checkedAt
        } | ConvertTo-Json -Depth 8 -Compress
        $newAssignments.Add($row)
        [void]$assignmentIds.Add($assignmentId)
        $position += 1
    }
}

$utf8 = [System.Text.UTF8Encoding]::new($false)
$entityLines = $entities | ForEach-Object { $_ | ConvertTo-Json -Depth 20 -Compress }
[System.IO.File]::WriteAllLines($entityPath, $entityLines, $utf8)
[System.IO.File]::WriteAllLines($screeningPath, @($screeningLines + $newScreening), $utf8)
[System.IO.File]::WriteAllLines($stagePath, @($stageLines + $newStage), $utf8)
[System.IO.File]::WriteAllLines($assignmentPath, @($assignmentLines + $newAssignments), $utf8)

[ordered]@{
    eligible = @($eligible).Count
    mapped_candidates = $mappedCandidates
    deferred_candidates = $deferredCandidates
    newly_promoted = $promoted
    new_screening_rows = $newScreening.Count
    new_assignments = $newAssignments.Count
} | ConvertTo-Json
