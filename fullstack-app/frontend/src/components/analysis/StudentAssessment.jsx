import { useState } from 'react'
import { Loader } from 'lucide-react'
import { Button } from '../ui/button'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '../ui/card'
import { Textarea } from '../ui/textarea'

const verdictOptions = ['SUPPORTED', 'REFUTED', 'INSUFFICIENT_INFORMATION', 'CONFLICTING_EVIDENCE']

export function StudentAssessmentForm({ onSave, onClear, initial = null, disabled = false }) {
  const [verdict, setVerdict] = useState(initial?.verdict || 'SUPPORTED')
  const [confidence, setConfidence] = useState(initial?.confidence ?? 0.5)
  const [sourcesCount, setSourcesCount] = useState(initial?.sourcesCount ?? 0)
  const [timeSpent, setTimeSpent] = useState(initial?.timeSpent ?? 5)
  const [reasoning, setReasoning] = useState(initial?.reasoning || '')
  const [keySources, setKeySources] = useState(initial?.keySources?.join('\n') || '')
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)

  const handleSubmit = () => {
    if (!reasoning.trim()) {
      setError('Please provide your reasoning before saving.')
      return
    }
    setError('')
    setSaving(true)
    const payload = {
      verdict,
      confidence: Number(confidence),
      sourcesCount: Number(sourcesCount),
      timeSpent: Number(timeSpent),
      reasoning: reasoning.trim(),
      keySources: keySources
        .split('\n')
        .map((s) => s.trim())
        .filter(Boolean),
      timestamp: new Date().toISOString(),
    }
    onSave?.(payload)
    setSaving(false)
  }

  return (
    <Card className="border-slate-200 bg-white shadow-[0_24px_50px_rgba(15,23,42,0.10)]">
      <CardHeader>
        <CardTitle className="text-lg">Your Assessment (optional)</CardTitle>
        <CardDescription>Make your own judgment before (or after) running the AI analysis.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid gap-4 md:grid-cols-2">
          <label className="flex flex-col gap-1 text-sm text-slate-700">
            Verdict
            <select
              className="rounded-xl border border-slate-200 px-3 py-2 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-emerald-400"
              value={verdict}
              onChange={(e) => setVerdict(e.target.value)}
              disabled={disabled}
            >
              {verdictOptions.map((v) => (
                <option key={v} value={v}>
                  {v}
                </option>
              ))}
            </select>
          </label>
          <label className="flex flex-col gap-1 text-sm text-slate-700">
            Confidence: {Number(confidence).toFixed(2)}
            <input
              type="range"
              min="0"
              max="1"
              step="0.05"
              value={confidence}
              onChange={(e) => setConfidence(e.target.value)}
              disabled={disabled}
            />
          </label>
          <label className="flex flex-col gap-1 text-sm text-slate-700">
            Sources checked
            <input
              type="number"
              min="0"
              className="rounded-xl border border-slate-200 px-3 py-2 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-emerald-400"
              value={sourcesCount}
              onChange={(e) => setSourcesCount(e.target.value)}
              disabled={disabled}
            />
          </label>
          <label className="flex flex-col gap-1 text-sm text-slate-700">
            Time spent (minutes)
            <input
              type="number"
              min="0"
              className="rounded-xl border border-slate-200 px-3 py-2 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-emerald-400"
              value={timeSpent}
              onChange={(e) => setTimeSpent(e.target.value)}
              disabled={disabled}
            />
          </label>
        </div>

        <div className="space-y-2">
          <label className="flex flex-col gap-1 text-sm text-slate-700">
            Reasoning (required)
            <Textarea
              value={reasoning}
              onChange={(e) => setReasoning(e.target.value)}
              placeholder="Why did you reach this verdict? What evidence did you find?"
              disabled={disabled}
            />
          </label>
          <label className="flex flex-col gap-1 text-sm text-slate-700">
            Key sources (one per line)
            <Textarea
              value={keySources}
              onChange={(e) => setKeySources(e.target.value)}
              placeholder="CDC report\nReuters article\nWikipedia page"
              disabled={disabled}
            />
          </label>
        </div>

        {error && <p className="rounded-xl border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-700">{error}</p>}
      </CardContent>
      <CardFooter className="flex flex-wrap items-center gap-3">
        <Button onClick={handleSubmit} disabled={disabled || saving} className="gap-2">
          {saving ? (
            <>
              <Loader className="h-4 w-4 animate-spin" />
              Saving...
            </>
          ) : (
            'Save Assessment'
          )}
        </Button>
        <Button variant="secondary" onClick={onClear} disabled={disabled}>
          Clear
        </Button>
      </CardFooter>
    </Card>
  )
}

export function StudentAssessmentSummary({ assessment }) {
  if (!assessment) return null
  return (
    <Card className="border-slate-200 bg-slate-50">
      <CardHeader>
        <CardTitle className="text-base">Your Saved Assessment</CardTitle>
        <CardDescription>Captured for comparison with AI.</CardDescription>
      </CardHeader>
      <CardContent className="grid gap-2 text-sm text-slate-700 md:grid-cols-2">
        <div>
          <p className="font-semibold text-slate-900">Verdict</p>
          <p>{assessment.verdict}</p>
        </div>
        <div>
          <p className="font-semibold text-slate-900">Confidence</p>
          <p>{assessment.confidence.toFixed(2)}</p>
        </div>
        <div>
          <p className="font-semibold text-slate-900">Sources checked</p>
          <p>{assessment.sourcesCount}</p>
        </div>
        <div>
          <p className="font-semibold text-slate-900">Time spent</p>
          <p>{assessment.timeSpent} min</p>
        </div>
        <div className="md:col-span-2">
          <p className="font-semibold text-slate-900">Reasoning</p>
          <p className="mt-1 whitespace-pre-line text-slate-700">{assessment.reasoning}</p>
        </div>
        {assessment.keySources?.length ? (
          <div className="md:col-span-2">
            <p className="font-semibold text-slate-900">Sources</p>
            <ul className="list-disc pl-4">
              {assessment.keySources.map((s, idx) => (
                <li key={idx}>{s}</li>
              ))}
            </ul>
          </div>
        ) : null}
      </CardContent>
    </Card>
  )
}
