import { useState } from 'react'
import { Loader, Sparkles } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card'
import { Badge } from '../ui/badge'
import { Button } from '../ui/button'
import { verdictColors, verdictLabel } from '../../lib/types'
import { cn } from '../../lib/utils'
import { postCompare } from '../../lib/api'

export function ComparePanel({ studentClaims = [], aiResult }) {
  const aiClaims = aiResult?.claim_results || []
  const [analysis, setAnalysis] = useState(null)
  const [analyzing, setAnalyzing] = useState(false)
  const [analysisError, setAnalysisError] = useState(null)

  const handleAnalyze = async () => {
    setAnalyzing(true)
    setAnalysisError(null)

    try {
      const result = await postCompare({
        student_claims: studentClaims,
        ai_result: aiResult
      })
      setAnalysis(result)
    } catch (error) {
      console.error('Analysis failed:', error)
      setAnalysisError(error.response?.data?.detail || error.message || 'Failed to analyze comparison')
    } finally {
      setAnalyzing(false)
    }
  }

  if (!studentClaims.length && !aiClaims.length) {
    return (
      <Card className="border-slate-200">
        <CardContent className="py-10 text-center text-slate-600">
          Add your claims and run AI analysis to view comparisons.
        </CardContent>
      </Card>
    )
  }

  if (!aiClaims.length) {
    return (
      <Card className="border-slate-200">
        <CardContent className="py-10 text-center text-slate-600">
          Run AI analysis to compare with your assessment.
        </CardContent>
      </Card>
    )
  }

  if (!studentClaims.length) {
    return (
      <Card className="border-slate-200">
        <CardContent className="py-10 text-center text-slate-600">
          You didn't create any claims. You can still review the AI results in the AI Analysis tab.
        </CardContent>
      </Card>
    )
  }

  // Calculate overall alignment statistics
  const totalComparisons = Math.min(studentClaims.length, aiClaims.length)
  let verdictMatches = 0
  let totalConfidenceDiff = 0

  for (let i = 0; i < totalComparisons; i++) {
    if (studentClaims[i]?.verdict === aiClaims[i]?.verdict) {
      verdictMatches++
    }
    totalConfidenceDiff += Math.abs((studentClaims[i]?.confidence || 0) - (aiClaims[i]?.confidence || 0))
  }

  const avgConfidenceDiff = totalComparisons > 0 ? totalConfidenceDiff / totalComparisons : 0
  const verdictAgreementRate = totalComparisons > 0 ? (verdictMatches / totalComparisons) * 100 : 0

  return (
    <div className="space-y-6">
      {/* Overall comparison summary */}
      <Card className="border-slate-200 bg-gradient-to-br from-purple-50 to-blue-50">
        <CardHeader>
          <CardTitle className="text-lg">Comparison Summary</CardTitle>
          <CardDescription>Overview of your claims vs AI-extracted claims</CardDescription>
        </CardHeader>
        <CardContent className="grid gap-4 md:grid-cols-3">
          <div className="rounded-2xl border border-slate-200 bg-white p-4 text-center">
            <p className="text-2xl font-bold text-slate-900">{studentClaims.length}</p>
            <p className="text-sm text-slate-600">Your Claims</p>
          </div>
          <div className="rounded-2xl border border-slate-200 bg-white p-4 text-center">
            <p className="text-2xl font-bold text-emerald-600">{aiClaims.length}</p>
            <p className="text-sm text-slate-600">AI-Extracted Claims</p>
          </div>
          <div className="rounded-2xl border border-slate-200 bg-white p-4 text-center">
            <p className="text-2xl font-bold text-blue-600">{verdictAgreementRate.toFixed(0)}%</p>
            <p className="text-sm text-slate-600">Verdict Agreement</p>
            <p className="text-xs text-slate-500 mt-1">
              Avg confidence diff: {avgConfidenceDiff.toFixed(2)}
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Side-by-side comparison */}
      <div className="grid gap-6 md:grid-cols-2">
        {/* Your claims column */}
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <div className="h-1 w-8 rounded bg-purple-500" />
            <h3 className="text-lg font-semibold text-slate-900">Your Claims ({studentClaims.length})</h3>
          </div>
          {studentClaims.map((claim, idx) => (
            <Card key={idx} className="border-purple-200 bg-white">
              <CardHeader className="pb-3">
                <div className="flex items-center gap-2">
                  <Badge className="bg-purple-100 text-purple-700 border-purple-200">
                    Claim {idx + 1}
                  </Badge>
                  <Badge className={cn('border', verdictColors[claim.verdict] || 'bg-slate-100 text-slate-700')}>
                    {verdictLabel(claim.verdict)}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent className="space-y-3">
                <div>
                  <p className="text-sm font-medium text-slate-900">{claim.claim}</p>
                </div>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div>
                    <span className="text-slate-500">Confidence:</span>
                    <span className="ml-1 font-medium text-slate-900">{claim.confidence.toFixed(2)}</span>
                  </div>
                  <div>
                    <span className="text-slate-500">Sources:</span>
                    <span className="ml-1 font-medium text-slate-900">{claim.sourcesCount}</span>
                  </div>
                  <div>
                    <span className="text-slate-500">Time:</span>
                    <span className="ml-1 font-medium text-slate-900">{claim.timeSpent}m</span>
                  </div>
                </div>
                <div>
                  <p className="text-xs font-semibold text-slate-700">Your Reasoning:</p>
                  <p className="mt-1 text-xs text-slate-600">{claim.reasoning}</p>
                </div>
                {claim.keySources?.length > 0 && (
                  <div>
                    <p className="text-xs font-semibold text-slate-700">Your Sources:</p>
                    <ul className="mt-1 list-disc pl-4 text-xs text-slate-600 space-y-1">
                      {claim.keySources.map((source, sIdx) => {
                        // Check if source is a plain URL (starts with http:// or https://)
                        const isPlainUrl = /^https?:\/\//i.test(source.trim())

                        // Parse source to extract URL if present (format: "Source Name [URL]")
                        const urlMatch = source.match(/\[(https?:\/\/[^\]]+)\]/)
                        const url = urlMatch ? urlMatch[1] : (isPlainUrl ? source.trim() : null)
                        const displayText = urlMatch ? source.replace(/\[https?:\/\/[^\]]+\]/, '').trim() : source

                        return (
                          <li key={sIdx}>
                            {url ? (
                              <a
                                href={url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-purple-600 hover:text-purple-800 hover:underline break-all"
                              >
                                {isPlainUrl ? url : displayText}
                              </a>
                            ) : (
                              <span>{source}</span>
                            )}
                          </li>
                        )
                      })}
                    </ul>
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>

        {/* AI claims column */}
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <div className="h-1 w-8 rounded bg-emerald-500" />
            <h3 className="text-lg font-semibold text-slate-900">AI-Extracted Claims ({aiClaims.length})</h3>
          </div>
          {aiClaims.map((claim, idx) => {
            const studentClaim = studentClaims[idx]
            const verdictMatch = studentClaim?.verdict === claim.verdict
            const confidenceDiff = studentClaim ? Math.abs(studentClaim.confidence - claim.confidence) : null

            return (
              <Card key={idx} className="border-emerald-200 bg-white">
                <CardHeader className="pb-3">
                  <div className="flex items-center gap-2">
                    <Badge className="bg-emerald-100 text-emerald-700 border-emerald-200">
                      Claim {idx + 1}
                    </Badge>
                    <Badge className={cn('border', verdictColors[claim.verdict] || 'bg-slate-100 text-slate-700')}>
                      {verdictLabel(claim.verdict)}
                    </Badge>
                    {studentClaim && (
                      <Badge
                        className={cn(
                          'text-xs',
                          verdictMatch ? 'bg-green-100 text-green-700 border-green-200' : 'bg-yellow-100 text-yellow-700 border-yellow-200'
                        )}
                      >
                        {verdictMatch ? '✓ Match' : '⚠ Differs'}
                      </Badge>
                    )}
                  </div>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div>
                    <p className="text-sm font-medium text-slate-900">{claim.claim}</p>
                  </div>
                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <div>
                      <span className="text-slate-500">Confidence:</span>
                      <span className="ml-1 font-medium text-slate-900">{claim.confidence?.toFixed(2)}</span>
                    </div>
                    <div>
                      <span className="text-slate-500">Sources:</span>
                      <span className="ml-1 font-medium text-slate-900">{claim.key_sources?.length || 0}</span>
                    </div>
                  </div>
                  {studentClaim && confidenceDiff !== null && (
                    <div className="rounded-lg border border-slate-200 bg-slate-50 p-2">
                      <p className="text-xs font-semibold text-slate-700">Comparison with Your Claim {idx + 1}:</p>
                      <p className="text-xs text-slate-600 mt-1">
                        Confidence diff: <span className="font-medium">{confidenceDiff.toFixed(2)}</span>
                      </p>
                      <p className="text-xs text-slate-600">
                        Verdict: {verdictMatch ?
                          <span className="text-green-700 font-medium">Agreement ✓</span> :
                          <span className="text-yellow-700 font-medium">
                            {studentClaim.verdict} → {claim.verdict}
                          </span>
                        }
                      </p>
                    </div>
                  )}
                  <div>
                    <p className="text-xs font-semibold text-slate-700">AI Justification:</p>
                    <p className="mt-1 text-xs text-slate-600">{claim.justification}</p>
                  </div>
                  {claim.key_sources?.length > 0 && (
                    <div>
                      <p className="text-xs font-semibold text-slate-700">AI Sources:</p>
                      <ul className="mt-1 list-disc pl-4 text-xs text-slate-600 space-y-1">
                        {claim.key_sources.map((source, sIdx) => {
                          // Check if source is a plain URL (starts with http:// or https://)
                          const isPlainUrl = /^https?:\/\//i.test(source.trim())

                          // Parse source to extract URL if present (format: "Source Name [URL]")
                          const urlMatch = source.match(/\[(https?:\/\/[^\]]+)\]/)
                          const url = urlMatch ? urlMatch[1] : (isPlainUrl ? source.trim() : null)
                          const displayText = urlMatch ? source.replace(/\[https?:\/\/[^\]]+\]/, '').trim() : source

                          return (
                            <li key={sIdx}>
                              {url ? (
                                <a
                                  href={url}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="text-emerald-600 hover:text-emerald-800 hover:underline break-all"
                                >
                                  {isPlainUrl ? url : displayText}
                                </a>
                              ) : (
                                <span>{source}</span>
                              )}
                            </li>
                          )
                        })}
                      </ul>
                    </div>
                  )}
                </CardContent>
              </Card>
            )
          })}
        </div>
      </div>

      {/* AI-Powered Analysis Section */}
      <Card className="border-indigo-200 bg-gradient-to-br from-indigo-50 to-purple-50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-lg">
            <Sparkles className="h-5 w-5 text-indigo-600" />
            AI Feedback & Analysis
          </CardTitle>
          <CardDescription>Get personalized feedback on your fact-checking performance</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {!analysis ? (
            <div className="text-center py-6">
              <p className="text-sm text-slate-600 mb-4">
                Click the button below to get AI-powered feedback comparing your work with the AI's analysis.
              </p>
              <Button
                onClick={handleAnalyze}
                disabled={analyzing}
                className="gap-2 bg-indigo-600 hover:bg-indigo-700"
              >
                {analyzing ? (
                  <>
                    <Loader className="h-4 w-4 animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <Sparkles className="h-4 w-4" />
                    Analyze My Performance
                  </>
                )}
              </Button>
              {analysisError && (
                <p className="mt-3 text-sm text-rose-600">{analysisError}</p>
              )}
            </div>
          ) : (
            <div className="space-y-6">
              {/* Overall Summary */}
              {analysis.overall_summary && (
                <div className="rounded-xl border border-indigo-200 bg-indigo-50 p-4">
                  <h4 className="text-sm font-semibold text-indigo-900 mb-2">Summary</h4>
                  <p className="text-sm text-slate-700 leading-relaxed">{analysis.overall_summary}</p>
                </div>
              )}

              {/* Areas for Improvement */}
              {analysis.areas_for_improvement?.length > 0 && (
                <div className="rounded-xl border border-amber-200 bg-amber-50 p-4">
                  <h4 className="text-sm font-semibold text-amber-900 mb-2">💡 Areas for Improvement</h4>
                  <ul className="list-disc pl-4 space-y-1 text-sm text-slate-700">
                    {analysis.areas_for_improvement.map((item, idx) => (
                      <li key={idx} className="leading-relaxed">{item}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Re-analyze button */}
              <div className="text-center pt-2">
                <Button
                  onClick={() => {
                    setAnalysis(null)
                    setAnalysisError(null)
                  }}
                  variant="secondary"
                  size="sm"
                >
                  Clear Analysis
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Reflection prompts */}
      <Card className="border-slate-200 bg-slate-50">
        <CardHeader>
          <CardTitle className="text-base">Reflection Questions</CardTitle>
          <CardDescription>Consider these questions to deepen your critical thinking</CardDescription>
        </CardHeader>
        <CardContent>
          <ul className="list-disc pl-4 space-y-2 text-sm text-slate-700">
            <li>Where did your claims differ from the AI's extracted claims? Did you identify claims the AI missed?</li>
            <li>When verdicts matched, did you and the AI rely on similar evidence and reasoning?</li>
            <li>When verdicts differed, what might explain the disagreement? Source quality? Interpretation?</li>
            <li>How does your confidence level compare to the AI's? What drives those differences?</li>
            <li>What sources did you consult that the AI didn't? What did the AI find that you didn't?</li>
            <li>If you were to re-assess, what would you change based on the AI's analysis?</li>
          </ul>
        </CardContent>
      </Card>
    </div>
  )
}
