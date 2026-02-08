import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card'
import { Button } from '../ui/button'
import { DomainLegend } from './DomainLegend'
import { ChevronDown, ChevronRight } from 'lucide-react'

// Collapsible Section Component
function CollapsibleSection({ title, children, defaultOpen = false }) {
  const [isOpen, setIsOpen] = useState(defaultOpen)

  return (
    <div className="border border-slate-200 rounded-lg overflow-hidden">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full px-4 py-3 bg-slate-50 hover:bg-slate-100 transition-colors flex items-center justify-between text-left"
      >
        <h3 className="text-base font-semibold text-slate-900">{title}</h3>
        {isOpen ? (
          <ChevronDown className="w-5 h-5 text-slate-600" />
        ) : (
          <ChevronRight className="w-5 h-5 text-slate-600" />
        )}
      </button>
      {isOpen && (
        <div className="p-4 bg-white space-y-3">
          {children}
        </div>
      )}
    </div>
  )
}

export function ToolDocumentation({ categories }) {
  const [activeTab, setActiveTab] = useState('getting-started')

  const tabs = [
    { key: 'getting-started', label: 'How to Use' },
    { key: 'verdicts', label: 'Understanding Verdicts' },
    { key: 'sources', label: 'Evidence Sources' },
    { key: 'workflow', label: 'How It Works' },
    { key: 'educational', label: 'Educational Use' },
  ]

  return (
    <Card className="border-slate-200">
      <CardHeader>
        <CardTitle className="text-2xl">MetaCheck Documentation</CardTitle>
        <p className="text-sm text-slate-600 mt-2">
          Complete guide to using MetaCheck for educational fact-checking and media literacy learning
        </p>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Tab Navigation */}
        <div className="flex flex-wrap gap-2 border-b border-slate-200 pb-3">
          {tabs.map((tab) => (
            <Button
              key={tab.key}
              variant={activeTab === tab.key ? 'default' : 'ghost'}
              onClick={() => setActiveTab(tab.key)}
              className="text-sm"
              size="sm"
            >
              {tab.label}
            </Button>
          ))}
        </div>

        {/* Tab Content */}
        <div className="text-sm text-slate-700 space-y-6 pt-2">
          {activeTab === 'getting-started' && <GettingStartedTab />}
          {activeTab === 'verdicts' && <VerdictsTab />}
          {activeTab === 'sources' && <SourcesTab categories={categories} />}
          {activeTab === 'workflow' && <WorkflowTab />}
          {activeTab === 'educational' && <EducationalTab />}
        </div>
      </CardContent>
    </Card>
  )
}

