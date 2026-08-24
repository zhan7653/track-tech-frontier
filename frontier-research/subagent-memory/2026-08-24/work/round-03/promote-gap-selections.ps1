$ErrorActionPreference = 'Stop'

$bundle = 'D:\Code\track-tech-frontier\frontier-research\subagent-memory\2026-08-24'
$checkedAt = '2026-08-23T17:30:00Z'
$selections = @(
    @{ Id='E-dd4466ba0b1d5fed657f'; Clusters=@('SM-C06','SM-C03') },
    @{ Id='E-7e67b2313ef4d5539fc4'; Clusters=@('SM-C06') },
    @{ Id='E-81899f5024eabef5f882'; Clusters=@('SM-C01','SM-C08','SM-C03') },
    @{ Id='E-e22b43efc892ba3291fb'; Clusters=@('SM-C08') },
    @{ Id='E-b94f4285bcd2d0315272'; Clusters=@('SM-C08') },
    @{ Id='E-03f42722b0f4f8f64e6c'; Clusters=@('SM-C08') },
    @{ Id='E-545bab874300f16e3f07'; Clusters=@('SM-C01','SM-C08') },
    @{ Id='E-8e68bb4ef1a64c687173'; Clusters=@('SM-C08') },
    @{ Id='E-5807dd248c59ba4df873'; Clusters=@('SM-C08','SM-C05') },
    @{ Id='E-e6a00f0b68c8400978a0'; Clusters=@('SM-C08','SM-C01') },
    @{ Id='E-cb2d0a0bab1320def666'; Clusters=@('SM-C01','SM-C08') },
    @{ Id='E-8b52952bbf4ba88f86bc'; Clusters=@('SM-C01','SM-C08') },
    @{ Id='E-63f4d8e317bcf42bdc26'; Clusters=@('SM-C01','SM-C07') },
    @{ Id='E-5b4b0fa82d47ac084ece'; Clusters=@('SM-C06') },
    @{ Id='E-3dc1ab588fa4b7363416'; Clusters=@('SM-C01','SM-C08') },
    @{ Id='E-0d6c7a9829c068231d6f'; Clusters=@('SM-C08','SM-C06') },
    @{ Id='E-fe34d6911bee722ce71c'; Clusters=@('SM-C05','SM-C06') },
    @{ Id='E-c04f0329e54c36b188a8'; Clusters=@('SM-C01','SM-C08','SM-C02') },
    @{ Id='E-95c9acb517a5a5752009'; Clusters=@('SM-C06') },
    @{ Id='E-0a30a3d802a87e1c7873'; Clusters=@('SM-C04','SM-C05') },
    @{ Id='E-abc234890fda1937fe62'; Clusters=@('SM-C06') },
    @{ Id='E-b666c511823c69efc6da'; Clusters=@('SM-C06','SM-C04') },
    @{ Id='E-83c77c4d80b58090c88e'; Clusters=@('SM-C06','SM-C04') },
    @{ Id='E-29307b3a29dd5194bcbd'; Clusters=@('SM-C02','SM-C01') },
    @{ Id='E-5f2c073e5b9f57d3b1b6'; Clusters=@('SM-C01') },
    @{ Id='E-1a5cf3efa623abf66614'; Clusters=@('SM-C01','SM-C08') },
    @{ Id='E-f4cef789f57a6edd3120'; Clusters=@('SM-C02','SM-C07') },
    @{ Id='E-188c71b8c2c81a3e72bf'; Clusters=@('SM-C03','SM-C06','SM-C07') },
    @{ Id='E-c52e4fbd73fa90879319'; Clusters=@('SM-C04','SM-C05','SM-C01') },
    @{ Id='E-bb052dbcae5ea3cd4d8b'; Clusters=@('SM-C02','SM-C07') },
    @{ Id='E-2dbec917af784df6f009'; Clusters=@('SM-C06') }
)

$entityPath = Join-Path $bundle 'entities.jsonl'
$entities = @(Get-Content -LiteralPath $entityPath | ForEach-Object { $_ | ConvertFrom-Json })
$entityById = @{}
foreach ($entity in $entities) { $entityById[[string]$entity.entity_id] = $entity }

