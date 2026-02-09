import { useState, useEffect } from 'react'
import { useCreateClaim, useUpdateClaim } from '../../hooks/useClaims'

const CERTAINTY_OPTIONS = [
  { value: '', label: 'Auto-detect' },
  { value: 'tier_1_done_deal', label: 'Done Deal' },
  { value: 'tier_2_advanced', label: 'Advanced' },
  { value: 'tier_3_active', label: 'Active Talks' },
  { value: 'tier_4_concrete_interest', label: 'Concrete Interest' },
  { value: 'tier_5_early_intent', label: 'Early Intent' },
  { value: 'tier_6_speculation', label: 'Speculation' },
]

const SOURCE_TYPE_OPTIONS = [
  { value: 'original', label: 'Original Scoop' },
  { value: 'citing', label: 'Citing Another Source' },
]

const VALIDATION_OPTIONS = [
  { value: 'pending', label: 'Pending' },
  { value: 'confirmed_true', label: 'Confirmed True' },
  { value: 'proven_false', label: 'Proven False' },
  { value: 'partially_true', label: 'Partially True' },
]

const initialFormState = {
  claim_text: '',
  journalist_name: '',
  publication: '',
  article_url: '',
  player_name: '',
  from_club: '',
  to_club: '',
  transfer_fee: '',
  certainty_level: '',
  source_type: 'original',
  validation_status: 'pending',
}

