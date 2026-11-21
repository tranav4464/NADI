$ErrorActionPreference = 'Stop'
$env:OMP_NUM_THREADS = '1'
$env:MKL_NUM_THREADS = '1'
$repo = Split-Path -Parent $PSScriptRoot
$python = Join-Path $repo '.venv\Scripts\python.exe'
& $python -m nadi.cli audit-resources
& $python -m nadi.cli prepare
& $python -m nadi.cli train-risk
& $python -m nadi.cli generate-hydraulics
& $python -m pytest (Join-Path $repo 'tests') -q
& $python -m nadi.cli run-demo --seed 20261118 --budget 3
& $python -m nadi.cli build-evidence
& $python (Join-Path $repo 'scripts/update_resource_manifest_authentic.py')
$liraWorkbook = Join-Path (Split-Path -Parent $repo) 'nadi_resources\datasets\NADI_NETWORK_PRIORITY_2026_11_19\lira_uganda_mendeley_jv6drgtvzc\extracted\A water quality dataset of physicochemical, microb\Water Quality dataset Final.xlsx'
if (Test-Path -LiteralPath $liraWorkbook) {
  & $python (Join-Path $repo 'scripts/audit_lira_piped_water.py') --input $liraWorkbook
} else {
  Write-Warning 'Lira workbook not present; skipping optional external drinking-water endpoint audit.'
}
& $python (Join-Path $repo 'scripts/evaluate_bristol_telemetry.py')
& $python (Join-Path $repo 'scripts/build_performance_matrix.py')
& $python (Join-Path $repo 'scripts/run_sdaif_ablations.py')
& $python (Join-Path $repo 'scripts/build_repro_manifest.py')
& $python (Join-Path $repo 'scripts/audit_claim_boundaries.py')
& $python (Join-Path $repo 'scripts/audit_xylem_submission_pack.py')
& $python (Join-Path $repo 'scripts/audit_prior_art_repos.py')
& $python (Join-Path $repo 'scripts/replicate_prior_art_smoke.py')
& $python (Join-Path $repo 'scripts/reconstruct_open_ecoli_on_real_marion.py')
& $python (Join-Path $repo 'scripts/train_ea_ecoli_authentic.py')
& $python (Join-Path $repo 'scripts/train_ea_physchem_panel.py')
& $python (Join-Path $repo 'scripts/evaluate_ea_physchem_geographic_holdout.py')
& $python (Join-Path $repo 'scripts/download_ea_openmeteo_weather_panel.py')
& $python (Join-Path $repo 'scripts/train_ea_weather_enriched_holdout.py')
& $python (Join-Path $repo 'scripts/replicate_open_ecoli_xgb_authentic_subset.py')
& $python (Join-Path $repo 'scripts/evaluate_wds_eventdb.py')
