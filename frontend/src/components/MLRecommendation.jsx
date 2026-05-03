import { Trophy, TrendingUp, AlertTriangle, CheckCircle, XCircle } from 'lucide-react';

const formatName = (name) => name?.replace('_', ' ').replace(/\b\w/g, c => c.toUpperCase());

export default function MLRecommendation({ analysis }) {
  if (!analysis) {
    return (
      <div className="card text-center" style={{ padding: 'var(--space-2xl) var(--space-lg)', color: 'var(--text-muted)' }}>
        Run an experiment to see ML-based recommendations.
      </div>
    );
  }

  const { rankings, best_architecture, recommendation_details } = analysis;
  const bestArch = recommendation_details?.best_arch;
  const worstArch = recommendation_details?.worst_arch;
  const bestData = rankings?.find(r => r.architecture === bestArch);
  const worstData = rankings?.find(r => r.architecture === worstArch);

  return (
    <div className="section-stack">

      {/* Recommendation Header */}
      <div className="card" style={{ background: 'var(--success-bg)', borderColor: '#a7f3d0', padding: 'var(--space-lg)' }}>
        <div className="flex items-start" style={{ gap: 'var(--space-md)' }}>
          <div className="flex items-center justify-center rounded-xl shrink-0"
            style={{ width: 48, height: 48, background: 'var(--success)' }}>
            <Trophy size={22} color="white" />
          </div>
          <div>
            <h3 className="font-bold" style={{ color: 'var(--success)', fontSize: 18, marginBottom: 4 }}>
              Algorithm Recommended: {formatName(best_architecture)}
            </h3>
            <p className="text-sm font-medium" style={{ color: 'var(--text-secondary)' }}>
              Based on your selected priorities, {formatName(best_architecture)} achieved the highest composite score
              ({bestData?.composite_score}/100) with a {bestData?.confidence}% ML confidence rating.
            </p>
          </div>
        </div>
      </div>

      {/* Why / Why Not Section */}
      {recommendation_details && (
        <div className="card-grid-2">
          <div className="card" style={{ padding: 'var(--space-lg)', borderLeft: '4px solid #16a34a' }}>
            <h3 className="font-bold text-sm mb-4" style={{ color: '#16a34a', display: 'flex', alignItems: 'center', gap: 8 }}>
              <CheckCircle size={16} /> Why Recommended ({formatName(bestArch)})
            </h3>
            <ul className="text-sm space-y-2" style={{ color: 'var(--text-secondary)' }}>
              {recommendation_details.why_recommended?.map((reason, i) => (
                <li key={i} style={{ display: 'flex', gap: 8 }}>
                  <span style={{ color: '#16a34a' }}>•</span> {reason}
                </li>
              ))}
              {(!recommendation_details.why_recommended || recommendation_details.why_recommended.length === 0) && (
                <li>Strongest overall performance across selected metrics.</li>
              )}
            </ul>
          </div>

          <div className="card" style={{ padding: 'var(--space-lg)', borderLeft: '4px solid #dc2626' }}>
            <h3 className="font-bold text-sm mb-4" style={{ color: '#dc2626', display: 'flex', alignItems: 'center', gap: 8 }}>
              <XCircle size={16} /> Why Not Recommended ({formatName(worstArch)})
            </h3>
            <ul className="text-sm space-y-2" style={{ color: 'var(--text-secondary)' }}>
              {recommendation_details.why_not_recommended?.map((reason, i) => (
                <li key={i} style={{ display: 'flex', gap: 8 }}>
                  <span style={{ color: '#dc2626' }}>•</span> {reason}
                </li>
              ))}
              {(!recommendation_details.why_not_recommended || recommendation_details.why_not_recommended.length === 0) && (
                <li>Lowest overall performance across selected metrics.</li>
              )}
            </ul>
          </div>
        </div>
      )}

      {/* Final Ranking Board */}
      <div className="card" style={{ padding: 'var(--space-lg)' }}>
        <h3 className="font-bold text-sm mb-4" style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
          <TrendingUp size={16} className="accent-text" />
          Final Architecture Ranking Board
        </h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {rankings?.map((r, idx) => (
            <div key={r.architecture} className="flex justify-between items-center rounded-lg border" style={{ background: 'var(--bg-muted)', padding: '12px' }}>

              <div className="flex items-center gap-4">
                <div className="flex items-center justify-center font-bold text-white rounded-md flex-shrink-0"
                  style={{ width: 32, height: 32, background: idx === 0 ? 'var(--accent)' : 'var(--text-muted)' }}>
                  #{r.rank}
                </div>
                <div>
                  <p className="font-bold text-sm">{formatName(r.architecture)}</p>
                  <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
                    Quality: {r.quality_score} &middot; Speed: {r.speed_score} &middot; Maint: {r.maintainability_score}
                  </p>
                </div>
              </div>

              <div className="text-right flex flex-col items-end gap-1">
                <span className="font-bold text-sm" style={{ color: 'var(--accent)' }}>Score: {r.composite_score}</span>
                <span className="text-xs font-medium rounded-full" style={{ padding: '2px 8px', background: 'var(--accent-bg)', color: 'var(--accent)' }}>
                  ML Conf: {r.confidence}%
                </span>
              </div>

            </div>
          ))}
        </div>
      </div>

      {/* Strengths & Weaknesses Breakdown */}
      <div className="card" style={{ padding: 'var(--space-lg)' }}>
        <h3 className="font-bold text-sm mb-4" style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
          <AlertTriangle size={16} className="accent-text" />
          Academic Profile Breakdown
        </h3>
        <div className="card-grid-3">
          {rankings?.map((r) => (
            <div key={r.architecture} className="border rounded-lg" style={{ padding: '16px', background: 'var(--bg-muted)' }}>
              <h4 className="font-bold text-sm mb-2">{formatName(r.architecture)}</h4>

              <p className="text-xs font-bold" style={{ color: 'var(--success)', marginTop: 8, marginBottom: 4 }}>Strengths:</p>
              <ul className="text-xs list-disc" style={{ color: 'var(--text-secondary)', paddingLeft: 16, display: 'flex', flexDirection: 'column', gap: 4 }}>
                {r.strengths?.map((s, i) => <li key={i}>{s}</li>)}
                {(!r.strengths || r.strengths.length === 0) && <li>Standard architectural pattern.</li>}
              </ul>

              <p className="text-xs font-bold" style={{ color: 'var(--danger)', marginTop: 12, marginBottom: 4 }}>Weaknesses:</p>
              <ul className="text-xs list-disc" style={{ color: 'var(--text-secondary)', paddingLeft: 16, display: 'flex', flexDirection: 'column', gap: 4 }}>
                {r.weaknesses?.map((w, i) => <li key={i}>{w}</li>)}
                {(!r.weaknesses || r.weaknesses.length === 0) && <li>No specific weaknesses listed.</li>}
              </ul>
            </div>
          ))}
        </div>
      </div>

    </div>
  );
}
