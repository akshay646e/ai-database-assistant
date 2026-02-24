'use client'
import { useState } from 'react'
import type { DBConfig, QueryResult } from '@/types'
import ConnectPage from '@/components/ConnectPage'
import DashboardPage from '@/components/DashboardPage'

export default function Home() {
  const [config, setConfig] = useState<DBConfig | null>(null)
  const [schema, setSchema] = useState<any>(null)

  // State managed by DashboardPage now for continuous chat

  const handleConnected = (cfg: DBConfig, s: any) => {
    setConfig(cfg)
    setSchema(s)
  }

  const handleDisconnect = () => {
    setConfig(null)
    setSchema(null)
  }

  const refreshSchema = async () => {
    if (!config) return
    try {
      const res = await fetch('http://localhost:8000/api/schema', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config),
      })
      const json = await res.json()
      if (res.ok) setSchema(json.schema)
    } catch (e) {
      console.error(e)
    }
  }

  const handleQuery = async (question: string) => {
    if (!config) throw new Error("No config");

    const res = await fetch('http://localhost:8000/api/query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        db_config: config,
        question
      })
    })
    const json = await res.json()
    if (!res.ok) throw new Error(json.detail || 'Query failed')
    return json;
  }

  if (!config) {
    return <ConnectPage onConnected={handleConnected} />
  }

  return (
    <DashboardPage
      dbConfig={config}
      schema={schema}
      onQuery={handleQuery}
      onDisconnect={handleDisconnect}
      onRefreshSchema={refreshSchema}
    />
  )
}




