$ErrorActionPreference = 'Stop'

$bundle='D:\Code\track-tech-frontier\frontier-research\subagent-memory\2026-08-24'
$windows=@('W_PRE_FRONTIER','W_ROLLING_12M','W_ROLLING_90D')
$clusters=Get-Content -LiteralPath (Join-Path $bundle 'clusters.jsonl')|ForEach-Object{$_|ConvertFrom-Json}
$assignments=Get-Content -LiteralPath (Join-Path $bundle 'cluster_assignments.jsonl')|ForEach-Object{$_|ConvertFrom-Json}
$entityById=@{}
Get-Content -LiteralPath (Join-Path $bundle 'entities.jsonl')|ForEach-Object{$e=$_|ConvertFrom-Json;$entityById[$e.entity_id]=$e}

$manualLaneEntities=@{
    'SM-C01|benchmark'=@('E-cc1dd347e0acce5ec8e6')
    'SM-C01|negative'=@('E-cc1dd347e0acce5ec8e6','E-NEG002')
    'SM-C02|benchmark'=@('E-d87cf6c5b204c445ca08','E-7791537f505c3ca8e6e6','E-cf598e92eaf38159f31b')
    'SM-C02|negative'=@('E-d87cf6c5b204c445ca08','E-cf598e92eaf38159f31b')
    'SM-C03|benchmark'=@('E-79a0cab9c5744230877e')
    'SM-C03|negative'=@()
    'SM-C04|benchmark'=@('E-c7eebd719afe1ca81747','E-93fed05c0ea7c899435f','E-acc662e921435d2e8532','E-79a0cab9c5744230877e')
    'SM-C04|negative'=@('E-c7eebd719afe1ca81747','E-93fed05c0ea7c899435f','E-cf598e92eaf38159f31b')
    'SM-C05|benchmark'=@('E-738f837ea9126670daa6','E-47a626be6ce1fd38d858','E-73f73c532ad06bcc6187')
    'SM-C05|negative'=@('E-550735dab28c1bd588b7','E-NEG001','E-NEG002')
    'SM-C06|benchmark'=@('E-ba357fa153e2dd3eeea2','E-76e5fc9464465e7f9c4b','E-e29ba9f58fc41d31f9c5','E-71dcb6c6e4d8549ae376','E-73f73c532ad06bcc6187')
    'SM-C06|negative'=@('E-71dcb6c6e4d8549ae376')
    'SM-C07|benchmark'=@('E-738f837ea9126670daa6','E-ba357fa153e2dd3eeea2','E-e29ba9f58fc41d31f9c5','E-fb83c465f9b49395386f')
    'SM-C07|negative'=@('E-738f837ea9126670daa6','E-fb83c465f9b49395386f')
    'SM-C08|benchmark'=@()
    'SM-C08|negative'=@('E-NEG002')
}

$rows=[System.Collections.Generic.List[object]]::new()
foreach($cluster in $clusters){
    $assignedIds=@($assignments|Where-Object cluster_id -eq $cluster.cluster_id|ForEach-Object entity_id|Sort-Object -Unique)
    foreach($lane in $cluster.required_lanes){
        foreach($window in $windows){
            $ids=@()
            if($lane -eq 'paper'){$ids=@($assignedIds|Where-Object{$entityById[$_].entity_type -eq 'paper'})}
            elseif($lane -eq 'repository'){$ids=@($assignedIds|Where-Object{$entityById[$_].entity_type -eq 'repository'})}
            elseif($lane -eq 'product'){$ids=@($assignedIds|Where-Object{$entityById[$_].entity_type -eq 'product'})}
            elseif($manualLaneEntities.ContainsKey($cluster.cluster_id+'|'+$lane)){$ids=@($manualLaneEntities[$cluster.cluster_id+'|'+$lane])}

            if($lane -eq 'product' -and $window -in @('W_ROLLING_12M','W_ROLLING_90D')){
                $windowIds=@($ids)
            }else{
                $windowIds=@($ids|Where-Object{$entityById.ContainsKey($_) -and $entityById[$_].time_window_ids -contains $window})
            }
            $count=$windowIds.Count
            if($window -eq 'W_PRE_FRONTIER' -and $count -eq 0){$status='not-applicable'}
            elseif($count -eq 0){$status='gap'}
            else{
                $threshold=if($lane -in @('paper','repository')){5}elseif($lane -eq 'product'){2}else{2}
                $status=if($count -ge $threshold){'covered'}else{'partial'}
            }
            $rows.Add([ordered]@{
                cluster_id=$cluster.cluster_id;lane=$lane;window_id=$window;status=$status;
                entity_count=$count;entity_ids=$windowIds
            })
        }
    }
}

$utf8=[System.Text.UTF8Encoding]::new($false)
$gridLines=$rows|ForEach-Object{[ordered]@{cluster_id=$_.cluster_id;lane=$_.lane;status=$_.status;window_id=$_.window_id}|ConvertTo-Json -Compress}
[System.IO.File]::WriteAllLines((Join-Path $bundle 'cluster_coverage.jsonl'),$gridLines,$utf8)
$diagnostic=[ordered]@{
    generated_at=(Get-Date -AsUTC -Format o)
    rule='Counts are diagnostic. covered requires >=5 mapped paper/repository entities or >=2 product/benchmark/negative entities in the window; pre-frontier zero is not-applicable because the reader contract has no historical quota.'
    rows=$rows
}
[System.IO.File]::WriteAllText((Join-Path $bundle 'work\round-03\coverage-diagnostic.json'),($diagnostic|ConvertTo-Json -Depth 12),$utf8)

$rows|Group-Object status|Select-Object Count,Name|Format-Table -AutoSize
