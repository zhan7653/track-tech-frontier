$ErrorActionPreference='Stop'

$bundle='D:\Code\track-tech-frontier\frontier-research\subagent-memory\2026-08-24'
$cloneRoot=Join-Path $bundle 'tmp\repositories\round-05'
$manifestPath=Join-Path $bundle 'work\round-05\clone-manifest.jsonl'
New-Item -ItemType Directory -Path $cloneRoot -Force|Out-Null

$repositories=@(
    'openai/openai-agents-python',
    'openai/codex',
    'langchain-ai/langgraph',
    'langchain-ai/deepagents',
    'microsoft/autogen',
    'microsoft/UFO',
    'caura-ai/caura',
    'smaramwbc/statewave-multi-agent-memory',
    'kimdanny/matm',
    'MehulG/memX'
)

$records=[System.Collections.Generic.List[string]]::new()
foreach($repo in $repositories){
    $slug=$repo.Replace('/','--')
    $target=Join-Path $cloneRoot $slug
    $started=Get-Date -AsUTC
    try{
        if(-not (Test-Path -LiteralPath (Join-Path $target '.git'))){
            & gh repo clone $repo $target -- --depth 1
            if($LASTEXITCODE -ne 0){throw "gh repo clone exited $LASTEXITCODE"}
        }
        $commit=(& git -C $target rev-parse HEAD).Trim()
        $tree=(& git -C $target rev-parse 'HEAD^{tree}').Trim()
        $commitTime=(& git -C $target show -s --format=%cI HEAD).Trim()
        $release=$null
        $releaseJson=& gh api ('repos/'+$repo+'/releases/latest') 2>$null
        if($LASTEXITCODE -eq 0){
            $releaseObject=$releaseJson|ConvertFrom-Json
            $release=[ordered]@{tag_name=$releaseObject.tag_name;published_at=$releaseObject.published_at;html_url=$releaseObject.html_url}
        }
        $record=[ordered]@{repository=$repo;status='cloned';path=$target;commit=$commit;tree=$tree;commit_time=$commitTime;latest_release=$release;started_at=$started.ToString('o');ended_at=(Get-Date -AsUTC -Format o)}
    }catch{
        $record=[ordered]@{repository=$repo;status='failed';path=$target;started_at=$started.ToString('o');ended_at=(Get-Date -AsUTC -Format o);error=$_.Exception.Message}
    }
    $records.Add(($record|ConvertTo-Json -Depth 8 -Compress))
}
[System.IO.File]::WriteAllLines($manifestPath,$records,[System.Text.UTF8Encoding]::new($false))
$parsed=$records|ForEach-Object{$_|ConvertFrom-Json}
[ordered]@{requested=$repositories.Count;cloned=@($parsed|Where-Object status -eq 'cloned').Count;failed=@($parsed|Where-Object status -eq 'failed').Count}|ConvertTo-Json
