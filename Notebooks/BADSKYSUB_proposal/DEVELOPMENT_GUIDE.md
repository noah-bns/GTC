# Testing the BADSKYSUB extraction change

## Version history

v3.0 + Noah Bensoussan, 16/11/2026

- Relocated the feature checkout and its dedicated virtual environment into
  the GTC folder.
- Added version-history entries and local annotations to each changed PypeIt
  source, test, and instrument documentation section.
- Renamed the dedicated environment to `.PypeIt-dev-venv` and clarified when
  the checkout and environment are used.

v3.1 + Noah Bensoussan, 17/11/2026

- Updated the extraction-time pixel slitmask to follow extraction eligibility,
  so the opt-in can actually supply pixels to the BADSKYSUB boxcar path.
- Clarified that object finding runs before the final BADSKYSUB flag is set;
  failed or absent object detections are not synthesized or extracted. The
  reported slit 137 was already found, but absent from the pixel slitmask.

## What is `PypeIt-dev`?

`PypeIt-dev` is a separate working copy of PypeIt's source code, based on the
`3.0.0` release and checked out on the `badskysub-no-sky-extraction` branch.
It is where the proposed source-code changes live. It is not a new Python
package name: Python still imports the package as `pypeit`.

The `.PypeIt-dev-venv` folder is the separate Python environment. It contains
Python and the dependencies needed to run this working copy without changing
the GTC project's existing `.venv`.

## When is `PypeIt-dev` used?

The modified code is used only when you run Python or PypeIt commands through
`.PypeIt-dev-venv`. That environment installs PypeIt in editable mode, which
means it imports `pypeit` directly from `PypeIt-dev`. Therefore, edits in that
checkout are picked up immediately. Running your usual GTC commands through
the GTC `.venv` continues to use its existing PypeIt installation and does
not use the prototype changes.

## Why use an editable PypeIt checkout?

PypeIt is installed and imported as the package `pypeit`. Renaming the library
to `pypeit_new` would require changing imports and packaging and risks mixing
the modified source with the installed package. The safer setup is a separate
PypeIt 3.0.0 source checkout, a feature branch, and a dedicated virtual
environment with that checkout installed in editable mode.

The prepared checkout is inside the GTC repository folder:

```text
C:\Users\noah.bensoussan\GTC\PypeIt-dev
```

The feature branch is `badskysub-no-sky-extraction`. The isolated environment
is:

```text
C:\Users\noah.bensoussan\GTC\.PypeIt-dev-venv
```

The GTC project's existing `.venv` and installed PypeIt package are not used
for development changes.

## Confirm which PypeIt Python imports

Run in PowerShell:

```powershell
& 'C:\Users\noah.bensoussan\GTC\.PypeIt-dev-venv\Scripts\python.exe' -c "import sys, pypeit; print(sys.executable); print(pypeit.__file__); print(pypeit.__version__)"
```

The executable should be `GTC\.PypeIt-dev-venv\Scripts\python.exe`, the
imported module should resolve under `GTC\PypeIt-dev\pypeit`, and the
checkout should be on the `badskysub-no-sky-extraction` branch based on the
`3.0.0` Git tag. Since this is an editable development install, the reported
package version may include a `.dev0` suffix. Source edits in the checkout
are used immediately.

If rebuilding the environment is needed, use the Python executable from the
GTC environment to create it, then install the PypeIt checkout with its test
dependencies:

```powershell
& 'C:\Users\noah.bensoussan\GTC\.venv\Scripts\python.exe' -m venv 'C:\Users\noah.bensoussan\GTC\.PypeIt-dev-venv'
& 'C:\Users\noah.bensoussan\GTC\.PypeIt-dev-venv\Scripts\python.exe' -m pip install -e 'C:\Users\noah.bensoussan\GTC\PypeIt-dev[test]'
```

The outer GTC `.gitignore` excludes only the nested development checkout and
its environment; use `git -C 'C:\Users\noah.bensoussan\GTC\PypeIt-dev' status`
to inspect the feature branch changes.

## What changed in PypeIt

- `pypeit/par/pypeitpar.py` defines `reduce.extraction.extract_badskysub`,
  defaulting to `False`.
- In `pypeit/extraction.py`, `Extract.__init__` determines the
  `gtc_osiris_plus` opt-in and extraction masks before calling
  `initialize_slits`. `initialize_slits` then builds the extraction pixel
  slitmask from the same eligibility mask. This gives an opted-in
  BADSKYSUB-only slit pixels in `self.slitmask`, while other blocking flags
  remain excluded. The original slit flag is retained.
- The BADSKYSUB path uses a boxcar over the science image with a zero sky
  model and skips both global and local spectral-flexure measurements for
  these slits.
- Object finding is intentionally unchanged. In the normal flow it runs
  before the final sky-subtraction attempt marks failed slits as `BADSKYSUB`;
  only objects already returned by object finding are passed to extraction.
  A failed or absent object detection remains unextracted.
- `pypeit/tests/test_badskysub_slitmask.py` is the proposal's new focused
  regression test. It checks that extraction's pixel slitmask includes
  eligible BADSKYSUB slits and still excludes slits blocked by another flag.
- The existing full-checkout tests for BADSKYSUB extraction and parameter
  parsing should also be run after applying these proposal files to the
  complete PypeIt checkout.
- `doc/spectrographs/gtc_osiris.rst` documents the option, its limitations,
  and flexure behavior.

## Run focused tests

From `C:\Users\noah.bensoussan\GTC\PypeIt-dev`:

```powershell
& 'C:\Users\noah.bensoussan\GTC\.PypeIt-dev-venv\Scripts\python.exe' -m pytest pypeit\tests\test_badskysub_extraction.py pypeit\tests\test_pypeitpar.py -q
```

Before a real reduction, keep `extract_badskysub = False` and verify normal
behavior is unchanged. Then enable it only in a copy of the GTC/OSIRIS
PypeIt file, reduce a representative exposure, and inspect both the 2D
sky-subtraction residuals and the extracted 1D spectrum. A produced spectrum
from a `BADSKYSUB` slit contains unsubtracted sky; it may be unsuitable for
science without further processing.
