import { useEffect, useMemo, useState } from 'react'

import { Button } from '../ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card'
import { Input } from '../ui/input'
import { postReloadSettings } from '../../lib/api'
import { cn } from '../../lib/utils'

function ModeSettingsTable({ modeLabel, values, ranges, onChange, disabled = false }) {
  return (
    <Card className="border-slate-200">
      <CardHeader>
        <CardTitle className="text-base">{modeLabel} mode</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto rounded-xl border border-slate-200">
          <table className="w-full min-w-[760px] border-collapse text-left text-sm">
            <thead className="bg-slate-50 text-slate-900">
              <tr>
                <th className="border-b border-slate-200 px-3 py-2 font-semibold">Category</th>
                <th className="border-b border-slate-200 px-3 py-2 font-semibold">Setting</th>
                <th className="border-b border-slate-200 px-3 py-2 font-semibold">Value</th>
                <th className="border-b border-slate-200 px-3 py-2 font-semibold">Allowed range/options</th>
              </tr>
            </thead>
            <tbody className="text-slate-700">
              <tr className="align-top">
                <td className="border-b border-slate-100 px-3 py-2">Verification scope</td>
                <td className="border-b border-slate-100 px-3 py-2">Max claims to verify per run</td>
                <td className="border-b border-slate-100 px-3 py-2">
                  <Input
                    type="number"
                    min={1}
                    max={5}
                    value={values.max_claims_to_verify_per_run}
                    onChange={(event) =>
                      onChange('max_claims_to_verify_per_run', Number(event.target.value))
                    }
                    disabled={disabled}
                    className={cn("h-9 rounded-lg px-3 text-sm", disabled && "bg-slate-100 cursor-not-allowed")}
                  />
                </td>
                <td className="border-b border-slate-100 px-3 py-2">
                  {ranges?.max_claims_to_verify_per_run || '1-5'}
                </td>
              </tr>
              <tr className="align-top">
                <td className="border-b border-slate-100 px-3 py-2">Verification scope</td>
                <td className="border-b border-slate-100 px-3 py-2">Max claims to extract</td>
                <td className="border-b border-slate-100 px-3 py-2">
                  <Input
                    type="number"
                    min={1}
                    max={10}
                    value={values.max_claims_to_extract}
                    onChange={(event) => onChange('max_claims_to_extract', Number(event.target.value))}
                    disabled={disabled}
                    className={cn("h-9 rounded-lg px-3 text-sm", disabled && "bg-slate-100 cursor-not-allowed")}
                  />
                </td>
                <td className="border-b border-slate-100 px-3 py-2">{ranges?.max_claims_to_extract || '1-10'}</td>
              </tr>
              <tr className="align-top">
                <td className="border-b border-slate-100 px-3 py-2">Evidence sources</td>
                <td className="border-b border-slate-100 px-3 py-2">Max web search results (Tavily)</td>
                <td className="border-b border-slate-100 px-3 py-2">
                  <Input
                    type="number"
                    min={1}
                    max={5}
                    value={values.max_web_sources}
                    onChange={(event) => onChange('max_web_sources', Number(event.target.value))}
                    disabled={disabled}
                    className={cn("h-9 rounded-lg px-3 text-sm", disabled && "bg-slate-100 cursor-not-allowed")}
                  />
                </td>
                <td className="border-b border-slate-100 px-3 py-2">{ranges?.max_sources || '1-5'}</td>
              </tr>
              <tr className="align-top">
                <td className="border-b border-slate-100 px-3 py-2">Evidence sources</td>
                <td className="border-b border-slate-100 px-3 py-2">Max Wikipedia results</td>
                <td className="border-b border-slate-100 px-3 py-2">
                  <Input
                    type="number"
                    min={1}
                    max={5}
                    value={values.max_wikipedia_sources}
                    onChange={(event) => onChange('max_wikipedia_sources', Number(event.target.value))}
                    disabled={disabled}
                    className={cn("h-9 rounded-lg px-3 text-sm", disabled && "bg-slate-100 cursor-not-allowed")}
                  />
                </td>
                <td className="border-b border-slate-100 px-3 py-2">{ranges?.max_sources || '1-5'}</td>
              </tr>
              <tr className="align-top">
                <td className="px-3 py-2">Evidence sources</td>
                <td className="px-3 py-2">Max Google Fact Check results</td>
                <td className="px-3 py-2">
                  <Input
                    type="number"
                    min={1}
                    max={5}
                    value={values.max_fact_check_sources}
                    onChange={(event) => onChange('max_fact_check_sources', Number(event.target.value))}
                    disabled={disabled}
                    className={cn("h-9 rounded-lg px-3 text-sm", disabled && "bg-slate-100 cursor-not-allowed")}
                  />
                </td>
                <td className="px-3 py-2">{ranges?.max_sources || '1-5'}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  )
}

