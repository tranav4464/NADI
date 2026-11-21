<#!
Downloads the immediately accessible, priority NADI network data identified in
docs/NADI_DATA_READINESS_AUDIT_2026-11-19.md. It never creates labels or
hydraulic scenarios. Every downloaded file receives a SHA-256 in the manifest.
#>

[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$resourcesRoot = [System.IO.Path]::GetFullPath((Join-Path $projectRoot '..\nadi_resources'))
$destination = Join-Path $resourcesRoot 'datasets\NADI_NETWORK_PRIORITY_2026_11_19'
New-Item -ItemType Directory -Force -Path $destination | Out-Null

$manifest = [System.Collections.Generic.List[object]]::new()

function Add-ManifestRecord {
    param(
        [string]$Dataset,
        [string]$Origin,
        [string]$SourceUrl,
        [string]$EvidenceType,
        [string]$ClaimBoundary,
        [string]$Status,
        [string]$RelativePath = '',
        [string]$ErrorMessage = ''
    )

    $sha256 = ''
    $bytes = $null
    if ($RelativePath) {
        $absolutePath = Join-Path $destination $RelativePath
        if (Test-Path -LiteralPath $absolutePath -PathType Leaf) {
            $sha256 = (Get-FileHash -LiteralPath $absolutePath -Algorithm SHA256).Hash.ToLowerInvariant()
            $bytes = (Get-Item -LiteralPath $absolutePath).Length
        }
    }

    $manifest.Add([ordered]@{
        acquired_utc = [DateTime]::UtcNow.ToString('o')
        dataset = $Dataset
        origin = $Origin
        source_url = $SourceUrl
        evidence_type = $EvidenceType
        claim_boundary = $ClaimBoundary
        status = $Status
        relative_path = $RelativePath
        bytes = $bytes
        sha256 = $sha256
        error = $ErrorMessage
    })
}

function Download-File {
    param(
        [string]$Dataset,
        [string]$Origin,
        [string]$SourceUrl,
        [string]$RelativePath,
        [string]$EvidenceType,
        [string]$ClaimBoundary
    )

    $outputPath = Join-Path $destination $RelativePath
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $outputPath) | Out-Null
    try {
        Invoke-WebRequest -Uri $SourceUrl -OutFile $outputPath -UseBasicParsing -Headers @{ 'User-Agent' = 'NADI-data-acquisition/1.0' } -TimeoutSec 180
        Add-ManifestRecord -Dataset $Dataset -Origin $Origin -SourceUrl $SourceUrl -EvidenceType $EvidenceType -ClaimBoundary $ClaimBoundary -Status 'DOWNLOADED' -RelativePath $RelativePath
        Write-Host "Downloaded: $RelativePath"
    }
    catch {
        if (Test-Path -LiteralPath $outputPath) { Remove-Item -LiteralPath $outputPath -Force }
        Add-ManifestRecord -Dataset $Dataset -Origin $Origin -SourceUrl $SourceUrl -EvidenceType $EvidenceType -ClaimBoundary $ClaimBoundary -Status 'FAILED' -RelativePath $RelativePath -ErrorMessage $_.Exception.Message
        Write-Warning "Failed: $RelativePath :: $($_.Exception.Message)"
    }
}

# Slovak utility: observed hourly anomaly scores and verified leak-proximity labels.
$slovak = Invoke-RestMethod -Uri 'https://zenodo.org/api/records/15096167' -TimeoutSec 60
foreach ($file in $slovak.files) {
    Download-File -Dataset 'Slovak utility operational/leak dataset' -Origin 'AUTHENTIC_OBSERVED' -SourceUrl $file.links.self -RelativePath (Join-Path 'slovak_utility_zenodo_15096167' $file.key) -EvidenceType 'hourly operational and leak evidence' -ClaimBoundary 'No topology and no microbiological endpoint; use only as operational/intrusion evidence.'
}

# IIT Bombay: India-relevant intermittent/flow-starved WaterGEMS model.
$iitb = Invoke-RestMethod -Uri 'https://zenodo.org/api/records/7162154' -TimeoutSec 60
foreach ($file in $iitb.files) {
    Download-File -Dataset 'IIT Bombay flow-starved Indian WaterGEMS model' -Origin 'MODEL_INPUT' -SourceUrl $file.links.self -RelativePath (Join-Path 'iitb_flow_starved_zenodo_7162154' $file.key) -EvidenceType 'India-relevant network model' -ClaimBoundary 'Network model only. Any simulated movement or contamination outcome remains SIMULATED.'
}

# City D: public field leak repair records; do not claim the unshared model was acquired.
$cityDBase = 'https://raw.githubusercontent.com/mutianwei521/wdsgpu/main/datasets'
foreach ($file in @('README.md', 'SHA256SUMS.txt', 'city_d_leak_records.csv', 'city_d_leak_records.json')) {
    Download-File -Dataset 'City D municipal field leak records' -Origin 'AUTHENTIC_OBSERVED' -SourceUrl "$cityDBase/$file" -RelativePath (Join-Path 'city_d_field_leaks' $file) -EvidenceType 'field leak repair work orders' -ClaimBoundary 'No E. coli labels. Do not infer a full network topology from node identifiers alone.'
}

# One real-system-derived EPANET topology. This direct source may return HTTP 403;
# it is retained as an explicit acquisition attempt rather than silently replaced.
Download-File -Dataset 'Kentucky KY1 real-system-derived topology' -Origin 'REAL_SYSTEM_DERIVED_MODEL' -SourceUrl 'https://uknowledge.uky.edu/cgi/viewcontent.cgi?article=1002&context=wdst&filename=1&type=additional' -RelativePath 'kentucky_ky1\KY1.inp' -EvidenceType 'EPANET topology and hydraulic model' -ClaimBoundary 'Real-system-derived topology; no paired microbial or event outcome data.'

# Mendeley's public record pages expose a stable public ZIP endpoint.
Download-File -Dataset 'Lira Uganda piped-water microbiology and chemistry' -Origin 'AUTHENTIC_OBSERVED' -SourceUrl 'https://data.mendeley.com/public-api/zip/jv6drgtvzc/download/1' -RelativePath 'lira_uganda_mendeley_jv6drgtvzc\lira_uganda_water_quality.zip' -EvidenceType 'E. coli/chemistry/GPS piped-water samples' -ClaimBoundary 'No topology or operations; use for drinking-water microbial endpoint/transfer analysis only.'
Download-File -Dataset 'Texas physical pipe-network leak benchmark' -Origin 'AUTHENTIC_OBSERVED' -SourceUrl 'https://data.mendeley.com/public-api/zip/tbrnp6vrnj/download/1' -RelativePath 'texas_physical_pipe_testbed_tbrnp6vrnj\texas_pipe_leak_benchmark.zip' -EvidenceType 'controlled physical pipe-network pressure/acoustic leak measurements' -ClaimBoundary 'No microbial endpoint; use as physical hydraulic validation only.'

$manifestPath = Join-Path $destination 'acquisition_manifest.json'
$manifest | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $manifestPath -Encoding utf8
Write-Host "Manifest: $manifestPath"
