'use client'

type Props = {
  insights: string[]
  suggestions: string[]
  onSuggestionClick: (q: string) => void
}

export default function InsightsSuggestions({ insights, suggestions, onSuggestionClick }: Props) {
  if (!insights?.length && !suggestions?.length) return null

  return (
    <div style={{ display: 'grid', gridTemplateColumns: suggestions?.length ? '1fr 1fr' : '1fr', gap: 20, marginBottom: 24 }}>

      {/* AI Insights */}
      {insights?.length > 0 && (
        <div style={{ background: '#fff', borderRadius: 16, padding: 20, boxShadow: '0 2px 12px rgba(0,0,0,0.06)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 16 }}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="#f59e0b" stroke="#f59e0b" strokeWidth="1">
              <path d="M12 2a7 7 0 017 7c0 2.38-1.19 4.47-3 5.74V17a1 1 0 01-1 1H9a1 1 0 01-1-1v-2.26C6.19 13.47 5 11.38 5 9a7 7 0 017-7z" />
              <line x1="9" y1="21" x2="15" y2="21" /><line x1="10" y1="17" x2="10" y2="21" /><line x1="14" y1="17" x2="14" y2="21" />
            </svg>
            <span style={{ fontSize: 14, fontWeight: 600, color: '#1a1d2e' }}>AI Insights</span>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            {insights.map((ins, i) => (
              <div key={i} style={{ display: 'flex', gap: 12 }}>
                <div style={{
                  width: 24, height: 24, borderRadius: '50%',
                  background: 'rgba(108,71,255,0.1)', display: 'flex', alignItems: 'center',
                  justifyContent: 'center', fontSize: 11, fontWeight: 700, color: '#6c47ff', flexShrink: 0, marginTop: 1,
                }}>{i + 1}</div>
                <p style={{ fontSize: 13, color: '#5a6075', lineHeight: 1.6 }}>{ins}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Smart Suggestions */}
      {suggestions?.length > 0 && (
        <div style={{ background: '#fff', borderRadius: 16, padding: 20, boxShadow: '0 2px 12px rgba(0,0,0,0.06)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 16 }}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#14b8a6" strokeWidth="2">
              <path d="M12 2L2 7l10 5 10-5-10-5z" /><path d="M2 17l10 5 10-5" /><path d="M2 12l10 5 10-5" />
            </svg>
            <span style={{ fontSize: 14, fontWeight: 600, color: '#1a1d2e' }}>Smart Suggestions</span>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {suggestions.map((s, i) => (
              <button
                key={i}
                onClick={() => onSuggestionClick(s)}
                style={{
                  textAlign: 'left', padding: '10px 14px',
                  border: '1.5px solid rgba(20,184,166,0.2)',
                  borderRadius: 10, background: 'rgba(20,184,166,0.04)',
                  color: '#0f766e', fontSize: 13, cursor: 'pointer',
                  fontFamily: 'inherit', transition: 'all 0.2s', lineHeight: 1.4,
                  display: 'flex', alignItems: 'flex-start', gap: 8,
                }}
                onMouseOver={e => { e.currentTarget.style.background = 'rgba(20,184,166,0.1)'; e.currentTarget.style.borderColor = 'rgba(20,184,166,0.4)' }}
                onMouseOut={e => { e.currentTarget.style.background = 'rgba(20,184,166,0.04)'; e.currentTarget.style.borderColor = 'rgba(20,184,166,0.2)' }}
              >
                <span style={{ color: '#14b8a6', marginTop: 1 }}>▶</span>
                {s}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
