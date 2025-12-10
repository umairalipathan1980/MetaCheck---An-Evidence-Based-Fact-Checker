import { Badge } from '../ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card'
import { verdictColors, verdictLabel, stanceColors } from '../../lib/types'
import { cn } from '../../lib/utils'

function KeySources({ sources }) {
  if (!sources?.length) return null

  const renderSource = (src) => {
    try {
      const match = src.match(/\[(https?:\/\/[^\]]+)\]/)
      if (match) {
        const url = match[1]
        const label = src.replace(match[0], '').trim() || url
        return (
          <a href={url} target="_blank" rel="noreferrer" className="text-emerald-700 hover:underline break-all">
            {label}
          </a>
        )
      }
    } catch (e) {
      return src
    }
    return src
  }

  return (
    <div className="space-y-2">
      <h4 className="text-sm font-semibold text-slate-800">Key Sources</h4>
      <ul className="list-disc space-y-1 pl-4 text-sm text-slate-700">
        {sources.map((src, idx) => (
          <li key={idx} className="break-words">
            {renderSource(src)}
          </li>
        ))}
      </ul>
    </div>
  )
}

function EvidenceList({ evidence, sourcesAssessed, mode = 'basic' }) {
  if (!evidence?.length) return <p className="text-sm text-slate-600">No evidence listed.</p>

  const isComprehensive = mode === 'comprehensive'

  const detailByUrl = {}
  if (sourcesAssessed?.length) {
    sourcesAssessed.forEach((s) => {
      if (s.url) {
        detailByUrl[s.url] = s
      }
    })
  }

  if (!isComprehensive) {
    return (
      <div className="space-y-3">
        {evidence.map((ev, idx) => (
          <div
            key={idx}
            className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-800 shadow-sm"
          >
            <div className="flex flex-wrap items-center gap-2">
              <Badge
                className={cn('border', stanceColors[ev.stance] || 'bg-slate-100 text-slate-700 border-slate-200')}
              >
                {ev.source_type} | {ev.stance || 'n/a'}
              </Badge>
              <span className="rounded-lg bg-white px-2 py-1 text-xs text-slate-600">
                Cred: {(ev.credibility_score ?? 0).toFixed(2)}
              </span>
              <span className="rounded-lg bg-white px-2 py-1 text-xs text-slate-600">
                Relevance: {(ev.relevance_score ?? 0).toFixed(2)}
              </span>
            </div>

            <div className="mt-2">
              <p className="font-semibold text-slate-900">{ev.source_name}</p>
              {ev.url ? (
                <a
                  href={ev.url}
                  target="_blank"
                  rel="noreferrer"
                  className="text-xs text-emerald-700 hover:underline break-all"
                >
                  {ev.url}
                </a>
              ) : null}
            </div>

            {ev.snippet ? (
              <div className="mt-2">
                <p className="text-xs uppercase text-slate-500">Snippet</p>
                <p className="text-sm text-slate-700">{ev.snippet}</p>
              </div>
            ) : null}
          </div>
        ))}
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {evidence.map((ev, idx) => {
        const detail = detailByUrl[ev.url] || {}
        const title = detail.title || ev.source_name
        const credibilityText = detail.credibility_reasoning || ''
        const relevanceText = detail.relevance_reasoning || ''
        const stanceText = detail.stance_reasoning || ''
        const keyQuotes = detail.key_quotes || []
        const credibilityFactors = detail.credibility_factors || []
        const relevanceFactors = detail.relevance_factors || []

        return (
          <div
            key={idx}
            className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-800 shadow-sm"
          >
            <div className="flex flex-wrap items-center gap-2">
              <Badge
                className={cn('border', stanceColors[ev.stance] || 'bg-slate-100 text-slate-700 border-slate-200')}
              >
                {ev.source_type} | {ev.stance || 'n/a'}
              </Badge>
              <span className="rounded-lg bg-white px-2 py-1 text-xs text-slate-600">
                Cred: {(ev.credibility_score ?? 0).toFixed(2)}
              </span>
              <span className="rounded-lg bg-white px-2 py-1 text-xs text-slate-600">
                Relevance: {(ev.relevance_score ?? 0).toFixed(2)}
              </span>
            </div>

            <div className="mt-2">
              <p className="font-semibold text-slate-900">{title}</p>
              {ev.url ? (
                <a
                  href={ev.url}
                  target="_blank"
                  rel="noreferrer"
                  className="text-xs text-emerald-700 hover:underline break-all"
                >
                  {ev.url}
                </a>
              ) : null}
            </div>

            {credibilityText && (
              <div className="mt-2">
                <p className="text-xs uppercase text-slate-500">Credibility</p>
                <p className="text-sm text-slate-700">{credibilityText}</p>
                {credibilityFactors.length ? (
                  <p className="text-xs text-slate-500">Factors: {credibilityFactors.join(', ')}</p>
                ) : null}
              </div>
            )}

            {relevanceText && (
              <div className="mt-2">
                <p className="text-xs uppercase text-slate-500">Relevance</p>
                <p className="text-sm text-slate-700">{relevanceText}</p>
                {relevanceFactors.length ? (
                  <p className="text-xs text-slate-500">Factors: {relevanceFactors.join(', ')}</p>
                ) : null}
              </div>
            )}

            {stanceText && (
              <div className="mt-2">
                <p className="text-xs uppercase text-slate-500">Stance reasoning</p>
                <p className="text-sm text-slate-700">{stanceText}</p>
              </div>
            )}

            {keyQuotes.length ? (
              <div className="mt-2 space-y-1">
                <p className="text-xs uppercase text-slate-500">Key Evidence</p>
                {keyQuotes.map((quote, qIdx) => (
                  <p key={qIdx} className="rounded-xl bg-white px-3 py-2 text-sm text-slate-800">
                    {quote}
                  </p>
                ))}
              </div>
            ) : null}

            {ev.snippet ? (
              <div className="mt-2">
                <p className="text-xs uppercase text-slate-500">Snippet</p>
                <p className="text-sm text-slate-700">{ev.snippet}</p>
              </div>
            ) : null}
          </div>
        )
      })}
    </div>
  )
}

function VerdictReasoning({ reasoning }) {
  if (!reasoning) return null
  return (
    <div className="space-y-2">
      <div className="grid grid-cols-1 gap-2 text-sm text-slate-700 md:grid-cols-3">
        <div className="rounded-xl bg-emerald-50 p-3">
          <p className="text-xs uppercase text-emerald-700">Supporting weight</p>
          <p className="text-lg font-semibold text-emerald-900">{reasoning.supporting_weight?.toFixed(2)}</p>
        </div>
        <div className="rounded-xl bg-rose-50 p-3">
          <p className="text-xs uppercase text-rose-700">Refuting weight</p>
          <p className="text-lg font-semibold text-rose-900">{reasoning.refuting_weight?.toFixed(2)}</p>
        </div>
        <div className="rounded-xl bg-slate-50 p-3">
          <p className="text-xs uppercase text-slate-600">Neutral weight</p>
          <p className="text-lg font-semibold text-slate-900">{reasoning.neutral_weight?.toFixed(2)}</p>
        </div>
      </div>
      <div className="rounded-xl border border-slate-200 bg-white p-3 text-sm text-slate-700">
        <p className="font-semibold text-slate-900">Decision rule</p>
        <p>{reasoning.decision_rule_applied}</p>
        {reasoning.decisive_factor && (
          <>
            <p className="mt-2 font-semibold text-slate-900">Decisive factor</p>
            <p>{reasoning.decisive_factor}</p>
          </>
        )}
        {reasoning.decisive_sources?.length ? (
          <>
            <p className="mt-2 font-semibold text-slate-900">Decisive sources</p>
            <ul className="list-disc pl-4">
              {reasoning.decisive_sources.map((src, idx) => (
                <li key={idx}>{src}</li>
              ))}
            </ul>
          </>
        ) : null}
        {reasoning.alternative_verdicts_considered?.length ? (
          <>
            <p className="mt-2 font-semibold text-slate-900">Alternatives considered</p>
            <ul className="list-disc pl-4">
              {reasoning.alternative_verdicts_considered.map((alt, idx) => (
                <li key={idx}>{alt}</li>
              ))}
            </ul>
          </>
        ) : null}
        {reasoning.why_not_alternatives ? (
          <>
            <p className="mt-2 font-semibold text-slate-900">Why alternatives were rejected</p>
            <p>{reasoning.why_not_alternatives}</p>
          </>
        ) : null}
        {reasoning.confidence_reasoning ? (
          <>
            <p className="mt-2 font-semibold text-slate-900">Confidence reasoning</p>
            <p>{reasoning.confidence_reasoning}</p>
          </>
        ) : null}
        {reasoning.confidence_factors?.length ? (
          <>
            <p className="mt-2 font-semibold text-slate-900">Confidence factors</p>
            <ul className="list-disc pl-4">
              {reasoning.confidence_factors.map((f, idx) => (
                <li key={idx}>{f}</li>
              ))}
            </ul>
          </>
        ) : null}
      </div>
    </div>
  )
}

function SearchQueries({ queries }) {
  if (!queries?.length) return null
  return (
    <div className="space-y-2">
      <h4 className="text-sm font-semibold text-slate-800">Search Strategy</h4>
      <div className="grid gap-2 md:grid-cols-2">
        {queries.map((q, idx) => (
          <div key={idx} className="rounded-2xl border border-slate-200 bg-white p-3 text-sm">
            <p className="font-semibold text-slate-900">{q.query_text}</p>
            <p className="text-xs text-slate-500">Tool: {q.source_tool} | Strategy: {q.search_strategy}</p>
            <p className="mt-1 text-slate-700">{q.query_reasoning}</p>
          </div>
        ))}
      </div>
    </div>
  )
}

function ContradictionSection({ data }) {
  if (!data) return null
  if (!data.detected) {
    return (
      <div className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-emerald-700">
        No contradictions detected among sources.
      </div>
    )
  }
  return (
    <div className="rounded-2xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
      <p className="font-semibold">Contradictions detected ({data.severity})</p>
      {data.description ? <p className="mt-1">{data.description}</p> : null}
      {data.contradicting_sources?.length ? (
        <ul className="mt-1 list-disc pl-4">
          {data.contradicting_sources.map((src, idx) => (
            <li key={idx}>{src}</li>
          ))}
        </ul>
      ) : null}
    </div>
  )
}

function SensitivitySection({ data }) {
  if (!data) return null
  if (!data.is_sensitive) {
    return (
      <div className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-700">
        Not identified as a sensitive topic.
      </div>
    )
  }
  return (
    <div className="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-800">
      <p className="font-semibold">Sensitive topic detected</p>
      {data.sensitive_categories?.length ? (
        <p className="mt-1 text-sm text-rose-700">Categories: {data.sensitive_categories.join(', ')}</p>
      ) : null}
      {data.reasoning ? <p className="mt-1">{data.reasoning}</p> : null}
    </div>
  )
}

function EscalationSection({ data }) {
  if (!data) return null
  return (
    <div className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-800">
      <p className="font-semibold">
        Escalation: {data.should_escalate ? 'Required' : 'Not needed'}
      </p>
      {data.reasons?.length ? (
        <ul className="mt-1 list-disc pl-4">
          {data.reasons.map((reason, idx) => (
            <li key={idx}>{reason}</li>
          ))}
        </ul>
      ) : null}
      {data.suggested_actions?.length ? (
        <>
          <p className="mt-2 font-semibold">Suggested actions</p>
          <ul className="list-disc pl-4">
            {data.suggested_actions.map((action, idx) => (
              <li key={idx}>{action}</li>
            ))}
          </ul>
        </>
      ) : null}
      {data.instructor_notes ? (
        <>
          <p className="mt-2 font-semibold">Instructor notes</p>
          <p>{data.instructor_notes}</p>
        </>
      ) : null}
    </div>
  )
}

export function ClaimDetail({ claimResult, mode = 'basic' }) {
  if (!claimResult) return null
  const { claim, verdict, confidence, justification, key_sources, evidence_list, metacognitive_detail } = claimResult
  const isComprehensive = mode === 'comprehensive'

  return (
    <Card className="border-slate-200 bg-white shadow-[0_20px_60px_rgba(15,23,42,0.10)]">
      <CardHeader className="flex flex-col gap-2">
        <div className="flex flex-wrap items-center gap-3">
          <Badge className={cn('border', verdictColors[verdict] || 'bg-slate-100 text-slate-700 border-slate-200')}>
            {verdictLabel(verdict)}
          </Badge>
          <span className="rounded-xl bg-slate-50 px-3 py-1 text-sm text-slate-700">
            Confidence {(confidence ?? 0).toFixed(2)}
          </span>
          <span className="rounded-xl bg-slate-50 px-3 py-1 text-xs font-semibold uppercase text-slate-600">
            Mode: {mode}
          </span>
        </div>
        <CardTitle className="text-xl leading-tight">{claim}</CardTitle>
        <p className="text-sm text-slate-600">{justification}</p>
      </CardHeader>
      <CardContent className="space-y-6">
        {!isComprehensive && (
          <div className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-700">
            Basic mode shows essential facts only. Re-run in comprehensive mode to see full metacognitive reasoning.
          </div>
        )}
        <KeySources sources={key_sources} />
        <EvidenceList evidence={evidence_list} sourcesAssessed={metacognitive_detail?.sources_assessed} mode={mode} />
        {isComprehensive && metacognitive_detail?.contradiction_detection ? (
          <div className="space-y-2">
            <h4 className="text-sm font-semibold text-slate-800">Contradiction analysis</h4>
            <ContradictionSection data={metacognitive_detail.contradiction_detection} />
          </div>
        ) : null}
        {isComprehensive && metacognitive_detail?.sensitivity_analysis ? (
          <div className="space-y-2">
            <h4 className="text-sm font-semibold text-slate-800">Sensitivity analysis</h4>
            <SensitivitySection data={metacognitive_detail.sensitivity_analysis} />
          </div>
        ) : null}
        {isComprehensive && metacognitive_detail?.verdict_reasoning && (
          <VerdictReasoning reasoning={metacognitive_detail.verdict_reasoning} />
        )}
        {isComprehensive && metacognitive_detail?.search_queries && (
          <SearchQueries queries={metacognitive_detail.search_queries} />
        )}
        {isComprehensive && metacognitive_detail?.escalation_decision ? (
          <div className="space-y-2">
            <h4 className="text-sm font-semibold text-slate-800">Escalation decision</h4>
            <EscalationSection data={metacognitive_detail.escalation_decision} />
          </div>
        ) : null}
        {isComprehensive && metacognitive_detail?.ai_uncertainties?.length ? (
          <div>
            <h4 className="text-sm font-semibold text-slate-800">AI Uncertainties</h4>
            <ul className="list-disc pl-4 text-sm text-slate-700">
              {metacognitive_detail.ai_uncertainties.map((item, idx) => (
                <li key={idx}>{item}</li>
              ))}
            </ul>
          </div>
        ) : null}
        {isComprehensive && metacognitive_detail?.assumptions_made?.length ? (
          <div>
            <h4 className="text-sm font-semibold text-slate-800">Assumptions</h4>
            <ul className="list-disc pl-4 text-sm text-slate-700">
              {metacognitive_detail.assumptions_made.map((item, idx) => (
                <li key={idx}>{item}</li>
              ))}
            </ul>
          </div>
        ) : null}
        {isComprehensive && metacognitive_detail?.potential_weaknesses?.length ? (
          <div>
            <h4 className="text-sm font-semibold text-slate-800">Potential weaknesses</h4>
            <ul className="list-disc pl-4 text-sm text-slate-700">
              {metacognitive_detail.potential_weaknesses.map((item, idx) => (
                <li key={idx}>{item}</li>
              ))}
            </ul>
          </div>
        ) : null}
        {isComprehensive && metacognitive_detail?.metacognitive_summary ? (
          <div>
            <h4 className="text-sm font-semibold text-slate-800">Metacognitive summary</h4>
            <p className="text-sm text-slate-700">{metacognitive_detail.metacognitive_summary}</p>
          </div>
        ) : null}
        {isComprehensive && metacognitive_detail?.total_assessment_time ? (
          <p className="text-xs text-slate-500">
            Total assessment time: {metacognitive_detail.total_assessment_time.toFixed(1)} seconds
          </p>
        ) : null}
      </CardContent>
    </Card>
  )
}
