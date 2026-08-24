$ErrorActionPreference='Stop'

$bundle='D:\Code\track-tech-frontier\frontier-research\subagent-memory\2026-08-24'
$pdfRoot=Join-Path $bundle 'tmp\pdfs\round-04'
New-Item -ItemType Directory -Path $pdfRoot -Force|Out-Null
$ids=@(
    '2605.08460','2602.07398','2604.09744','2604.14228','2602.13258',
    '2505.18279','2606.24535','2606.18829','2608.10509','2605.14498','2602.11510',
    '2605.29313','2606.14445','2510.01285','2507.07957',
    '2607.05844','2607.23929','2608.08236','2606.17182','2608.12984',
    '2606.00756','2601.22758','2605.04811','2605.16746','2606.04329','2607.14611',
    '2606.19911','2605.22721','2603.23234','2606.08702','2510.04851','2605.10064',
    '2606.18837','2603.18718','2511.10030','2605.09278','2506.07398','2608.00426',
    '2606.28349','2603.12631','2603.10062','2605.10481'
)

$manifestPath=Join-Path $pdfRoot 'download-manifest.jsonl'
$existing=@{}
if(Test-Path -LiteralPath $manifestPath){
    Get-Content -LiteralPath $manifestPath|ForEach-Object{$row=$_|ConvertFrom-Json;$existing[$row.arxiv_id]=$row}
}
$rows=[System.Collections.Generic.List[string]]::new()
foreach($id in $ids){
    $path=Join-Path $pdfRoot ($id+'.pdf')
    if(Test-Path -LiteralPath $path){continue}
    $url='https://arxiv.org/pdf/'+$id
    $started=Get-Date -AsUTC
    try{
        Invoke-WebRequest -Uri $url -OutFile $path -Headers @{'User-Agent'='track-tech-frontier/1.0'} -MaximumRetryCount 3 -RetryIntervalSec 2
        $item=Get-Item -LiteralPath $path
        $row=[ordered]@{arxiv_id=$id;url=$url;status='downloaded';bytes=$item.Length;started_at=$started.ToString('o');ended_at=(Get-Date -AsUTC -Format o);path=$path}
    }catch{
        $row=[ordered]@{arxiv_id=$id;url=$url;status='failed';bytes=$null;started_at=$started.ToString('o');ended_at=(Get-Date -AsUTC -Format o);path=$path;error=$_.Exception.Message}
    }
    $rows.Add(($row|ConvertTo-Json -Compress))
}
if($rows.Count -gt 0){Add-Content -LiteralPath $manifestPath -Value $rows -Encoding utf8}

[ordered]@{requested=$ids.Count;downloaded=(Get-ChildItem -LiteralPath $pdfRoot -Filter '*.pdf' -File).Count;failures=if(Test-Path -LiteralPath $manifestPath){@(Get-Content -LiteralPath $manifestPath|ForEach-Object{$_|ConvertFrom-Json}|Where-Object status -eq 'failed').Count}else{0}}|ConvertTo-Json