// ============================================================================
// GETTING STARTED TAB
// ============================================================================
function GettingStartedTab() {
  return (
    <div className="space-y-4">
      <CollapsibleSection title="What is MetaCheck?" defaultOpen={true}>
        <p className="leading-relaxed">
          MetaCheck is an educational fact-checking tool designed to help students and educators learn how to evaluate
          information critically. Unlike commercial fact-checkers, MetaCheck's primary goal is <strong>educational transparency</strong> —
          showing students <em>how</em> AI systems verify claims, not just what verdict they reach.
        </p>
        <p className="leading-relaxed">
          The tool combines three evidence sources (web search via Tavily, Wikipedia, and professional fact-checking databases)
          with transparent reasoning to help students understand the fact-checking process, learn about source credibility,
          and develop critical thinking skills for the digital age.
        </p>
      </CollapsibleSection>

      <CollapsibleSection title="Recommended Educational Workflow" defaultOpen={true}>
        <p className="leading-relaxed">
          While you <em>can</em> use the <strong>"AI Analysis"</strong> tab directly to fact-check any text, MetaCheck is
          designed for <strong>educational learning</strong>. The most effective way to develop critical thinking skills
          is to follow this three-step workflow:
        </p>

        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border-2 border-blue-300 rounded-xl p-6 my-4">
          <h4 className="font-bold text-indigo-900 mb-4 text-base flex items-center gap-2">
            <span className="bg-indigo-600 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm">✓</span>
            The Complete Learning Sequence
          </h4>

          <div className="space-y-4">
            <div className="flex gap-4">
              <div className="flex-shrink-0">
                <div className="bg-blue-600 text-white font-bold rounded-full w-8 h-8 flex items-center justify-center">1</div>
              </div>
              <div className="flex-1">
                <h5 className="font-semibold text-blue-900 mb-1">Start with "Your Assessment" Tab</h5>
                <p className="text-sm text-blue-900 leading-relaxed">
                  <strong>This is where learning begins.</strong> Before seeing AI results, manually create your own fact-checking
                  assessment. Read the text, identify claims you think are verifiable, research them using search engines,
                  evaluate sources, and make your own verdicts with confidence scores and reasoning. This independent work
                  forces you to think critically before knowing the "answer."
                </p>
              </div>
            </div>

            <div className="h-px bg-blue-200 my-2"></div>

            <div className="flex gap-4">
              <div className="flex-shrink-0">
                <div className="bg-indigo-600 text-white font-bold rounded-full w-8 h-8 flex items-center justify-center">2</div>
              </div>
              <div className="flex-1">
                <h5 className="font-semibold text-indigo-900 mb-1">Then Use "AI Analysis" Tab</h5>
                <p className="text-sm text-indigo-900 leading-relaxed">
                  After completing your own assessment, use AI Analysis to verify the same text. Extract claims automatically,
                  select the claims you want to verify (preferably the same ones you assessed), and run the AI fact-checking
                  workflow. Review the AI's verdicts, confidence scores, sources, and reasoning. Use <strong>Comprehensive Mode</strong>
                  to see the full metacognitive detail about how the AI reached its conclusions.
                </p>
              </div>
            </div>

            <div className="h-px bg-blue-200 my-2"></div>

            <div className="flex gap-4">
              <div className="flex-shrink-0">
                <div className="bg-purple-600 text-white font-bold rounded-full w-8 h-8 flex items-center justify-center">3</div>
              </div>
              <div className="flex-1">
                <h5 className="font-semibold text-purple-900 mb-1">Finally, "Compare" Your Results</h5>
                <p className="text-sm text-purple-900 leading-relaxed">
                  Go to the <strong>"Compare"</strong> tab to see side-by-side differences between your assessment and the AI's.
                  Did you reach the same verdicts? Were your confidence levels similar? Did you use the same sources or different ones?
                  How did your reasoning differ? Use the <strong>"Analyze My Performance"</strong> button to get an AI-generated
                  analysis of your fact-checking skills, including strengths, areas for improvement, and specific feedback on
                  your source evaluation, evidence synthesis, and verdict reasoning.
                </p>
              </div>
            </div>
          </div>

          <div className="mt-5 pt-4 border-t border-blue-200">
            <p className="text-xs text-blue-800 leading-relaxed">
              <strong>💡 Why this sequence matters:</strong> Trying to fact-check claims independently <em>before</em> seeing
              AI results helps you develop your own reasoning skills. If you see the AI answer first, you're more likely to
              anchor to its verdict rather than building your own critical thinking capacity. The comparison step reveals
              your blind spots and learning opportunities.
            </p>
          </div>
        </div>

        <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
          <p className="font-semibold text-amber-900 mb-2 text-sm">⚡ Quick Option: Direct AI Analysis</p>
          <p className="text-sm text-amber-900 leading-relaxed">
            If you just want to fact-check something quickly without the learning workflow, you can skip directly to
            <strong> "AI Analysis"</strong> and use it as a standalone fact-checker. This is useful when you need fast
            verification but aren't focused on educational learning. However, you'll miss out on the valuable comparison
            and self-reflection that makes MetaCheck educational.
          </p>
        </div>
      </CollapsibleSection>

      <CollapsibleSection title="Understanding 'Analyze My Performance'">
        <p className="leading-relaxed">
          After completing both your own assessment and AI verification, the <strong>"Compare"</strong> tab offers an
          <strong> "Analyze My Performance"</strong> button. This feature uses AI to evaluate your fact-checking skills
          and provide personalized feedback.
        </p>

        <div className="bg-slate-50 border border-slate-200 rounded-lg p-4 space-y-3">
          <div>
            <h5 className="font-semibold text-slate-900 mb-2 text-sm">What It Analyzes:</h5>
            <ul className="ml-4 space-y-1.5 text-sm text-slate-700">
              <li className="leading-relaxed">
                <strong>Verdict Agreement:</strong> Did you reach the same conclusions as the AI? If not, why might your
                assessments differ? Were you overconfident about uncertain claims or too cautious about supported claims?
              </li>
              <li className="leading-relaxed">
                <strong>Confidence Calibration:</strong> How well-calibrated is your confidence? Do you tend to be overconfident,
                underconfident, or appropriately uncertain? Good fact-checkers match confidence to evidence quality.
              </li>
              <li className="leading-relaxed">
                <strong>Source Evaluation:</strong> Did you identify and use credible sources? Did you rely on high-credibility
                sources (fact-checkers, government, academic) or low-credibility sources (blogs, forums)? Did you miss
                important sources that the AI found?
              </li>
              <li className="leading-relaxed">
                <strong>Evidence Synthesis:</strong> How well did you integrate multiple pieces of evidence? Did you properly
                weight evidence by credibility, or did you just count sources? Did you identify when evidence was conflicting?
              </li>
              <li className="leading-relaxed">
                <strong>Reasoning Quality:</strong> Is your justification clear, logical, and evidence-based? Does it explain
                <em>why</em> you reached your verdict, not just <em>what</em> the verdict is?
              </li>
            </ul>
          </div>

          <div>
            <h5 className="font-semibold text-slate-900 mb-2 text-sm">What You Get:</h5>
            <div className="bg-white rounded p-3 text-sm space-y-2">
              <p className="leading-relaxed">
                <strong>Strengths:</strong> Specific skills you demonstrated well (e.g., "You correctly identified high-credibility
                sources and weighted them appropriately")
              </p>
              <p className="leading-relaxed">
                <strong>Areas for Improvement:</strong> Skills to work on (e.g., "Consider checking fact-checking databases
                in addition to news sources")
              </p>
              <p className="leading-relaxed">
                <strong>Specific Feedback:</strong> Detailed observations about your claim-by-claim assessments, highlighting
                where you excelled and where you could improve
              </p>
              <p className="leading-relaxed">
                <strong>Learning Recommendations:</strong> Actionable suggestions for developing your fact-checking skills
              </p>
            </div>
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded p-3">
            <p className="text-xs text-blue-900 leading-relaxed">
              <strong>💡 Educational Value:</strong> This feedback helps you understand not just whether you were "right"
              or "wrong," but <em>why</em> your reasoning differed from the AI's. Over time, this builds metacognitive
              awareness about your own fact-checking process and helps you identify patterns in your thinking that may
              need adjustment.
            </p>
          </div>
        </div>
      </CollapsibleSection>

      <CollapsibleSection title="Quick Start Guide (Direct AI Analysis)">
        <p className="text-sm text-slate-600 mb-3">
          If you want to use AI Analysis directly without the full educational workflow, follow these steps:
        </p>
        <div className="space-y-4">
          <div className="bg-slate-50 border border-slate-200 rounded-lg p-4">
            <h4 className="font-semibold text-slate-900 mb-2">Step 1: Input Your Text</h4>
            <p className="leading-relaxed">
              Go to the <strong>"AI Analysis"</strong> tab and paste or type text containing claims you want to verify.
              This could be a social media post, news article excerpt, political statement, or any text with factual claims.
            </p>
            <p className="text-xs text-slate-600 mt-2">
              <strong>Limit:</strong> Up to 2,000 characters (about 300-400 words)
            </p>
          </div>

          <div className="bg-slate-50 border border-slate-200 rounded-lg p-4">
            <h4 className="font-semibold text-slate-900 mb-2">Step 2: Choose Your Mode</h4>
            <p className="leading-relaxed mb-2">Select the analysis depth:</p>
            <ul className="space-y-2 ml-4">
              <li className="leading-relaxed">
                <strong>Basic Mode:</strong> Quick verification with concise justification. Best for classroom demonstrations
                or when you need fast results. Shows verdict, confidence, key sources, and brief reasoning.
              </li>
              <li className="leading-relaxed">
                <strong>Comprehensive Mode:</strong> Deep analysis with full metacognitive transparency. Shows search strategy,
                source assessments, verdict reasoning, AI uncertainties, and assumptions. Best for learning <em>how</em> fact-checking works.
              </li>
            </ul>
          </div>

          <div className="bg-slate-50 border border-slate-200 rounded-lg p-4">
            <h4 className="font-semibold text-slate-900 mb-2">Step 3: Extract Claims</h4>
            <p className="leading-relaxed">
              Click <strong>"Extract Claims"</strong> to automatically identify verifiable factual claims in your text.
              The AI will filter out opinions, well-known facts, and vague statements, focusing only on specific,
              checkable assertions that require evidence.
            </p>
            <p className="text-xs text-slate-600 mt-2">
              <strong>Note:</strong> Not all sentences are verifiable claims! The extractor looks for specific, falsifiable
              statements with concrete details (numbers, dates, names, locations).
            </p>
          </div>

          <div className="bg-slate-50 border border-slate-200 rounded-lg p-4">
            <h4 className="font-semibold text-slate-900 mb-2">Step 4: Select Claims to Verify</h4>
            <p className="leading-relaxed">
              Choose which extracted claims you want to verify (up to 5 claims in either mode). You don't need to verify
              all extracted claims — select the most important or interesting ones.
            </p>
          </div>

          <div className="bg-slate-50 border border-slate-200 rounded-lg p-4">
            <h4 className="font-semibold text-slate-900 mb-2">Step 5: Verify and Review</h4>
            <p className="leading-relaxed">
              Click <strong>"Verify Selected Claims"</strong> and wait for results (typically 10-30 seconds). Each claim
              is analyzed independently, searching multiple sources in parallel. Review the results to see verdicts,
              confidence scores, evidence, and reasoning.
            </p>
          </div>

          <div className="bg-slate-50 border border-slate-200 rounded-lg p-4">
            <h4 className="font-semibold text-slate-900 mb-2">Step 6: Compare with Your Assessment (Optional but Recommended)</h4>
            <p className="leading-relaxed mb-2">
              For maximum educational benefit, create your own assessment <strong>before</strong> running AI Analysis
              (see "Recommended Educational Workflow" above). If you've already created an assessment in the
              <strong> "Your Assessment"</strong> tab, go to the <strong>"Compare"</strong> tab to see how your
              evaluation differs from the AI's.
            </p>
            <p className="text-sm leading-relaxed text-slate-600">
              The <strong>"Analyze My Performance"</strong> button in the Compare tab provides personalized feedback
              on your fact-checking skills, including verdict agreement, confidence calibration, source evaluation,
              and reasoning quality. This helps identify your strengths and areas for improvement.
            </p>
          </div>
        </div>
      </CollapsibleSection>

      <CollapsibleSection title="Interface Overview">
        <div className="overflow-x-auto rounded-xl border border-slate-200">
          <table className="w-full min-w-[700px] border-collapse text-left">
            <thead className="bg-slate-50 text-slate-900">
              <tr>
                <th className="border-b border-slate-200 px-4 py-3 font-semibold">Tab</th>
                <th className="border-b border-slate-200 px-4 py-3 font-semibold">Purpose</th>
                <th className="border-b border-slate-200 px-4 py-3 font-semibold">When to Use</th>
              </tr>
            </thead>
            <tbody>
              <tr className="align-top">
                <td className="border-b border-slate-100 px-4 py-3 font-medium">Your Assessment</td>
                <td className="border-b border-slate-100 px-4 py-3">
                  Create your own evaluation before seeing AI results
                </td>
                <td className="border-b border-slate-100 px-4 py-3">
                  Use this to practice fact-checking skills independently, then compare with AI to learn
                </td>
              </tr>
              <tr className="align-top">
                <td className="border-b border-slate-100 px-4 py-3 font-medium">AI Analysis</td>
                <td className="border-b border-slate-100 px-4 py-3">
                  Run automated fact-checking with evidence and reasoning
                </td>
                <td className="border-b border-slate-100 px-4 py-3">
                  Main verification workflow — extract claims and verify them with multiple sources
                </td>
              </tr>
              <tr className="align-top">
                <td className="border-b border-slate-100 px-4 py-3 font-medium">Compare</td>
                <td className="border-b border-slate-100 px-4 py-3">
                  See differences between your assessment and AI's analysis
                </td>
                <td className="border-b border-slate-100 px-4 py-3">
                  Use after both assessments to identify learning opportunities and understand AI reasoning
                </td>
              </tr>
              <tr className="align-top">
                <td className="px-4 py-3 font-medium">Documentation</td>
                <td className="px-4 py-3">
                  Learn how the system works and how to interpret results
                </td>
                <td className="px-4 py-3">
                  Reference guide for understanding verdicts, sources, and system behavior
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </CollapsibleSection>

    </div>
  )
}

// ============================================================================
// VERDICTS TAB
// ============================================================================
function VerdictsTab() {
  return (
    <div className="space-y-4">
      <CollapsibleSection title="Understanding Verdict Classifications" defaultOpen={true}>
        <p className="leading-relaxed">
          MetaCheck uses a four-category verdict system based on professional fact-checking standards. Each verdict
          reflects the <strong>weight and quality of available evidence</strong>, not just majority opinion. Understanding
          these verdicts helps you interpret results correctly and avoid common misconceptions.
        </p>
      </CollapsibleSection>

      <CollapsibleSection title="SUPPORTED - Evidence Confirms the Claim">
        <div className="bg-emerald-50 border-2 border-emerald-200 rounded-lg p-5">
          <div className="flex items-start gap-3 mb-3">
            <div className="bg-emerald-600 text-white font-bold rounded px-3 py-1 text-sm">SUPPORTED</div>
          </div>
          <h4 className="font-semibold text-emerald-900 mb-2 text-base">Evidence Confirms the Claim</h4>
          <p className="text-emerald-900 leading-relaxed mb-3">
            This verdict means that <strong>credible sources confirm the claim</strong> and there is little or no credible
            contradictory evidence. It doesn't mean the claim is "absolutely true" — it means the available evidence supports it.
          </p>

          <h5 className="font-semibold text-emerald-900 text-sm mb-2">When SUPPORTED is assigned:</h5>
          <ul className="space-y-1.5 ml-4 text-emerald-900 text-sm">
            <li className="leading-relaxed">• Multiple credible sources (credibility ≥ 0.7) align with the claim</li>
            <li className="leading-relaxed">• Evidence directly addresses the core assertion</li>
            <li className="leading-relaxed">• No credible contradictory evidence exists</li>
            <li className="leading-relaxed">• Sources are authoritative and up-to-date (for time-sensitive claims)</li>
          </ul>

          <div className="mt-4 pt-4 border-t border-emerald-200">
            <p className="font-semibold text-emerald-900 text-sm mb-2">Example Scenarios:</p>
            <div className="space-y-2 text-sm text-emerald-900">
              <div className="bg-white bg-opacity-60 rounded p-3">
                <p className="font-medium mb-1">Claim: "The Eiffel Tower is 330 meters tall"</p>
                <p className="text-xs">
                  <strong>Why SUPPORTED:</strong> Multiple reliable sources (Wikipedia 0.80, official website 0.85,
                  encyclopedia 0.82) confirm this measurement with no contradictions
                </p>
              </div>
              <div className="bg-white bg-opacity-60 rounded p-3">
                <p className="font-medium mb-1">Claim: "COVID-19 vaccines reduce severe illness"</p>
                <p className="text-xs">
                  <strong>Why SUPPORTED:</strong> High-credibility sources (CDC 0.90, WHO 0.90, peer-reviewed studies 0.85)
                  provide consistent evidence with extensive clinical data
                </p>
              </div>
            </div>
          </div>
        </div>
      </CollapsibleSection>

      <CollapsibleSection title="REFUTED - Evidence Contradicts the Claim">
        <div className="bg-rose-50 border-2 border-rose-200 rounded-lg p-5">
          <div className="flex items-start gap-3 mb-3">
            <div className="bg-rose-600 text-white font-bold rounded px-3 py-1 text-sm">REFUTED</div>
          </div>
          <h4 className="font-semibold text-rose-900 mb-2 text-base">Evidence Contradicts the Claim</h4>
          <p className="text-rose-900 leading-relaxed mb-3">
            This verdict indicates that <strong>credible sources explicitly contradict the claim</strong> with direct
            counter-evidence. Importantly, even if some low-credibility sources support the claim, high-credibility
            refutations take precedence.
          </p>

          <h5 className="font-semibold text-rose-900 text-sm mb-2">When REFUTED is assigned:</h5>
          <ul className="space-y-1.5 ml-4 text-rose-900 text-sm">
            <li className="leading-relaxed">• Credible sources (credibility ≥ 0.7) provide clear counter-factual information</li>
            <li className="leading-relaxed">• Contradiction is direct and unambiguous</li>
            <li className="leading-relaxed">• High-credibility sources (&gt; 0.8) outweigh low-credibility supporting sources</li>
            <li className="leading-relaxed">• Evidence specifically addresses and disproves the claim</li>
          </ul>

          <div className="mt-4 pt-4 border-t border-rose-200">
            <p className="font-semibold text-rose-900 text-sm mb-2">Important Note About Evidence Weight:</p>
            <div className="bg-white bg-opacity-60 rounded p-3 text-sm text-rose-900 mb-3">
              <p className="leading-relaxed">
                <strong>One high-credibility source (0.95) can outweigh multiple low-credibility sources (0.50-0.65).</strong>
                This reflects how professional fact-checkers work: a statement from the CDC carries more weight than ten
                anonymous blog posts, even if the blogs say the opposite.
              </p>
            </div>

            <p className="font-semibold text-rose-900 text-sm mb-2">Example Scenarios:</p>
            <div className="space-y-2 text-sm text-rose-900">
              <div className="bg-white bg-opacity-60 rounded p-3">
                <p className="font-medium mb-1">Claim: "The COVID-19 vaccine contains microchips"</p>
                <p className="text-xs">
                  <strong>Why REFUTED:</strong> Multiple fact-checkers (0.95), medical authorities (0.90), and scientific
                  sources (0.85) explicitly debunk this with detailed explanations. Low-credibility blogs supporting the
                  claim (0.50-0.60) are outweighed.
                </p>
              </div>
              <div className="bg-white bg-opacity-60 rounded p-3">
                <p className="font-medium mb-1">Claim: "The 2020 US election was stolen"</p>
                <p className="text-xs">
                  <strong>Why REFUTED:</strong> Official government sources (0.90), fact-checkers (0.95), and courts (0.88)
                  found no evidence of widespread fraud. High-credibility consensus outweighs partisan claims.
                </p>
              </div>
            </div>
          </div>
        </div>
      </CollapsibleSection>

      <CollapsibleSection title="INSUFFICIENT_INFORMATION - Not Enough Evidence">
        <div className="bg-slate-50 border-2 border-slate-200 rounded-lg p-5">
          <div className="flex items-start gap-3 mb-3">
            <div className="bg-slate-600 text-white font-bold rounded px-3 py-1 text-sm">INSUFFICIENT_INFORMATION</div>
          </div>
          <h4 className="font-semibold text-slate-900 mb-2 text-base">Not Enough Reliable Evidence to Decide</h4>
          <p className="text-slate-900 leading-relaxed mb-3">
            This verdict means the system <strong>couldn't find enough credible evidence</strong> to make a determination.
            This is <em>not</em> the same as "probably false" — it means we genuinely don't have sufficient information.
          </p>

          <h5 className="font-semibold text-slate-900 text-sm mb-2">When INSUFFICIENT_INFORMATION is assigned:</h5>
          <ul className="space-y-1.5 ml-4 text-slate-900 text-sm">
            <li className="leading-relaxed">• Very few sources found (fewer than 2 sources total)</li>
            <li className="leading-relaxed">• All available sources lack credibility (all below 0.7)</li>
            <li className="leading-relaxed">• Evidence is indirect, vague, or incomplete on all sides</li>
            <li className="leading-relaxed">• Key information is missing for proper verification</li>
            <li className="leading-relaxed">• Evidence is outdated for time-sensitive claims</li>
          </ul>

          <div className="mt-4 pt-4 border-t border-slate-200">
            <p className="font-semibold text-slate-900 text-sm mb-2">Common Reasons for This Verdict:</p>
            <div className="space-y-2 text-sm text-slate-900">
              <div className="bg-white rounded p-3">
                <p className="font-medium mb-1">1. Obscure or Recent Claims</p>
                <p className="text-xs leading-relaxed">
                  Very recent events or niche topics may not have been covered by credible sources yet.
                  Example: A claim about a local event from yesterday may not be in Wikipedia or fact-checking databases.
                </p>
              </div>
              <div className="bg-white rounded p-3">
                <p className="font-medium mb-1">2. Only Low-Credibility Sources Available</p>
                <p className="text-xs leading-relaxed">
                  If the claim is only discussed in blogs, forums, or unverified sources (all below 0.7 credibility),
                  the system cannot make a confident determination.
                </p>
              </div>
              <div className="bg-white rounded p-3">
                <p className="font-medium mb-1">3. Vague or Ambiguous Claims</p>
                <p className="text-xs leading-relaxed">
                  Claims lacking specific details make it hard to find relevant evidence.
                  Example: "Technology companies are becoming more powerful" is too vague to verify with specific evidence.
                </p>
              </div>
            </div>

            <div className="mt-3 bg-amber-50 border border-amber-200 rounded p-3 text-sm text-amber-900">
              <p className="font-semibold mb-1">⚠️ Important Distinction:</p>
              <p className="text-xs leading-relaxed">
                <strong>INSUFFICIENT_INFORMATION is NOT used when credible evidence clearly supports or refutes a claim.</strong>
                If high-credibility sources definitively confirm or debunk something, the verdict will be SUPPORTED or REFUTED,
                even if some low-credibility sources disagree.
              </p>
            </div>
          </div>
        </div>
      </CollapsibleSection>

      <CollapsibleSection title="CONFLICTING_EVIDENCE - Credible Sources Disagree">
        <div className="bg-amber-50 border-2 border-amber-200 rounded-lg p-5">
          <div className="flex items-start gap-3 mb-3">
            <div className="bg-amber-600 text-white font-bold rounded px-3 py-1 text-sm">CONFLICTING_EVIDENCE</div>
          </div>
          <h4 className="font-semibold text-amber-900 mb-2 text-base">Credible Evidence Exists on Both Sides</h4>
          <p className="text-amber-900 leading-relaxed mb-3">
            This verdict indicates that <strong>credible sources disagree</strong> with each other, providing evidence on
            both supporting and refuting sides. This represents genuine uncertainty or ongoing debate among reliable sources.
          </p>

          <h5 className="font-semibold text-amber-900 text-sm mb-2">When CONFLICTING_EVIDENCE is assigned:</h5>
          <ul className="space-y-1.5 ml-4 text-amber-900 text-sm">
            <li className="leading-relaxed">• Multiple credible sources (≥ 0.7) present opposing views on BOTH sides</li>
            <li className="leading-relaxed">• Both supporting and refuting evidence comes from credible sources</li>
            <li className="leading-relaxed">• Credibility and quantity are roughly balanced between both sides</li>
            <li className="leading-relaxed">• No clear resolution from available evidence</li>
          </ul>

          <div className="mt-4 pt-4 border-t border-amber-200">
            <p className="font-semibold text-amber-900 text-sm mb-2">Critical Requirement:</p>
            <div className="bg-white bg-opacity-60 rounded p-3 text-sm text-amber-900 mb-3">
              <p className="leading-relaxed">
                <strong>This verdict requires GENUINE conflict between credible sources.</strong> It's NOT assigned when
                low-credibility sources contradict high-credibility sources — in that case, high credibility wins and the
                verdict is SUPPORTED or REFUTED. Both sides must have credible evidence (≥ 0.7).
              </p>
            </div>

            <p className="font-semibold text-amber-900 text-sm mb-2">Example Scenarios:</p>
            <div className="space-y-2 text-sm text-amber-900">
              <div className="bg-white bg-opacity-60 rounded p-3">
                <p className="font-medium mb-1">Claim: "Coffee consumption increases lifespan"</p>
                <p className="text-xs">
                  <strong>Why CONFLICTING:</strong> Multiple peer-reviewed studies (0.80-0.85) show both positive and
                  negative correlations. Medical sources (0.85) acknowledge conflicting research. No scientific consensus exists.
                </p>
              </div>
              <div className="bg-white bg-opacity-60 rounded p-3">
                <p className="font-medium mb-1">Claim: "Remote work increases productivity"</p>
                <p className="text-xs">
                  <strong>Why CONFLICTING:</strong> Credible business sources (0.75-0.80) and research organizations (0.82)
                  cite studies supporting both increased and decreased productivity, depending on industry and individual factors.
                </p>
              </div>
            </div>

            <div className="mt-3 bg-rose-50 border border-rose-200 rounded p-3 text-sm text-rose-900">
              <p className="font-semibold mb-1">❌ NOT Conflicting Evidence:</p>
              <div className="text-xs leading-relaxed space-y-1">
                <p>• High-credibility sources (0.95) refute vs. low-credibility blogs (0.50-0.60) support → <strong>REFUTED</strong></p>
                <p>• Scientific consensus (0.85) supports vs. fringe websites (0.55) refute → <strong>SUPPORTED</strong></p>
                <p>• Only low-credibility sources disagree with each other → <strong>INSUFFICIENT_INFORMATION</strong></p>
              </div>
            </div>
          </div>
        </div>
      </CollapsibleSection>

      <CollapsibleSection title="Confidence Scores Explained">
        <p className="leading-relaxed">
          Along with each verdict, MetaCheck provides a <strong>confidence score (0.0 to 1.0)</strong> indicating how
          certain the system is about its verdict. This reflects both the quality and quantity of evidence.
        </p>

        <div className="overflow-x-auto rounded-xl border border-slate-200 mt-3">
          <table className="w-full min-w-[700px] border-collapse text-left">
            <thead className="bg-slate-50 text-slate-900">
              <tr>
                <th className="border-b border-slate-200 px-4 py-3 font-semibold">Confidence Range</th>
                <th className="border-b border-slate-200 px-4 py-3 font-semibold">Interpretation</th>
                <th className="border-b border-slate-200 px-4 py-3 font-semibold">Typical Causes</th>
              </tr>
            </thead>
            <tbody className="text-sm">
              <tr className="align-top">
                <td className="border-b border-slate-100 px-4 py-3 font-medium">0.85 - 1.0<br /><span className="text-xs text-emerald-700 font-semibold">Very High</span></td>
                <td className="border-b border-slate-100 px-4 py-3">
                  Strong confidence in the verdict with robust evidence
                </td>
                <td className="border-b border-slate-100 px-4 py-3">
                  Multiple high-credibility sources (&gt; 0.8) all agree; fact-checkers or official sources confirm;
                  no contradictory credible evidence
                </td>
              </tr>
              <tr className="align-top">
                <td className="border-b border-slate-100 px-4 py-3 font-medium">0.70 - 0.84<br /><span className="text-xs text-blue-700 font-semibold">High</span></td>
                <td className="border-b border-slate-100 px-4 py-3">
                  Confident but acknowledging some limitations
                </td>
                <td className="border-b border-slate-100 px-4 py-3">
                  Several credible sources (≥ 0.7) support verdict; minor gaps or limited source diversity;
                  mostly clear evidence
                </td>
              </tr>
              <tr className="align-top">
                <td className="border-b border-slate-100 px-4 py-3 font-medium">0.50 - 0.69<br /><span className="text-xs text-amber-700 font-semibold">Moderate</span></td>
                <td className="border-b border-slate-100 px-4 py-3">
                  Reasonable verdict but with notable uncertainty
                </td>
                <td className="border-b border-slate-100 px-4 py-3">
                  Limited number of credible sources; some conflicting signals; evidence addresses claim indirectly;
                  credibility scores in mid-range
                </td>
              </tr>
              <tr className="align-top">
                <td className="px-4 py-3 font-medium">0.0 - 0.49<br /><span className="text-xs text-rose-700 font-semibold">Low</span></td>
                <td className="px-4 py-3">
                  Limited confidence; verdict is best guess with available evidence
                </td>
                <td className="px-4 py-3">
                  Very few sources; low credibility scores; vague or incomplete evidence; significant uncertainty;
                  missing key information
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mt-4">
          <p className="text-sm text-blue-900 leading-relaxed">
            <strong>💡 Learning Tip:</strong> Pay attention to confidence scores when comparing your assessment with AI results.
            Low confidence scores indicate uncertainty — these are excellent learning opportunities to discuss why evidence
            might be limited or ambiguous.
          </p>
        </div>
      </CollapsibleSection>
    </div>
  )
}

// ============================================================================
// SOURCES TAB
// ============================================================================
function SourcesTab({ categories }) {
  return (
    <div className="space-y-4">
      <CollapsibleSection title="How MetaCheck Gathers Evidence" defaultOpen={true}>
        <p className="leading-relaxed">
          MetaCheck uses <strong>three parallel evidence sources</strong> to verify claims, each providing different types of
          information. Understanding these sources and how they're weighted is crucial for interpreting results correctly.
        </p>
        <p className="leading-relaxed">
          All three sources run <strong>simultaneously</strong> (in parallel), making the fact-checking process fast while
          ensuring comprehensive coverage across different types of authoritative information.
        </p>
      </CollapsibleSection>

      <CollapsibleSection title="The Three Evidence Sources">
        <div className="space-y-4">
          <div className="bg-blue-50 border-2 border-blue-200 rounded-lg p-5">
            <h4 className="font-semibold text-blue-900 mb-3 text-base flex items-center gap-2">
              <span className="bg-blue-600 text-white text-xs px-2 py-1 rounded">SOURCE 1</span>
              Web Search (Tavily API)
            </h4>

            <p className="text-blue-900 leading-relaxed mb-3">
              Searches the open web for relevant information using <strong>Tavily</strong>, a search API optimized for
              AI applications. This provides current articles, news reports, organization websites, and other online content.
            </p>

            <div className="space-y-3">
              <div>
                <p className="font-semibold text-blue-900 text-sm mb-1.5">What it finds:</p>
                <ul className="ml-4 space-y-1 text-sm text-blue-900">
                  <li>• News articles from media organizations</li>
                  <li>• Government and organizational websites</li>
                  <li>• Academic institution pages</li>
                  <li>• Expert blogs and professional publications</li>
                  <li>• Press releases and official statements</li>
                </ul>
              </div>

              <div>
                <p className="font-semibold text-blue-900 text-sm mb-1.5">Credibility scoring:</p>
                <div className="bg-white rounded p-3 text-sm text-blue-900">
                  <p className="leading-relaxed mb-2">
                    Web sources receive <strong>variable credibility scores (0.50 - 0.85)</strong> based on domain classification.
                    MetaCheck analyzes the URL domain to determine the source type and assigns credibility accordingly.
                  </p>
                  <p className="text-xs text-blue-800">
                    See the <strong>Domain Categories</strong> section below for specific domain credibility ratings.
                  </p>
                </div>
              </div>

              <div>
                <p className="font-semibold text-blue-900 text-sm mb-1.5">Strengths:</p>
                <ul className="ml-4 space-y-1 text-sm text-blue-900">
                  <li>• Most current information (including recent events)</li>
                  <li>• Broad coverage across many topics and domains</li>
                  <li>• Access to official statements and primary sources</li>
                </ul>
              </div>

              <div>
                <p className="font-semibold text-blue-900 text-sm mb-1.5">Limitations:</p>
                <ul className="ml-4 space-y-1 text-sm text-blue-900">
                  <li>• Quality varies significantly by source</li>
                  <li>• May include biased or low-credibility content</li>
                  <li>• Cannot access paywalled content or subscription databases</li>
                </ul>
              </div>

              <div className="bg-blue-100 rounded p-3 text-sm">
                <p className="font-semibold text-blue-900 mb-1">Typical Results Per Mode:</p>
                <p className="text-blue-900 text-xs">• Basic: 3 results • Comprehensive: 5 results</p>
              </div>
            </div>
          </div>

          <div className="bg-indigo-50 border-2 border-indigo-200 rounded-lg p-5">
            <h4 className="font-semibold text-indigo-900 mb-3 text-base flex items-center gap-2">
              <span className="bg-indigo-600 text-white text-xs px-2 py-1 rounded">SOURCE 2</span>
              Wikipedia
            </h4>

            <p className="text-indigo-900 leading-relaxed mb-3">
              Searches <strong>Wikipedia articles</strong> for encyclopedic information about the claim. Wikipedia provides
              well-researched, community-verified information on an enormous range of topics.
            </p>

            <div className="space-y-3">
              <div>
                <p className="font-semibold text-indigo-900 text-sm mb-1.5">What it provides:</p>
                <ul className="ml-4 space-y-1 text-sm text-indigo-900">
                  <li>• Established facts and historical information</li>
                  <li>• Scientific and technical explanations</li>
                  <li>• Biographical and geographical data</li>
                  <li>• Context and background for claims</li>
                  <li>• Cited references to additional sources</li>
                </ul>
              </div>

              <div>
                <p className="font-semibold text-indigo-900 text-sm mb-1.5">Credibility scoring:</p>
                <div className="bg-white rounded p-3 text-sm text-indigo-900">
                  <p className="leading-relaxed mb-2">
                    Wikipedia receives a <strong>fixed credibility score of 0.80</strong> (high credibility tier). While not
                    perfect, Wikipedia's editorial process, citation requirements, and community oversight make it a reliable
                    source for established factual information.
                  </p>
                  <p className="text-xs text-indigo-800 leading-relaxed">
                    <strong>Why 0.80?</strong> Wikipedia is generally accurate for established facts but can have quality
                    variations, lacks expertise verification, and may have recency issues. It's very credible but not
                    primary-source level.
                  </p>
                </div>
              </div>

              <div>
                <p className="font-semibold text-indigo-900 text-sm mb-1.5">Strengths:</p>
                <ul className="ml-4 space-y-1 text-sm text-indigo-900">
                  <li>• Extensive coverage of mainstream topics</li>
                  <li>• Community-verified and regularly updated</li>
                  <li>• Neutral point of view policy</li>
                  <li>• Citations to primary and secondary sources</li>
                </ul>
              </div>

              <div>
                <p className="font-semibold text-indigo-900 text-sm mb-1.5">Limitations:</p>
                <ul className="ml-4 space-y-1 text-sm text-indigo-900">
                  <li>• May lack coverage of very recent events</li>
                  <li>• Controversial topics can have edit wars or bias</li>
                  <li>• Niche or obscure topics may have limited information</li>
                  <li>• Not suitable for breaking news or emerging issues</li>
                </ul>
              </div>

              <div className="bg-indigo-100 rounded p-3 text-sm">
                <p className="font-semibold text-indigo-900 mb-1">Typical Results Per Mode:</p>
                <p className="text-indigo-900 text-xs">• Basic: 2 results • Comprehensive: 3 results</p>
              </div>
            </div>
          </div>

          <div className="bg-purple-50 border-2 border-purple-200 rounded-lg p-5">
            <h4 className="font-semibold text-purple-900 mb-3 text-base flex items-center gap-2">
              <span className="bg-purple-600 text-white text-xs px-2 py-1 rounded">SOURCE 3</span>
              Google Fact Check API
            </h4>

            <p className="text-purple-900 leading-relaxed mb-3">
              Queries the <strong>Google Fact Check Tools API</strong>, which aggregates fact-checks from professional
              fact-checking organizations worldwide (PolitiFact, Snopes, FactCheck.org, AFP, Reuters, and 100+ others).
            </p>

            <div className="space-y-3">
              <div>
                <p className="font-semibold text-purple-900 text-sm mb-1.5">What it provides:</p>
                <ul className="ml-4 space-y-1 text-sm text-purple-900">
                  <li>• Professional fact-checker verdicts and ratings</li>
                  <li>• Detailed explanations from verified organizations</li>
                  <li>• Claims that have already been fact-checked</li>
                  <li>• Ratings like "True", "False", "Mostly True", "Misleading"</li>
                </ul>
              </div>

              <div>
                <p className="font-semibold text-purple-900 text-sm mb-1.5">Credibility scoring:</p>
                <div className="bg-white rounded p-3 text-sm text-purple-900">
                  <p className="leading-relaxed mb-2">
                    Professional fact-checkers receive the <strong>highest credibility score of 0.95</strong>. These
                    organizations follow rigorous methodologies, cite sources, correct errors, and adhere to international
                    fact-checking standards (IFCN Code of Principles).
                  </p>
                  <p className="text-xs text-purple-800 leading-relaxed">
                    <strong>Why 0.95?</strong> Professional fact-checkers are the gold standard for verification. They have
                    expertise, editorial oversight, transparency, and accountability. Score isn't 1.0 because even experts can
                    occasionally make mistakes or have methodological limitations.
                  </p>
                </div>
              </div>

              <div>
                <p className="font-semibold text-purple-900 text-sm mb-1.5">Strengths:</p>
                <ul className="ml-4 space-y-1 text-sm text-purple-900">
                  <li>• Highest credibility and trustworthiness</li>
                  <li>• Expert analysis with detailed reasoning</li>
                  <li>• Covers viral misinformation and political claims</li>
                  <li>• Provides explicit ratings (True, False, etc.)</li>
                </ul>
              </div>

              <div>
                <p className="font-semibold text-purple-900 text-sm mb-1.5">Limitations:</p>
                <ul className="ml-4 space-y-1 text-sm text-purple-900">
                  <li>• Limited coverage (only previously fact-checked claims)</li>
                  <li>• Focus on viral/political claims, not all topics</li>
                  <li>• May not have entries for niche or new claims</li>
                  <li>• Dependent on fact-checkers selecting claims</li>
                </ul>
              </div>

              <div className="bg-purple-100 rounded p-3 text-sm">
                <p className="font-semibold text-purple-900 mb-1">Typical Results Per Mode:</p>
                <p className="text-purple-900 text-xs">• Basic: 2 results • Comprehensive: 3 results</p>
                <p className="text-purple-800 text-xs mt-1">Note: Many claims return zero results (not previously fact-checked)</p>
              </div>
            </div>
          </div>
        </div>
      </CollapsibleSection>

      <CollapsibleSection title="How Sources Are Weighted in Verdicts">
        <p className="leading-relaxed">
          MetaCheck doesn't simply count sources or take a majority vote. Instead, it uses <strong>credibility-weighted
          evidence synthesis</strong>, similar to how professional fact-checkers work.
        </p>

        <div className="bg-slate-50 border border-slate-200 rounded-lg p-4 space-y-3">
          <div>
            <p className="font-semibold text-slate-900 mb-2">The Weighting Process:</p>
            <ol className="ml-4 space-y-2 text-sm">
              <li className="leading-relaxed">
                <strong>1. Evidence Collection:</strong> All three sources search simultaneously and return results with snippets
              </li>
              <li className="leading-relaxed">
                <strong>2. Credibility Assignment:</strong> Each piece of evidence gets a credibility score (0.50-0.95)
                based on source type and domain
              </li>
              <li className="leading-relaxed">
                <strong>3. Stance Determination:</strong> AI analyzes each snippet to determine if it supports, refutes,
                or is neutral toward the claim
              </li>
              <li className="leading-relaxed">
                <strong>4. Weight Calculation:</strong> Credibility scores are summed for supporting vs. refuting evidence
              </li>
              <li className="leading-relaxed">
                <strong>5. Verdict Decision:</strong> The verdict is based on which side has higher credibility weight and
                whether thresholds are met (e.g., sufficient credible sources ≥ 0.7)
              </li>
            </ol>
          </div>

          <div className="bg-white rounded p-3">
            <p className="font-semibold text-slate-900 text-sm mb-2">Example Calculation:</p>
            <div className="text-xs space-y-1 text-slate-700">
              <p><strong>Claim:</strong> "Climate change is caused by human activity"</p>
              <p className="mt-2"><strong>Supporting Evidence:</strong></p>
              <ul className="ml-4">
                <li>• Fact-checker (0.95): "True - scientific consensus"</li>
                <li>• Wikipedia (0.80): Confirms with citations</li>
                <li>• Government site .gov (0.85): Official climate data</li>
                <li>• News article (0.75): Reports scientific findings</li>
              </ul>
              <p className="mt-1 font-medium">Total supporting weight: 3.35</p>

              <p className="mt-2"><strong>Refuting Evidence:</strong></p>
              <ul className="ml-4">
                <li>• Blog post (0.55): Claims it's natural cycles</li>
              </ul>
              <p className="mt-1 font-medium">Total refuting weight: 0.55</p>

              <p className="mt-2 text-emerald-700 font-semibold">
                Verdict: SUPPORTED (3.35 vs 0.55 = clear high-credibility consensus, confidence: 0.92)
              </p>
            </div>
          </div>
        </div>

        <div className="overflow-x-auto rounded-xl border border-slate-200 mt-4">
          <table className="w-full min-w-[700px] border-collapse text-left text-sm">
            <thead className="bg-slate-50">
              <tr>
                <th className="border-b border-slate-200 px-4 py-3 font-semibold">Credibility Tier</th>
                <th className="border-b border-slate-200 px-4 py-3 font-semibold">Score Range</th>
                <th className="border-b border-slate-200 px-4 py-3 font-semibold">Decision Influence</th>
                <th className="border-b border-slate-200 px-4 py-3 font-semibold">Example Sources</th>
              </tr>
            </thead>
            <tbody>
              <tr className="align-top">
                <td className="border-b border-slate-100 px-4 py-3 font-medium text-purple-700">
                  High Credibility
                </td>
                <td className="border-b border-slate-100 px-4 py-3">&gt; 0.80</td>
                <td className="border-b border-slate-100 px-4 py-3">
                  <strong>Strongest weight</strong> — Can outweigh multiple lower-tier sources
                </td>
                <td className="border-b border-slate-100 px-4 py-3">
                  Fact-checkers (0.95), Government sites (0.85-0.90), Major news (0.82-0.85), Wikipedia (0.80)
                </td>
              </tr>
              <tr className="align-top">
                <td className="border-b border-slate-100 px-4 py-3 font-medium text-blue-700">
                  Credible
                </td>
                <td className="border-b border-slate-100 px-4 py-3">0.70 - 0.80</td>
                <td className="border-b border-slate-100 px-4 py-3">
                  <strong>Primary threshold</strong> — Used to determine SUPPORTED/REFUTED/CONFLICTING
                </td>
                <td className="border-b border-slate-100 px-4 py-3">
                  Academic sites (0.75), Reputable news (0.72-0.78), Professional organizations (0.70-0.75)
                </td>
              </tr>
              <tr className="align-top">
                <td className="px-4 py-3 font-medium text-amber-700">
                  Low Credibility
                </td>
                <td className="px-4 py-3">&lt; 0.70</td>
                <td className="px-4 py-3">
                  <strong>Supporting context only</strong> — Not used to determine primary verdict
                </td>
                <td className="px-4 py-3">
                  General web (0.60), Blogs (0.55-0.60), Forums (0.50), User content (0.50)
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </CollapsibleSection>

      <CollapsibleSection title="Domain Categories and Credibility">
        <p className="leading-relaxed">
          Web search results are automatically classified based on their domain. MetaCheck uses a comprehensive taxonomy
          that examines the URL structure (domain, TLD, subdomains) to determine the source type and assign appropriate
          credibility scores.
        </p>

        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <p className="text-sm text-blue-900 leading-relaxed">
            <strong>💡 Why domain-based scoring?</strong> While not perfect, domain analysis provides a fast, transparent,
            and consistent way to assess source credibility. A .gov site is generally more reliable than a random blog,
            a .edu site is usually authoritative for its field, and fact-checking organizations have proven track records.
            This method is used as a practical heuristic in the absence of deep content analysis.
          </p>
        </div>

        <div className="space-y-4 mt-6">
          <h4 className="font-semibold text-slate-900 text-base">Understanding Domain Categories</h4>
          <p className="text-sm leading-relaxed text-slate-700">
            MetaCheck automatically analyzes the URL of each web search result and assigns it to one of several domain
            categories. Each category has a specific credibility score range based on the typical reliability of sources
            in that category. Here's what each category means:
          </p>

          <div className="space-y-3">
            <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-4">
              <h5 className="font-semibold text-emerald-900 mb-2 text-sm">🏛️ Government & Official Sources</h5>
              <p className="text-sm text-emerald-900 leading-relaxed mb-2">
                <strong>Credibility Range:</strong> 0.85 - 0.90 (Very High)
              </p>
              <p className="text-sm text-emerald-900 leading-relaxed mb-2">
                Official government websites, regulatory agencies, and intergovernmental organizations. These sources
                provide authoritative data, official statements, and verified information from public institutions.
              </p>
              <div className="bg-white rounded p-3 text-xs text-emerald-800">
                <p className="font-semibold mb-1">Examples:</p>
                <ul className="ml-4 space-y-0.5">
                  <li>• <strong>cdc.gov</strong> - Centers for Disease Control and Prevention</li>
                  <li>• <strong>nasa.gov</strong> - National Aeronautics and Space Administration</li>
                  <li>• <strong>who.int</strong> - World Health Organization</li>
                  <li>• <strong>europa.eu</strong> - European Union official sites</li>
                  <li>• <strong>whitehouse.gov</strong> - Official White House communications</li>
                  <li>• <strong>fda.gov</strong> - Food and Drug Administration</li>
                </ul>
              </div>
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h5 className="font-semibold text-blue-900 mb-2 text-sm">🎓 Academic & Research Institutions</h5>
              <p className="text-sm text-blue-900 leading-relaxed mb-2">
                <strong>Credibility Range:</strong> 0.75 - 0.82 (High)
              </p>
              <p className="text-sm text-blue-900 leading-relaxed mb-2">
                Universities, research centers, academic journals, and scholarly institutions. These sources provide
                peer-reviewed research, expert analysis, and evidence-based information.
              </p>
              <div className="bg-white rounded p-3 text-xs text-blue-800">
                <p className="font-semibold mb-1">Examples:</p>
                <ul className="ml-4 space-y-0.5">
                  <li>• <strong>harvard.edu</strong> - Harvard University</li>
                  <li>• <strong>stanford.edu</strong> - Stanford University</li>
                  <li>• <strong>ox.ac.uk</strong> - University of Oxford</li>
                  <li>• <strong>nature.com</strong> - Nature journal (peer-reviewed)</li>
                  <li>• <strong>sciencemag.org</strong> - Science journal</li>
                  <li>• <strong>nih.gov</strong> - National Institutes of Health (research arm)</li>
                </ul>
              </div>
            </div>

            <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
              <h5 className="font-semibold text-purple-900 mb-2 text-sm">✓ Fact-Checking Organizations</h5>
              <p className="text-sm text-purple-900 leading-relaxed mb-2">
                <strong>Credibility Range:</strong> 0.95 (Highest)
              </p>
              <p className="text-sm text-purple-900 leading-relaxed mb-2">
                Professional fact-checking organizations that follow IFCN (International Fact-Checking Network) standards.
                These are the most credible sources for claim verification, using rigorous methodologies and citing sources.
              </p>
              <div className="bg-white rounded p-3 text-xs text-purple-800">
                <p className="font-semibold mb-1">Examples:</p>
                <ul className="ml-4 space-y-0.5">
                  <li>• <strong>politifact.com</strong> - PolitiFact (Pulitzer Prize winner)</li>
                  <li>• <strong>snopes.com</strong> - Snopes</li>
                  <li>• <strong>factcheck.org</strong> - FactCheck.org</li>
                  <li>• <strong>fullfact.org</strong> - Full Fact (UK)</li>
                  <li>• <strong>apnews.com/APFactCheck</strong> - Associated Press Fact Check</li>
                  <li>• <strong>reuters.com/fact-check</strong> - Reuters Fact Check</li>
                </ul>
              </div>
            </div>

            <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-4">
              <h5 className="font-semibold text-indigo-900 mb-2 text-sm">📰 News & Media Organizations</h5>
              <p className="text-sm text-indigo-900 leading-relaxed mb-2">
                <strong>Credibility Range:</strong> 0.72 - 0.85 (Varies by reputation)
              </p>
              <p className="text-sm text-indigo-900 leading-relaxed mb-2">
                Established news organizations with editorial standards, journalists, and fact-checking processes. Credibility
                varies based on the outlet's reputation, editorial independence, and track record.
              </p>
              <div className="bg-white rounded p-3 text-xs text-indigo-800">
                <p className="font-semibold mb-1">Examples (Higher credibility 0.82-0.85):</p>
                <ul className="ml-4 space-y-0.5 mb-2">
                  <li>• <strong>apnews.com</strong> - Associated Press</li>
                  <li>• <strong>reuters.com</strong> - Reuters</li>
                  <li>• <strong>bbc.com</strong> - BBC News</li>
                  <li>• <strong>npr.org</strong> - NPR (National Public Radio)</li>
                  <li>• <strong>theguardian.com</strong> - The Guardian</li>
                </ul>
                <p className="font-semibold mb-1">Examples (Standard credibility 0.72-0.78):</p>
                <ul className="ml-4 space-y-0.5">
                  <li>• <strong>nytimes.com</strong> - New York Times</li>
                  <li>• <strong>washingtonpost.com</strong> - Washington Post</li>
                  <li>• <strong>cnn.com</strong> - CNN</li>
                  <li>• <strong>wsj.com</strong> - Wall Street Journal</li>
                </ul>
              </div>
            </div>

            <div className="bg-cyan-50 border border-cyan-200 rounded-lg p-4">
              <h5 className="font-semibold text-cyan-900 mb-2 text-sm">🏢 Professional & Non-Profit Organizations</h5>
              <p className="text-sm text-cyan-900 leading-relaxed mb-2">
                <strong>Credibility Range:</strong> 0.70 - 0.78 (Credible)
              </p>
              <p className="text-sm text-cyan-900 leading-relaxed mb-2">
                Established organizations, professional associations, and reputable non-profits that publish information
                in their domain of expertise. Generally trustworthy but may have specific organizational perspectives.
              </p>
              <div className="bg-white rounded p-3 text-xs text-cyan-800">
                <p className="font-semibold mb-1">Examples:</p>
                <ul className="ml-4 space-y-0.5">
                  <li>• <strong>redcross.org</strong> - American Red Cross</li>
                  <li>• <strong>mayo.edu</strong> - Mayo Clinic</li>
                  <li>• <strong>ama-assn.org</strong> - American Medical Association</li>
                  <li>• <strong>aclu.org</strong> - American Civil Liberties Union</li>
                  <li>• <strong>amnesty.org</strong> - Amnesty International</li>
                </ul>
              </div>
            </div>

            <div className="bg-teal-50 border border-teal-200 rounded-lg p-4">
              <h5 className="font-semibold text-teal-900 mb-2 text-sm">📚 Reference & Information Sites</h5>
              <p className="text-sm text-teal-900 leading-relaxed mb-2">
                <strong>Credibility Range:</strong> 0.65 - 0.75 (Moderate to Credible)
              </p>
              <p className="text-sm text-teal-900 leading-relaxed mb-2">
                Encyclopedias, dictionaries, and general reference sites. Useful for background information but may lack
                depth or specialist expertise. Wikipedia is scored separately at 0.80 due to its extensive citation system.
              </p>
              <div className="bg-white rounded p-3 text-xs text-teal-800">
                <p className="font-semibold mb-1">Examples:</p>
                <ul className="ml-4 space-y-0.5">
                  <li>• <strong>britannica.com</strong> - Encyclopaedia Britannica</li>
                  <li>• <strong>dictionary.com</strong> - Dictionary.com</li>
                  <li>• <strong>merriam-webster.com</strong> - Merriam-Webster</li>
                  <li>• <strong>howstuffworks.com</strong> - HowStuffWorks</li>
                </ul>
              </div>
            </div>

            <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
              <h5 className="font-semibold text-amber-900 mb-2 text-sm">🌐 General Web Content</h5>
              <p className="text-sm text-amber-900 leading-relaxed mb-2">
                <strong>Credibility Range:</strong> 0.55 - 0.65 (Moderate to Low)
              </p>
              <p className="text-sm text-amber-900 leading-relaxed mb-2">
                Commercial websites, general content sites, and online publications that don't fit into higher categories.
                These may contain accurate information but lack institutional credibility or editorial oversight.
              </p>
              <div className="bg-white rounded p-3 text-xs text-amber-800">
                <p className="font-semibold mb-1">Examples:</p>
                <ul className="ml-4 space-y-0.5">
                  <li>• <strong>healthline.com</strong> - Health information portal</li>
                  <li>• <strong>webmd.com</strong> - Medical information site</li>
                  <li>• <strong>investopedia.com</strong> - Financial education site</li>
                  <li>• <strong>medium.com</strong> - User-generated content platform</li>
                </ul>
              </div>
            </div>

            <div className="bg-rose-50 border border-rose-200 rounded-lg p-4">
              <h5 className="font-semibold text-rose-900 mb-2 text-sm">💬 Blogs, Forums & User-Generated Content</h5>
              <p className="text-sm text-rose-900 leading-relaxed mb-2">
                <strong>Credibility Range:</strong> 0.50 - 0.58 (Low)
              </p>
              <p className="text-sm text-rose-900 leading-relaxed mb-2">
                Personal blogs, forums, social media content, and user-generated platforms. While these may contain
                valuable insights, they typically lack editorial oversight, fact-checking, or institutional accountability.
              </p>
              <div className="bg-white rounded p-3 text-xs text-rose-800">
                <p className="font-semibold mb-1">Examples:</p>
                <ul className="ml-4 space-y-0.5">
                  <li>• <strong>reddit.com</strong> - User discussion forums</li>
                  <li>• <strong>quora.com</strong> - User Q&A platform</li>
                  <li>• <strong>wordpress.com</strong> - Personal blogs</li>
                  <li>• <strong>blogspot.com</strong> - Personal blogs</li>
                  <li>• Individual author blogs and opinion sites</li>
                </ul>
              </div>
            </div>
          </div>

          <div className="bg-slate-100 border border-slate-300 rounded-lg p-4 mt-4">
            <p className="text-sm text-slate-900 leading-relaxed">
              <strong>⚠️ Important Notes:</strong>
            </p>
            <ul className="ml-4 space-y-1 text-sm text-slate-800 mt-2">
              <li>• These scores are <strong>starting points</strong> based on domain type, not absolute judgments</li>
              <li>• Content quality varies within categories — a .gov page with outdated info is less reliable than a current expert blog</li>
              <li>• Context matters: a university website is highly credible for research, less so for current news events</li>
              <li>• Domain scoring is a <strong>heuristic</strong> (practical shortcut), not a replacement for reading and evaluating content</li>
              <li>• MetaCheck uses these scores as weights in evidence synthesis, not as final verdicts</li>
            </ul>
          </div>
        </div>

        <div className="mt-6">
          <h4 className="font-semibold text-slate-900 text-base mb-3">Domain Categories Reference Table</h4>
          <p className="text-sm text-slate-600 mb-3">
            Below is a complete reference showing all domain categories configured in MetaCheck, their credibility scores,
            and brief descriptions. This table is dynamically loaded from the backend configuration.
          </p>
          <DomainLegend categories={categories} />
        </div>
      </CollapsibleSection>

      <CollapsibleSection title="Search Status Indicators">
        <p className="leading-relaxed">
          Each source provides a status indicator showing whether the search succeeded, failed, or found no results.
          Understanding these statuses helps you interpret the completeness of evidence.
        </p>

        <div className="overflow-x-auto rounded-xl border border-slate-200 mt-3">
          <table className="w-full min-w-[700px] border-collapse text-left">
            <thead className="bg-slate-50 text-slate-900">
              <tr>
                <th className="border-b border-slate-200 px-4 py-3 font-semibold">Status</th>
                <th className="border-b border-slate-200 px-4 py-3 font-semibold">What It Means</th>
                <th className="border-b border-slate-200 px-4 py-3 font-semibold">Impact on Results</th>
                <th className="border-b border-slate-200 px-4 py-3 font-semibold">Action Needed</th>
              </tr>
            </thead>
            <tbody className="text-sm">
              <tr className="align-top bg-emerald-50">
                <td className="border-b border-slate-100 px-4 py-3 font-medium text-emerald-700">success</td>
                <td className="border-b border-slate-100 px-4 py-3">
                  Search ran successfully and returned evidence
                </td>
                <td className="border-b border-slate-100 px-4 py-3">
                  Source contributed to the verdict with its evidence
                </td>
                <td className="border-b border-slate-100 px-4 py-3">
                  None — working as expected
                </td>
              </tr>
              <tr className="align-top bg-slate-50">
                <td className="border-b border-slate-100 px-4 py-3 font-medium text-slate-700">no_results</td>
                <td className="border-b border-slate-100 px-4 py-3">
                  Search ran but found no matching evidence for this claim
                </td>
                <td className="border-b border-slate-100 px-4 py-3">
                  This is an absence of evidence, not a system error. The source simply didn't have relevant information.
                </td>
                <td className="border-b border-slate-100 px-4 py-3">
                  None — this is normal for many claims (especially with Fact Check API)
                </td>
              </tr>
              <tr className="align-top bg-rose-50">
                <td className="border-b border-slate-100 px-4 py-3 font-medium text-rose-700">error</td>
                <td className="border-b border-slate-100 px-4 py-3">
                  Search failed due to API error, network issue, or provider problem
                </td>
                <td className="border-b border-slate-100 px-4 py-3">
                  Evidence may be incomplete. Verdict is based only on sources that succeeded.
                </td>
                <td className="border-b border-slate-100 px-4 py-3">
                  Try again later or check system status. Report persistent errors.
                </td>
              </tr>
              <tr className="align-top bg-amber-50">
                <td className="px-4 py-3 font-medium text-amber-700">no_api_key</td>
                <td className="px-4 py-3">
                  API key for this source was not configured in the system
                </td>
                <td className="px-4 py-3">
                  That source type was disabled for this run. Verdict is based on remaining sources.
                </td>
                <td className="px-4 py-3">
                  System administrator needs to configure the API key (not a user issue)
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </CollapsibleSection>
    </div>
  )
}

// ============================================================================
// WORKFLOW TAB
// ============================================================================
function WorkflowTab() {
  return (
    <div className="space-y-4">
      <CollapsibleSection title="How MetaCheck Works Behind the Scenes" defaultOpen={true}>
        <p className="leading-relaxed">
          Understanding the technical workflow helps you interpret results and troubleshoot issues. MetaCheck uses an
          <strong> agentic AI architecture</strong> with specialized components working together.
        </p>
      </CollapsibleSection>

      <CollapsibleSection title="The Verification Pipeline">

        <div className="space-y-3">
          <div className="bg-slate-50 border-l-4 border-blue-500 p-4">
            <h5 className="font-semibold text-slate-900 mb-2">Phase 1: Claim Extraction</h5>
            <div className="text-sm space-y-2">
              <p className="leading-relaxed">
                <strong>Component:</strong> Claim Extractor Agent
              </p>
              <p className="leading-relaxed">
                <strong>What happens:</strong> The AI analyzes your input text and identifies statements that are:
              </p>
              <ul className="ml-4 space-y-1">
                <li>• Specific and concrete (not vague)</li>
                <li>• Falsifiable (can be proven true or false)</li>
                <li>• Require external verification (not common knowledge)</li>
                <li>• Contain verifiable details (numbers, dates, names, locations)</li>
              </ul>
              <p className="leading-relaxed">
                <strong>Output:</strong> A list of candidate claims extracted from your text
              </p>
            </div>
          </div>

          <div className="bg-slate-50 border-l-4 border-indigo-500 p-4">
            <h5 className="font-semibold text-slate-900 mb-2">Phase 2: Claim Selection</h5>
            <div className="text-sm space-y-2">
              <p className="leading-relaxed">
                <strong>Component:</strong> User Interface (Manual Selection)
              </p>
              <p className="leading-relaxed">
                <strong>What happens:</strong> You review the extracted claims and select which ones you want to verify
                (up to 5). This gives you control over what gets fact-checked and helps manage processing time and cost.
              </p>
              <p className="leading-relaxed">
                <strong>Why limit to 5?</strong> Thorough fact-checking is computationally expensive. Each claim requires
                multiple API calls, AI reasoning, and evidence synthesis. The 5-claim limit ensures timely results.
              </p>
            </div>
          </div>

          <div className="bg-slate-50 border-l-4 border-purple-500 p-4">
            <h5 className="font-semibold text-slate-900 mb-2">Phase 3: Parallel Evidence Gathering</h5>
            <div className="text-sm space-y-2">
              <p className="leading-relaxed">
                <strong>Component:</strong> Orchestrator Agent with comprehensive_evidence_tool
              </p>
              <p className="leading-relaxed">
                <strong>What happens:</strong> For each selected claim, the system simultaneously searches three sources:
              </p>
              <ol className="ml-4 space-y-1">
                <li>1. <strong>Tavily Web Search:</strong> Finds relevant web pages and snippets</li>
                <li>2. <strong>Wikipedia:</strong> Searches encyclopedic articles</li>
                <li>3. <strong>Google Fact Check API:</strong> Queries professional fact-checking databases</li>
              </ol>
              <p className="leading-relaxed">
                All three searches run <strong>in parallel</strong> (simultaneously), taking only ~5-10 seconds total
                instead of 15-30 seconds if they ran sequentially.
              </p>
              <p className="leading-relaxed">
                <strong>Output:</strong> Combined evidence bundle with snippets, URLs, source types, and preliminary scores
              </p>
            </div>
          </div>

          <div className="bg-slate-50 border-l-4 border-emerald-500 p-4">
            <h5 className="font-semibold text-slate-900 mb-2">Phase 4: Credibility Classification</h5>
            <div className="text-sm space-y-2">
              <p className="leading-relaxed">
                <strong>Component:</strong> Domain Classification (config-based lookup)
              </p>
              <p className="leading-relaxed">
                <strong>What happens:</strong> Each web search result is analyzed to determine its credibility:
              </p>
              <ul className="ml-4 space-y-1">
                <li>• Domain is extracted from the URL</li>
                <li>• Domain is matched against a taxonomy (government, academic, news, etc.)</li>
                <li>• Credibility score is assigned based on category (0.50-0.90)</li>
              </ul>
              <p className="leading-relaxed">
                <strong>Note:</strong> Wikipedia (0.80) and Fact Check (0.95) have fixed scores. Only web search results
                use dynamic domain classification.
              </p>
            </div>
          </div>

          <div className="bg-slate-50 border-l-4 border-amber-500 p-4">
            <h5 className="font-semibold text-slate-900 mb-2">Phase 5: Stance Analysis</h5>
            <div className="text-sm space-y-2">
              <p className="leading-relaxed">
                <strong>Component:</strong> Orchestrator Agent (AI Analysis)
              </p>
              <p className="leading-relaxed">
                <strong>What happens:</strong> The AI reads each evidence snippet and determines its stance:
              </p>
              <ul className="ml-4 space-y-1">
                <li>• <strong>Supports:</strong> Evidence confirms or aligns with the claim</li>
                <li>• <strong>Refutes:</strong> Evidence contradicts or disproves the claim</li>
                <li>• <strong>Neutral:</strong> Evidence is related but doesn't clearly support or refute</li>
                <li>• <strong>Unclear:</strong> Evidence is ambiguous or indirect</li>
              </ul>
              <p className="leading-relaxed">
                For Fact Check sources, the stance is automatically interpreted from ratings (e.g., "False" → refutes,
                "True" → supports). For web and Wikipedia, the AI analyzes the snippet text.
              </p>
            </div>
          </div>

          <div className="bg-slate-50 border-l-4 border-rose-500 p-4">
            <h5 className="font-semibold text-slate-900 mb-2">Phase 6: Verdict Synthesis</h5>
            <div className="text-sm space-y-2">
              <p className="leading-relaxed">
                <strong>Component:</strong> Orchestrator Agent (Decision Logic)
              </p>
              <p className="leading-relaxed">
                <strong>What happens:</strong> The AI synthesizes all evidence and reaches a verdict:
              </p>
              <ol className="ml-4 space-y-1.5">
                <li>1. Calculate total credibility weight for supporting evidence (sum of credibility scores)</li>
                <li>2. Calculate total credibility weight for refuting evidence</li>
                <li>3. Apply verdict criteria based on weights and thresholds</li>
                <li>4. Determine confidence score based on evidence quality and quantity</li>
                <li>5. Generate justification explaining the verdict</li>
                <li>6. (Comprehensive mode only) Document metacognitive detail with full reasoning transparency</li>
              </ol>
              <p className="leading-relaxed">
                <strong>Output:</strong> VerificationResult with verdict, confidence, justification, sources, and evidence list
              </p>
            </div>
          </div>
        </div>
      </CollapsibleSection>

      <CollapsibleSection title="Mode Differences Explained">
        <div className="overflow-x-auto rounded-xl border border-slate-200">
          <table className="w-full min-w-[800px] border-collapse text-left">
            <thead className="bg-slate-50 text-slate-900">
              <tr>
                <th className="border-b border-slate-200 px-4 py-3 font-semibold">Aspect</th>
                <th className="border-b border-slate-200 px-4 py-3 font-semibold">Basic Mode</th>
                <th className="border-b border-slate-200 px-4 py-3 font-semibold">Comprehensive Mode</th>
              </tr>
            </thead>
            <tbody className="text-sm">
              <tr className="align-top">
                <td className="border-b border-slate-100 px-4 py-3 font-medium">Primary Use Case</td>
                <td className="border-b border-slate-100 px-4 py-3">
                  Quick fact-checking, classroom demos, fast results
                </td>
                <td className="border-b border-slate-100 px-4 py-3">
                  Deep learning, understanding reasoning, educational transparency
                </td>
              </tr>
              <tr className="align-top">
                <td className="border-b border-slate-100 px-4 py-3 font-medium">Evidence Retrieved</td>
                <td className="border-b border-slate-100 px-4 py-3">
                  Limited (3 web, 2 wiki, 2 fact-check)
                </td>
                <td className="border-b border-slate-100 px-4 py-3">
                  More comprehensive (5 web, 3 wiki, 3 fact-check)
                </td>
              </tr>
              <tr className="align-top">
                <td className="border-b border-slate-100 px-4 py-3 font-medium">Justification</td>
                <td className="border-b border-slate-100 px-4 py-3">
                  1-2 concise sentences explaining verdict
                </td>
                <td className="border-b border-slate-100 px-4 py-3">
                  Detailed paragraph with reasoning and evidence summary
                </td>
              </tr>
              <tr className="align-top">
                <td className="border-b border-slate-100 px-4 py-3 font-medium">Metacognitive Detail</td>
                <td className="border-b border-slate-100 px-4 py-3">
                  Not included (empty)
                </td>
                <td className="border-b border-slate-100 px-4 py-3">
                  Full transparency: search queries, source assessments, verdict reasoning, AI uncertainties, assumptions
                </td>
              </tr>
              <tr className="align-top">
                <td className="border-b border-slate-100 px-4 py-3 font-medium">Processing Time</td>
                <td className="border-b border-slate-100 px-4 py-3">
                  Faster (~10-20 seconds per claim)
                </td>
                <td className="border-b border-slate-100 px-4 py-3">
                  Slower (~15-30 seconds per claim)
                </td>
              </tr>
              <tr className="align-top">
                <td className="border-b border-slate-100 px-4 py-3 font-medium">Max Claims</td>
                <td className="border-b border-slate-100 px-4 py-3">
                  5 claims
                </td>
                <td className="border-b border-slate-100 px-4 py-3">
                  5 claims
                </td>
              </tr>
              <tr className="align-top">
                <td className="px-4 py-3 font-medium">Best For</td>
                <td className="px-4 py-3">
                  Students need quick answers; teachers showing tool in class; practicing verdict assignment
                </td>
                <td className="px-4 py-3">
                  Students learning <em>how</em> fact-checking works; analyzing AI reasoning; comparing thought processes
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </CollapsibleSection>

      <CollapsibleSection title="Parallel vs. Sequential Processing">
        <p className="leading-relaxed">
          MetaCheck uses <strong>parallel processing</strong> at two levels to minimize wait time:
        </p>

        <div className="grid md:grid-cols-2 gap-4">
          <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-4">
            <h5 className="font-semibold text-emerald-900 mb-2">Parallel Source Gathering</h5>
            <p className="text-sm text-emerald-900 leading-relaxed mb-2">
              All three evidence sources (Tavily, Wikipedia, Fact Check) search <strong>simultaneously</strong> for each claim.
            </p>
            <div className="text-xs text-emerald-800 bg-white rounded p-2">
              <p className="font-medium mb-1">Time Savings:</p>
              <p>Sequential: 5s + 5s + 5s = 15 seconds</p>
              <p>Parallel: max(5s, 5s, 5s) = 5 seconds</p>
              <p className="mt-1 font-semibold">Result: 3x faster ✓</p>
            </div>
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h5 className="font-semibold text-blue-900 mb-2">Parallel Claim Verification</h5>
            <p className="text-sm text-blue-900 leading-relaxed mb-2">
              Multiple claims are verified <strong>concurrently</strong> (up to 5 at once).
            </p>
            <div className="text-xs text-blue-800 bg-white rounded p-2">
              <p className="font-medium mb-1">Time Savings:</p>
              <p>Sequential: 15s × 5 claims = 75 seconds</p>
              <p>Parallel: max(15s, 15s, 15s, 15s, 15s) = 15 seconds</p>
              <p className="mt-1 font-semibold">Result: 5x faster ✓</p>
            </div>
          </div>
        </div>

        <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-4 mt-4">
          <p className="text-sm text-indigo-900 leading-relaxed">
            <strong>Combined Effect:</strong> Verifying 5 claims with parallel processing takes ~15-20 seconds total.
            Without parallelization, it would take ~75 seconds (5 claims × 15 seconds each). This makes MetaCheck practical
            for classroom use and interactive learning.
          </p>
        </div>
      </CollapsibleSection>

      <CollapsibleSection title="Technical Architecture">
        <div className="bg-slate-50 border border-slate-200 rounded-lg p-4">
          <div className="grid md:grid-cols-2 gap-6 text-sm">
            <div>
              <h5 className="font-semibold text-slate-900 mb-2">Frontend (React)</h5>
              <ul className="space-y-1 text-slate-700">
                <li>• Modern React with hooks and motion animations</li>
                <li>• Four-tab interface (Your Assessment, AI Analysis, Compare, Documentation)</li>
                <li>• Real-time updates during verification</li>
                <li>• Responsive design for mobile and desktop</li>
              </ul>
            </div>

            <div>
              <h5 className="font-semibold text-slate-900 mb-2">Backend (Python/FastAPI)</h5>
              <ul className="space-y-1 text-slate-700">
                <li>• FastAPI web framework for high performance</li>
                <li>• OpenAI Agents SDK for agentic AI workflows</li>
                <li>• Async/await for parallel processing</li>
                <li>• Pydantic models for type safety</li>
              </ul>
            </div>

            <div>
              <h5 className="font-semibold text-slate-900 mb-2">AI Components</h5>
              <ul className="space-y-1 text-slate-700">
                <li>• Claim Extractor Agent (identifies verifiable claims)</li>
                <li>• Orchestrator Agent (coordinates verification)</li>
                <li>• Domain Classifier (assesses source credibility)</li>
                <li>• Evidence Synthesizer (combines and weighs evidence)</li>
              </ul>
            </div>

            <div>
              <h5 className="font-semibold text-slate-900 mb-2">External APIs</h5>
              <ul className="space-y-1 text-slate-700">
                <li>• OpenAI API (GPT-4 for reasoning)</li>
                <li>• Tavily API (web search)</li>
                <li>• Wikipedia API (encyclopedic knowledge)</li>
                <li>• Google Fact Check Tools API (professional fact-checks)</li>
              </ul>
            </div>
          </div>
        </div>
      </CollapsibleSection>
    </div>
  )
}

// ============================================================================
// EDUCATIONAL TAB
// ============================================================================
function EducationalTab() {
  return (
    <div className="space-y-4">
      <CollapsibleSection title="Using MetaCheck for Education" defaultOpen={true}>
        <p className="leading-relaxed">
          MetaCheck is designed specifically for educational purposes, focusing on <strong>teaching media literacy and
          critical thinking skills</strong> rather than just providing verdicts. This section helps educators and students
          get the most educational value from the tool.
        </p>
      </CollapsibleSection>

      <CollapsibleSection title="Learning Objectives">
        <p className="text-sm leading-relaxed text-slate-700">
          MetaCheck helps students develop these core competencies:
        </p>

        <div className="grid md:grid-cols-2 gap-4">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h5 className="font-semibold text-blue-900 mb-2 text-sm">1. Source Evaluation Skills</h5>
            <ul className="space-y-1 text-sm text-blue-900">
              <li>• Distinguish between high and low credibility sources</li>
              <li>• Understand domain-based credibility assessment</li>
              <li>• Recognize the difference between fact-checkers, news, Wikipedia, and general web</li>
              <li>• Learn why .gov, .edu, and verified organizations are more trustworthy</li>
            </ul>
          </div>

          <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-4">
            <h5 className="font-semibold text-indigo-900 mb-2 text-sm">2. Evidence-Based Reasoning</h5>
            <ul className="space-y-1 text-sm text-indigo-900">
              <li>• Weigh evidence by credibility, not just quantity</li>
              <li>• Understand that one high-credibility source can outweigh many low-credibility sources</li>
              <li>• Practice synthesizing multiple pieces of evidence</li>
              <li>• Learn to identify when evidence is insufficient or conflicting</li>
            </ul>
          </div>

          <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
            <h5 className="font-semibold text-purple-900 mb-2 text-sm">3. Claim Identification</h5>
            <ul className="space-y-1 text-sm text-purple-900">
              <li>• Distinguish facts from opinions</li>
              <li>• Identify verifiable vs. non-verifiable statements</li>
              <li>• Recognize what makes a claim "check-worthy"</li>
              <li>• Understand why vague or generic statements can't be fact-checked</li>
            </ul>
          </div>

          <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-4">
            <h5 className="font-semibold text-emerald-900 mb-2 text-sm">4. Metacognitive Awareness</h5>
            <ul className="space-y-1 text-sm text-emerald-900">
              <li>• Understand how AI systems verify information</li>
              <li>• Compare personal reasoning with AI reasoning</li>
              <li>• Identify gaps in own knowledge or reasoning</li>
              <li>• Develop self-awareness about biases and assumptions</li>
            </ul>
          </div>
        </div>
      </CollapsibleSection>

      <CollapsibleSection title="Recommended Workflow for Students">
        <div className="space-y-3">
          <div className="bg-slate-50 border-l-4 border-blue-500 p-4">
            <h5 className="font-semibold text-slate-900 mb-2 text-sm">Step 1: Attempt Your Own Assessment First</h5>
            <p className="text-sm leading-relaxed text-slate-700 mb-2">
              Before using AI verification, go to the <strong>"Your Assessment"</strong> tab and create your own evaluation:
            </p>
            <ul className="ml-4 space-y-1 text-sm text-slate-700">
              <li>1. Read the text and identify claims you think are verifiable</li>
              <li>2. For each claim, research using search engines (Google, Bing, etc.)</li>
              <li>3. Evaluate sources you find (credibility, bias, authority)</li>
              <li>4. Make your own verdict (SUPPORTED/REFUTED/INSUFFICIENT/CONFLICTING)</li>
              <li>5. Assign a confidence score (how certain are you?)</li>
              <li>6. Write your reasoning (why did you reach this verdict?)</li>
              <li>7. List key sources you relied on</li>
            </ul>
            <p className="text-xs text-slate-600 mt-2 italic">
              This independent work is crucial! It forces you to think critically before seeing the AI's answer.
            </p>
          </div>

          <div className="bg-slate-50 border-l-4 border-indigo-500 p-4">
            <h5 className="font-semibold text-slate-900 mb-2 text-sm">Step 2: Run AI Verification</h5>
            <p className="text-sm leading-relaxed text-slate-700 mb-2">
              Go to the <strong>"AI Analysis"</strong> tab and verify the same claims:
            </p>
            <ul className="ml-4 space-y-1 text-sm text-slate-700">
              <li>• Use <strong>Comprehensive Mode</strong> to see full reasoning</li>
              <li>• Extract claims automatically (compare with what you identified)</li>
              <li>• Verify the claims and review detailed results</li>
              <li>• Read the justification and evidence carefully</li>
              <li>• Check the sources AI used vs. what you found</li>
            </ul>
          </div>

          <div className="bg-slate-50 border-l-4 border-purple-500 p-4">
            <h5 className="font-semibold text-slate-900 mb-2 text-sm">Step 3: Compare and Reflect</h5>
            <p className="text-sm leading-relaxed text-slate-700 mb-2">
              Go to the <strong>"Compare"</strong> tab to see differences:
            </p>
            <ul className="ml-4 space-y-1 text-sm text-slate-700">
              <li>• <strong>Verdict Match:</strong> Did you reach the same conclusion?</li>
              <li>• <strong>Confidence Gap:</strong> Were you more or less certain than the AI?</li>
              <li>• <strong>Source Differences:</strong> Did you use similar or different sources?</li>
              <li>• <strong>Reasoning Comparison:</strong> How did your logic differ?</li>
            </ul>
          </div>

          <div className="bg-slate-50 border-l-4 border-emerald-500 p-4">
            <h5 className="font-semibold text-slate-900 mb-2 text-sm">Step 4: Identify Learning Opportunities</h5>
            <p className="text-sm leading-relaxed text-slate-700 mb-2">
              Reflect on discrepancies to learn:
            </p>
            <ul className="ml-4 space-y-1 text-sm text-slate-700">
              <li>• <strong>If verdicts differ:</strong> Why? Did you miss a credible source? Did you overweight a low-credibility source?</li>
              <li>• <strong>If confidence differs:</strong> Were you overconfident? Under-confident? What caused the gap?</li>
              <li>• <strong>If sources differ:</strong> Did AI find sources you didn't? Did you use sources AI didn't find?</li>
              <li>• <strong>If reasoning differs:</strong> How did AI weigh evidence differently than you?</li>
            </ul>
            <p className="text-xs text-slate-600 mt-2 italic">
              <strong>Remember:</strong> Disagreements are learning opportunities, not failures. The goal is understanding, not being "right."
            </p>
          </div>
        </div>
      </CollapsibleSection>

      <CollapsibleSection title="Classroom Activities">
        <div className="grid md:grid-cols-2 gap-4">
          <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
            <h5 className="font-semibold text-amber-900 mb-2 text-sm">Activity 1: Claim Scavenger Hunt</h5>
            <p className="text-sm text-amber-900 leading-relaxed mb-2">
              Students find claims "in the wild" from social media, news, or viral posts, then verify them with MetaCheck.
            </p>
            <p className="text-xs text-amber-800">
              <strong>Learning Goal:</strong> Real-world application of fact-checking to everyday information consumption
            </p>
          </div>

          <div className="bg-rose-50 border border-rose-200 rounded-lg p-4">
            <h5 className="font-semibold text-rose-900 mb-2 text-sm">Activity 2: Verdict Debates</h5>
            <p className="text-sm text-rose-900 leading-relaxed mb-2">
              Class verifies the same claim. Students who reached different verdicts debate their reasoning using evidence.
            </p>
            <p className="text-xs text-rose-800">
              <strong>Learning Goal:</strong> Practice defending conclusions with evidence and listening to alternative interpretations
            </p>
          </div>

          <div className="bg-teal-50 border border-teal-200 rounded-lg p-4">
            <h5 className="font-semibold text-teal-900 mb-2 text-sm">Activity 3: Source Credibility Lab</h5>
            <p className="text-sm text-teal-900 leading-relaxed mb-2">
              Students examine evidence from different source types (fact-checker vs. blog vs. Wikipedia) for the same claim.
            </p>
            <p className="text-xs text-teal-800">
              <strong>Learning Goal:</strong> Understand how source credibility affects verdict determination
            </p>
          </div>

          <div className="bg-cyan-50 border border-cyan-200 rounded-lg p-4">
            <h5 className="font-semibold text-cyan-900 mb-2 text-sm">Activity 4: AI vs. Human Challenge</h5>
            <p className="text-sm text-cyan-900 leading-relaxed mb-2">
              Students assess claims independently, then compare with AI to see who was more accurate and why.
            </p>
            <p className="text-xs text-cyan-800">
              <strong>Learning Goal:</strong> Metacognitive awareness of personal biases and reasoning gaps
            </p>
          </div>
        </div>
      </CollapsibleSection>

      <CollapsibleSection title="Common Student Misconceptions to Address">
        <div className="space-y-3">
          <div className="bg-rose-50 border border-rose-200 rounded-lg p-4">
            <p className="font-semibold text-rose-900 text-sm mb-1">❌ Misconception: "More sources = more true"</p>
            <p className="text-sm text-rose-900 leading-relaxed">
              <strong>Correction:</strong> Quality over quantity. One fact-checker (0.95) outweighs five blogs (0.55 each).
              Teach students to weigh evidence by credibility, not just count sources.
            </p>
          </div>

          <div className="bg-rose-50 border border-rose-200 rounded-lg p-4">
            <p className="font-semibold text-rose-900 text-sm mb-1">❌ Misconception: "AI is always right"</p>
            <p className="text-sm text-rose-900 leading-relaxed">
              <strong>Correction:</strong> AI makes mistakes. It's limited by available sources, search results, and reasoning
              capabilities. Low confidence scores indicate uncertainty. Encourage critical evaluation of AI results.
            </p>
          </div>

          <div className="bg-rose-50 border border-rose-200 rounded-lg p-4">
            <p className="font-semibold text-rose-900 text-sm mb-1">❌ Misconception: "INSUFFICIENT_INFORMATION means it's false"</p>
            <p className="text-sm text-rose-900 leading-relaxed">
              <strong>Correction:</strong> INSUFFICIENT means we don't know, not that it's false. It indicates a need for
              better sources or more research, not a negative verdict.
            </p>
          </div>

          <div className="bg-rose-50 border border-rose-200 rounded-lg p-4">
            <p className="font-semibold text-rose-900 text-sm mb-1">❌ Misconception: "All opinions can be fact-checked"</p>
            <p className="text-sm text-rose-900 leading-relaxed">
              <strong>Correction:</strong> Only factual claims are verifiable. "This policy is good" is an opinion (not
              fact-checkable). "This policy reduced unemployment by 2%" is a fact (verifiable). Teach students to distinguish.
            </p>
          </div>

          <div className="bg-rose-50 border border-rose-200 rounded-lg p-4">
            <p className="font-semibold text-rose-900 text-sm mb-1">❌ Misconception: "Wikipedia is unreliable"</p>
            <p className="text-sm text-rose-900 leading-relaxed">
              <strong>Correction:</strong> Wikipedia (0.80) is generally reliable for established facts, though not perfect.
              It's more credible than general web but less than fact-checkers or government sources. Teach nuanced evaluation.
            </p>
          </div>
        </div>
      </CollapsibleSection>

      <CollapsibleSection title="Discussion Questions for Class">
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <ul className="space-y-2 text-sm text-blue-900">
            <li className="leading-relaxed">
              1. <strong>Why does MetaCheck weight sources differently?</strong> Is this fair? How does this compare to
              how you evaluate information in your daily life?
            </li>
            <li className="leading-relaxed">
              2. <strong>What are the limitations of automated fact-checking?</strong> What can AI do well? What does it
              struggle with? What requires human judgment?
            </li>
            <li className="leading-relaxed">
              3. <strong>How can you tell if a source is credible?</strong> Beyond domain classification, what other
              factors matter? (Author credentials, citations, transparency, etc.)
            </li>
            <li className="leading-relaxed">
              4. <strong>When is CONFLICTING_EVIDENCE appropriate?</strong> Can you think of examples where credible
              sources genuinely disagree? How should you respond when evidence conflicts?
            </li>
            <li className="leading-relaxed">
              5. <strong>How might bias affect AI fact-checking?</strong> Where do domain credibility scores come from?
              Who decides what's credible? Could this introduce bias?
            </li>
            <li className="leading-relaxed">
              6. <strong>What's the difference between misinformation and disinformation?</strong> How does intent matter?
              Can AI detect intentional deception?
            </li>
          </ul>
        </div>
      </CollapsibleSection>

      <CollapsibleSection title="Tips for Educators">
        <div className="space-y-3">
          <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-3">
            <p className="text-sm text-emerald-900 leading-relaxed">
              <strong>✓ Start with obvious examples:</strong> Begin with claims that have clear verdicts (either clearly
              true or clearly false) before moving to ambiguous cases. This builds student confidence.
            </p>
          </div>

          <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-3">
            <p className="text-sm text-emerald-900 leading-relaxed">
              <strong>✓ Use Comprehensive Mode for learning:</strong> While Basic Mode is faster, Comprehensive Mode's
              metacognitive detail is crucial for understanding <em>how</em> fact-checking works, not just <em>what</em> the verdict is.
            </p>
          </div>

          <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-3">
            <p className="text-sm text-emerald-900 leading-relaxed">
              <strong>✓ Encourage disagreement with AI:</strong> If students think the AI is wrong, that's excellent!
              Have them explain why with evidence. This develops critical thinking and reasoning skills.
            </p>
          </div>

          <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-3">
            <p className="text-sm text-emerald-900 leading-relaxed">
              <strong>✓ Focus on process, not just answers:</strong> The educational value is in understanding the reasoning,
              not memorizing verdicts. Ask "How did you reach that conclusion?" more than "Is it true or false?"
            </p>
          </div>

          <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-3">
            <p className="text-sm text-emerald-900 leading-relaxed">
              <strong>✓ Discuss limitations openly:</strong> MetaCheck isn't perfect. Discussing its limitations teaches
              students to think critically about all tools and sources, including AI systems.
            </p>
          </div>
        </div>
      </CollapsibleSection>

      <CollapsibleSection title="Assessment Rubric Suggestion">
        <div className="overflow-x-auto rounded-xl border border-slate-200">
          <table className="w-full min-w-[700px] border-collapse text-left text-sm">
            <thead className="bg-slate-50">
              <tr>
                <th className="border-b border-slate-200 px-4 py-3 font-semibold">Skill Area</th>
                <th className="border-b border-slate-200 px-4 py-3 font-semibold">Criteria</th>
                <th className="border-b border-slate-200 px-4 py-3 font-semibold">Points</th>
              </tr>
            </thead>
            <tbody>
              <tr className="align-top">
                <td className="border-b border-slate-100 px-4 py-3 font-medium">Claim Identification</td>
                <td className="border-b border-slate-100 px-4 py-3">
                  Student correctly identifies verifiable claims and distinguishes them from opinions/vague statements
                </td>
                <td className="border-b border-slate-100 px-4 py-3">20 pts</td>
              </tr>
              <tr className="align-top">
                <td className="border-b border-slate-100 px-4 py-3 font-medium">Source Evaluation</td>
                <td className="border-b border-slate-100 px-4 py-3">
                  Student assesses source credibility appropriately (domain, authority, bias) and explains reasoning
                </td>
                <td className="border-b border-slate-100 px-4 py-3">25 pts</td>
              </tr>
              <tr className="align-top">
                <td className="border-b border-slate-100 px-4 py-3 font-medium">Evidence Synthesis</td>
                <td className="border-b border-slate-100 px-4 py-3">
                  Student weighs evidence by quality (not just quantity) and integrates multiple sources coherently
                </td>
                <td className="border-b border-slate-100 px-4 py-3">25 pts</td>
              </tr>
              <tr className="align-top">
                <td className="border-b border-slate-100 px-4 py-3 font-medium">Verdict Justification</td>
                <td className="border-b border-slate-100 px-4 py-3">
                  Student provides clear, logical reasoning for verdict with appropriate confidence level
                </td>
                <td className="border-b border-slate-100 px-4 py-3">20 pts</td>
              </tr>
              <tr className="align-top">
                <td className="px-4 py-3 font-medium">Metacognitive Reflection</td>
                <td className="px-4 py-3">
                  Student reflects on differences with AI assessment and identifies personal learning opportunities
                </td>
                <td className="px-4 py-3">10 pts</td>
              </tr>
            </tbody>
          </table>
        </div>
      </CollapsibleSection>
    </div>
  )
}
