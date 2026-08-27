import { describe, expect, it } from 'vitest'

import type { WizardAnswers } from '@/store/onboarding-wizard'

import { buildFirstTaskRunbook } from './setup-profile'

/**
 * What Setup learns has to reach the session Setup hands to.
 *
 * The whole promise of the handoff is that the work carries on where the
 * conversation left off — an agent that opens by asking their name again has
 * just told them the last five minutes went nowhere. The build session is an
 * ordinary session on the user's own profile, so the seeded runbook is the
 * only carrier: everything Setup learned has to be in it.
 */
const ANSWERS = {
  connectors: ['Notion', 'Slack'],
  context: 'kitchen reno, contractor quotes due Friday',
  name: 'Sam'
} as unknown as WizardAnswers

const runbook = () => buildFirstTaskRunbook('Plant tracker', ANSWERS)

describe('the picture Setup hands to the build session', () => {
  it('carries every fact the user gave', () => {
    for (const fact of ['Sam', 'kitchen reno', 'Notion', 'Slack']) {
      expect(runbook(), `the runbook drops "${fact}"`).toContain(fact)
    }
  })

  it('tells the agent not to ask again for what it was handed', () => {
    expect(runbook()).toMatch(/never introduce yourself or ask who they are/i)
    expect(runbook()).toMatch(/without re-asking/i)
  })

  // Naming the tools without this reads as "you have Slack" — and the first
  // build is the one thing that must never bounce the user into an OAuth page.
  it('names their tools as NOT connected', () => {
    expect(runbook()).toMatch(/none are connected yet/i)
  })

  // Setup can be skipped, and every answer is optional on the way through.
  it('says nothing at all about a user who told Setup nothing', () => {
    const bare = buildFirstTaskRunbook('Plant tracker', { connectors: [] } as unknown as WizardAnswers)

    expect(bare).not.toMatch(/undefined|\bnull\b/)
    expect(bare).not.toMatch(/user is called\b/i)
  })
})
