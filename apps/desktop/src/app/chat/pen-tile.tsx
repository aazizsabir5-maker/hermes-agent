import penMark from '@/assets/pen-mark.png'

import {
  type CanvasTab,
  canvasTileOpen,
  closeCanvasTile,
  openCanvasTile,
  registerCanvasProvider
} from './canvas-tile'
import { PenTilePane } from './pen-tile-pane'

const PEN_PROVIDER = 'pen'

registerCanvasProvider({
  id: PEN_PROVIDER,
  untitled: 'Canvas',
  tabLead: () => <img alt="" className="size-[0.8125rem] shrink-0" src={penMark} />,
  render: docId => <PenTilePane docId={docId} />,
  close: () => {
    void window.hermesDesktop?.pen?.close()
  }
})

export function openPenCanvasTile(tab: Omit<CanvasTab, 'provider'>): void {
  openCanvasTile({ ...tab, provider: PEN_PROVIDER })
}

export function closePenCanvasTile(docId: string): void {
  closeCanvasTile(PEN_PROVIDER, docId)
}

export function penCanvasTileOpen(): boolean {
  return canvasTileOpen(PEN_PROVIDER)
}
