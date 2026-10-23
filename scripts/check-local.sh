#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
command -v uv >/dev/null || { echo "uv is required" >&2; exit 127; }
uv lock --check
uv run --locked python -m compileall src addon
uv run --locked python scripts/bump_version.py --check
uv run --locked pytest -q
uv build
for version in 'mcp[cli]>=1.28.1,<2' 'mcp[cli]>=2,<3'; do
  uv run --locked --with "$version" freecad-mcp --help
  uv run --locked --with "$version" pytest -q
done
shopt -s nullglob
wheels=(dist/*.whl)
if [[ ${#wheels[@]} -ne 1 ]]; then echo "Expected exactly one built wheel under dist/, found ${#wheels[@]}" >&2; exit 1; fi
uv run --isolated --no-project --with "${wheels[0]}" python scripts/bump_version.py --check
uv run --isolated --no-project --with "${wheels[0]}" freecad-mcp --help
echo "FreeCAD MCP local checks passed"
