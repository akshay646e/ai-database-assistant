'use client'

const CARD_CONFIGS = [
  {
    key: 'total_rows',
    label: 'TOTAL RECORDS',
    sub: 'Count',
    color: '#3b82f6',
    barColor: '#3b82f6',
    pct: 100,
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" width="20" height="20">
        <rect x="3" y="3" width="18" height="18" rx="2" /><line x1="3" y1="9" x2="21" y2="9" />
        <line x1="3" y1="15" x2="21" y2="15" /><line x1="9" y1="3" x2="9" y2="21" /><line x1="15" y1="3" x2="15" y2="21" />
      </svg>
    ),
  },
  {
    key: 'avg',
    label: 'AVERAGE',
    sub: 'Average',
    color: '#22c55e',
    barColor: '#22c55e',
    pct: 65,
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" width="20" height="20">
        <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
      </svg>
    ),
  },
  {
    key: 'max',
    label: 'MAX',
    sub: 'Maximum',
    color: '#a855f7',
    barColor: '#a855f7',
    pct: 85,
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" width="20" height="20">
        <polyline points="23 6 13.5 15.5 8.5 10.5 1 18" /><polyline points="17 6 23 6 23 12" />
      </svg>
    ),
  },
  {
    key: 'min',
    label: 'MIN',
    sub: 'Minimum',
    color: '#f97316',
    barColor: '#f97316',
    pct: 40,
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" width="20" height="20">
        <circle cx="12" cy="12" r="10" /><line x1="8" y1="12" x2="16" y2="12" />
      </svg>
    ),
  },
]

export default function MetricCards({ metrics }: { metrics: any }) {
  if (!metrics) return null

  const h = metrics.kpis?.headline
  const total = metrics.kpis?.total_rows ?? 0

  const fmt = (v: number | undefined) => {
    if (v === undefined || v === null) return '—'
    return typeof v === 'number'
      ? v % 1 === 0 ? v.toLocaleString() : v.toLocaleString(undefined, { maximumFractionDigits: 2 })
      : String(v)
  }

  const values: Record<string, any> = {
    total_rows: total,
    avg: h ? fmt(h.avg) : '—',
    max: h ? fmt(h.max) : '—',
    min: h ? fmt(h.min) : '—',
  }

  const labels: Record<string, string> = {
    avg: h ? `AVERAGE ${h.column?.toUpperCase()}` : 'AVERAGE',
    max: h ? `MAX ${h.column?.toUpperCase()}` : 'MAX',
    min: h ? `MIN ${h.column?.toUpperCase()}` : 'MIN',
  }

  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: 'repeat(4, 1fr)',
      gap: 16,
      marginBottom: 24,
    }}>
      {CARD_CONFIGS.map(card => (
        <div
          key={card.key}
          style={{
            background: '#fff',
            borderRadius: 16,
            padding: '18px 20px 14px',
            boxShadow: '0 2px 12px rgba(0,0,0,0.06)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 8 }}>
            <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: '0.08em', textTransform: 'uppercase', color: '#8b92a9' }}>
              {card.key === 'total_rows' ? card.label : (labels[card.key] || card.label)}
            </div>
            <div style={{
              width: 42, height: 42, borderRadius: 10, background: card.color,
              display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
            }}>
              {card.icon}
            </div>
          </div>
          <div style={{ fontSize: 30, fontWeight: 700, color: '#1a1d2e', marginBottom: 4 }}>
            {fmt(values[card.key])}
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 11, color: '#8b92a9', marginBottom: 12 }}>
            <span style={{ width: 6, height: 6, borderRadius: '50%', background: card.color, display: 'inline-block' }} />
            {card.sub}
          </div>
          <div style={{ height: 3, borderRadius: 2, background: '#f0f2f8' }}>
            <div style={{ height: '100%', borderRadius: 2, background: card.barColor, width: `${card.pct}%`, transition: 'width 1s ease' }} />
          </div>
        </div>
      ))}
    </div>
  )
}
