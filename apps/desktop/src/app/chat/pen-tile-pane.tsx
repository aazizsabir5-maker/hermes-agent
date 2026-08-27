/**
 * The pen canvas pane body: a <webview> on app.pen.dev, chromeless.
 *
 * The webview fills the pane completely — pen's toolbar/canvas ARE the pane
 * content, with hermes contributing only the tree tab above it. The embed
 * preload is assigned by main's will-attach-webview hook, not here.
 */

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

    // Imperative, not JSX: <webview> is an Electron-only element and creating
    // it imperatively (the preview pane's pattern) keeps React's types and
    // reconciler out of its lifecycle.
    const webview = document.createElement('webview')

    webview.setAttribute('src', tab.url)
    // The embed-bridge preload is assigned by main's will-attach-webview hook
    // (keyed off the app.pen.dev origin), so no preload attribute here.
    webview.style.cssText = 'width:100%;height:100%;border:0;background:transparent'

    host.append(webview)

    return () => {
      webview.remove()
    }
  }, [docId])

  return <div className="size-full min-h-0 min-w-0 bg-(--ui-editor-surface-background)" ref={hostRef} />
}
