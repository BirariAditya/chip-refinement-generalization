param(
    [switch]$Setup,
    [ValidateSet('superblue18')][string]$Benchmark = 'superblue18',
    [ValidatePattern('^[A-Za-z0-9_-]+$')][string]$RunName = 'native194'
)

# Isolated native CPU component execution. This does not build DREAMPlace.
$reproCache = Join-Path $env:USERPROFILE '.cache/chip-refinement-reproduction'
$reproSource = Join-Path $reproCache 'macro-regulator'
$reproPython = Join-Path $reproCache '.venv/Scripts/python.exe'
$reproArchive = Join-Path $reproCache 'downloads/iccad2015.ot.zip'
$reproCommit = 'fe475473c86121bd09e031b6329f18e2d8b9d5ce'
$reproArchiveSha = '295120fa9f4e46013b68f90ed29603827e9768b84844c461c576881baa8e627a'

function Invoke-Checked {
    param([string]$Executable, [string[]]$Arguments)
    & $Executable @Arguments
    if ($LASTEXITCODE -ne 0) { throw ('Command failed: ' + $Executable) }
}

if ($Setup) {
    New-Item -ItemType Directory -Force -Path $reproCache | Out-Null
    Invoke-Checked uv @('python','install','3.8.20')
    if (-not (Test-Path -LiteralPath $reproPython)) {
        Invoke-Checked uv @('venv','--python','3.8.20',(Join-Path $reproCache '.venv'))
    }
    if (-not (Test-Path -LiteralPath (Join-Path $reproSource '.git'))) {
        Invoke-Checked git @('clone','https://github.com/lamda-bbo/macro-regulator.git',$reproSource)
        Invoke-Checked git @('-C',$reproSource,'checkout',$reproCommit)
    }
    Invoke-Checked uv @('pip','install','--python',$reproPython,'--index-url',
        'https://download.pytorch.org/whl/cpu','torch==1.7.1+cpu',
        'torchvision==0.8.2+cpu','torchaudio==0.7.2')
    Invoke-Checked uv @('pip','install','--python',$reproPython,
        'numpy==1.21.2','pillow==8.4.0','PyYAML==5.3.1','gym==0.22.0',
        'Shapely==2.0.4','matplotlib==3.4.3','cairocffi==1.7.0','tqdm==4.61.2',
        'tensorboard==2.14.0','scikit-learn==1.3.2')
    if (-not (Test-Path -LiteralPath $reproArchive)) {
        New-Item -ItemType Directory -Force -Path (Split-Path -Parent $reproArchive) | Out-Null
        Invoke-Checked uvx @('--python','3.8.20','--from','gdown==5.2.0','gdown','--fuzzy',
            'https://drive.google.com/file/d/1JEC17FmL2cM8BEAewENvRyG6aWxH53mX/view?usp=sharing',
            '-O',$reproArchive)
    }
}

if (-not (Test-Path -LiteralPath $reproPython)) { throw 'Run this script with -Setup first.' }
$reproActualCommit = (& git -C $reproSource rev-parse HEAD).Trim()
if ($reproActualCommit -ne $reproCommit) { throw 'Vendor checkout is not the pinned commit; inspect it before continuing.' }
$reproTrackedDiff = (& git -C $reproSource diff --stat | Out-String).Trim()
if ($reproTrackedDiff) { throw 'Vendor tracked files have local modifications. Preserve and inspect them before running.' }
$reproActualSha = (Get-FileHash -LiteralPath $reproArchive -Algorithm SHA256).Hash.ToLowerInvariant()
if ($reproActualSha -ne $reproArchiveSha) { throw 'Benchmark archive hash mismatch.' }

$reproExtract = @'
import pathlib, sys, zipfile
archive, destination, benchmark = sys.argv[1:]
root = pathlib.Path(destination).resolve()
with zipfile.ZipFile(archive) as data:
    for member in data.infolist():
        if not member.filename.startswith(benchmark + '/'):
            continue
        target = (root / member.filename).resolve()
        if root not in target.parents:
            raise ValueError('Unsafe archive path')
        if not target.exists():
            data.extract(member, str(root))
'@
Invoke-Checked $reproPython @('-c',$reproExtract,$reproArchive,(Join-Path $reproSource 'benchmark'),$Benchmark)
$env:PYTHONHASHSEED = '3'
$env:PYTHONUNBUFFERED = '1'
$reproArtifacts = Join-Path $PSScriptRoot 'artifacts'
$reproNative = Join-Path $reproArtifacts $RunName
New-Item -ItemType Directory -Force -Path $reproNative | Out-Null
Invoke-Checked $reproPython @((Join-Path $PSScriptRoot 'checkpoint_smoke.py'),
    '--source',$reproSource,'--output',(Join-Path $reproArtifacts 'checkpoint_smoke.json'))
Invoke-Checked $reproPython @((Join-Path $PSScriptRoot 'real_circuit_component.py'),
    '--source',$reproSource,'--benchmark',$Benchmark,'--canvas-mode','native',
    '--output-dir',$reproNative)
Invoke-Checked $reproPython @((Join-Path $PSScriptRoot 'audit_macro_hpwl.py'),
    '--source',$reproSource,'--artifact-dir',$reproNative)
Write-Output ('Component execution complete: ' + (Join-Path $reproNative 'real_circuit_component.json'))
Write-Output 'DREAMPlace global HPWL, routing, PPA and training were not executed.'