export function ToolSettings({ settingsConfig, onSave, isAdmin = false }) {
  const [form, setForm] = useState(null)
  const [status, setStatus] = useState('idle')
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!settingsConfig) return
    setForm({
      basic: {
        max_claims_to_verify_per_run: settingsConfig.basic?.max_claims_to_verify_per_run ?? 5,
        max_claims_to_extract: settingsConfig.basic?.max_claims_to_extract ?? 10,
        max_web_sources: settingsConfig.basic?.max_web_sources ?? 3,
        max_wikipedia_sources: settingsConfig.basic?.max_wikipedia_sources ?? 2,
        max_fact_check_sources: settingsConfig.basic?.max_fact_check_sources ?? 2,
      },
      comprehensive: {
        max_claims_to_verify_per_run: settingsConfig.comprehensive?.max_claims_to_verify_per_run ?? 5,
        max_claims_to_extract: settingsConfig.comprehensive?.max_claims_to_extract ?? 10,
        max_web_sources: settingsConfig.comprehensive?.max_web_sources ?? 5,
        max_wikipedia_sources: settingsConfig.comprehensive?.max_wikipedia_sources ?? 3,
        max_fact_check_sources: settingsConfig.comprehensive?.max_fact_check_sources ?? 3,
      },
      performance_cost_controls: {
        model_choice: settingsConfig.basic?.model_choice_current || 'gpt-5.1',
        per_claim_timeout_seconds: settingsConfig.basic?.per_claim_timeout_seconds ?? 90,
        tavily_search_depth: settingsConfig.basic?.tavily_search_depth || 'basic',
      },
    })
    setStatus('idle')
    setError(null)
  }, [settingsConfig])

  const modelChoices = useMemo(
    () => settingsConfig?.basic?.model_choices || ['gpt-5.1', 'gpt-4.1-mini', 'gpt-5-mini'],
    [settingsConfig]
  )

  if (!settingsConfig || !form) {
    return (
      <Card className="border-slate-200">
        <CardContent className="py-8 text-sm text-slate-600">Settings are not available.</CardContent>
      </Card>
    )
  }

  const setModeField = (mode, key, value) => {
    setForm((prev) => ({
      ...prev,
      [mode]: {
        ...prev[mode],
        [key]: value,
      },
    }))
  }

  const setPerfField = (key, value) => {
    setForm((prev) => ({
      ...prev,
      performance_cost_controls: {
        ...prev.performance_cost_controls,
        [key]: value,
      },
    }))
  }

  const handleSave = async () => {
    if (!onSave) return

    // Validate claim numbers are >= 1
    if (form.basic.max_claims_to_verify_per_run < 1 || form.basic.max_claims_to_extract < 1) {
      setStatus('error')
      setError('Number of claims must be at least 1')
      return
    }
    if (form.comprehensive.max_claims_to_verify_per_run < 1 || form.comprehensive.max_claims_to_extract < 1) {
      setStatus('error')
      setError('Number of claims must be at least 1')
      return
    }
    // Validate source limits are >= 1 and <= 5
    if (form.basic.max_web_sources < 1 || form.basic.max_web_sources > 5 ||
        form.basic.max_wikipedia_sources < 1 || form.basic.max_wikipedia_sources > 5 ||
        form.basic.max_fact_check_sources < 1 || form.basic.max_fact_check_sources > 5) {
      setStatus('error')
      setError('Source limits must be between 1 and 5')
      return
    }
    if (form.comprehensive.max_web_sources < 1 || form.comprehensive.max_web_sources > 5 ||
        form.comprehensive.max_wikipedia_sources < 1 || form.comprehensive.max_wikipedia_sources > 5 ||
        form.comprehensive.max_fact_check_sources < 1 || form.comprehensive.max_fact_check_sources > 5) {
      setStatus('error')
      setError('Source limits must be between 1 and 5')
      return
    }
    if (form.performance_cost_controls.per_claim_timeout_seconds < 1) {
      setStatus('error')
      setError('Timeout must be at least 1 second')
      return
    }

    setStatus('saving')
    setError(null)
    try {
      const payload = {
        basic: form.basic,
        comprehensive: form.comprehensive,
        performance_cost_controls: form.performance_cost_controls,
      }
      await onSave(payload)
      console.log('Settings saved successfully')

      // Trigger backend reload to apply settings immediately
      try {
        const reloadResult = await postReloadSettings()
        console.log('Backend settings reloaded:', reloadResult)
        setStatus('saved')
      } catch (reloadErr) {
        console.error('Failed to reload backend settings:', reloadErr)
        // Still mark as saved since the settings were written to file
        setStatus('saved')
        setError('Settings saved but backend reload failed. Restart may be needed.')
      }
    } catch (err) {
      setStatus('error')
      setError(err?.response?.data?.detail || err?.message || 'Failed to save settings')
    }
  }

  return (
    <div className="space-y-4">
      {!isAdmin && (
        <div className="rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
          🔒 Login as admin to edit these settings
        </div>
      )}
      <ModeSettingsTable
        modeLabel="Basic"
        values={form.basic}
        ranges={settingsConfig.ranges}
        onChange={(key, value) => setModeField('basic', key, value)}
        disabled={!isAdmin}
      />
      <ModeSettingsTable
        modeLabel="Comprehensive"
        values={form.comprehensive}
        ranges={settingsConfig.ranges}
        onChange={(key, value) => setModeField('comprehensive', key, value)}
        disabled={!isAdmin}
      />

      <Card className="border-slate-200">
        <CardHeader>
          <CardTitle className="text-base">Performance/cost controls</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto rounded-xl border border-slate-200">
            <table className="w-full min-w-[760px] border-collapse text-left text-sm">
              <thead className="bg-slate-50 text-slate-900">
                <tr>
                  <th className="border-b border-slate-200 px-3 py-2 font-semibold">Setting</th>
                  <th className="border-b border-slate-200 px-3 py-2 font-semibold">Value</th>
                  <th className="border-b border-slate-200 px-3 py-2 font-semibold">Allowed range/options</th>
                </tr>
              </thead>
              <tbody className="text-slate-700">
                <tr className="align-top">
                  <td className="border-b border-slate-100 px-3 py-2">Model choice</td>
                  <td className="border-b border-slate-100 px-3 py-2">
                    <select
                      value={form.performance_cost_controls.model_choice}
                      onChange={(event) => setPerfField('model_choice', event.target.value)}
                      disabled={!isAdmin}
                      className={cn("h-10 w-full rounded-lg border border-slate-200 bg-white px-3 text-sm text-slate-900 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400 focus-visible:ring-offset-2 focus-visible:ring-offset-white", !isAdmin && "bg-slate-100 cursor-not-allowed")}
                    >
                      {modelChoices.map((m) => (
                        <option key={m} value={m}>
                          {m}
                        </option>
                      ))}
                    </select>
                  </td>
                  <td className="border-b border-slate-100 px-3 py-2">{modelChoices.join(', ')}</td>
                </tr>
                <tr className="align-top">
                  <td className="border-b border-slate-100 px-3 py-2">Tavily search depth</td>
                  <td className="border-b border-slate-100 px-3 py-2">
                    <select
                      value={form.performance_cost_controls.tavily_search_depth}
                      onChange={(event) => setPerfField('tavily_search_depth', event.target.value)}
                      disabled={!isAdmin}
                      className={cn("h-10 w-full rounded-lg border border-slate-200 bg-white px-3 text-sm text-slate-900 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400 focus-visible:ring-offset-2 focus-visible:ring-offset-white", !isAdmin && "bg-slate-100 cursor-not-allowed")}
                    >
                      <option value="basic">Basic (faster, cheaper)</option>
                      <option value="advanced">Advanced (more thorough, slower)</option>
                    </select>
                  </td>
                  <td className="border-b border-slate-100 px-3 py-2">basic | advanced</td>
                </tr>
                <tr className="align-top">
                  <td className="px-3 py-2">Per-claim timeout (seconds)</td>
                  <td className="px-3 py-2">
                    <Input
                      type="number"
                      min={1}
                      step="1"
                      value={form.performance_cost_controls.per_claim_timeout_seconds}
                      onChange={(event) =>
                        setPerfField('per_claim_timeout_seconds', Number(event.target.value))
                      }
                      disabled={!isAdmin}
                      className={cn("h-9 rounded-lg px-3 text-sm", !isAdmin && "bg-slate-100 cursor-not-allowed")}
                    />
                  </td>
                  <td className="px-3 py-2">Positive number (seconds)</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div className="mt-4 flex items-center justify-end gap-3">
            <Button onClick={handleSave} disabled={status === 'saving' || !isAdmin}>
              {status === 'saving' ? 'Saving...' : 'Save'}
            </Button>
          </div>
          {status === 'saved' && !error && (
            <p className="mt-2 text-sm text-emerald-700">Settings saved and applied successfully.</p>
          )}
          {status === 'error' && <p className="mt-2 text-sm text-rose-700">{error}</p>}
        </CardContent>
      </Card>
    </div>
  )
}
