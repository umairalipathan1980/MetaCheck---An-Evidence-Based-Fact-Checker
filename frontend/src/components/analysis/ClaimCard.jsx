import { Badge } from '../ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card'
import { verdictColors, verdictLabel } from '../../lib/types'
import { cn } from '../../lib/utils'

export function ClaimCard({ claim, verdict, confidence, keySources = [], onSelect, selected = false, index }) {
  return (
    <Card
      className={cn(
        'cursor-pointer border-slate-200 transition hover:-translate-y-0.5 hover:shadow-lg',
        selected && 'ring-2 ring-emerald-400'
      )}
      onClick={onSelect}
    >
      <CardHeader className="flex flex-row items-start gap-3">
        <Badge className={cn('border', verdictColors[verdict] || 'bg-slate-100 text-slate-700 border-slate-200')}>
          {verdictLabel(verdict)}
        </Badge>
        <div className="flex-1">
          <CardTitle className="text-base font-semibold leading-tight">Claim {index + 1}</CardTitle>
          <p className="mt-1 text-sm text-slate-600 line-clamp-3">{claim}</p>
        </div>
        <div className="rounded-2xl bg-slate-50 px-3 py-2 text-right">
          <p className="text-xs text-slate-500">Confidence</p>
          <p className="text-sm font-semibold text-slate-900">{(confidence ?? 0).toFixed(2)}</p>
        </div>
      </CardHeader>
      <CardContent className="flex items-center gap-3 pt-0 text-sm text-slate-600">
        <span className="rounded-lg bg-slate-100 px-2 py-1">Sources: {keySources.length}</span>
      </CardContent>
    </Card>
  )
}
