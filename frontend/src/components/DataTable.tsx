'use client'
import { useState, useMemo } from 'react'

type Props = {
  columns: string[]
  data: Record<string, any>[]
  totalRows: number
}

const PAGE_SIZE = 10

export default function DataTable({ columns, data, totalRows }: Props) {
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(0)

  const filtered = useMemo(() => {
    if (!search.trim()) return data
    const term = search.toLowerCase()
    return data.filter(row =>
      Object.values(row).some(v => String(v ?? '').toLowerCase().includes(term))
    )
  }, [data, search])

  const pageData = filtered.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE)
  const totalPages = Math.ceil(filtered.length / PAGE_SIZE)

  const start = page * PAGE_SIZE + 1
  const end = Math.min((page + 1) * PAGE_SIZE, filtered.length)

  return (
    <div style={{ background: '#fff', borderRadius: 16, boxShadow: '0 2px 12px rgba(0,0,0,0.06)', overflow: 'hidden', marginBottom: 24 }}>
      {/* Header */}
      <div style={{ padding: '16px 20px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid #e2e6f0' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <div style={{ width: 8, height: 8, borderRadius: '50%', background: '#22c55e' }} />
          <span style={{ fontSize: 14, fontWeight: 600, color: '#1a1d2e' }}>Data Results</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 12, color: '#8b92a9' }}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <ellipse cx="12" cy="5" rx="9" ry="3" /><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3" />
            <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5" />
          </svg>
          {start}–{end} of {filtered.length} results
          {filtered.length < totalRows && <span>(filtered from {totalRows})</span>}
        </div>
      </div>

      {/* Search */}
      <div style={{ padding: '10px 16px', borderBottom: '1px solid #e2e6f0', display: 'flex', alignItems: 'center', gap: 10 }}>
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#8b92a9" strokeWidth="2">
          <circle cx="11" cy="11" r="8" /><line x1="21" y1="21" x2="16.65" y2="16.65" />
        </svg>
        <input
          type="text"
          placeholder="Search across all data..."
          value={search}
          onChange={e => { setSearch(e.target.value); setPage(0) }}
          style={{
            border: 'none', outline: 'none', background: 'transparent',
            fontSize: 14, color: '#1a1d2e', width: '100%', fontFamily: 'inherit',
          }}
        />
        {search && (
          <button onClick={() => setSearch('')} style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#8b92a9', fontSize: 16 }}>×</button>
        )}
      </div>

      {/* Table */}
      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ background: '#f8f9fd' }}>
              {columns.map(col => (
                <th key={col} style={{
                  padding: '12px 20px', textAlign: 'left', fontSize: 13,
                  fontWeight: 600, color: '#5a6075', borderBottom: '1px solid #e2e6f0',
                  whiteSpace: 'nowrap',
                }}>{col}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {pageData.length === 0 ? (
              <tr>
                <td colSpan={columns.length} style={{ padding: '32px', textAlign: 'center', color: '#8b92a9', fontSize: 14 }}>
                  No results found
                </td>
              </tr>
            ) : pageData.map((row, i) => (
              <tr key={i}
                style={{ borderBottom: '1px solid #f0f2f8' }}
                onMouseOver={e => (e.currentTarget.style.background = '#f8f9fd')}
                onMouseOut={e => (e.currentTarget.style.background = '')}
              >
                {columns.map(col => (
                  <td key={col} style={{
                    padding: '12px 20px', fontSize: 14, color: '#1a1d2e',
                    whiteSpace: 'nowrap', maxWidth: 240, overflow: 'hidden', textOverflow: 'ellipsis',
                  }}>
                    {row[col] === null || row[col] === undefined
                      ? <span style={{ color: '#c0c7d8', fontStyle: 'italic' }}>null</span>
                      : String(row[col])}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div style={{
          padding: '12px 20px', borderTop: '1px solid #e2e6f0',
          display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: 8,
        }}>
          <button onClick={() => setPage(0)} disabled={page === 0} style={pgBtn}>«</button>
          <button onClick={() => setPage(p => p - 1)} disabled={page === 0} style={pgBtn}>‹</button>
          <span style={{ fontSize: 13, color: '#5a6075' }}>Page {page + 1} of {totalPages}</span>
          <button onClick={() => setPage(p => p + 1)} disabled={page >= totalPages - 1} style={pgBtn}>›</button>
          <button onClick={() => setPage(totalPages - 1)} disabled={page >= totalPages - 1} style={pgBtn}>»</button>
        </div>
      )}
    </div>
  )
}

const pgBtn: React.CSSProperties = {
  padding: '5px 10px', border: '1px solid #e2e6f0', borderRadius: 6,
  background: '#fff', cursor: 'pointer', fontSize: 14, color: '#5a6075',
  fontFamily: 'inherit',
}
