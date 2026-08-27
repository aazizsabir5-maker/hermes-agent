/**
 * Renderer entry — a dispatcher and nothing else.
 *
 * Every `?win=` kind gets its own dynamic import, so an overlay window loads
 * only its own subtree. Anything static here is paid for by ALL of them,
 * including the transparent 60fps ones; main-window work belongs in
 * `main-window.tsx`.
 */

import './styles.css'
// Side-effect: applies the persisted window translucency on load.
import './store/translucency'
// Dev-only render/state churn counters. MUST precede any `react-dom` import:
// react-dom captures the devtools hook at module init, so bippy has to install
// during THIS import's evaluation or every commit goes unseen (verified — a
// late install reports renderers=0, commits=0). Static, and ahead of every
// dynamic window import below, so the ordering holds for whichever one runs.
// `vite.config.ts` aliases this specifier to a no-op module for non-dev builds,
// so neither the counters nor bippy reach a shipped renderer.
import '@/debug/dev-only'

import { installClipboardShim } from './lib/clipboard'
import { installSelectionCopyColorGuard } from './lib/selection-copy-colors'

installClipboardShim()
// Chromium serializes selection copies (Cmd+C, right-click Copy) with the
// theme's computed colors inlined; without this guard a dark-theme selection
// pastes as near-white text into light-background targets.
installSelectionCopyColorGuard()

// The perf probe ships in dev, and in a production build ONLY when explicitly
// opted in (VITE_PERF_PROBE=1) — this lets the perf harness measure a real,
// minified production renderer for representative absolute numbers. Normal
// `npm run build` leaves the flag unset, so the probe never reaches users.
if (import.meta.env.MODE !== 'production' || import.meta.env.VITE_PERF_PROBE === '1') {
  import('./app/chat/perf-probe')
}

const WINDOW_ROOTS: Record<string, () => Promise<{ mount: () => void }>> = {
  hud: async () => {
    document.title = 'Hermes HUD'

    return import('./main-window').then(m => ({ mount: m.mountMainWindow }))
  },
  intro: () => import('./components/intro-reveal/intro-root').then(m => ({ mount: m.mountIntroReveal })),
  onboarding: () => import('./components/onboarding-wizard/wizard-root').then(m => ({ mount: m.mountOnboardingWizard })),
  overlay: () => import('./app/pet-overlay/overlay-root').then(m => ({ mount: m.mountPetOverlay })),
  quick: () => import('./app/quick-entry/quick-entry-root').then(m => ({ mount: m.mountQuickEntry })),
  wake: () => import('./app/wake-indicator/wake-indicator-root').then(m => ({ mount: m.mountWakeIndicator }))
}

const win = new URLSearchParams(window.location.search).get('win')
const root = (win && WINDOW_ROOTS[win]) || (() => import('./main-window').then(m => ({ mount: m.mountMainWindow })))

void root().then(({ mount }) => mount())
