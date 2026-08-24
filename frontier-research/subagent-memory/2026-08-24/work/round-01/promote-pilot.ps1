$ErrorActionPreference = 'Stop'

$bundle = 'D:\Code\track-tech-frontier\frontier-research\subagent-memory\2026-08-24'
$checkedAt = '2026-08-23T16:49:00Z'
$selected = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::Ordinal)
@(
    'E-738f837ea9126670daa6', 'E-acc662e921435d2e8532', 'E-cf598e92eaf38159f31b',
    'E-ba357fa153e2dd3eeea2', 'E-dee50844111acebbada9', 'E-970df532c829ed4cdde8',
    'E-e29ba9f58fc41d31f9c5', 'E-79a0cab9c5744230877e', 'E-76e5fc9464465e7f9c4b',
    'E-550735dab28c1bd588b7', 'E-fb83c465f9b49395386f', 'E-cc1dd347e0acce5ec8e6',
    'E-73f73c532ad06bcc6187', 'E-93fed05c0ea7c899435f', 'E-d87cf6c5b204c445ca08',
    'E-47a626be6ce1fd38d858', 'E-71dcb6c6e4d8549ae376', 'E-7791537f505c3ca8e6e6',
    'E-3de9b0393fe61ff1082d', 'E-fad4a3ce55347c2e3732', 'E-579d8cef0aa8ddd0a484',
    'E-26dc545ddf28608d4f89', 'E-475cf1357077a26661b3', 'E-d30b650acadfb1b8fc25',
    'E-5175534a78aeb5da81d5', 'E-dc2d1eef06d5ec3538f5', 'E-3c06113def93e462d408',
    'E-15485d04878c4de58699'
) | ForEach-Object { [void]$selected.Add($_) }

$entityPath = Join-Path $bundle 'entities.jsonl'
$entities = Get-Content -LiteralPath $entityPath | ForEach-Object { $_ | ConvertFrom-Json }
$stageEvents = [System.Collections.Generic.List[object]]::new()
$screening = [System.Collections.Generic.List[object]]::new()
$screeningPath = Join-Path $bundle 'screening.jsonl'
$existingScreening = if (Test-Path -LiteralPath $screeningPath) { @(Get-Content -LiteralPath $screeningPath) } else { @() }
$existingScreeningIds = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::Ordinal)
$existingScreening | ForEach-Object { [void]$existingScreeningIds.Add([string](($_ | ConvertFrom-Json).screening_id)) }

foreach ($entity in $entities) {
    if (-not $selected.Contains([string]$entity.entity_id)) { continue }
    if ($entity.stage -eq 'discovered') {
        $entity.stage = 'mapped'
        $stageEvents.Add([ordered]@{
            event_id = 'SE-R1-' + ([string]$entity.entity_id).Substring(2)
            entity_id = $entity.entity_id
            from_stage = 'discovered'
            to_stage = 'mapped'
            occurred_at = $checkedAt
            rationale = 'Manual Pilot review confirmed topic relevance and contribution to the initial Subagent Memory mechanism map.'
        })
    }
    foreach ($discoveryId in $entity.discovery_ids) {
        $screeningId = 'SC-R1-' + ([string]$discoveryId).Substring(2)
        if ($existingScreeningIds.Contains($screeningId)) { continue }
        $screening.Add([ordered]@{
            screening_id = $screeningId
            discovery_id = $discoveryId
            decision = 'map'
            reason = 'Identity and topic relevance confirmed during manual Pilot mapping; deep verification remains a separate promotion.'
            checked_at = $checkedAt
        })
    }
}

$utf8 = [System.Text.UTF8Encoding]::new($false)
$entityLines = $entities | ForEach-Object { $_ | ConvertTo-Json -Depth 20 -Compress }
[System.IO.File]::WriteAllLines($entityPath, $entityLines, $utf8)

$stagePath = Join-Path $bundle 'stage_events.jsonl'
$existingStage = if (Test-Path -LiteralPath $stagePath) { @(Get-Content -LiteralPath $stagePath) } else { @() }
$newStage = $stageEvents | ForEach-Object { $_ | ConvertTo-Json -Depth 8 -Compress }
[System.IO.File]::WriteAllLines($stagePath, @($existingStage + $newStage), $utf8)

$newScreening = $screening | ForEach-Object { $_ | ConvertTo-Json -Depth 8 -Compress }
[System.IO.File]::WriteAllLines($screeningPath, @($existingScreening + $newScreening), $utf8)

[ordered]@{
    selected = $selected.Count
    promoted = $stageEvents.Count
    screening_rows = $screening.Count
} | ConvertTo-Json
