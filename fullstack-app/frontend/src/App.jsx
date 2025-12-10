import { useEffect, useMemo, useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { Activity, Loader, ShieldCheck, Target } from 'lucide-react'

import { Button } from './components/ui/button'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from './components/ui/card'
import { Textarea } from './components/ui/textarea'
import { Badge } from './components/ui/badge'
import { ClaimCard } from './components/analysis/ClaimCard'
import { ClaimDetail } from './components/analysis/ClaimDetail'
import { DomainLegend } from './components/analysis/DomainLegend'
import { StudentAssessmentForm, StudentAssessmentSummary } from './components/analysis/StudentAssessment'
import { ComparePanel } from './components/analysis/ComparePanel'
import { useVerify } from './hooks/useVerify'
import { getDomainConfig, getHealth } from './lib/api'
import { cn } from './lib/utils'

function App() {
  const [text, setText] = useState('')
  const [verbose, setVerbose] = useState(false)
  const [mode, setMode] = useState('basic')
  const [selectedIdx, setSelectedIdx] = useState(0)
  const [health, setHealth] = useState(null)
  const [domainConfig, setDomainConfig] = useState(null)
  const [loadingHealth, setLoadingHealth] = useState(false)
  const [healthError, setHealthError] = useState(null)
  const [studentAssessment, setStudentAssessment] = useState(null)
  const [tab, setTab] = useState('your') // your | ai | compare | docs

  const { assessment, runVerify, status, error, elapsedMs, summary, reset } = useVerify()

  useEffect(() => {
    async function bootstrap() {
      try {
        setLoadingHealth(true)
        setHealth(await getHealth())
        setDomainConfig(await getDomainConfig())
      } catch (err) {
        setHealthError(err?.message || 'Health check failed')
      } finally {
        setLoadingHealth(false)
      }
    }
    bootstrap()
  }, [])

  useEffect(() => {
    if (assessment?.claim_results?.length) {
      setSelectedIdx(0)
    }
  }, [assessment])

  const activeMode = useMemo(() => assessment?.mode || mode, [assessment?.mode, mode])

  const selectedClaim = useMemo(() => {
    if (!assessment?.claim_results?.length) return null
    return assessment.claim_results[selectedIdx]
  }, [assessment, selectedIdx])

  const handleSubmit = async () => {
    if (!text.trim()) return
    await runVerify({ text, verbose, mode })
  }

  const handleExportJSON = () => {
    if (!assessment) return
    const blob = new Blob([JSON.stringify(assessment, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `metacheck_${Date.now()}.json`
    link.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="relative min-h-screen overflow-hidden">
      <div className="pointer-events-none absolute inset-0 bg-grid-radial opacity-60" aria-hidden="true" />
      <div className="relative z-10 flex min-h-screen flex-col">
        <header className="w-full px-4 pt-16 pb-10">
          <div className="mx-auto max-w-6xl">
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div className="w-full max-w-4xl mx-auto text-center">
                <img
                  src="/metacheck-logo.png"
                  alt="MetaCheck"
                  className="mx-auto w-full max-w-4xl drop-shadow-sm"
                />
                <p className="mt-8 text-base font-semibold text-slate-700 sm:text-lg md:text-xl">
                  Do your own assessment, then see how AI weighs evidence and compares with you.
                </p>
              </div>
              {healthError && <p className="text-sm text-rose-600">{healthError}</p>}
            </div>
            <div className="mt-12 mb-6 flex flex-wrap gap-3 justify-center">
              {[
                { key: 'your', label: 'Your Assessment' },
                { key: 'ai', label: 'AI Analysis' },
                { key: 'compare', label: 'Compare' },
                { key: 'docs', label: 'Documentation' },
              ].map((item) => (
                <Button
                  key={item.key}
                  variant={tab === item.key ? 'default' : 'secondary'}
                  onClick={() => setTab(item.key)}
                  className="gap-2"
                >
                  {item.label}
                </Button>
              ))}
            </div>
          </div>
        </header>

        <hr className="border-t-2 border-slate-200 mx-auto max-w-6xl" />

        <main className="flex-1 px-4 pb-20 pt-4">
          <div className="mx-auto flex max-w-6xl flex-col gap-6">
            {tab === 'your' && (
              <motion.section
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, ease: 'easeOut' }}
                className="space-y-6"
              >
                <div className="flex items-center justify-center gap-3 w-full">
                  <Badge className="border border-emerald-200 bg-emerald-50 text-emerald-800">Step 1</Badge>
                  <h2 className="text-xl font-semibold text-slate-900">Your Assessment (optional)</h2>
                </div>
                <StudentAssessmentForm
                  onSave={(data) => setStudentAssessment(data)}
                  onClear={() => setStudentAssessment(null)}
                  initial={studentAssessment}
                  disabled={status === 'loading'}
                />
                {studentAssessment && (
                  <StudentAssessmentSummary assessment={studentAssessment} />
                )}
              </motion.section>
            )}

            {tab === 'ai' && (
              <motion.section
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, ease: 'easeOut' }}
                className="space-y-4"
              >
                <div className="flex items-center justify-center gap-3 w-full">
                  <Badge className="border border-sky-200 bg-sky-50 text-sky-800">Step 2</Badge>
                  <h2 className="text-xl font-semibold text-slate-900">AI Analysis & Results</h2>
                </div>
                <Card className="border-slate-200 bg-white shadow-[0_30px_60px_rgba(15,23,42,0.12)]">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-xl">
                      <ShieldCheck className="h-5 w-5 text-emerald-500" aria-hidden="true" />
                      Run MetaCheck
                    </CardTitle>
                    <CardDescription>
                      Paste text with one or more factual claims. MetaCheck will extract, search, classify domains, and
                      return verdicts with metacognitive details.
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <Textarea
                      value={text}
                      onChange={(event) => setText(event.target.value)}
                      placeholder="Example: Donald Trump increased military recruitment in© 2025. COVID-19 vaccines are safe."
                      disabled={status === 'loading'}
                      className="min-h-[160px]"
                    />
                    <div className="flex flex-wrap items-center justify-between gap-3">
                      <div className="flex flex-wrap items-center gap-3">
                        <label className="flex items-center gap-2 text-sm text-slate-700">
                          <input
                            type="checkbox"
                            checked={verbose}
                            onChange={(e) => setVerbose(e.target.checked)}
                            disabled={status === 'loading'}
                            className="h-4 w-4 rounded border-slate-300 text-emerald-600 focus:ring-emerald-400"
                          />
                          Verbose backend logs
                        </label>
                        <div className="flex items-center gap-2 text-sm text-slate-700">
                          <span>Mode:</span>
                          <div className="flex rounded-full border border-slate-200 bg-white p-1 shadow-sm">
                            {['basic', 'comprehensive'].map((value) => (
                              <button
                                key={value}
                                type="button"
                                onClick={() => setMode(value)}
                                disabled={status === 'loading'}
                                className={cn(
                                  'rounded-full px-3 py-1 text-xs font-semibold capitalize transition',
                                  mode === value
                                    ? 'bg-emerald-500 text-white shadow'
                                    : 'text-slate-600 hover:bg-slate-100'
                                )}
                              >
                                {value}
                              </button>
                            ))}
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <Button
                          variant="secondary"
                          onClick={() => {
                            setText('')
                            reset()
                          }}
                          disabled={status === 'loading'}
                        >
                          Clear
                        </Button>
                        <Button onClick={handleSubmit} disabled={status === 'loading' || !text.trim()} className="gap-2">
                          {status === 'loading' ? (
                            <>
                              <Loader className="h-4 w-4 animate-spin" aria-hidden="true" />
                              Checking...
                            </>
                          ) : (
                            <>
                              <Target className="h-4 w-4" aria-hidden="true" />
                              Run MetaCheck
                            </>
                          )}
                        </Button>
                      </div>
                    </div>
                    <AnimatePresence>
                      {error && (
                        <motion.div
                          initial={{ opacity: 0, y: -6 }}
                          animate={{ opacity: 1, y: 0 }}
                          exit={{ opacity: 0, y: -6 }}
                          className="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700"
                        >
                          {error}
                        </motion.div>
                      )}
                    </AnimatePresence>
                    {status === 'success' && assessment?.claim_results?.length === 0 && (
                      <div className="rounded-2xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-700">
                        No verifiable claims found.
                      </div>
                    )}
                    {summary && (
                      <div className="grid gap-3 sm:grid-cols-3">
                        <div className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3">
                          <p className="text-xs uppercase text-slate-500">Claims</p>
                          <p className="text-xl font-semibold text-slate-900">{summary.totalClaims}</p>
                        </div>
                        <div className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3">
                          <p className="text-xs uppercase text-slate-500">Avg confidence</p>
                          <p className="text-xl font-semibold text-slate-900">{summary.avgConfidence.toFixed(2)}</p>
                        </div>
                        <div className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3">
                          <p className="text-xs uppercase text-slate-500">Elapsed</p>
                          <p className="text-xl font-semibold text-slate-900">{elapsedMs} ms</p>
                        </div>
                      </div>
                    )}
                  </CardContent>
                  {assessment && (
                    <CardFooter className="flex flex-wrap items-center justify-between gap-3">
                      <p className="text-sm text-slate-600">
                        Generated at: {assessment.generated_at?.split('T')[0] || 'now'}
                      </p>
                      <div className="flex gap-3">
                        <Button variant="outline" onClick={handleExportJSON}>
                          Export JSON
                        </Button>
                      </div>
                    </CardFooter>
                  )}
                </Card>

                <Card className="border-slate-200">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-lg">
                      <Activity className="h-5 w-5 text-emerald-500" />
                      Claims overview
                    </CardTitle>
                    <CardDescription>
                      {activeMode === 'basic'
                        ? 'Basic mode shows essential facts. Switch to comprehensive for full reasoning.'
                        : 'Select a claim to see detailed reasoning.'}
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="grid gap-6 lg:grid-cols-3">
                    <div className="space-y-3 lg:col-span-1">
                      {assessment?.claim_results?.map((cr, idx) => (
                        <ClaimCard
                          key={idx}
                          claim={cr.claim}
                          verdict={cr.verdict}
                          confidence={cr.confidence}
                          keySources={cr.key_sources}
                          index={idx}
                          selected={idx === selectedIdx}
                          onSelect={() => setSelectedIdx(idx)}
                        />
                      ))}
                      {!assessment && <p className="text-sm text-slate-600">Run MetaCheck to see results.</p>}
                    </div>
                    <div className="lg:col-span-2">
                      {selectedClaim ? (
                        <ClaimDetail claimResult={selectedClaim} mode={activeMode} />
                      ) : (
                        <Card className="border-dashed border-slate-200 bg-slate-50">
                          <CardContent className="py-12 text-center text-slate-500">
                            No claim selected. Run MetaCheck to view analysis.
                          </CardContent>
                        </Card>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </motion.section>
            )}

            {tab === 'compare' && (
              <motion.section
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, ease: 'easeOut' }}
              >
                <div className="mb-4 flex items-center justify-center gap-3 w-full">
                  <Badge className="border border-purple-200 bg-purple-50 text-purple-800">Step 4</Badge>
                  <h2 className="text-xl font-semibold text-slate-900">Compare</h2>
                </div>
                <ComparePanel studentAssessment={studentAssessment} aiResult={assessment} />
              </motion.section>
            )}

            {tab === 'docs' && (
              <motion.section
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, ease: 'easeOut' }}
                className="space-y-4"
              >
                <div className="mb-4 flex items-center justify-center gap-3 w-full">
                  <Badge className="border border-slate-200 bg-slate-50 text-slate-800">Docs</Badge>
                  <h2 className="text-xl font-semibold text-slate-900">Domain categories</h2>
                </div>
                <div className="flex justify-center">
                  <Card className="w-full max-w-4xl border-slate-200">
                    <CardHeader>
                      <CardTitle className="text-lg">Domain credibility taxonomy</CardTitle>
                      <CardDescription>How MetaCheck scores domains from config.json.</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <DomainLegend categories={domainConfig?.categories} />
                    </CardContent>
                  </Card>
                </div>
              </motion.section>
            )}
          </div>
        </main>

        <footer className="mt-auto border-t border-slate-200 bg-white/80 px-4 py-6">
          <div className="mx-auto flex max-w-6xl flex-col items-center justify-center text-sm text-slate-600">
            <span>© 2025 MetaCheck. All rights reserved.</span>
          </div>
        </footer>
      </div>
    </div>
  )
}

export default App












