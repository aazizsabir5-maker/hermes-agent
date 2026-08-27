/**
 * The main window's React boot — everything `?win=` overlays must NOT pay for.
 *
 * Split out of `main.tsx` so the entry is a pure dispatcher: one dynamic import
 * per window kind. It used to `import App from './app'` statically, which put
 * the ENTIRE desktop app in the entry chunk, so the intro cinematic's
 * transparent overlay downloaded and evaluated every route, provider and store
 * in Hermes before it could draw its first particle. Under Vite's unbundled dev
 * server that is thousands of module requests for a window that renders a
 * canvas — the "the movie takes years to load" report.
 *
 * Keep it that way: anything imported here is main-window-only by definition.
 * A static import that belongs to every window goes in `main.tsx` instead.
 */

// Side-effect: reports in-flight turns to the main process for the quit guard.
// Pulls the session store, so it is the heaviest of the boot side effects.
import './store/active-work'
// Side-effect: mirrors the machine's AC/battery state for poll demotion.
import './store/power'

import { QueryClientProvider } from '@tanstack/react-query'
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { HashRouter } from 'react-router'

import App from './app'
import { RootErrorBoundary } from './components/error-boundary'
import { HapticsProvider } from './components/haptics-provider'
import { RootTooltipProvider } from './components/ui/tooltip'
import { I18nProvider } from './i18n'
import { queryClient } from './lib/query-client'
import { installRendererAnimationPauseState } from './lib/renderer-loop-pause'
import { ThemeProvider } from './themes/context'

export function mountMainWindow(): void {
  // CSS animations do not inherit Chromium's JS-loop pause policy. Mirror the
  // main window's focus/visibility state to :root so decorative infinite
  // animations stop producing frames when nobody can see them.
  installRendererAnimationPauseState()

  createRoot(document.getElementById('root')!).render(
    <StrictMode>
      <RootErrorBoundary>
        <QueryClientProvider client={queryClient}>
          <I18nProvider>
            <ThemeProvider>
              <HapticsProvider>
                {/* ONE tooltip provider for the whole app. Every `Tip` used to
                    carry its own, and with ~107 call sites those subtrees
                    dominated unrelated interactions (52,784 TooltipProvider
                    renders in a single sash drag). Radix's provider holds only
                    refs and stable callbacks, so hoisting is what it's for. */}
                <RootTooltipProvider>
                  {/* useTransitions={false}: react-router v7's HashRouter wraps every
                    route state update in React.startTransition() by default. In
                    React 19's concurrent renderer, transitions are non-urgent — React
                    can yield mid-render and resume later. When the app is under load
                    (streaming token deltas, gateway events, store updates), those
                    higher-priority updates keep interrupting the transition, starving
                    the route change commit. The session sidebar highlight + main pane
                    both freeze for seconds despite the main thread being free.
                    Disabling transitions makes navigate() commit at default priority. */}
                  <HashRouter useTransitions={false}>
                    <App />
                  </HashRouter>
                </RootTooltipProvider>
              </HapticsProvider>
            </ThemeProvider>
          </I18nProvider>
        </QueryClientProvider>
      </RootErrorBoundary>
    </StrictMode>
  )
}
