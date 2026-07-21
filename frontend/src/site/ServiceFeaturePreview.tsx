type ServiceFeaturePreviewProps = { code: string; title: string; step?: number };

const bars = [42, 68, 51, 83, 62, 91, 72];

export function ServiceFeaturePreview({ code, title, step = 1 }: ServiceFeaturePreviewProps) {
  const normalized = code.toUpperCase();
  const variant = normalized.includes("BASKET") ? "basket" : normalized.includes("CHURN") ? "churn" : normalized.includes("CLV") ? "clv" : normalized.includes("PROPENSITY") ? "propensity" : normalized.includes("ANOMALY") ? "anomaly" : "rfm";
  return <div className={`service-preview preview-${variant}`} aria-label={`${title} dashboard preview`}>
    <header><div><i /><i /><i /></div><span>{title}</span><b>Live report</b></header>
    <div className="service-preview-body">
      <aside><strong>InsightFlow</strong>{["Overview","Segments","Customers","Reports"].map((label,index)=><span className={index === (step - 1) % 4 ? "active" : ""} key={label}>{label}</span>)}</aside>
      <div className="service-preview-main">
        <div className="preview-metrics"><article><span>Customers</span><strong>{(12480 + step * 327).toLocaleString()}</strong><small>+12.4%</small></article><article><span>Confidence</span><strong>{88 + step}.2%</strong><small>Updated now</small></article><article><span>Actions</span><strong>{36 + step * 4}</strong><small>Ready</small></article></div>
        <div className="preview-workspace">
          {variant === "basket" && <div className="preview-basket">{[["Running shoes","Sports socks","3.4×"],["Coffee","Oat milk","2.8×"],["Phone","Protective case","2.5×"]].map(row=><div key={row[0]}><span>{row[0]}</span><b>→</b><span>{row[1]}</span><strong>{row[2]}</strong></div>)}</div>}
          {variant === "rfm" && <div className="preview-segments"><div className="segment-cloud">{Array.from({length:26},(_,index)=><i key={index} style={{left:`${8+(index*31)%84}%`,top:`${9+(index*47)%78}%`}} />)}</div><ul><li><i/>Champions <b>24%</b></li><li><i/>Loyal <b>31%</b></li><li><i/>At risk <b>18%</b></li></ul></div>}
          {(variant === "clv" || variant === "propensity") && <div className="preview-bars">{bars.map((height,index)=><i key={index} style={{height:`${Math.max(24,height-step*2+(index%2)*7)}%`}} />)}</div>}
          {(variant === "churn" || variant === "anomaly") && <div className="preview-line"><svg viewBox="0 0 600 220" preserveAspectRatio="none"><path d="M0 170 C70 155 95 182 155 138 S245 80 300 125 S390 176 440 72 S520 92 600 35"/><circle cx="440" cy="72" r="7"/></svg><div><span>Risk detected</span><strong>{variant === "churn" ? "High-value customers" : "Unusual sales spike"}</strong></div></div>}
        </div>
      </div>
    </div>
  </div>;
}
