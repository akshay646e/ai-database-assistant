'use client'
import { useState, useRef } from 'react'
import type { DBConfig, QueryResult } from '@/types'
import FileUpload from './FileUpload'
import MetricCards from './MetricCards'
import DataTable from './DataTable'
import ChartSection from './ChartSection'
import InsightsSuggestions from './InsightsSuggestions'

type Props = {
  dbConfig: DBConfig
  schema: any
  queryResult: QueryResult | null
  queryLoading: boolean
  queryError: string
  onQuery: (q: string) => void
  onDisconnect: () => void
  onRefreshSchema: () => void
}

export default function DashboardPage({
  dbConfig, schema, queryResult, queryLoading, queryError, onQuery, onDisconnect, onRefreshSchema
}: Props) {
  const [question, setQuestion] = useState('')
  const resultsRef = useRef<HTMLDivElement>(null)

  const handleExecute = () => {
    if (!question.trim() || queryLoading) return
    onQuery(question.trim())
    setTimeout(() => resultsRef.current?.scrollIntoView({ behavior: 'smooth' }), 300)
  }

  const handleSuggestionClick = (s: string) => {
    setQuestion(s)
    onQuery(s)
    setTimeout(() => resultsRef.current?.scrollIntoView({ behavior: 'smooth' }), 300)
  }

  return (
    <div style={{ minHeight: '100vh', background: 'linear-gradient(145deg,#eef1f8,#e4e8f5)', display: 'flex', flexDirection: 'column' }}>
      {/* Top bar */}
      <div style={{ height: 8, background: '#1a1d2e' }} />

      {/* Dashboard Header */}
      <div style={{
        background: '#fff',
        borderBottom: '1px solid #e2e6f0',
        padding: '14px 32px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <div style={{
            width: 44, height: 44, background: '#1a1d2e', borderRadius: 12,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: 22, fontWeight: 700, color: '#fff', fontStyle: 'italic', fontFamily: 'Georgia, serif',
          }}>b</div>
          <div>
            <div style={{ fontSize: 18, fontWeight: 700, color: '#1a1d2e' }}>The Baap Company</div>
            <div style={{ fontSize: 11, color: '#8b92a9' }}>Business Applications and Platforms</div>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 20 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 7, fontSize: 13, fontWeight: 500, color: '#5a6075' }}>
            <div style={{ width: 8, height: 8, borderRadius: '50%', background: '#22c55e', boxShadow: '0 0 6px rgba(34,197,94,0.6)' }} />
            Connected to <strong style={{ color: '#1a1d2e' }}>{dbConfig.database}</strong>
          </div>
          <FileUpload dbConfig={dbConfig} onUploadSuccess={onRefreshSchema} />
          <button
            onClick={onDisconnect}
            style={{
              display: 'flex', alignItems: 'center', gap: 7,
              padding: '8px 16px', border: '1.5px solid #e2e6f0', borderRadius: 10,
              background: '#fff', color: '#5a6075', fontSize: 13, fontWeight: 500,
              fontFamily: 'inherit', cursor: 'pointer', transition: 'all 0.2s',
            }}
            onMouseOver={e => (e.currentTarget.style.borderColor = '#5a6075')}
            onMouseOut={e => (e.currentTarget.style.borderColor = '#e2e6f0')}
          >
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4" />
              <polyline points="16 17 21 12 16 7" />
              <line x1="21" y1="12" x2="9" y2="12" />
            </svg>
            Disconnect
          </button>
        </div>
      </div>

      {/* Page Title */}
      <div style={{ textAlign: 'center', padding: '24px 0 8px' }}>
        <h2 style={{ fontSize: 26, fontWeight: 700, color: '#1a1d2e' }}>Analytics Dashboard</h2>
        <p style={{ fontSize: 13, color: '#8b92a9', marginTop: 5 }}>Connect to your database to unlock powerful insights</p>
      </div>

      {/* Main content */}
      <div style={{ flex: 1, maxWidth: 1100, width: '100%', margin: '0 auto', padding: '16px 24px 40px' }}>

        {/* AI Query Assistant */}
        <div style={{
          background: '#fff', borderRadius: 16, padding: '24px',
          boxShadow: '0 2px 12px rgba(0,0,0,0.06)', marginBottom: 24,
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 15, fontWeight: 600, color: '#1a1d2e', marginBottom: 14 }}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="#6c47ff" stroke="#6c47ff" strokeWidth="1">
              <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
            </svg>
            AI Query Assistant
          </div>
          <textarea
            value={question}
            onChange={e => setQuestion(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && e.ctrlKey && handleExecute()}
            placeholder={'Ask a question about your data...\ne.g. show the number of students per standard'}
            rows={4}
            style={{
              width: '100%', border: '1.5px solid #6c47ff', borderRadius: 10,
              padding: '12px 14px', fontSize: 14, fontFamily: 'inherit',
              color: '#1a1d2e', resize: 'vertical', outline: 'none',
              boxShadow: '0 0 0 3px rgba(108,71,255,0.08)',
            }}
          />
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: 12 }}>
            <span style={{ fontSize: 12, color: '#8b92a9' }}>Tip: Press Ctrl+Enter to execute</span>
            <button
              onClick={handleExecute}
              disabled={queryLoading || !question.trim()}
              style={{
                display: 'flex', alignItems: 'center', gap: 8,
                padding: '11px 22px', background: queryLoading ? '#9b85ff' : '#6c47ff',
                color: '#fff', border: 'none', borderRadius: 10,
                fontSize: 14, fontWeight: 600, fontFamily: 'inherit',
                cursor: queryLoading ? 'not-allowed' : 'pointer', transition: 'background 0.2s',
              }}
            >
              {queryLoading ? (
                <>
                  <span style={{ width: 16, height: 16, border: '2px solid rgba(255,255,255,0.3)', borderTopColor: '#fff', borderRadius: '50%', display: 'inline-block', animation: 'spin 0.7s linear infinite' }} />
                  Thinking...
                </>
              ) : (
                <>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <line x1="22" y1="2" x2="11" y2="13" />
                    <polygon points="22 2 15 22 11 13 2 9 22 2" />
                  </svg>
                  Execute Query
                </>
              )}
            </button>
          </div>
        </div>

        {/* Error */}
        {queryError && (
          <div style={{
            background: '#fef2f2', border: '1px solid #fca5a5', borderRadius: 12,
            padding: '14px 18px', color: '#dc2626', fontSize: 14, marginBottom: 20,
          }}>
            <strong>⚠️ Error:</strong> {queryError}
          </div>
        )}

        {/* Loading state */}
        {queryLoading && (
          <div style={{
            background: '#fff', borderRadius: 16, padding: '32px',
            textAlign: 'center', boxShadow: '0 2px 12px rgba(0,0,0,0.06)', marginBottom: 24,
          }}>
            <div style={{ display: 'inline-flex', alignItems: 'center', gap: 12, color: '#6c47ff', fontSize: 15 }}>
              <span style={{ width: 24, height: 24, border: '3px solid #e2e6f0', borderTopColor: '#6c47ff', borderRadius: '50%', display: 'inline-block', animation: 'spin 0.7s linear infinite' }} />
              BAAP AI is thinking...
            </div>
          </div>
        )}

        {/* Results */}
        {queryResult && !queryLoading && (
          <div ref={resultsRef}>

            {/* Mode badge + AI Answer bubble — always shown */}
            <div style={{
              background: '#fff', borderRadius: 16, padding: '20px 24px',
              boxShadow: '0 2px 12px rgba(0,0,0,0.06)', marginBottom: 20,
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: queryResult.answer ? 12 : 0 }}>
                <div style={{
                  padding: '3px 10px', borderRadius: 20, fontSize: 11, fontWeight: 700,
                  letterSpacing: '0.05em', textTransform: 'uppercase' as const,
                  background:
                    queryResult.mode === 'sql' ? '#eff6ff' :
                      queryResult.mode === 'rag' ? '#f0fdf4' :
                        queryResult.mode === 'hybrid' ? '#faf5ff' : '#f8f9fd',
                  color:
                    queryResult.mode === 'sql' ? '#2563eb' :
                      queryResult.mode === 'rag' ? '#16a34a' :
                        queryResult.mode === 'hybrid' ? '#7c3aed' : '#6c47ff',
                }}>
                  {queryResult.mode === 'sql' ? '🗄 SQL' :
                    queryResult.mode === 'rag' ? '📄 Document' :
                      queryResult.mode === 'hybrid' ? '⚡ Hybrid' : '💬 Chat'}
                </div>
                <span style={{ fontSize: 13, color: '#8b92a9' }}>BAAP AI Response</span>
              </div>
              {queryResult.answer && (
                <p style={{ fontSize: 14, color: '#1a1d2e', lineHeight: 1.7, margin: 0 }}>
                  {queryResult.answer}
                </p>
              )}
            </div>

            {/* Generated SQL — only for sql/hybrid mode */}
            {queryResult.sql_query && (
              <>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 10 }}>
                  <div style={{ width: 8, height: 8, borderRadius: '50%', background: '#22c55e' }} />
                  <span style={{ fontSize: 14, fontWeight: 600, color: '#1a1d2e' }}>Generated SQL Query</span>
                </div>
                <div style={{
                  background: '#0f1117', borderRadius: 12, padding: '16px 20px',
                  fontFamily: "'JetBrains Mono', monospace", fontSize: 13,
                  color: '#00ff9d', lineHeight: 1.7, overflowX: 'auto', marginBottom: 24,
                  position: 'relative',
                }}>
                  <CopyBtn text={queryResult.sql_query} />
                  {queryResult.sql_query}
                </div>
              </>
            )}

            {/* Metrics — only when present */}
            {queryResult.metrics && <MetricCards metrics={queryResult.metrics} />}

            {/* Data Table — only when data is present */}
            {queryResult.data && queryResult.columns && (
              <DataTable
                columns={queryResult.columns}
                data={queryResult.data}
                totalRows={queryResult.total_rows ?? 0}
              />
            )}

            {/* Chart — only when chart_config is present */}
            {queryResult.chart_config && <ChartSection chart={queryResult.chart_config} />}

            {/* Insights + Suggestions — only when present */}
            {(queryResult.insights || queryResult.suggestions) && (
              <InsightsSuggestions
                insights={queryResult.insights ?? []}
                suggestions={queryResult.suggestions ?? []}
                onSuggestionClick={handleSuggestionClick}
              />
            )}
          </div>
        )}

        {/* Schema Explorer (when no query yet) */}
        {!queryResult && !queryLoading && schema && (
          <SchemaExplorer schema={schema} onAskQuestion={(q: string) => { setQuestion(q); onQuery(q) }} />
        )}
      </div>

      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  )
}

