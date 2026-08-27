import { useEffect, useRef } from 'react'

import { $canvasTabs } from './canvas-tile'

export function PenTilePane({ docId }: { docId: string }) {
  const hostRef = useRef<HTMLDivElement | null>(null)

  useEffect(() => {
    const host = hostRef.current
    const tab = $canvasTabs.get().find(t => t.provider === 'pen' && t.docId === docId)

    if (!host || !tab) {
      return
    }

    const webview = document.createElement('webview')

    webview.setAttribute('src', tab.url)
    webview.style.cssText = 'width:100%;height:100%;border:0;background:transparent'
    host.append(webview)

    return () => {
      webview.remove()
    }
  }, [docId])

  return <div className="size-full min-h-0 min-w-0 bg-(--ui-editor-surface-background)" ref={hostRef} />
}
