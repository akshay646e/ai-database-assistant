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
  sql: string
  columns: string[]
  data: any[]
  total_rows: number
  metrics: Metric[]
  chart: ChartConfig | null
  insights: string[]
  suggestions: string[]
}
