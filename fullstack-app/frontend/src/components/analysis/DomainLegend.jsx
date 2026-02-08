import { Card, CardContent, CardHeader, CardTitle } from '../ui/card'

const colorPalette = [
  'bg-emerald-100 text-emerald-800 border-emerald-200',
  'bg-sky-100 text-sky-800 border-sky-200',
  'bg-amber-100 text-amber-800 border-amber-200',
  'bg-indigo-100 text-indigo-800 border-indigo-200',
  'bg-rose-100 text-rose-800 border-rose-200',
  'bg-lime-100 text-lime-800 border-lime-200',
  'bg-fuchsia-100 text-fuchsia-800 border-fuchsia-200',
  'bg-slate-100 text-slate-800 border-slate-200',
]

export function DomainLegend({ categories }) {
  if (!categories) return null
  const entries = Object.entries(categories)
  const toSentenceCaseLabel = (key) => {
    const normalized = key.replace(/_/g, ' ').trim().toLowerCase()
    return normalized.charAt(0).toUpperCase() + normalized.slice(1)
  }
  return (
    <Card className="border-slate-200">
      <CardHeader>
        <CardTitle className="text-base">Domain Categories</CardTitle>
      </CardHeader>
      <CardContent className="grid grid-cols-1 gap-2 text-sm md:grid-cols-2">
        {entries.map(([key, value], idx) => (
          <div
            key={key}
            className={`rounded-2xl border px-3 py-2 ${colorPalette[idx % colorPalette.length]}`}
          >
            <p className="font-semibold">{toSentenceCaseLabel(key)}</p>
            <p className="text-xs opacity-80">{value.description}</p>
            <p className="text-xs mt-1">Score: {value.score}</p>
          </div>
        ))}
      </CardContent>
    </Card>
  )
}
