// Pen canvas host — Hermes embeds pen.dev's hosted editor.
//
//   - library.ts    canvas files (~/.hermes/pens) + status / open / rename
//   - documents.ts  create / open / close (one live document)
//   - web-bridge.ts MessagePort embed protocol (storage + mcp-tool-call)
//   - tools.ts      agent tool proxy (forwards to the live editor schema)
//   - state.ts      document registry + event feed
//
// The renderer loads app.pen.dev/new?embed in a <webview>. Hermes owns the
// .pen file; the editor talks to us over the documented embed port.

export { closeDocument, closeOtherPenDocuments, documentIsOpen, shutdownPenHost } from './documents'
export { deletePenCanvas, openPenCanvas, penCanvasUrl, penLibrary, type PenLibraryItem, penStatus, type PenStatus, renamePenCanvas } from './library'
export { onPenEvent, type PenDocumentInfo } from './state'
export { type PenToolResult, runPenTool } from './tools'
export { bindPenWebGuest, isPenWebUrl, repaintPenWebTheme, shutdownPenWebBridge } from './web-bridge'
