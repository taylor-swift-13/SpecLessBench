param(
    [string]$QcipRoot = '\\wsl.localhost\Ubuntu-22.04\home\yangfp\QCIP',
    [string]$XiZiRoot = '\\wsl.localhost\Ubuntu-22.04\home\yangfp\crtos\Ubiquitous\XiZi_IIoT_Macro'
)

$ErrorActionPreference = 'Stop'
$workspace = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$bank = Join-Path $workspace 'benchmarks/source-material'
$selection = Get-Content (Join-Path $bank 'import-selection.json') -Raw | ConvertFrom-Json
$localAudit = Get-Content (Join-Path $workspace 'benchmarks/research/qcip-source-audit.json') -Raw | ConvertFrom-Json
$webAudit = Get-Content (Join-Path $workspace 'benchmarks/research/web-source-audit.json') -Raw | ConvertFrom-Json

function Hash-Bytes([byte[]]$Bytes) {
    return [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($Bytes)).ToLowerInvariant()
}

function Save-Snapshot([string]$Relative, [byte[]]$Bytes, [string]$Expected) {
    $digest = Hash-Bytes $Bytes
    if ($Expected -and $digest -ne $Expected) { throw "Source drift: $Relative" }
    $destination = Join-Path $bank $Relative
    [IO.Directory]::CreateDirectory([IO.Path]::GetDirectoryName($destination)) | Out-Null
    [IO.File]::WriteAllBytes($destination, $Bytes)
    return $digest
}

$records = @()
foreach ($relative in $selection.qcip_paths) {
    $source = @($localAudit.files | Where-Object path -EQ $relative)
    if ($source.Count -ne 1) { throw "Missing audit entry: $relative" }
    $bytes = [IO.File]::ReadAllBytes((Join-Path $QcipRoot $relative))
    $target = 'qcip/' + $relative
    $digest = Save-Snapshot $target $bytes $source[0].sha256
    $lineage = if ($relative.StartsWith('OUTPUT/xizi/')) { 'XiZi MulanPSL-2.0 lineage; QCIP annotations/adaptations' } else { 'QCIP MIT; retain per-file notices' }
    $records += @{
        source = 'QCIP'; source_path = $relative; destination = $target; sha256 = $digest
        repository_head = $localAudit.repository_head; matches_head_blob = $source[0].matches_head_blob
        git_status = $source[0].git_status; license_lineage = $lineage
        contains_source_annotations = [Text.Encoding]::UTF8.GetString($bytes).Contains('/*@')
        evaluation_ready = $false
    }
}

foreach ($relative in $selection.vst_paths) {
    $source = @($webAudit.files | Where-Object path -EQ $relative)
    if ($source.Count -ne 1) { throw "Missing web audit entry: $relative" }
    $response = Invoke-WebRequest -Uri $source[0].url
    $bytes = $response.RawContentStream.ToArray()
    $target = 'vst/' + $relative
    $digest = Save-Snapshot $target $bytes $source[0].sha256
    $records += @{
        source = 'VST'; source_path = $relative; source_url = $source[0].url
        destination = $target; sha256 = $digest; repository_head = $webAudit.revision
        license_lineage = 'BSD-2-Clause under VST LICENSE for progs'; evaluation_ready = $false
    }
}

$licenseRecords = @()
foreach ($item in @(
    @{ origin = (Join-Path $QcipRoot 'LICENSE'); target = 'licenses/QCIP-MIT.txt' },
    @{ origin = (Join-Path $XiZiRoot 'LICENSE'); target = 'licenses/XiZi-MulanPSL-2.0.txt' }
)) {
    $bytes = [IO.File]::ReadAllBytes($item.origin)
    $digest = Save-Snapshot $item.target $bytes ''
    $licenseRecords += @{ destination = $item.target; sha256 = $digest }
}
$vstLicense = @($webAudit.files | Where-Object path -EQ 'LICENSE')[0]
$response = Invoke-WebRequest -Uri $vstLicense.url
$licenseRecords += @{
    destination = 'licenses/VST-LICENSE.txt'
    sha256 = (Save-Snapshot 'licenses/VST-LICENSE.txt' $response.RawContentStream.ToArray() $vstLicense.sha256)
}

$report = @{
    schema_version = 1; import_date = (Get-Date -Format 'yyyy-MM-dd'); source_file_count = $records.Count
    method = 'Exact raw-byte snapshots checked against source-inspection hashes; no compilation or proof checking.'
    agent_facing = $false; files = $records; licenses = $licenseRecords
}
[IO.File]::WriteAllText((Join-Path $bank 'import-manifest.json'), ($report | ConvertTo-Json -Depth 8) + "`n", [Text.UTF8Encoding]::new($false))
Write-Output "Imported $($records.Count) curator C snapshots; source hashes matched; no proofs run."