function CopyBtn({ text }: { text: string }) {
  const [copied, setCopied] = useState(false)
  return (
    <button
      onClick={() => { navigator.clipboard.writeText(text); setCopied(true); setTimeout(() => setCopied(false), 2000) }}
      style={{
        position: 'absolute', top: 12, right: 14, background: 'rgba(255,255,255,0.1)',
        border: '1px solid rgba(255,255,255,0.15)', borderRadius: 6,
        padding: '3px 10px', color: '#fff', fontSize: 11, cursor: 'pointer', fontFamily: 'inherit',
      }}
    >
      {copied ? '✓ Copied' : 'Copy'}
    </button>
  )
}

function SchemaExplorer({ schema, onAskQuestion }: { schema: any, onAskQuestion: (q: string) => void }) {
  const [open, setOpen] = useState<string | null>(null)
  const starters = [
    'Show all records from the first table',
    'Count total rows in each table',
    'Show the first 10 rows of data',
  ]
  return (
    <div>
      <div style={{
        background: '#fff', borderRadius: 16, padding: 20,
        boxShadow: '0 2px 12px rgba(0,0,0,0.06)', marginBottom: 20,
      }}>
        <p style={{ fontSize: 13, color: '#8b92a9', marginBottom: 12 }}>💡 Try these starter questions:</p>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
          {starters.map((s, i) => (
            <button key={i} onClick={() => onAskQuestion(s)}
              style={{
                padding: '7px 14px', border: '1.5px solid rgba(108,71,255,0.3)',
                borderRadius: 8, background: 'rgba(108,71,255,0.05)',
                color: '#6c47ff', fontSize: 13, cursor: 'pointer', fontFamily: 'inherit',
              }}>{s}</button>
          ))}
        </div>
      </div>
      <div style={{ background: '#fff', borderRadius: 16, padding: 20, boxShadow: '0 2px 12px rgba(0,0,0,0.06)' }}>
        <div style={{ fontSize: 15, fontWeight: 600, color: '#1a1d2e', marginBottom: 14 }}>📊 Schema Explorer</div>
        {Object.entries(schema).map(([table, info]: any) => (
          <div key={table} style={{ border: '1px solid #e2e6f0', borderRadius: 10, overflow: 'hidden', marginBottom: 8 }}>
            <button
              onClick={() => setOpen(open === table ? null : table)}
              style={{
                width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                padding: '12px 16px', background: 'none', border: 'none', cursor: 'pointer', fontFamily: 'inherit',
              }}
            >
              <span style={{ fontFamily: "'JetBrains Mono', monospace", color: '#6c47ff', fontSize: 13 }}>{table}</span>
              <span style={{ fontSize: 12, color: '#8b92a9' }}>{info.row_count?.toLocaleString()} rows · {info.columns.length} cols</span>
            </button>
            {open === table && (
              <div style={{ borderTop: '1px solid #e2e6f0', padding: '12px 16px', background: '#fafbfd', display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                {info.columns.map((col: any) => (
                  <span key={col.name} style={{ fontSize: 12, padding: '3px 10px', borderRadius: 6, background: '#fff', border: '1px solid #e2e6f0' }}>
                    <span style={{ color: '#14b8a6', fontWeight: 600 }}>{col.name}</span>
                    <span style={{ color: '#8b92a9', marginLeft: 4 }}>{col.type}</span>
                  </span>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
