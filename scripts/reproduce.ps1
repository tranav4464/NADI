$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
$python = Join-Path $repo '.venv\Scripts\python.exe'
& $python -m nadi.cli audit-resources
& $python -m nadi.cli prepare
& $python -m nadi.cli train-risk
& $python -m nadi.cli generate-hydraulics
& $python -m pytest (Join-Path $repo 'tests') -q
& $python -m nadi.cli run-demo --seed 20261118 --budget 3
& $python -m nadi.cli build-evidence
