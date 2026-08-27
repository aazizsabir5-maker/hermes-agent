/**
 * The "magic lego" assembly for in-chat onboarding.
 *
 * The guided chat starts SOLO: just the chat pane in a small window — no
 * sidebar, no statusbar, nothing to explain. When the user picks a layout in
 * the ::onboarding card, the app assembles around the conversation:
 *
 * 1. The OS window grows OUTWARD by the MINIMUM each layout needs — the
 *    sidebar's width to the left, the terminal/rail minimums where a layout
 *    has them — animated (macOS setBounds animate), so the chat stays roughly
 *    where it was and the window ends as small as the layout allows.
 * 2. The new panes mount into the grown area with a staggered snap-in
 *    animation (`pane-lego-in`).
 * 3. The statusbar comes back; its height is pre-added to the bottom growth
 *    so its arrival doesn't lift the composer.
 */

import { atom } from 'nanostores'
import type { CSSProperties } from 'react'

import { allPaneIds, findGroupOfPane, group, type LayoutNode } from '@/components/pane-shell/tree/model'
import { applyLayoutPreset } from '@/components/pane-shell/tree/presets'
import {
  $layoutTree,
  adoptContributedPanes,
  dismissTreePane,
  resetEnforcedDocks,
  setActiveTreePane,
  undismissTreePanes
} from '@/components/pane-shell/tree/store'
import { registry } from '@/contrib/registry'
import { redockLivePane } from '@/store/first-screen-live'
import { setSidebarOpen } from '@/store/layout'
import { machineUserName } from '@/store/machine'
import { setOnboardingSurfaceActive } from '@/store/onboarding-presence'
import { onboardingDevStage, skipOnboardingWizard } from '@/store/onboarding-wizard'
import { $statusbarVisible } from '@/store/statusbar-prefs'
import { setTranslucency, setTranslucencyMaterial, setTranslucencyMode } from '@/store/translucency'
import { setZoomPercent } from '@/store/zoom'

/** True from guide kickoff until the layout pick assembles the app. */
export const $chatOnboardingSolo = atom(false)

// Presence mirror — see onboarding-presence.ts (update toast stands down).
$chatOnboardingSolo.subscribe(solo => setOnboardingSurfaceActive('solo-chat', solo))

/** The guided-setup session's ids — stored AND runtime, because consumers key
 *  sessions differently (the thread list by stored id, the composer by runtime
 *  id). That one thread gets the onboarding transcript treatment and drops the
 *  composer's git strip; every other session is untouched. */
export const $chatOnboardingThreadIds = atom<readonly string[]>([])

/** The opening line of the guided chat — PRE-BANKED, never generated. The
 *  first thing a new user sees must be instant; the model's cold-stack first
 *  turn took up to 10 seconds in live runs. The transcript renders this
 *  client-side the moment the chat opens; the model is told what was said
 *  and picks up from the user's answer. */
const GREETINGS = [
  "Hey, come on in. I'm Hermes. Give me two minutes to set the place up around you, then we'll put me to work on something you actually want done.\n\nFirst though, what should I call you?",
  "Hey there, I'm Hermes. A couple of quick things and this will feel like yours, then we'll find you something worth doing.\n\nSo, what should I call you?",
  "Hi, you found me. I'm Hermes. Let me get everything arranged around you, then we'll pick something real to start on.\n\nFirst things first though, what should I call you?"
] as const

export const $onboardingGreeting = atom('')

/** Pick (and remember) the canned opening line for this run. When the host
 *  reports a suggestable account name (machineUserName), the greeting ends by
 *  offering it as a default — \"or I can just call you akp\". The suggestion
 *  rides the SAME word the seed rows bank, so the canonical row, the typed
 *  reveal, and what the runbook says was said can never disagree. */
export function pickOnboardingGreeting(): string {
  const existing = $onboardingGreeting.get()

  if (existing) {
    return existing
  }

  const line = GREETINGS[Math.floor(Math.random() * GREETINGS.length)] ?? GREETINGS[0]
  const suggested = machineUserName()

  $onboardingGreeting.set(suggested ? `${line}\n\n(I can also just call you ${suggested}, if you prefer.)` : line)

  return $onboardingGreeting.get()
}

/** Whether the layout card's pick happened. A STORE, not card-local state:
 *  applying the layout replaces the pane tree, which remounts the chat pane
 *  and the card with it — component state would forget the selection the
 *  moment it takes effect. */
export const $chatLayoutPicked = atom(false)

// The statusbar footer is h-5 (see statusbar-controls.tsx).
const STATUSBAR_PX = 20

