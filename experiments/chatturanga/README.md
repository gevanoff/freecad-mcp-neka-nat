# Chatturanga MCP branch experiment

Outcome: build a simple foot-soldier study through the actual stdio MCP server,
then save an editable FreeCAD document and verify STEP/STL exchange geometry.
This is a project-inspired pawn form, not a historical reconstruction or a change
to the Android game's approved assets.

Geometry: millimetres, Z up, centered on XY, flat base at Z=0. Base diameter
22 mm, overall height 31.5 mm. Four overlapping parametric primitives feed one
refined Boolean union. No physical print, material strength, or fit is claimed.

Baseline: neka-nat/freecad-mcp at
`78bf0230a03324b56c9a0b7f55150fb5be2a0d42`, package/addon 0.1.27.
FreeCAD 1.1.4 Windows x86-64 (bundled Python 3.11), external Python 3.14.2,
locked MCP SDK 1.30.0. Official portable archive SHA256:
`4828741fc91ee37fafcdb97a1abacb18b04ba451ac4372d9ff7a7349b36f4d6d`.
Winget verified the installer but launch returned 0x800704c7; the official
portable distribution was extracted successfully instead. uv's automatic 3.12
installation failed; the existing supported 3.14 interpreter was selected.

## Reproduce

Install `addon/FreeCADMCP` in the running FreeCAD user Mod directory and start
its RPC server (or launch `start_rpc.FCMacro`). Keep the default loopback-only
listener. Use the same addon revision as the checkout; restart FreeCAD after
changing it. Install dependencies with `uv sync --locked` using a supported
external interpreter. From the repo root:

```powershell
.venv\Scripts\python.exe experiments\chatturanga\mcp_call.py experiments\chatturanga\pilot.json experiments\chatturanga\results\baseline
.venv\Scripts\python.exe -m pytest -q tests\test_property_link_list.py
```

Start each pilot with no open document named ChatturangaPilot. The runner uses
MCP initialize, tools/list, and tools/call over stdio, not direct FreeCAD scripting
in place of the MCP. It records tool errors rather than exiting at the first
failure, so its exit code alone is not an acceptance check.

## A/B contract

- A: `experiment/chatturanga-baseline`, unchanged production code, red regression
  tests and captured live failure. Original upstream suite: 248 passed, 1 skipped.
- B: `fix/json-link-list-properties`, identical pilot and environment, corrected
  JSON link-list conversion, regression tests, export/reimport checks.
- Main gate: create_object Part::MultiFuse accepts the four existing object
  names, returns success, and produces one valid solid with the declared bounds.
- Regression gates: preserve list order, support other PropertyLinkList fields,
  reject missing/malformed references without replacing an existing list, allow
  clearing links, preserve ordinary string-list values.

This is a deterministic baseline-versus-fix comparison by one agent using the
coding and modeling playbooks. It is not a blinded or independent experiment
measuring the playbooks' effect on agent performance.
