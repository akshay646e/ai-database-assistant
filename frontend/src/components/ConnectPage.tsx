'use client'
import { useState, useRef } from 'react'
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
  
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [uploading, setUploading] = useState(false)

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

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    if (!form.database.trim()) {
      setError('Database Name is required to upload a file into it');
      return;
    }

    setUploading(true)
    setError('')

    const formData = new FormData()
    formData.append('file', file)
    formData.append('db_config', JSON.stringify(form))

    try {
      const res = await fetch('http://localhost:8001/api/upload', {
        method: 'POST',
        body: formData,
      })
      const json = await res.json()
      if (!res.ok) throw new Error(json.detail || 'Upload failed')

      // After upload, connect to the DB to fetch the updated schema
      const schemaRes = await fetch('http://localhost:8001/api/connect', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      })
      const schemaJson = await schemaRes.json()
      if (!schemaRes.ok) throw new Error(schemaJson.detail || 'Connection failed after upload')
      
      onConnected(form, schemaJson.schema)
    } catch (err: any) {
      if (err.message === 'Failed to fetch' || err.name === 'TypeError') {
        setBackendStatus('down')
        setError('BACKEND NOT RUNNING!\n\nPlease ensure your backend is running on port 8001.')
      } else {
        setError(err.message)
      }
    } finally {
      setUploading(false)
      if (fileInputRef.current) fileInputRef.current.value = ''
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

      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileUpload}
        style={{ display: 'none' }}
        accept=".csv,.xlsx,.xls,.pdf,.docx"
      />

      {/* Backend status and Top Upload button */}
      <div style={{ display: 'flex', justifyContent: 'center', marginBottom: 16, gap: 12 }}>
        <button onClick={checkBackend} style={{
          padding: '7px 18px', borderRadius: 8, cursor: 'pointer', fontFamily: 'inherit',
          fontSize: 13, display: 'flex', alignItems: 'center', gap: 7,
          border: `1.5px solid ${backendStatus === 'ok' ? '#86efac' : backendStatus === 'down' ? '#fca5a5' : '#e2e6f0'}`,
          background: backendStatus === 'ok' ? '#f0fdf4' : backendStatus === 'down' ? '#fef2f2' : '#fff',
          color: backendStatus === 'ok' ? '#16a34a' : backendStatus === 'down' ? '#dc2626' : '#5a6075',
        }}>
          {backendStatus === 'ok' ? '✅ Backend is running!' : backendStatus === 'down' ? '❌ Backend not found' : '🔍 Check if backend is running'}
        </button>

        <button onClick={() => fileInputRef.current?.click()} disabled={uploading || loading} style={{
          padding: '7px 18px', borderRadius: 8, cursor: uploading || loading ? 'not-allowed' : 'pointer', fontFamily: 'inherit',
          fontSize: 13, display: 'flex', alignItems: 'center', gap: 7,
          border: '1.5px solid #22c55e', background: '#f0fdf4', color: '#16a34a',
          fontWeight: 600, opacity: (uploading || loading) ? 0.7 : 1, transition: 'all 0.2s'
        }}>
          {uploading ? (
            <>
              <span style={{ width: 14, height: 14, border: '2px solid rgba(22,163,74,0.3)', borderTopColor: '#16a34a', borderRadius: '50%', display: 'inline-block', animation: 'spin 0.7s linear infinite' }} />
              Uploading...
            </>
          ) : (
            <>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                <polyline points="17 8 12 3 7 8" />
                <line x1="12" y1="3" x2="12" y2="15" />
              </svg>
              Upload CSV / Excel
            </>
          )}
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

          <button onClick={connect} disabled={loading || uploading} style={{
            width: '100%', padding: '14px',
            background: loading ? '#4a3a8a' : '#2d1f6e',
            color: '#fff', border: 'none', borderRadius: 12,
            fontSize: 15, fontWeight: 600, fontFamily: 'inherit',
            cursor: (loading || uploading) ? 'not-allowed' : 'pointer',
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

          <div style={{ display: 'flex', alignItems: 'center', margin: '20px 0', gap: 12 }}>
            <div style={{ flex: 1, height: 1, background: '#e2e6f0' }} />
            <span style={{ fontSize: 13, color: '#8b92a9', fontWeight: 500 }}>or use a file instead</span>
            <div style={{ flex: 1, height: 1, background: '#e2e6f0' }} />
          </div>

          <button onClick={() => fileInputRef.current?.click()} disabled={uploading || loading} style={{
            width: '100%', padding: '14px',
            background: '#fff',
            color: '#6c47ff', border: '1.5px solid #6c47ff', borderRadius: 12,
            fontSize: 15, fontWeight: 600, fontFamily: 'inherit',
            cursor: (uploading || loading) ? 'not-allowed' : 'pointer',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            gap: 8, transition: 'all 0.2s',
            opacity: (uploading || loading) ? 0.7 : 1
          }}>
            {uploading ? (
              <>
                <span style={{ width: 18, height: 18, border: '2px solid rgba(108,71,255,0.3)', borderTopColor: '#6c47ff', borderRadius: '50%', display: 'inline-block', animation: 'spin 0.7s linear infinite' }} />
                Uploading File...
              </>
            ) : (
              <>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                  <polyline points="17 8 12 3 7 8" />
                  <line x1="12" y1="3" x2="12" y2="15" />
                </svg>
                Upload CSV / Excel File
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
