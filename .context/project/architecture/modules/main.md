---
id: MOD-MAIN
type: module
title: CLI Entrypoint
status: active
role: Parse argv and emit tool response envelope
boundary: Owns argparse and process-level exit behavior
depends_on: [MOD-CLI-MAPPER, MOD-TOOLS-DISPATCH]
provides: [SCH-TOOL-ENVELOPE, SCH-TOOL-ERROR]
consumes: []
must_not:
  - Must not contain business selection policy
invariants:
  - Always emit JSON envelope
related_flows: [FLOW-TOOL-DISPATCH]
links: [MOD-CLI-MAPPER, MOD-TOOLS-DISPATCH, SCH-TOOL-ENVELOPE]
---

# Main Module

Entrypoint for CLI command parsing, tool invocation, and envelope output.
