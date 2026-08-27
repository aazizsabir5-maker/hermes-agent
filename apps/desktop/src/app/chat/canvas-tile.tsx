/** Design surfaces as layout-tree panes. Pen registers as the provider. */

import type { ReactNode } from 'react'
import { atom } from 'nanostores'

import { revealTreePane } from '@/components/pane-shell/tree/store'

import { paneMirror } from './pane-mirror'

export interface CanvasTab {
  provider: string
  docId: string
  title: string
  url: string
}

export interface CanvasProvider {
  id: string
  untitled: string
  tabLead: () => ReactNode
  render: (docId: string) => ReactNode
  close: (docId: string) => void
}

const providers = new Map<string, CanvasProvider>()

export function registerCanvasProvider(provider: CanvasProvider): void {
  if (!providers.has(provider.id)) {
    providers.set(provider.id, provider)
  }
}

export const $canvasTabs = atom<CanvasTab[]>([])

const CANVAS_TILE_PREFIX = 'canvas-tile'

const tileKey = (tab: Pick<CanvasTab, 'docId' | 'provider'>) => `${tab.provider}:${tab.docId}`

export function openCanvasTile(tab: CanvasTab): void {
  $canvasTabs.set([tab])
  revealTreePane(`${CANVAS_TILE_PREFIX}:${tileKey(tab)}`)
}

export function closeCanvasTile(provider: string, docId: string): void {
  $canvasTabs.set($canvasTabs.get().filter(t => t.provider !== provider || t.docId !== docId))
}

export function canvasTileOpen(provider?: string): boolean {
  const tabs = $canvasTabs.get()

  return provider ? tabs.some(t => t.provider === provider) : tabs.length > 0
}

function tabForKey(key: string): CanvasTab | null {
  return $canvasTabs.get().find(t => tileKey(t) === key) ?? null
}

function providerForKey(key: string): CanvasProvider | null {
  return providers.get(key.split(':', 1)[0]) ?? null
}

const docIdOf = (key: string) => key.slice(key.indexOf(':') + 1)

export const watchCanvasTiles = paneMirror<CanvasTab>({
  source: $canvasTabs,
  key: tileKey,
  prefix: CANVAS_TILE_PREFIX,
  dir: () => 'right',
  minWidth: '24rem',
  title: key => tabForKey(key)?.title || providerForKey(key)?.untitled || 'Canvas',
  tabLead: key => providerForKey(key)?.tabLead() ?? null,
  render: key => providerForKey(key)?.render(docIdOf(key)) ?? null,
  close: key => {
    providerForKey(key)?.close(docIdOf(key))
    closeCanvasTile(key.split(':', 1)[0], docIdOf(key))
  }
})
