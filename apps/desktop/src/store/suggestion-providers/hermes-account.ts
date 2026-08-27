import { translateNow } from '@/i18n'
import { type ComposerSuggestion, offerSuggestions } from '@/store/composer-suggestions'

/**
 * The account offer: sign in to Hermes, or carry on exactly as you are.
 *
 * Raised once during the first build, after the agent has done enough real
 * work to have earned the ask (see first-build.ts). Deliberately ONE pill and
 * no counter-pill — declining is not an action, it is the default. Staying on
 * this machine costs nothing and needs no click, so putting "stay local"
 * beside "sign in" would invent a decision the user does not have to make.
 *
 * The strip's ignore ledger does the rest: a pill that appears and dies
 * uninvoked enough times stops being offered.
 */

const PROVIDER = 'hermes-account'

function suggestion(): ComposerSuggestion {
  const copy = (key: string) => translateNow(`composer.hermesAccount.${key}`)

  return {
    id: 'sign-in',
    provider: PROVIDER,
    icon: 'cloud',
    label: copy('label'),
    tip: copy('tip'),
    invoke: async () => {
      await window.hermesDesktop?.cloud?.login()
    },
    workingLabel: copy('working'),
    workingTip: copy('workingTip'),
    doneLabel: copy('done'),
    doneTip: copy('doneTip')
  }
}

/** Offer the pill in `sessionId`, unless this install is already signed in. */
export function offerAccountChoice(sessionId: null | string | undefined): void {
  void Promise.resolve(window.hermesDesktop?.cloud?.status())
    .then(status => {
      if (!status?.signedIn) {
        offerSuggestions(sessionId, PROVIDER, [suggestion()])
      }
    })
    .catch(() => undefined)
}
