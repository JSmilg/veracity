// Validation status constants
export const VALIDATION_STATUS = {
  PENDING: 'pending',
  CONFIRMED_TRUE: 'confirmed_true',
  PROVEN_FALSE: 'proven_false',
  PARTIALLY_TRUE: 'partially_true',
}

// Status display labels
export const STATUS_LABELS = {
  [VALIDATION_STATUS.PENDING]: 'Pending',
  [VALIDATION_STATUS.CONFIRMED_TRUE]: 'Confirmed',
  [VALIDATION_STATUS.PROVEN_FALSE]: 'False',
  [VALIDATION_STATUS.PARTIALLY_TRUE]: 'Partial',
}

// Status colors (dark-mode Tailwind classes)
export const STATUS_COLORS = {
  [VALIDATION_STATUS.PENDING]: {
    bg: 'bg-pending/10',
    text: 'text-pending',
    border: 'border-pending/25',
  },
  [VALIDATION_STATUS.CONFIRMED_TRUE]: {
    bg: 'bg-verified/10',
    text: 'text-verified',
    border: 'border-verified/25',
  },
  [VALIDATION_STATUS.PROVEN_FALSE]: {
    bg: 'bg-refuted/10',
    text: 'text-refuted',
    border: 'border-refuted/25',
  },
  [VALIDATION_STATUS.PARTIALLY_TRUE]: {
    bg: 'bg-partial/10',
    text: 'text-partial',
    border: 'border-partial/25',
  },
}

// Certainty level constants (6-tier confidence taxonomy)
export const CERTAINTY_LEVEL = {
  TIER_1_DONE_DEAL: 'tier_1_done_deal',
  TIER_2_ADVANCED: 'tier_2_advanced',
  TIER_3_ACTIVE: 'tier_3_active',
  TIER_4_CONCRETE_INTEREST: 'tier_4_concrete_interest',
  TIER_5_EARLY_INTENT: 'tier_5_early_intent',
  TIER_6_SPECULATION: 'tier_6_speculation',
}

// Source type constants
export const SOURCE_TYPE = {
  ORIGINAL: 'original',
  CITING: 'citing',
}

// Score types
export const SCORE_TYPE = {
  TRUTHFULNESS: 'truthfulness',
  SPEED: 'speed',
}
