import { useCallback, useMemo, useState } from 'react'
import { postVerify } from '../lib/api'

export function useVerify() {
  const [status, setStatus] = useState('idle') // idle | loading | success | error
  const [assessment, setAssessment] = useState(null)
  const [error, setError] = useState(null)
  const [elapsedMs, setElapsedMs] = useState(0)

  const runVerify = useCallback(async ({ text, verbose = false }) => {
    const start = performance.now()
    setStatus('loading')
    setError(null)
    try {
      const data = await postVerify({ text, verbose })
      setAssessment(data)
      setStatus('success')
    } catch (err) {
      setError(err?.response?.data?.detail || err.message || 'Verification failed')
      setStatus('error')
    } finally {
      setElapsedMs(Math.round(performance.now() - start))
    }
  }, [])

  const reset = useCallback(() => {
    setAssessment(null)
    setError(null)
    setElapsedMs(0)
    setStatus('idle')
  }, [])

  const summary = useMemo(() => {
    if (!assessment?.claim_results?.length) return null
    const totalClaims = assessment.claim_results.length
    const avgConfidence =
      assessment.claim_results.reduce((sum, cr) => sum + (cr.confidence || 0), 0) / totalClaims
    return { totalClaims, avgConfidence }
  }, [assessment])

  return {
    status,
    assessment,
    error,
    elapsedMs,
    summary,
    runVerify,
    reset,
  }
}
