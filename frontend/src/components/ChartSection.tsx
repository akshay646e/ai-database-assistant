'use client'
import { useState, useEffect, useRef } from 'react'
import {
  Chart as ChartJS,
  CategoryScale, LinearScale, BarElement,
  LineElement, PointElement, ArcElement,
  Title, Tooltip, Legend,
} from 'chart.js'
import { Bar, Line, Pie } from 'react-chartjs-2'

ChartJS.register(
  CategoryScale, LinearScale, BarElement,
  LineElement, PointElement, ArcElement,
  Title, Tooltip, Legend
)

const COLORS = [
  '#6c47ff','#22c55e','#3b82f6','#f97316','#a855f7',
  '#14b8a6','#f43f5e','#eab308','#0ea5e9','#8b5cf6',
  '#ec4899','#84cc16','#06b6d4','#f59e0b','#10b981',
]

type ChartType = 'bar' | 'line' | 'pie'

export default function ChartSection({ chart }: { chart: any }) {
  const [activeType, setActiveType] = useState<ChartType>('bar')

  useEffect(() => {
    if (chart?.chart_type) setActiveType(chart.chart_type as ChartType)
  }, [chart])

  if (!chart || !chart.labels?.length || !chart.datasets?.length) return null

  const dataset = chart.datasets[0]
  const barColors = chart.labels.map((_: any, i: number) => COLORS[i % COLORS.length])

  const chartData = {
    labels: chart.labels,
    datasets: [{
      ...dataset,
      backgroundColor: activeType === 'bar' || activeType === 'pie' ? barColors : 'rgba(108,71,255,0.15)',
      borderColor: activeType === 'line' ? '#6c47ff' : barColors,
      borderWidth: activeType === 'line' ? 2 : 0,
      borderRadius: activeType === 'bar' ? 6 : 0,
      hoverBackgroundColor: activeType === 'bar' || activeType === 'pie'
        ? barColors.map((c: string) => c + 'cc')
        : 'rgba(108,71,255,0.25)',
      tension: 0.4,
      fill: false,
      pointBackgroundColor: '#6c47ff',
      pointRadius: activeType === 'line' ? 4 : 0,
    }],
  }

  const commonOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: activeType === 'pie', position: 'right' as const },
      tooltip: {
        backgroundColor: '#fff',
        titleColor: '#1a1d2e',
        bodyColor: '#6c47ff',
        borderColor: '#e2e6f0',
        borderWidth: 1,
        padding: 12,
        cornerRadius: 10,
        callbacks: {
          label: (ctx: any) => `  value : ${ctx.raw}`,
        },
      },
    },
    scales: activeType === 'pie' ? {} : {
      x: {
        grid: { color: 'rgba(0,0,0,0.03)', drawBorder: false },
        ticks: { color: '#8b92a9', font: { size: 11 } },
        border: { display: false },
      },
      y: {
        grid: { color: 'rgba(0,0,0,0.04)', drawBorder: false },
        ticks: { color: '#8b92a9', font: { size: 11 } },
        beginAtZero: true,
        border: { display: false },
      },
    },
  }

  const btnStyle = (t: ChartType): React.CSSProperties => ({
    width: 34, height: 34, borderRadius: 8,
    border: `1.5px solid ${activeType === t ? '#6c47ff' : '#e2e6f0'}`,
    background: activeType === t ? '#6c47ff' : '#fff',
    color: activeType === t ? '#fff' : '#8b92a9',
    cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center',
    transition: 'all 0.2s',
  })

  return (
    <div style={{
      background: '#fff', borderRadius: 16, padding: '20px',
      boxShadow: '0 2px 12px rgba(0,0,0,0.06)', marginBottom: 24,
    }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <div style={{ width: 8, height: 8, borderRadius: '50%', background: '#22c55e' }} />
          <span style={{ fontSize: 14, fontWeight: 600, color: '#1a1d2e' }}>Data Visualizations</span>
        </div>
        <div style={{ display: 'flex', gap: 6 }}>
          {/* Bar */}
          <button onClick={() => setActiveType('bar')} style={btnStyle('bar')} title="Bar Chart">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
              <rect x="3" y="12" width="4" height="9" /><rect x="10" y="7" width="4" height="14" />
              <rect x="17" y="3" width="4" height="18" />
            </svg>
          </button>
          {/* Line */}
          <button onClick={() => setActiveType('line')} style={btnStyle('line')} title="Line Chart">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
            </svg>
          </button>
          {/* Pie */}
          <button onClick={() => setActiveType('pie')} style={btnStyle('pie')} title="Pie Chart">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21.21 15.89A10 10 0 118 2.83" /><path d="M22 12A10 10 0 0012 2v10z" />
            </svg>
          </button>
        </div>
      </div>

      {/* Chart */}
      <div style={{ height: 300, position: 'relative' }}>
        {activeType === 'bar' && <Bar data={chartData} options={commonOptions} />}
        {activeType === 'line' && <Line data={chartData} options={commonOptions} />}
        {activeType === 'pie' && <Pie data={chartData} options={{ ...commonOptions, scales: {} }} />}
      </div>
    </div>
  )
}
