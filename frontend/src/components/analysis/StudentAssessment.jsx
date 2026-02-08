import { useState } from 'react'
import { Loader, Plus, Trash2, Edit2, X, ChevronDown, ChevronRight } from 'lucide-react'
import { Button } from '../ui/button'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '../ui/card'
import { Textarea } from '../ui/textarea'

const verdictOptions = ['SUPPORTED', 'REFUTED', 'INSUFFICIENT_INFORMATION', 'CONFLICTING_EVIDENCE']

export function StudentAssessmentForm({ claims = [], onSave, disabled = false }) {
  const [editingIndex, setEditingIndex] = useState(null)
  const [showForm, setShowForm] = useState(false)
  const [showGuidelines, setShowGuidelines] = useState(false)

  // Form state
  const [claimText, setClaimText] = useState('')
  const [verdict, setVerdict] = useState('SUPPORTED')
  const [confidence, setConfidence] = useState(0.5)
  const [sourcesCount, setSourcesCount] = useState(0)
  const [timeSpent, setTimeSpent] = useState(5)
  const [reasoning, setReasoning] = useState('')
  const [keySources, setKeySources] = useState('')
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)

  const resetForm = () => {
    setClaimText('')
    setVerdict('SUPPORTED')
    setConfidence(0.5)
    setSourcesCount(0)
    setTimeSpent(5)
    setReasoning('')
    setKeySources('')
    setError('')
    setEditingIndex(null)
  }

  const handleEdit = (index) => {
    const claim = claims[index]
    setClaimText(claim.claim)
    setVerdict(claim.verdict)
    setConfidence(claim.confidence)
    setSourcesCount(claim.sourcesCount)
    setTimeSpent(claim.timeSpent)
    setReasoning(claim.reasoning)
    setKeySources(claim.keySources?.join('\n') || '')
    setEditingIndex(index)
    setShowForm(true)
  }

  const handleDelete = (index) => {
    const updatedClaims = claims.filter((_, i) => i !== index)
    onSave?.(updatedClaims)
  }

  const handleSubmit = () => {
    if (!claimText.trim()) {
      setError('Please enter the claim text.')
      return
    }
    if (!reasoning.trim()) {
      setError('Please provide your reasoning.')
      return
    }

    setError('')
    setSaving(true)

    const payload = {
      claim: claimText.trim(),
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

    let updatedClaims
    if (editingIndex !== null) {
      // Update existing claim
      updatedClaims = claims.map((c, i) => (i === editingIndex ? payload : c))
    } else {
      // Add new claim
      updatedClaims = [...claims, payload]
    }

    onSave?.(updatedClaims)
    setSaving(false)
    resetForm()
    setShowForm(false)
  }

  const handleCancel = () => {
    resetForm()
    setShowForm(false)
  }

  return (
    <div className="space-y-4">
      {/* List of created claims */}
      {claims.length > 0 && (
        <Card className="border-slate-200 bg-slate-50">
          <CardHeader>
            <CardTitle className="text-base">Your Claims ({claims.length})</CardTitle>
            <CardDescription>Claims you've created and assessed</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {claims.map((claim, index) => (
              <Card key={index} className="border-slate-200 bg-white">
                <CardContent className="pt-4">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 space-y-2">
                      <div className="flex items-center gap-2">
                        <span className="rounded-full bg-emerald-100 px-2 py-0.5 text-xs font-medium text-emerald-700">
                          Claim {index + 1}
                        </span>
                        <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                          claim.verdict === 'SUPPORTED' ? 'bg-green-100 text-green-700' :
                          claim.verdict === 'REFUTED' ? 'bg-red-100 text-red-700' :
                          claim.verdict === 'CONFLICTING_EVIDENCE' ? 'bg-yellow-100 text-yellow-700' :
                          'bg-gray-100 text-gray-700'
                        }`}>
                          {claim.verdict}
                        </span>
                        <span className="text-xs text-slate-500">
                          Confidence: {claim.confidence.toFixed(2)}
                        </span>
                      </div>
                      <p className="text-sm font-medium text-slate-900">{claim.claim}</p>
                      <p className="text-xs text-slate-600">{claim.reasoning}</p>
                      {claim.keySources?.length > 0 && (
                        <div className="text-xs text-slate-500">
                          Sources: {claim.sourcesCount} | Time: {claim.timeSpent}m
                        </div>
                      )}
                    </div>
                    <div className="flex gap-1">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleEdit(index)}
                        disabled={disabled}
                        className="h-8 w-8 p-0"
                      >
                        <Edit2 className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDelete(index)}
                        disabled={disabled}
                        className="h-8 w-8 p-0 text-rose-600 hover:text-rose-700"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Add/Edit claim form */}
      {showForm ? (
        <Card className="border-slate-200 bg-white shadow-[0_24px_50px_rgba(15,23,42,0.10)]">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-lg">
                  {editingIndex !== null ? 'Edit Claim' : 'Add New Claim'}
                </CardTitle>
                <CardDescription>
                  {editingIndex !== null
                    ? 'Update your claim and assessment'
                    : 'Create a verifiable claim and provide your verdict'}
                </CardDescription>
              </div>
              <Button variant="ghost" size="sm" onClick={handleCancel} className="h-8 w-8 p-0">
                <X className="h-4 w-4" />
              </Button>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Claim text field */}
            <div className="space-y-2">
              <label className="flex flex-col gap-1 text-sm text-slate-700">
                Claim Text (required)
                <Textarea
                  value={claimText}
                  onChange={(e) => setClaimText(e.target.value)}
                  placeholder="Enter a specific, verifiable claim (e.g., 'The Eiffel Tower was completed in 1889')"
                  disabled={disabled}
                  className="min-h-[80px]"
                />
              </label>
            </div>

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
                editingIndex !== null ? 'Update Claim' : 'Save Claim'
              )}
            </Button>
            <Button variant="secondary" onClick={handleCancel} disabled={disabled}>
              Cancel
            </Button>
          </CardFooter>
        </Card>
      ) : (
        <>
          <Button onClick={() => setShowForm(true)} disabled={disabled} className="w-full gap-2">
            <Plus className="h-4 w-4" />
            Add New Claim
          </Button>

          {/* Guidelines Section */}
          <Card className="border-blue-200 bg-blue-50">
            <button
              onClick={() => setShowGuidelines(!showGuidelines)}
              className="w-full px-4 py-3 hover:bg-blue-100 transition-colors flex items-center justify-between text-left"
            >
              <h3 className="text-base font-semibold text-blue-900">📋 How to Assess Claims (Guidelines)</h3>
              {showGuidelines ? (
                <ChevronDown className="w-5 h-5 text-blue-700" />
              ) : (
                <ChevronRight className="w-5 h-5 text-blue-700" />
              )}
            </button>
            {showGuidelines && (
              <div className="px-4 pb-4 space-y-4 text-sm text-blue-900">
                {/* Step 1: Extract Verifiable Claims */}
                <div className="bg-white rounded-lg p-4 border border-blue-200">
                  <h4 className="font-bold text-blue-900 mb-2 flex items-center gap-2">
                    <span className="bg-blue-600 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs">1</span>
                    Extract Verifiable Claims
                  </h4>
                  <p className="mb-2 leading-relaxed">Identify statements that can be proven true or false with evidence:</p>
                  <ul className="list-disc list-inside space-y-1 ml-4">
                    <li><strong>Verifiable:</strong> "The Eiffel Tower is 330 meters tall" (can check measurements)</li>
                    <li><strong>Verifiable:</strong> "Biden won the 2020 election" (can verify official results)</li>
                    <li><strong>Not verifiable:</strong> "The Eiffel Tower is beautiful" (opinion)</li>
                    <li><strong>Not verifiable:</strong> "Paris is the best city" (subjective)</li>
                  </ul>
                  <p className="mt-2 text-xs italic">💡 Look for specific facts, statistics, dates, names, and events</p>
                </div>

                {/* Step 2: Collect Evidence */}
                <div className="bg-white rounded-lg p-4 border border-blue-200">
                  <h4 className="font-bold text-blue-900 mb-2 flex items-center gap-2">
                    <span className="bg-blue-600 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs">2</span>
                    Collect Evidence from Multiple Sources
                  </h4>
                  <p className="mb-2 leading-relaxed">Research each claim using diverse, credible sources:</p>
                  <ul className="list-disc list-inside space-y-1 ml-4">
                    <li><strong>Search engines:</strong> Google, Bing, DuckDuckGo</li>
                    <li><strong>Wikipedia:</strong> Good starting point for general facts</li>
                    <li><strong>Fact-checking sites:</strong> Snopes, FactCheck.org, PolitiFact</li>
                    <li><strong>Primary sources:</strong> Government data, research papers, official websites</li>
                    <li><strong>News sources:</strong> Reuters, AP, BBC (check multiple outlets)</li>
                  </ul>
                  <p className="mt-2 text-xs italic">⚠️ Avoid relying on a single source. Cross-reference information!</p>
                </div>

                {/* Step 3: Evaluate Source Credibility */}
                <div className="bg-white rounded-lg p-4 border border-blue-200">
                  <h4 className="font-bold text-blue-900 mb-2 flex items-center gap-2">
                    <span className="bg-blue-600 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs">3</span>
                    Evaluate Source Credibility
                  </h4>
                  <p className="mb-2 leading-relaxed">Not all sources are equally trustworthy. Ask yourself:</p>
                  <ul className="list-disc list-inside space-y-1 ml-4">
                    <li><strong>Authority:</strong> Who wrote this? Are they an expert?</li>
                    <li><strong>Bias:</strong> Does the source have an agenda or political leaning?</li>
                    <li><strong>Evidence:</strong> Does it cite original sources or just opinions?</li>
                    <li><strong>Timeliness:</strong> Is the information current or outdated?</li>
                    <li><strong>Domain:</strong> .gov, .edu, .org sites are often more reliable than random blogs</li>
                  </ul>
                  <p className="mt-2 text-xs italic">🎯 Professional fact-checkers &gt; Academic sources &gt; News outlets &gt; Social media</p>
                </div>

                {/* Step 4: Choose a Verdict */}
                <div className="bg-white rounded-lg p-4 border border-blue-200">
                  <h4 className="font-bold text-blue-900 mb-2 flex items-center gap-2">
                    <span className="bg-blue-600 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs">4</span>
                    Choose a Verdict
                  </h4>
                  <p className="mb-2 leading-relaxed">Based on the evidence, select the appropriate verdict:</p>
                  <div className="space-y-2 ml-4">
                    <div>
                      <strong className="text-green-700">✓ SUPPORTED:</strong>
                      <p className="text-xs">Multiple credible sources confirm the claim. Little to no contradictory evidence.</p>
                    </div>
                    <div>
                      <strong className="text-red-700">✗ REFUTED:</strong>
                      <p className="text-xs">Credible sources explicitly contradict the claim. Evidence shows it's false.</p>
                    </div>
                    <div>
                      <strong className="text-gray-700">? INSUFFICIENT_INFORMATION:</strong>
                      <p className="text-xs">Not enough reliable sources found, or sources lack credibility (under 0.7). Cannot verify.</p>
                    </div>
                    <div>
                      <strong className="text-yellow-700">⚠ CONFLICTING_EVIDENCE:</strong>
                      <p className="text-xs">Credible sources disagree. Some support, some refute. No clear consensus.</p>
                    </div>
                  </div>
                </div>

                {/* Step 5: Set Confidence Level */}
                <div className="bg-white rounded-lg p-4 border border-blue-200">
                  <h4 className="font-bold text-blue-900 mb-2 flex items-center gap-2">
                    <span className="bg-blue-600 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs">5</span>
                    Set Your Confidence Level
                  </h4>
                  <p className="mb-2 leading-relaxed">How certain are you about this verdict? (0.0 = no confidence, 1.0 = completely certain)</p>
                  <ul className="list-disc list-inside space-y-1 ml-4">
                    <li><strong>0.9-1.0:</strong> Extremely confident (many high-quality sources agree)</li>
                    <li><strong>0.7-0.8:</strong> Confident (solid evidence from reliable sources)</li>
                    <li><strong>0.5-0.6:</strong> Moderately confident (some evidence, but gaps remain)</li>
                    <li><strong>0.0-0.4:</strong> Low confidence (weak evidence, uncertainty)</li>
                  </ul>
                  <p className="mt-2 text-xs italic">💭 Be honest! It's okay to have low confidence if evidence is unclear.</p>
                </div>

                {/* Step 6: Write Your Reasoning */}
                <div className="bg-white rounded-lg p-4 border border-blue-200">
                  <h4 className="font-bold text-blue-900 mb-2 flex items-center gap-2">
                    <span className="bg-blue-600 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs">6</span>
                    Write Your Reasoning
                  </h4>
                  <p className="mb-2 leading-relaxed">Explain WHY you reached this verdict. Include:</p>
                  <ul className="list-disc list-inside space-y-1 ml-4">
                    <li><strong>What evidence did you find?</strong> Summarize key findings</li>
                    <li><strong>Which sources did you trust most?</strong> Why?</li>
                    <li><strong>Were there contradictions?</strong> How did you resolve them?</li>
                    <li><strong>What assumptions did you make?</strong> Any uncertainties?</li>
                  </ul>
                  <p className="mt-2 text-xs italic">📝 Good reasoning shows your critical thinking process!</p>
                </div>

                {/* Tips */}
                <div className="bg-gradient-to-r from-purple-50 to-indigo-50 rounded-lg p-4 border-2 border-purple-300">
                  <h4 className="font-bold text-purple-900 mb-2">🎓 Pro Tips</h4>
                  <ul className="list-disc list-inside space-y-1 ml-4 text-purple-900">
                    <li>Track your time to see how long fact-checking actually takes</li>
                    <li>Count how many sources you checked (aim for at least 3-5)</li>
                    <li>List specific source names (not just "I googled it")</li>
                    <li>Be skeptical of claims that seem too extreme or emotional</li>
                    <li>When in doubt, look for what professional fact-checkers say</li>
                  </ul>
                </div>
              </div>
            )}
          </Card>
        </>
      )}
    </div>
  )
}
