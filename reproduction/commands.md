# Commands actually executed

Date: 17 October 2026. Paths below describe this local execution. Vendor source was first inspected in a temporary clone, then cloned without hard links into a durable external cache. Its origin was set to the official URL; tracked source remains pristine at `fe475473c86121bd09e031b6329f18e2d8b9d5ce`.

## Isolated setup

```powershell
uv python install 3.8
$reproRoot = Join-Path $env:USERPROFILE '.cache/chip-refinement-reproduction'
uv venv --python 3.8 (Join-Path $reproRoot '.venv')
git clone --no-hardlinks `
  (Join-Path $env:TEMP 'chip-rl-source-audit/macro-regulator') `
  (Join-Path $reproRoot 'macro-regulator')
git -C (Join-Path $reproRoot 'macro-regulator') remote set-url origin `
  https://github.com/lamda-bbo/macro-regulator.git
$reproPython = Join-Path $reproRoot '.venv/Scripts/python.exe'
uv pip install --python $reproPython --index-url https://download.pytorch.org/whl/cpu `
  'torch==1.7.1+cpu' 'torchvision==0.8.2+cpu'
uv pip install --python $reproPython `
  'numpy==1.21.2' 'pillow==8.4.0' 'gym==0.22.0' 'matplotlib==3.4.3' `
  'Shapely==2.0.4' 'tqdm==4.61.2' 'scikit-learn==1.3.2' `
  'tensorboard==2.14.0' 'cairocffi==1.7.0' 'PyYAML==6.0.3'
uv pip install --python $reproPython 'PyYAML==5.3.1'
uv pip install --python $reproPython --index-url https://download.pytorch.org/whl/cpu `
  'torchaudio==0.7.2'
```

All exited successfully. The initially installed PyYAML 6.0.3 was explicitly replaced with upstream's 5.3.1 before experiments. Torch's first install resolved NumPy 1.24.4; the second command replaced it with the upstream pin 1.21.2. Final environment versions, rather than transient resolutions, are recorded in `artifacts/environment_freeze.txt`.

## Data acquisition and extraction

```powershell
$reproArchive = Join-Path $reproRoot 'downloads/iccad2015.ot.zip'
uvx --python 3.8 --from 'gdown==5.2.0' gdown --fuzzy `
  'https://drive.google.com/file/d/1JEC17FmL2cM8BEAewENvRyG6aWxH53mX/view?usp=sharing' `
  -O $reproArchive
```

The download completed: 530,920,224 bytes; SHA-256 `295120fa9f4e46013b68f90ed29603827e9768b84844c461c576881baa8e627a`. A Python `zipfile` inspection found 66 entries, 2,309,686,707 uncompressed bytes. Only members beginning with `superblue18/` were extracted: 9 entries, 516,143,939 bytes. See `artifacts/benchmark_extract.txt` and the extracted-file hashes in `artifacts/manifest.json`. The one-command script reproduces this extraction.

## Official checkpoint execution

```powershell
$reproSource = Join-Path $reproRoot 'macro-regulator'
& $reproPython .\reproduction\checkpoint_smoke.py --source $reproSource `
  --output .\reproduction\artifacts\checkpoint_smoke.json
```

Exit 0. The original constructor downloaded its required ImageNet ResNet-18 initializer, about 44.7 MiB. The official full model checkpoint then loaded with the original strict `load_state_dict` calls. No model-layer or tensor-shape adaptation was used. Console: `artifacts/checkpoint_smoke.txt`.

## Original end-to-end entry point

From the official checkout's `src` directory:

```powershell
& $reproPython main.py '--benchmark_train=[]' '--benchmark_eval=[superblue18]' `
  '--check_point_path=../policy/pretrained_model.pkl' '--eval_policy=True' `
  '--use_cuda=False' '--n_dmp_eval=1'
```

Exit 1: `ModuleNotFoundError: No module named 'DREAMPlace'`. This happened during imports before any whole-pipeline placement metric could be produced. Console: `artifacts/original_entrypoint.txt`.

## Native CPU backend configuration attempt

```powershell
uv pip install --python $reproPython 'cmake==3.27.9' 'ninja==1.11.1.1'
$reproScripts = Join-Path $reproRoot '.venv/Scripts'
& (Join-Path $reproScripts 'cmake.exe') `
  -S (Join-Path $reproSource 'DREAMPlace_source') `
  -B (Join-Path $reproRoot 'build-windows-cpu') -G Ninja `
  ('-DCMAKE_MAKE_PROGRAM=' + (Join-Path $reproScripts 'ninja.exe')) `
  '-DCMAKE_CXX_COMPILER=C:/msys64/mingw64/bin/g++.exe' `
  ('-DPython_EXECUTABLE=' + $reproPython) `
  ('-DCMAKE_INSTALL_PREFIX=' + (Join-Path $reproSource 'DREAMPlace'))
```

Package install succeeded. Configuration exit 1: required Boost headers not found. It first detected GCC 15.2, Python 3.8.20 with development components, Torch 1.7, CPU mode, OpenMP 4.5 and ZLIB 1.3.1. No compiled backend or fake configure module was installed into the source checkout. Console: `artifacts/dreamplace_configure.txt`.

## Real-circuit component experiment

```powershell
$env:PYTHONHASHSEED = '3'
& $reproPython .\reproduction\real_circuit_component.py --source $reproSource `
  --canvas-mode native --output-dir .\reproduction\artifacts\native194
& $reproPython .\reproduction\audit_macro_hpwl.py --source $reproSource `
  --artifact-dir .\reproduction\artifacts\native194
```

Both final corrected commands exited 0. Native active canvas remained 194, policy grid 224. Saved results cover one original-policy pass and one greedy pass, each with 512 legal sampled/selected actions, on authentic superblue18 selected nets. Detailed adapter deviations are embedded in the result JSON and README.

An earlier full-canvas diagnostic and the first audit attempt completed their calculations but failed at JSON serialization of NumPy scalar values. The adapter now serializes such values via `.item()`, saves per-pass results/positions immediately and completed the final native-canvas run. The diagnostic's failure trace is retained in `artifacts/real_circuit_component.txt`; the successful final logs are `artifacts/native194_console.txt` and `artifacts/native194_metric_audit_console.txt`.

## Checks performed after execution

- Compiled all three Python adapter files using the isolated Python's `py_compile`.
- Parsed `run_local.ps1` with the PowerShell language parser: no syntax errors. Then executed the complete cached wrapper once using `pwsh -NoProfile -File reproduction/run_local.ps1 -RunName native194_integration`; exit 0. The separate integration folder preserves the first result. Console: `artifacts/local_wrapper_integration.txt`. Final comparison: `artifacts/integration_verification.json`.
- Verified original tracked vendor files have an empty `git diff --stat`.
- Computed SHA-256 of archive, checkpoint, all extracted benchmark files and Python adapters.
- Inspected the resulting three-panel plot.
- Independently checked rectangle geometry and selected-net pin HPWL, then decomposed the disagreement with upstream macro HPWL per net. The helper omits nets using its x-coordinate/height condition; this is not a validation of global HPWL, routing or PPA.
