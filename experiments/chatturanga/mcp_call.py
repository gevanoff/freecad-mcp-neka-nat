"""Exercise the real stdio MCP server; persist text and image responses.

Usage: python mcp_call.py request.json output-directory
The request is a list of {tool, arguments} entries. execute_code entries can
instead use code_file, resolved relative to the request file.
"""
import asyncio
import base64
import json
from pathlib import Path
import subprocess
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    request = Path(sys.argv[1]).resolve()
    output = Path(sys.argv[2]).resolve()
    output.mkdir(parents=True, exist_ok=True)
    root = Path(__file__).resolve().parents[2]
    parameters = StdioServerParameters(
        command=str(Path(sys.executable).with_name("freecad-mcp.exe")),
        args=["--host", "127.0.0.1"],
        cwd=str(root),
    )
    records = []
    async with stdio_client(parameters) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            available = await session.list_tools()
            (output / "tools.json").write_text(available.model_dump_json(indent=2), encoding="utf-8")
            for index, call in enumerate(json.loads(request.read_text(encoding="utf-8"))):
                args = dict(call.get("arguments", {}))
                if "code_file" in call:
                    args["code"] = (request.parent / call["code_file"]).read_text(encoding="utf-8")
                response = await session.call_tool(call["tool"], args)
                record = {"tool": call["tool"], "arguments": args, "isError": response.isError, "content": []}
                for block_index, block in enumerate(response.content):
                    if block.type == "image":
                        file = f"{index:02}-{block_index}-{call['tool']}.png"
                        (output / file).write_bytes(base64.b64decode(block.data))
                        record["content"].append({"type": "image", "file": file})
                    else:
                        record["content"].append(block.model_dump())
                records.append(record)
                (output / "responses.json").write_text(json.dumps(records, indent=2), encoding="utf-8")
                print(json.dumps({"tool": record["tool"], "isError": record["isError"], "content": record["content"]}), flush=True)
    (output / "revision.txt").write_text(subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True), encoding="utf-8")


if __name__ == "__main__":
    asyncio.run(main())
