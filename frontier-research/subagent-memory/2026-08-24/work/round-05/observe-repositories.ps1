$ErrorActionPreference='Stop'

$repoRoot='D:\Code\track-tech-frontier'
$bundle=Join-Path $repoRoot 'frontier-research\subagent-memory\2026-08-24'
$outRoot=Join-Path $bundle 'work\round-05\observations'
$rawRoot=Join-Path $outRoot 'raw'
New-Item -ItemType Directory -Path $outRoot,$rawRoot -Force|Out-Null
$repos=@(
    'openai/openai-agents-python','openai/codex','langchain-ai/langgraph','langchain-ai/deepagents',
    'microsoft/autogen','microsoft/UFO','caura-ai/caura','smaramwbc/statewave-multi-agent-memory','kimdanny/matm'
)
$failures=[System.Collections.Generic.List[string]]::new()
foreach($repo in $repos){
    $slug=$repo.Replace('/','--')
    $out=Join-Path $outRoot ($slug+'.jsonl')
    $meta=Join-Path $outRoot ($slug+'-run.json')
    if((Test-Path -LiteralPath $out)-and(Test-Path -LiteralPath $meta)){continue}
    $raw=Join-Path $rawRoot $slug
    & python scripts\discover_frontier.py github-observe --repo $repo --from 2026-05-27 --to 2026-08-24 --window-id W_ROLLING_90D --raw-dir $raw --output $out --metadata $meta
    if($LASTEXITCODE -ne 0){
        $failures.Add(([ordered]@{repository=$repo;failed_at=(Get-Date -AsUTC -Format o);exit_code=$LASTEXITCODE}|ConvertTo-Json -Compress))
    }
}
if($failures.Count){[System.IO.File]::WriteAllLines((Join-Path $outRoot 'failures.jsonl'),$failures,[System.Text.UTF8Encoding]::new($false))}
$observations=Get-ChildItem -LiteralPath $outRoot -Filter '*.jsonl' -File|Where-Object Name -ne 'failures.jsonl'|ForEach-Object{Get-Content -LiteralPath $_.FullName|ForEach-Object{$_|ConvertFrom-Json}}
[ordered]@{requested=$repos.Count;observed=@($observations).Count;failures=$failures.Count}|ConvertTo-Json
