// Shared mutable core of the pen host: the document registry, the
// renderer-facing event feed, and the logger. Imports none of its siblings.

import { EventEmitter } from 'node:events'

const log = {
  debug: (..._args: unknown[]) => {},
  info: (...args: unknown[]) => console.log('[pen]', ...args),
  warn: (...args: unknown[]) => console.warn('[pen]', ...args),
  error: (...args: unknown[]) => console.error('[pen]', ...args)
}

export interface PenDocumentInfo {
  docId: string
  fileURI: string
  displayName: string
}

export interface PenDocument {
  docId: string
  fileURI: string
  displayName: string
}

export const documents = new Map<string, PenDocument>()
export const events = new EventEmitter()

/** Renderer-facing change feed (documents opened/closed). */
export function onPenEvent(event: string, listener: (...args: any[]) => void): () => void {
  events.on(event, listener)

  return () => events.off(event, listener)
}

export { log }
