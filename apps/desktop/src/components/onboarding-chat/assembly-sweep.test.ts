import { atom } from 'nanostores'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { allPaneIds, findGroupOfPane, group, split } from '@/components/pane-shell/tree/model'
import {
  $dismissedPanes,
  $layoutTree,
  $paneVisible,
  adoptContributedPanes,
  bindToolPaneCollapse,
  tabStripVisibleForGroup
} from '@/components/pane-shell/tree/store'
import { registry } from '@/contrib/registry'

import { $chatOnboardingSolo, assembleChatOnboarding } from './assembly'

vi.mock('@/store/first-screen-live', () => ({ redockLivePane: vi.fn() }))
vi.mock('@/store/zoom', () => ({ setZoomPercent: vi.fn() }))

const BOTS_PANE = 'hermes-bots:pane'

const disposers: (() => void)[] = []

function registerPane(id: string, data: Record<string, unknown>) {
  const dispose = registry.register({ area: 'panes', data, id, render: () => null, title: id })

  disposers.push(dispose)

  return dispose
}

beforeEach(() => {
  window.localStorage.clear()
  $dismissedPanes.set(new Set())
  // The state a layout card is clicked in: the guided chat, still solo.
  $chatOnboardingSolo.set(true)

  for (const dispose of disposers.splice(0)) {
    dispose()
  }

  registerPane('workspace', { placement: 'main', uncloseable: true })
  registerPane('sessions', { collapsible: true, placement: 'left', width: '237px' })
  registerPane(BOTS_PANE, {
    collapsible: true,
    dock: { enforce: true, pane: 'sessions', pos: 'center' },
    placement: 'left',
    width: '260px'
  })
})

/** The Basic layout: sessions sidebar beside the conversation. */
const basic = () => split('row', [group(['sessions']), group(['workspace'])])

describe('onboarding assembly dismisses panes it never asked for', () => {
  // Contributed panes can register the moment a pane becomes VISIBLE, and
  // assembly fronts the sidebar face — so such a pane is a consequence of the
  // assembly, not a precondition of it. A sweep that ran before the fronting
  // saw a tree the pane could not be in yet, and Basic landed with an empty
  // Cronjobs column beside the chat (twice).
  it('drops a main pane that only registers once the sidebar face is fronted', () => {
    let cronjobs: (() => void) | null = null

    // What the app root does (`watchContributedPanes`) — without it a late
    // registration never reaches the tree and the test proves nothing.
    const stopAdopting = registry.subscribe(adoptContributedPanes)

    const stop = $paneVisible('sessions').listen(visible => {
      if (visible) {
        cronjobs ??= registerPane('hermes-bots:routines', {
          dock: { enforce: true, pane: 'workspace', pos: 'right' },
          placement: 'main',
          width: '250px'
        })
      }
    })

    try {
      assembleChatOnboarding('basic', basic())

      expect(cronjobs, 'the face never fronted, so this asserts nothing').not.toBeNull()
      expect(allPaneIds($layoutTree.get()!)).not.toContain('hermes-bots:routines')
    } finally {
      stop()
      stopAdopting()
    }
  })

  it('keeps what the layout does declare', () => {
    assembleChatOnboarding('basic', basic())

    const placed = allPaneIds($layoutTree.get()!)

    expect(placed).toContain('workspace')
    expect(placed).toContain('sessions')
  })

  // The Bots roster docks onto `sessions` with `enforce: true`, so adoption
  // re-homes it there on every pick. Onboarding shows no bot surface at all —
  // and a second pane in the left zone is also what conjures a tab strip over
  // what should read as a plain sessions sidebar.
  it('leaves the sessions sidebar alone, whichever layout is picked', () => {
    for (const [id, tree] of [
      ['basic', basic()],
      ['terminal-deck', split('row', [group(['sessions']), group(['workspace']), group(['files'])])]
    ] as const) {
      assembleChatOnboarding(id, tree)

      expect(allPaneIds($layoutTree.get()!)).not.toContain(BOTS_PANE)
      expect(findGroupOfPane($layoutTree.get()!, 'sessions')?.panes).toEqual(['sessions'])
      expect(tabStripVisibleForGroup(findGroupOfPane($layoutTree.get()!, 'sessions')!)).toBe(false)
    }
  })
})

// Layouts are re-pickable from the card, and everything assembly writes
// persists — dismissals most of all. A re-pick that only swapped the preset
// tree inherited the previous layout's records, so the two came up mixed:
// Elite's terminal was placed and invisible because Basic had dismissed it.
describe('picking a different layout replaces the previous one', () => {
  const elite = () => split('row', [group(['sessions']), split('column', [group(['workspace']), group(['terminal'])])])

  beforeEach(() => {
    registerPane('terminal', { collapsible: true, placement: 'bottom' })

    // Through the real binding, or the pane isn't a collapse pane and the
    // sweep has no reason to touch it — the test would prove nothing.
    const $open = atom(true)

    bindToolPaneCollapse(
      'terminal',
      $open,
      () => $open.set(false),
      () => $open.set(true)
    )
  })

  it('brings back a pane the previous layout dismissed', () => {
    assembleChatOnboarding('basic', basic())
    expect($dismissedPanes.get().has('terminal'), 'Basic should have dismissed it').toBe(true)

    assembleChatOnboarding('terminal-deck', elite())

    expect($dismissedPanes.get().has('terminal')).toBe(false)
    expect(allPaneIds($layoutTree.get()!)).toContain('terminal')
  })

  it('drops it again on the way back', () => {
    assembleChatOnboarding('terminal-deck', elite())
    assembleChatOnboarding('basic', basic())

    expect(allPaneIds($layoutTree.get()!)).not.toContain('terminal')
  })

  // A pick is a request for the layout as a whole, tab included. Fronting
  // only on the first pick rebuilt Basic's panes on the way back but left the
  // sidebar showing whatever Elite had.
  it('fronts Sessions again on the way back', () => {
    assembleChatOnboarding('basic', basic())
    assembleChatOnboarding('terminal-deck', elite())
    assembleChatOnboarding('basic', basic())

    expect(findGroupOfPane($layoutTree.get()!, 'sessions')?.active).toBe('sessions')
  })

  // EVERY pick opens on Sessions: the Setup guide's chat is a visible
  // Sessions row, and fronting anything else navigated the user away from the
  // conversation they were mid-sentence in (they had to click back to
  // Sessions to recover it).
  it('opens both Elite and Basic on Sessions', () => {
    assembleChatOnboarding('terminal-deck', elite())
    expect(findGroupOfPane($layoutTree.get()!, 'sessions')?.active).toBe('sessions')

    assembleChatOnboarding('basic', basic())
    expect(findGroupOfPane($layoutTree.get()!, 'sessions')?.active).toBe('sessions')
  })
})