$screeningPath = Join-Path $bundle 'screening.jsonl'
$screeningLines = @(Get-Content -LiteralPath $screeningPath)
$screeningIds = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::Ordinal)
$screeningLines | ForEach-Object { [void]$screeningIds.Add([string](($_ | ConvertFrom-Json).screening_id)) }
$stagePath = Join-Path $bundle 'stage_events.jsonl'
$stageLines = @(Get-Content -LiteralPath $stagePath)
$stageIds = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::Ordinal)
$stageLines | ForEach-Object { [void]$stageIds.Add([string](($_ | ConvertFrom-Json).event_id)) }
$assignmentPath = Join-Path $bundle 'cluster_assignments.jsonl'
$assignmentLines = @(Get-Content -LiteralPath $assignmentPath)
$assignmentIds = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::Ordinal)
$assignmentLines | ForEach-Object { [void]$assignmentIds.Add([string](($_ | ConvertFrom-Json).assignment_id)) }

$newScreening = [System.Collections.Generic.List[string]]::new()
$newStage = [System.Collections.Generic.List[string]]::new()
$newAssignments = [System.Collections.Generic.List[string]]::new()
$promoted = 0

foreach ($selection in $selections) {
    $entity = $entityById[$selection.Id]
    if ($null -eq $entity) { throw "Missing selected entity: $($selection.Id)" }
    foreach ($discoveryId in $entity.discovery_ids) {
        $screeningId = 'SC-R3-' + ([string]$discoveryId).Substring(2)
        if ($screeningIds.Contains($screeningId)) { continue }
        $newScreening.Add(([ordered]@{
            screening_id=$screeningId; discovery_id=$discoveryId; decision='map';
            reason='Gap-directed manual selection for sparse inheritance, local-persistence or population-experience coverage; deep verification remains separate.';
            checked_at=$checkedAt
        } | ConvertTo-Json -Compress))
        [void]$screeningIds.Add($screeningId)
    }
    if ($entity.stage -eq 'discovered') {
        $entity.stage = 'mapped'
        $eventId = 'SE-R3-' + ([string]$entity.entity_id).Substring(2)
        if (-not $stageIds.Contains($eventId)) {
            $newStage.Add(([ordered]@{
                event_id=$eventId; entity_id=$entity.entity_id; from_stage='discovered'; to_stage='mapped'; occurred_at=$checkedAt;
                rationale='Gap-directed manual mapping for a sparse important branch.'
            } | ConvertTo-Json -Compress))
            [void]$stageIds.Add($eventId)
        }
        $promoted += 1
    }
    $position = 0
    foreach ($clusterId in $selection.Clusters) {
        $assignmentId = 'A-R3-' + ([string]$entity.entity_id).Substring(2) + '-' + $clusterId.Substring(3)
        if ($assignmentIds.Contains($assignmentId)) { continue }
        $newAssignments.Add(([ordered]@{
            assignment_id=$assignmentId; cluster_id=$clusterId; confidence='medium'; entity_id=$entity.entity_id;
            membership=if($position -eq 0){'primary'}else{'secondary'}; method='gap-directed manual mapping';
            rationale='Selected after inspecting sparse-branch candidates and the item title/abstract or repository description.'; time=$checkedAt
        } | ConvertTo-Json -Compress))
        [void]$assignmentIds.Add($assignmentId)
        $position += 1
    }
}

$utf8=[System.Text.UTF8Encoding]::new($false)
[System.IO.File]::WriteAllLines($entityPath, @($entities|ForEach-Object{$_|ConvertTo-Json -Depth 20 -Compress}), $utf8)
[System.IO.File]::WriteAllLines($screeningPath, @($screeningLines+$newScreening), $utf8)
[System.IO.File]::WriteAllLines($stagePath, @($stageLines+$newStage), $utf8)
[System.IO.File]::WriteAllLines($assignmentPath, @($assignmentLines+$newAssignments), $utf8)

[ordered]@{selected=$selections.Count;promoted=$promoted;screening_rows=$newScreening.Count;assignments=$newAssignments.Count}|ConvertTo-Json