/** The Sessions list pane (app/contrib/controller). */
const SESSIONS_PANE_ID = 'sessions'

let statusbarWasVisible = true

/** Strip the app to the conversation: chat-only layout, no statusbar. The
 *  window itself is born small when `dev:chat` bakes the stage (main.ts). */
export function startChatOnboardingSolo(): void {
  if ($chatOnboardingSolo.get()) {
    return
  }

  $chatOnboardingSolo.set(true)
  $chatLayoutPicked.set(false)
  // First-run look: the glass material is the default face of the app —
  // the cinematic hands into a translucent window, not a flat slab, and the
  // look PERSISTS after onboarding (the translucency book is localStorage-
  // backed like any Appearance edit). Mode alone isn't enough: the dark-mac
  // default is intensity 22 on the titlebar material — vibrancy under the
  // titlebar only, body effectively opaque — so the blur would vanish the
  // moment the app assembles. Write the full recipe: under-window (the real
  // full-window blur) with enough tint pulled off for it to read. The store
  // guards unsupported platforms, and this is a first-run write on a fresh
  // profile, so no user pref is clobbered.
  setTranslucencyMode('glass')
  setTranslucencyMaterial('under-window')
  setTranslucency(50)
  // First-run type size: the shipped 90% preset reads small in the guided
  // chat (side-by-side screenshots: the wanted size is ~1.3x). 118% is the
  // measured target; real Chromium zoom, so every surface scales coherently
  // and nothing can break layout. Persisted by the main process — the user
  // keeps this size after onboarding until they change UI Scale themselves.
  setZoomPercent(118)
  // Both the statusbar pref and the layout persist — a dev run killed mid-flow
  // must not leave the bar hidden forever, so the dev:chat stage always
  // restores to visible (a real first run has it visible anyway).
  statusbarWasVisible = $statusbarVisible.get() || onboardingDevStage() === 'chat'
  $statusbarVisible.set(false)
  // One zone, strip pinned off. applyTree ADOPTS panes the preset doesn't
  // declare (sessions, terminal, …) into this group as tabs — with the strip
  // never shown and workspace active, they're simply invisible until the
  // assembled layout re-places them. That adoption is also why reactive
  // unhides (files on cwd-arrival) can't pop a zone open mid-flow: there is
  // no other zone to open.
  applyLayoutPreset('chat-solo', group(['workspace'], { tabStrip: 'never' }))
}

/** Minimal per-edge growth per layout — the least the window must gain for
 *  the new panes to be usable, NOT a chat-size-preserving projection (which
 *  balloons the window). Left = sessions sidebar; Elite adds its right rail
 *  and terminal row. Tune by feel. */
const LAYOUT_GROWTH: Record<string, { bottom?: number; left?: number; right?: number; top?: number }> = {
  'basic': { left: 220 },
  'terminal-deck': { bottom: 200, left: 220, right: 240 }
}

/**
 * Put the tree in the state this layout describes — on the first pick AND on
 * every re-pick.
 *
 * All of it has to re-run, because all of it persists: dismissals, dock
 * enforcement, the sidebar's open state. A re-pick that only swapped the
 * preset tree inherited the previous layout's records and came up as a mix of
 * the two (Elite after Basic kept Basic's terminal dismissal, so Elite's
 * terminal was placed and invisible).
 */
