export const verdictColors = {
  SUPPORTED: 'bg-emerald-100 text-emerald-700 border-emerald-200',
  REFUTED: 'bg-rose-100 text-rose-700 border-rose-200',
  INSUFFICIENT_INFORMATION: 'bg-amber-100 text-amber-700 border-amber-200',
  CONFLICTING_EVIDENCE: 'bg-sky-100 text-sky-700 border-sky-200',
}

export const stanceColors = {
  supports: 'bg-emerald-50 text-emerald-700 border-emerald-200',
  refutes: 'bg-rose-50 text-rose-700 border-rose-200',
  neutral: 'bg-slate-100 text-slate-700 border-slate-200',
  unclear: 'bg-amber-50 text-amber-700 border-amber-200',
}

export function verdictLabel(verdict) {
  return verdict?.replace(/_/g, ' ') || 'Unknown'
}
