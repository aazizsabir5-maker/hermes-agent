// Canvas library + status: what canvases exist, opening documents, availability
// for the renderer. Always available — the hosted editor needs no local install.

import path from 'node:path'
import { fileURLToPath } from 'node:url'

import { deletePenFromLibrary, listPenLibrary, type PenLibraryEntry, penLibraryRoot, penWebEditorUrl, renamePenInLibrary } from '../pen-host'

import { closeDocument, createDocument, describeDocument, openDocument } from './documents'
import { documents, type PenDocumentInfo } from './state'

export interface PenStatus {
  available: boolean
  loggedIn: boolean
  version: string
  running: boolean
  openDocuments: PenDocumentInfo[]
  /** Always null — no Pen.app icon to borrow. Renderer falls back to a glyph. */
  icon: null | string
}

export function penStatus(): PenStatus {
  return {
    available: true,
    loggedIn: true,
    version: '',
    running: documents.size > 0,
    icon: null,
    openDocuments: [...documents.values()].map(describeDocument)
  }
}

export async function openPenCanvas(options: {
  name?: string
  path?: string
  template?: string
}): Promise<PenDocumentInfo> {
  if (options.path) {
    return openDocument(options.path)
  }

  return createDocument(options.name)
}

/** URL the renderer webview loads. Same hosted editor for every document;
 *  the embed bridge supplies the file via storage-load. */
export function penCanvasUrl(_docId?: string): string {
  return penWebEditorUrl()
}

export interface PenLibraryItem extends PenLibraryEntry {
  /** Open in the pane right now. */
  open: boolean
  /** The live document id, when open. */
  docId: null | string
}

export function penLibrary(): { items: PenLibraryItem[]; root: string } {
  const openByPath = new Map<string, string>()

  for (const doc of documents.values()) {
    try {
      openByPath.set(path.resolve(fileURLToPath(doc.fileURI)), doc.docId)
    } catch {
      // Non-file URI — can't collide with a library path.
    }
  }

  const items = listPenLibrary().map(entry => {
    const docId = openByPath.get(path.resolve(entry.path)) ?? null

    return { ...entry, docId, open: Boolean(docId) }
  })

  return { items, root: penLibraryRoot() }
}

/** Delete a canvas. Closes the live document first. */
export function deletePenCanvas(target: string): boolean {
  const resolved = path.resolve(target)

  for (const doc of documents.values()) {
    try {
      if (path.resolve(fileURLToPath(doc.fileURI)) === resolved) {
        closeDocument(doc.docId)
        break
      }
    } catch {
      // Not a file URI.
    }
  }

  return deletePenFromLibrary(resolved)
}

/** Rename a canvas. Refuses while it's open. */
export function renamePenCanvas(target: string, nextName: string): null | string {
  const resolved = path.resolve(target)

  for (const doc of documents.values()) {
    try {
      if (path.resolve(fileURLToPath(doc.fileURI)) === resolved) {
        return null
      }
    } catch {
      // Not a file URI.
    }
  }

  return renamePenInLibrary(resolved, nextName)
}