function reconcileLayout(id: string, tree: LayoutNode): void {
  assembleStamp = Date.now()
  assembleOrder = 0
  applyLayoutPreset(id, tree)

  const declared = new Set(allPaneIds(tree))

  // Everything this layout asks for is wanted, whatever the last one decided.
  undismissTreePanes(declared)

  // The preset IS the layout. Adoption otherwise keeps every pane the preset
  // doesn't declare, and during a first run each of them is a surface the
  // user has no idea exists: a Terminal tab beside the chat on Basic, an
  // empty Cronjobs column, a Bots roster tabbed onto Sessions (its dock is
  // `enforce: true`, so it re-homes there on every pick). That last one also
  // costs the sidebar its plain face — two panes in the left zone is what
  // conjures a tab strip over what should just be the sessions list.
  //
  // So: anything the picked layout didn't ask for is dismissed. The pane
  // isn't gone, only unplaced — its own toggle (⌃` for the terminal, the
  // Layout menu, `revealTreePane`) brings it back the moment the user wants
  // it, and the living-screen pane re-docks itself right after this runs.
  //
  // Candidates come from the REGISTRY, not just the tree: a pane that isn't
  // placed yet still gets its dismissal recorded, and adoption skips dismissed
  // panes — so this holds whether the pane arrives before or after the sweep.
  const dismissUndeclared = () => {
    for (const paneId of new Set([
      ...allPaneIds($layoutTree.get() ?? tree),
      ...registry.getArea('panes').map(pane => pane.id)
    ])) {
      if (!declared.has(paneId)) {
        dismissTreePane(paneId)
      }
    }
  }

  // The tree now HAS a sessions column, but the renderer drops the whole left
  // column when the persisted ⌘B state says closed ($sidebarOpen →
  // $collapsedTreeSides) — picking a layout with a sidebar is an explicit
  // intent to see it, so open the side through its store (truthful toggle),
  // the same way resetLayoutTree reopens bound sides.
  setSidebarOpen(true)

  // Dock invariants normally run once at boot, against whatever tree existed
  // then — the SOLO tree, which has no sessions column for a left-docking
  // pane to anchor to. That pass burns the ledger entry, so re-running
  // adoption alone left those panes stranded as tabs in the chat zone. Reopen
  // the window first, now that the layout they should dock into exists.
  resetEnforcedDocks()
  adoptContributedPanes()

  // The sidebar opens on Sessions. A pick re-arranges panes; it must never
  // navigate the user away from the conversation they are mid-sentence in, so
  // this is only ever a SIDEBAR payoff — if the docking above didn't take and
  // the pane is stacked with the chat, fronting it there would bury them.
  const assembled = $layoutTree.get()
  const faceGroup = assembled ? findGroupOfPane(assembled, SESSIONS_PANE_ID) : null

  if (faceGroup && !faceGroup.panes.includes('workspace')) {
    setActiveTreePane(SESSIONS_PANE_ID)
  }

  // LAST, because panes can be a CONSEQUENCE of the assembly above: a plugin
  // registers more panes the moment one of its own becomes visible. Sweeping
  // before that point swept a tree those arrivals had not happened in yet,
  // and Basic still landed with an empty Cronjobs column beside the chat.
  dismissUndeclared()
}

/**
 * A layout pick, from the chat card. The FIRST one also performs the solo→app
 * transition (see module header); later picks re-arrange the app that is
 * already there.
 *
 * The window is grown once, on that first pick. `grow` moves the edges OUTWARD
 * by a delta, so re-growing per pick would ratchet the window bigger every
 * time the user toggled between two layouts.
 */
export function assembleChatOnboarding(id: string, tree: LayoutNode): void {
  const firstPick = $chatOnboardingSolo.get()

  if (firstPick) {
    const growth = LAYOUT_GROWTH[id] ?? { left: 220 }

    window.hermesDesktop?.chatOnboarding?.grow({
      bottom: (growth.bottom ?? 0) + (statusbarWasVisible ? STATUSBAR_PX : 0),
      left: growth.left ?? 0,
      right: growth.right ?? 0,
      top: growth.top ?? 0
    })
  }

  reconcileLayout(id, tree)

  if (statusbarWasVisible) {
    $statusbarVisible.set(true)
  }

  $chatOnboardingSolo.set(false)
}

/** Skip the guided setup: assemble the default layout so the user lands in
 *  the full app immediately, and mark onboarding done so nothing resumes it.
 *  The guided chat stays in the transcript — skipping is about ending the
 *  questionnaire, not destroying the conversation. */
export function skipChatOnboarding(): void {
  const preset = registry.getArea('layouts').find(contribution => contribution.id === 'basic')

  if (preset?.data) {
    assembleChatOnboarding(preset.id, preset.data as LayoutNode)
    // Assembly dismisses panes the preset doesn't declare — a mid-flow skip
    // must not eat the living dashboard the user already has beside the chat.
    redockLivePane()
  } else {
    // No layout contribution (shouldn't happen): at minimum leave solo mode
    // and put the statusbar back.
    $chatOnboardingSolo.set(false)
    $statusbarVisible.set(statusbarWasVisible)
  }

  skipOnboardingWizard()
}

// ── Pane entrance ("lego") ───────────────────────────────────────────────────
//
// Groups mounting within the window after an assembly snap in with a stagger.
// The chat group is exempt — it must not move. Read once at mount (not a
// subscription): entrance is a birth property, not live state.

const LEGO_WINDOW_MS = 1500
const LEGO_EASE = 'cubic-bezier(0.22, 1.2, 0.36, 1)'

let assembleStamp = 0
let assembleOrder = 0

export function paneEntranceStyle(panes: readonly string[]): CSSProperties | undefined {
  if (panes.includes('workspace') || Date.now() - assembleStamp > LEGO_WINDOW_MS) {
    return undefined
  }

  return { animation: `pane-lego-in 420ms ${LEGO_EASE} ${assembleOrder++ * 80}ms both` }
}
