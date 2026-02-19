export default function BrandHeader() {
  return (
    <div
      style={{
        background: '#fff',
        borderBottom: '1px solid #e2e6f0',
        padding: '16px 32px',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: '6px',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
        <div
          style={{
            width: 52,
            height: 52,
            background: '#1a1d2e',
            borderRadius: 14,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: 26,
            fontWeight: 700,
            color: '#fff',
            fontStyle: 'italic',
            fontFamily: 'Georgia, serif',
            flexShrink: 0,
          }}
        >
          b
        </div>
        <div>
          <div style={{ fontSize: 22, fontWeight: 700, color: '#1a1d2e', lineHeight: 1.1 }}>
            The Baap Company
          </div>
          <div style={{ fontSize: 12, color: '#8b92a9' }}>Business Applications and Platforms</div>
        </div>
      </div>
    </div>
  )
}
