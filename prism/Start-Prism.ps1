param(
    [string[]]$RunDir,
    [ValidateRange(1, 65535)][int]$Port = 8765,
    [string]$Python,
    [switch]$NoBrowser
)
$ErrorActionPreference = 'Stop'
if (-not $RunDir) {
    $sampleRun = Join-Path $PSScriptRoot '../arena/exports/readiness-20261101/single-run'
    if (Test-Path -LiteralPath (Join-Path $sampleRun 'iteration-state.json')) {
        $RunDir = @($sampleRun)
    } else {
        throw 'Pass -RunDir with an Arena iterative run directory.'
    }
}
if (-not $Python) {
    $localPython = Join-Path $env:LOCALAPPDATA 'Programs/Python/Python311/python.exe'
    if (Test-Path -LiteralPath $localPython) {
        $Python = $localPython
    } else {
        $command = Get-Command python -ErrorAction SilentlyContinue
        if ($command -and $command.Source -notmatch 'WindowsApps') { $Python = $command.Source }
    }
}
if (-not $Python) { throw 'Python 3.11+ required. Pass -Python with the executable path.' }
$resolvedRuns = @($RunDir | ForEach-Object { (Resolve-Path -LiteralPath $_).Path })
$previousPythonPath = $env:PYTHONPATH
try {
    $env:PYTHONPATH = Join-Path $PSScriptRoot 'src'
    $prismArguments = @('-m', 'prism', 'serve', '--port', "$Port")
    foreach ($run in $resolvedRuns) { $prismArguments += @('--run-dir', $run) }
    if (-not $NoBrowser) { $prismArguments += '--open' }
    & $Python @prismArguments
    if ($LASTEXITCODE -ne 0) { throw "Prism exited with code $LASTEXITCODE" }
} finally {
    $env:PYTHONPATH = $previousPythonPath
}
