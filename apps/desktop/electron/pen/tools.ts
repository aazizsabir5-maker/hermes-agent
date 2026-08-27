// Agent tool surface: every canvas op except open/close is an MCP tool call
// through the embed bridge. Tool names are discovered live (get-mcp-schema);
// this module does not keep a catalog.

import { runWebPenTool } from './web-bridge'

export interface PenToolResult {
  success: boolean
  result?: unknown
  error?: string
}

export async function runPenTool(name: string, payload: Record<string, unknown>): Promise<PenToolResult> {
  return runWebPenTool(name, payload || {})
}
