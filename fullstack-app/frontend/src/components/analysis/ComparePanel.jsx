import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card'
import { Badge } from '../ui/badge'
import { verdictColors, verdictLabel } from '../../lib/types'
import { cn } from '../../lib/utils'

export function ComparePanel({ studentAssessment, aiResult }) {
  const aiClaim = aiResult?.claim_results?.[0]

  if (!studentAssessment && !aiResult) {
    return (
      <Card className="border-slate-200">
        <CardContent className="py-10 text-center text-slate-600">
          Add your assessment and run AI analysis to view comparisons.
        </CardContent>
      </Card>
    )
  }

  if (!aiResult) {
    return (
      <Card className="border-slate-200">
        <CardContent className="py-10 text-center text-slate-600">
          Run AI analysis to compare with your assessment.
        </CardContent>
      </Card>
    )
  }

  if (!studentAssessment) {
    return (
      <Card className="border-slate-200">
        <CardContent className="py-10 text-center text-slate-600">
          You skipped your own assessment. You can still review the AI results above.
        </CardContent>
      </Card>
    )
  }

  const verdictMatch = studentAssessment.verdict === aiClaim?.verdict
  const confidenceDiff = aiClaim ? Math.abs(studentAssessment.confidence - aiClaim.confidence) : null

  return (
    <Card className="border-slate-200 bg-white shadow-[0_20px_50px_rgba(15,23,42,0.08)]">
      <CardHeader>
        <CardTitle className="text-lg">Compare your assessment with AI</CardTitle>
        <CardDescription>See where you align or differ.</CardDescription>
      </CardHeader>
      <CardContent className="grid gap-4 md:grid-cols-2">
        <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
          <p className="text-xs uppercase text-slate-500">Your verdict</p>
          <p className="mt-1 text-lg font-semibold text-slate-900">{studentAssessment.verdict}</p>
          <p className="text-sm text-slate-600">Confidence {studentAssessment.confidence.toFixed(2)}</p>
        </div>
        {aiClaim ? (
          <div className="rounded-2xl border border-slate-200 bg-emerald-50/60 p-4">
            <p className="text-xs uppercase text-emerald-700">AI verdict (claim 1)</p>
            <Badge
              className={cn(
                'mt-2 border',
                verdictColors[aiClaim.verdict] || 'bg-slate-100 text-slate-700 border-slate-200'
              )}
            >
              {verdictLabel(aiClaim.verdict)}
            </Badge>
            <p className="mt-2 text-sm text-slate-700">
              Confidence {aiClaim.confidence?.toFixed(2)} · {aiClaim.key_sources?.length || 0} sources
            </p>
          </div>
        ) : (
          <div className="rounded-2xl border border-slate-200 bg-white p-4 text-sm text-slate-600">
            AI did not return claims.
          </div>
        )}

        <div className="md:col-span-2 rounded-2xl border border-slate-200 bg-white p-4">
          <p className="text-sm font-semibold text-slate-900">Reasoning (you)</p>
          <p className="mt-1 text-sm text-slate-700 whitespace-pre-line">{studentAssessment.reasoning}</p>
        </div>

        <div className="md:col-span-2 grid gap-3 md:grid-cols-2">
          <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-700">
            <p className="text-xs uppercase text-slate-500">Key sources (you)</p>
            {studentAssessment.keySources?.length ? (
              <ul className="mt-2 list-disc pl-4">
                {studentAssessment.keySources.map((s, idx) => (
                  <li key={idx}>{s}</li>
                ))}
              </ul>
            ) : (
              <p className="mt-2 text-slate-500">No sources provided.</p>
            )}
          </div>
          <div className="rounded-2xl border border-slate-200 bg-emerald-50/50 p-4 text-sm text-slate-700">
            <p className="text-xs uppercase text-emerald-700">Key sources (AI claim 1)</p>
            {aiClaim?.key_sources?.length ? (
              <ul className="mt-2 list-disc pl-4">
                {aiClaim.key_sources.map((s, idx) => (
                  <li key={idx}>{s}</li>
                ))}
              </ul>
            ) : (
              <p className="mt-2 text-emerald-700/80">No sources listed.</p>
            )}
          </div>
        </div>

        {aiClaim && (
          <div className="md:col-span-2 rounded-2xl border border-slate-200 bg-white p-4 text-sm text-slate-700">
            <p className="text-xs uppercase text-slate-500">Alignment</p>
            <p className="mt-1 text-sm font-semibold text-slate-900">
              {verdictMatch ? 'Verdicts match' : 'Verdicts differ'}
            </p>
            {confidenceDiff !== null && (
              <p className="text-sm text-slate-700">Confidence difference: {confidenceDiff.toFixed(2)}</p>
            )}
          </div>
        )}

        <div className="md:col-span-2 rounded-2xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-700">
          <p className="text-xs uppercase text-slate-500">Reflection prompts</p>
          <ul className="mt-2 list-disc pl-4 space-y-1">
            <li>Why did you reach your verdict? What evidence mattered most?</li>
            <li>Where do your sources differ from the AI’s key sources?</li>
            <li>If verdicts differ, what would change your mind?</li>
          </ul>
        </div>
      </CardContent>
    </Card>
  )
}
