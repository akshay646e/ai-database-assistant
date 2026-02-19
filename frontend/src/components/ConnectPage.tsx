'use client'
import { useState } from 'react'
import BrandHeader from './BrandHeader'
import type { DBConfig } from '@/types'

type Props = {
  onConnected: (config: DBConfig, schema: any) => void
}

export default function ConnectPage({ onConnected }: Props) {
  const [form, setForm] = useState<DBConfig>({
    db_type: 'mysql',
    host: 'localhost',
    port: 3306,
    username: 'root',
    password: '',
    database: '',
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [backendStatus, setBackendStatus] = useState<'unknown' | 'ok' | 'down'>('unknown')

  const set = (key: keyof DBConfig, value: any) =>
    setForm(f => ({ ...f, [key]: value }))

  const handleDriverChange = (driver: string) => {
    set('db_type', driver)
    set('port', driver === 'postgresql' ? 5432 : 3306)
  }

  const checkBackend = async () => {
    try {
      const res = await fetch('http://localhost:8001/')
      if (res.ok) { setBackendStatus('ok'); setError('') }
      else setBackendStatus('down')
    } catch {
      setBackendStatus('down')
      setError('Backend is not running! See instructions below.')
    }
  }

  const connect = async () => {
    if (!form.database.trim()) { setError('Database Name is required'); return }
    setLoading(true)
    setError('')
    try {
      const res = await fetch('http://localhost:8001/api/connect', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      })
      const json = await res.json()
      if (!res.ok) throw new Error(json.detail || 'Connection failed')
      onConnected(form, json.schema)
    } catch (e: any) {
      if (e.message === 'Failed to fetch' || e.name === 'TypeError') {
        setBackendStatus('down')
        setError('BACKEND NOT RUNNING!\n\nOpen a NEW terminal window and run these commands one by one:\n\n  1.  cd backend\n  2.  venv\\Scripts\\activate\n  3.  uvicorn main:app --reload --port 8001\n\nKeep that terminal open, then try connecting again.')
      } else {
        setError(e.message)
      }
    } finally {
      setLoading(false)
    }
  }

  const inp: React.CSSProperties = {
    width: '100%', padding: '10px 14px',
    border: '1.5px solid #e2e6f0', borderRadius: 10,
    fontSize: 14, fontFamily: 'inherit',
    color: '#1a1d2e', background: '#fff',
    transition: 'border-color 0.2s, box-shadow 0.2s',
  }

  return (
    <div style={{ minHeight: '100vh', background: 'linear-gradient(145deg,#eef1f8,#e4e8f5)', display: 'flex', flexDirection: 'column' }}>
      <div style={{ height: 8, background: '#1a1d2e' }} />
      <BrandHeader />

      <div style={{ textAlign: 'center', margin: '30px 0 12px' }}>
        <h2 style={{ fontSize: 28, fontWeight: 700, color: '#1a1d2e' }}>Database Analytics</h2>
        <p style={{ fontSize: 14, color: '#8b92a9', marginTop: 6 }}>Connect to your database to unlock powerful insights</p>
      </div>

      {/* Backend status button */}
      <div style={{ display: 'flex', justifyContent: 'center', marginBottom: 16 }}>
        <button onClick={checkBackend} style={{
          padding: '7px 18px', borderRadius: 8, cursor: 'pointer', fontFamily: 'inherit',
          fontSize: 13, display: 'flex', alignItems: 'center', gap: 7,
          border: `1.5px solid ${backendStatus === 'ok' ? '#86efac' : backendStatus === 'down' ? '#fca5a5' : '#e2e6f0'}`,
          background: backendStatus === 'ok' ? '#f0fdf4' : backendStatus === 'down' ? '#fef2f2' : '#fff',
          color: backendStatus === 'ok' ? '#16a34a' : backendStatus === 'down' ? '#dc2626' : '#5a6075',
        }}>
          {backendStatus === 'ok' ? '✅ Backend is running!' : backendStatus === 'down' ? '❌ Backend not found' : '🔍 Check if backend is running'}
        </button>
      </div>

      <div style={{ display: 'flex', justifyContent: 'center', padding: '0 20px 40px' }}>
        <div style={{ background: '#fff', borderRadius: 20, padding: 32, width: '100%', maxWidth: 500, boxShadow: '0 4px 24px rgba(0,0,0,0.09)' }}>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 16 }}>
            <div>
              <label style={lbl}>Database Driver</label>
              <select value={form.db_type} onChange={e => handleDriverChange(e.target.value)}
                style={{ ...inp, appearance: 'none', cursor: 'pointer' }}>
                <option value="mysql">mysql</option>
                <option value="postgresql">postgresql</option>
              </select>
            </div>
            <div>
              <label style={lbl}>Port</label>
              <input type="number" value={form.port}
                onChange={e => set('port', parseInt(e.target.value) || 3306)} style={inp} />
            </div>
          </div>

          <div style={{ marginBottom: 16 }}>
            <label style={lbl}>Host/Server</label>
            <input type="text" value={form.host} onChange={e => set('host', e.target.value)}
              placeholder="localhost" style={inp} />
          </div>

          <div style={{ marginBottom: 16 }}>
            <label style={lbl}>Database Name</label>
            <input type="text" value={form.database} onChange={e => set('database', e.target.value)}
              placeholder="e.g. analytics_db" autoFocus
              onKeyDown={e => e.key === 'Enter' && connect()}
              style={{ ...inp, borderColor: form.database ? '#6c47ff' : '#e2e6f0' }} />
          </div>

          <div style={{ marginBottom: 16 }}>
            <label style={lbl}>Username</label>
            <input type="text" value={form.username} onChange={e => set('username', e.target.value)}
              placeholder="root" style={inp} />
          </div>

          <div style={{ marginBottom: 16 }}>
            <label style={lbl}>Password</label>
            <input type="password" value={form.password} onChange={e => set('password', e.target.value)}
              placeholder="Enter password" style={inp} />
          </div>

          {/* Error message */}
          {error && (
            <div style={{
              padding: '12px 14px', background: '#fef2f2',
              border: '1px solid #fca5a5', borderRadius: 10,
              color: '#dc2626', fontSize: 13, marginBottom: 16,
              whiteSpace: 'pre-line', lineHeight: 1.8,
              fontFamily: error.includes('cd backend') ? "'JetBrains Mono', monospace" : 'inherit',
            }}>
              {error}
            </div>
          )}

          <button onClick={connect} disabled={loading} style={{
            width: '100%', padding: '14px',
            background: loading ? '#4a3a8a' : '#2d1f6e',
            color: '#fff', border: 'none', borderRadius: 12,
            fontSize: 15, fontWeight: 600, fontFamily: 'inherit',
            cursor: loading ? 'not-allowed' : 'pointer',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            gap: 8, marginTop: 4, transition: 'background 0.2s',
          }}>
            {loading ? (
              <>
                <span style={{ width: 18, height: 18, border: '2px solid rgba(255,255,255,0.3)', borderTopColor: '#fff', borderRadius: '50%', display: 'inline-block', animation: 'spin 0.7s linear infinite' }} />
                Connecting...
              </>
            ) : (
              <>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <rect x="2" y="3" width="20" height="14" rx="2" /><path d="M8 21h8M12 17v4" />
                </svg>
                Connect to Database
              </>
            )}
          </button>
        </div>
      </div>
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  )
}

const lbl: React.CSSProperties = {
  display: 'block', fontSize: 13, fontWeight: 500, color: '#5a6075', marginBottom: 7,
}