const ClaimForm = ({ claim, isOpen, onClose }) => {
  const isEdit = !!claim
  const [form, setForm] = useState(initialFormState)
  const [errors, setErrors] = useState({})

  const createMutation = useCreateClaim()
  const updateMutation = useUpdateClaim()
  const mutation = isEdit ? updateMutation : createMutation

  useEffect(() => {
    if (claim) {
      setForm({
        claim_text: claim.claim_text || '',
        journalist_name: claim.journalist_name || '',
        publication: claim.publication || '',
        article_url: claim.article_url || '',
        player_name: claim.player_name || '',
        from_club: claim.from_club || '',
        to_club: claim.to_club || '',
        transfer_fee: claim.transfer_fee || '',
        certainty_level: claim.certainty_level || '',
        source_type: claim.source_type || 'original',
        validation_status: claim.validation_status || 'pending',
      })
    } else {
      setForm(initialFormState)
    }
    setErrors({})
  }, [claim, isOpen])

  if (!isOpen) return null

  const handleChange = (e) => {
    const { name, value } = e.target
    setForm((prev) => ({ ...prev, [name]: value }))
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: undefined }))
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setErrors({})

    // Build payload — omit empty optional fields
    const payload = { ...form }
    if (!payload.certainty_level) delete payload.certainty_level
    if (!payload.article_url) delete payload.article_url

    try {
      if (isEdit) {
        await mutation.mutateAsync({ id: claim.id, data: payload })
      } else {
        await mutation.mutateAsync(payload)
      }
      onClose()
    } catch (err) {
      if (err.response?.data) {
        const apiErrors = err.response.data
        const mapped = {}
        for (const [key, val] of Object.entries(apiErrors)) {
          mapped[key] = Array.isArray(val) ? val.join(' ') : val
        }
        setErrors(mapped)
      }
    }
  }

  const inputClass =
    'w-full bg-surface-2 border border-edge rounded-lg px-3 py-2 text-sm font-sans text-zinc-200 focus:outline-none focus:border-accent/50 focus:ring-1 focus:ring-accent/20 transition-colors'
  const labelClass = 'block text-xs font-sans font-medium text-zinc-500 uppercase tracking-wider mb-1.5'
  const errorClass = 'text-xs text-refuted mt-1 font-sans'

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={onClose} />
      <div className="relative bg-surface-1 border border-edge rounded-xl shadow-elevation-3 w-full max-w-2xl max-h-[90vh] overflow-y-auto m-4">
        <div className="sticky top-0 bg-surface-1 border-b border-edge px-6 py-4 flex items-center justify-between rounded-t-xl z-10">
          <h2 className="text-xl font-display text-zinc-100">
            {isEdit ? 'Edit Claim' : 'Add Rumour'}
          </h2>
          <button
            onClick={onClose}
            className="text-zinc-500 hover:text-zinc-200 transition-colors"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-5">
          {/* Claim Text */}
          <div>
            <label className={labelClass}>Claim Text *</label>
            <textarea
              name="claim_text"
              value={form.claim_text}
              onChange={handleChange}
              required
              rows={3}
              className={inputClass}
              placeholder="e.g. Arsenal are interested in signing a Barcelona midfielder"
            />
            {errors.claim_text && <p className={errorClass}>{errors.claim_text}</p>}
          </div>

          {/* Journalist + Publication */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className={labelClass}>Journalist Name *</label>
              <input
                type="text"
                name="journalist_name"
                value={form.journalist_name}
                onChange={handleChange}
                required
                className={inputClass}
                placeholder="e.g. Fabrizio Romano"
              />
              {errors.journalist_name && <p className={errorClass}>{errors.journalist_name}</p>}
            </div>
            <div>
              <label className={labelClass}>Publication</label>
              <input
                type="text"
                name="publication"
                value={form.publication}
                onChange={handleChange}
                className={inputClass}
                placeholder="Defaults to journalist name"
              />
              {errors.publication && <p className={errorClass}>{errors.publication}</p>}
            </div>
          </div>

          {/* Article URL */}
          <div>
            <label className={labelClass}>Article URL</label>
            <input
              type="url"
              name="article_url"
              value={form.article_url}
              onChange={handleChange}
              className={inputClass}
              placeholder="https://..."
            />
            {errors.article_url && <p className={errorClass}>{errors.article_url}</p>}
          </div>

          {/* Player + Clubs + Fee */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className={labelClass}>Player Name</label>
              <input
                type="text"
                name="player_name"
                value={form.player_name}
                onChange={handleChange}
                className={inputClass}
                placeholder="e.g. Pedri"
              />
            </div>
            <div>
              <label className={labelClass}>Transfer Fee</label>
              <input
                type="text"
                name="transfer_fee"
                value={form.transfer_fee}
                onChange={handleChange}
                className={inputClass}
                placeholder="e.g. £50M"
              />
            </div>
            <div>
              <label className={labelClass}>From Club</label>
              <input
                type="text"
                name="from_club"
                value={form.from_club}
                onChange={handleChange}
                className={inputClass}
                placeholder="Auto-detected if left blank"
              />
            </div>
            <div>
              <label className={labelClass}>To Club</label>
              <input
                type="text"
                name="to_club"
                value={form.to_club}
                onChange={handleChange}
                className={inputClass}
                placeholder="Auto-detected if left blank"
              />
            </div>
          </div>

          {/* Dropdowns */}
          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className={labelClass}>Certainty</label>
              <select name="certainty_level" value={form.certainty_level} onChange={handleChange} className={inputClass}>
                {CERTAINTY_OPTIONS.map((o) => (
                  <option key={o.value} value={o.value}>{o.label}</option>
                ))}
              </select>
            </div>
            <div>
              <label className={labelClass}>Source Type</label>
              <select name="source_type" value={form.source_type} onChange={handleChange} className={inputClass}>
                {SOURCE_TYPE_OPTIONS.map((o) => (
                  <option key={o.value} value={o.value}>{o.label}</option>
                ))}
              </select>
            </div>
            <div>
              <label className={labelClass}>Status</label>
              <select name="validation_status" value={form.validation_status} onChange={handleChange} className={inputClass}>
                {VALIDATION_OPTIONS.map((o) => (
                  <option key={o.value} value={o.value}>{o.label}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Non-field errors */}
          {errors.non_field_errors && (
            <p className={errorClass}>{errors.non_field_errors}</p>
          )}

          {/* Actions */}
          <div className="flex justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm font-sans font-medium text-zinc-400 hover:text-zinc-200 bg-surface-2 border border-edge rounded-lg hover:border-zinc-600 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={mutation.isPending}
              className="btn-primary disabled:opacity-50"
            >
              {mutation.isPending ? 'Saving...' : isEdit ? 'Save Changes' : 'Add Rumour'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default ClaimForm
