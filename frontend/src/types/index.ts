export interface DBConfig {
  db_type: string
  host: string
  port: number
  username: string
  password: string
  database: string
}

export interface Metric {
  title: string
  value: string | number
  change?: string
  isPositive?: boolean
}

export interface ChartConfig {
  type: 'bar' | 'line' | 'pie' | 'doughnut'
  data: any
  options?: any
}

export interface QueryResult {
  // v2 fields — always present
  mode: 'chat' | 'sql' | 'rag' | 'hybrid'
  answer: string | null
  // SQL fields — present only in sql/hybrid mode
  sql_query: string | null
  columns: string[] | null
  data: Record<string, any>[] | null
  total_rows: number | null
  metrics: Metric[] | null
  chart_config: ChartConfig | null
  insights: string[] | null
  suggestions: string[] | null
}

