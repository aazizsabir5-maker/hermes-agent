// Pen canvas host — Hermes embeds pen.dev's hosted editor.
//
//   - library.ts    canvas files (~/.hermes/pens) + status / open / rename
//   - documents.ts  create / open / close (one live document)
//   - sessions.ts   chat ↔ canvas ties (persist across launches)
//   - embed-url.ts  stay on /new?embed
//   - web-bridge.ts MessagePort embed protocol (storage + mcp-tool-call)
//   - wire.ts       ipcMain + webview attach (called once from main)
//   - state.ts      document registry + event feed

export { closeDocument, closeOtherPenDocuments, documentIsOpen, shutdownPenHost } from './documents'
export { isPenWebUrl } from './embed-url'
export { deletePenCanvas, openPenCanvas, penCanvasUrl, penLibrary, type PenLibraryItem, penStatus, type PenStatus, renamePenCanvas } from './library'
export { onPenEvent, type PenDocumentInfo } from './state'
export { type PenToolResult, runPenTool } from './web-bridge'
export { attachPenWebGuest, bindPenWebGuest, repaintPenWebTheme, shutdownPenWebBridge } from './web-bridge'
export { syncPenWebTheme, wirePenCanvas } from './wire'
