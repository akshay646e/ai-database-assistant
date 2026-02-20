'use client'
import { useState, useRef } from 'react'
import type { DBConfig } from '@/types'

type Props = {
  dbConfig: DBConfig
  onUploadSuccess: (tableName: string) => void
}

export default function FileUpload({ dbConfig, onUploadSuccess }: Props) {
  const [uploading, setUploading] = useState(false)
  const [message, setMessage] = useState('')
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    setUploading(true)
    setMessage('')

    const formData = new FormData()
    formData.append('file', file)
    formData.append('db_config', JSON.stringify(dbConfig))

    try {
      const res = await fetch('http://localhost:8001/api/upload', {
        method: 'POST',
        body: formData,
      })
      const json = await res.json()
      
      if (!res.ok) throw new Error(json.detail || 'Upload failed')
      
      setMessage(`✅ Success! Table: ${json.table}`)
      onUploadSuccess(json.table)
      
      // Clear message after 3 seconds
      setTimeout(() => setMessage(''), 3000)
    } catch (err: any) {
      setMessage(`❌ Error: ${err.message}`)
    } finally {
      setUploading(false)
      if (fileInputRef.current) fileInputRef.current.value = ''
    }
  }

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        style={{ display: 'none' }}
        accept=".csv,.xlsx,.xls,.pdf,.docx"
      />
      
      <button
        onClick={() => fileInputRef.current?.click()}
        disabled={uploading}
        style={{
          padding: '8px 16px',
          background: '#6c47ff',
          color: 'white',
          border: 'none',
          borderRadius: 8,
          fontSize: 13,
          fontWeight: 600,
          cursor: uploading ? 'not-allowed' : 'pointer',
          display: 'flex', alignItems: 'center', gap: 6,
          opacity: uploading ? 0.7 : 1,
          transition: 'all 0.2s',
        }}
      >
        {uploading ? (
          <>
            <span style={{ width: 12, height: 12, border: '2px solid rgba(255,255,255,0.3)', borderTopColor: '#fff', borderRadius: '50%', display: 'inline-block', animation: 'spin 0.7s linear infinite' }} />
            Uploading...
          </>
        ) : (
          <>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
              <polyline points="17 8 12 3 7 8" />
              <line x1="12" y1="3" x2="12" y2="15" />
            </svg>
            Upload Data
          </>
        )}
      </button>

      {message && (
        <div style={{
          fontSize: 12,
          color: message.startsWith('✅') ? '#16a34a' : '#dc2626',
          fontWeight: 500,
          animation: 'fadeIn 0.3s ease',
        }}>
          {message}
        </div>
      )}
      <style>{`@keyframes fadeIn { from { opacity: 0; transform: translateY(-5px); } to { opacity: 1; transform: translateY(0); } }`}</style>
    </div>
  )
}
