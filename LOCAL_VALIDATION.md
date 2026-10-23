# Local validation

Run `bash scripts/check-local.sh` with `uv` installed. Checks locked dependencies, compilation, version, pytest, sdist/wheel, installed-wheel CLI and both MCP major SDK ranges. Prefer a clean `dist/` directory; the script fails closed if more than one wheel is found. Run with Python 3.12 and 3.13 separately as needed. Capturing exact SHA and output for reviews is required. GitHub-hosted checks are removed; local execution remains unverified.
