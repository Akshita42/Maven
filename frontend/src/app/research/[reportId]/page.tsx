'use client';

import { useEffect, useState, use } from 'react';
import { CheckCircle2, AlertTriangle, Target, Clock, Code, BookOpen, Shield, TrendingUp, BarChart3, Users, LineChart, FileText } from 'lucide-react';
import Link from 'next/link';
import { motion } from 'framer-motion';

export default function ReportPage({ params }: { params: Promise<{ reportId: string }> }) {
  const resolvedParams = use(params);
  const [report, setReport] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [devMode, setDevMode] = useState(false);

  useEffect(() => {
    async function fetchReport() {
      try {
        const response = await fetch(`http://localhost:8000/api/v1/report/${resolvedParams.reportId}`);
        if (!response.ok) {
          throw new Error('Report not found');
        }
        const data = await response.json();
        setReport(data.data);
      } catch (err: any) {
        setError(err.message || 'Failed to load report');
      } finally {
        setLoading(false);
      }
    }
    fetchReport();
  }, [resolvedParams.reportId]);

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center bg-[var(--color-maven-bg)]">
        <div className="text-[var(--color-maven-gray-400)] animate-pulse">Loading comprehensive research...</div>
      </div>
    );
  }

  if (error || !report) {
    return (
      <div className="flex flex-col h-screen items-center justify-center bg-[var(--color-maven-bg)] gap-4">
        <div className="text-[var(--color-maven-primary)]">{error || 'Report not found'}</div>
        <Link href="/research" className="text-white bg-white/10 px-4 py-2 rounded-md hover:bg-white/20">
          Back to Research
        </Link>
      </div>
    );
  }

  const { executiveSummary, companyOverview, recommendation, intelligence, committee, critique, evidence } = report;

  let stanceColor = "text-[var(--color-maven-gray-400)] border-[var(--color-maven-gray-500)] bg-white/5";
  if (recommendation.stance === "BUY" || recommendation.stance === "STRONG_BUY") stanceColor = "text-emerald-400 border-emerald-500/30 bg-emerald-500/10";
  if (recommendation.stance === "SELL" || recommendation.stance === "STRONG_SELL") stanceColor = "text-[var(--color-maven-primary)] border-[var(--color-maven-primary)]/30 bg-[var(--color-maven-primary)]/10";

  const traceMetrics: any[] = [];
  const investDecision =
  recommendation.stance === "BUY" || recommendation.stance === "STRONG_BUY"
    ? "INVEST"
    : "PASS";

  const topReasons =
  recommendation.keyPositives?.slice(0, 3) || [];

  const biggestConcern =
  recommendation.keyRisks?.[0] || "No significant concerns identified.";
  if (evidence?.financials?.value?.annualDerivedMetrics?.[0]?.metrics) {
    const finMetrics = evidence.financials.value.annualDerivedMetrics[0].metrics;
    if (finMetrics.revenueGrowthYoY && finMetrics.revenueGrowthYoY.value !== undefined) traceMetrics.push({ name: "Revenue Growth YoY", value: (finMetrics.revenueGrowthYoY.value * 100).toFixed(2) + '%', metadata: finMetrics.revenueGrowthYoY.provenance });
    if (finMetrics.operatingMargin && finMetrics.operatingMargin.value !== undefined) traceMetrics.push({ name: "Operating Margin", value: (finMetrics.operatingMargin.value * 100).toFixed(2) + '%', metadata: finMetrics.operatingMargin.provenance });
    if (finMetrics.returnOnEquity && finMetrics.returnOnEquity.value !== undefined) traceMetrics.push({ name: "Return on Equity", value: (finMetrics.returnOnEquity.value * 100).toFixed(2) + '%', metadata: finMetrics.returnOnEquity.provenance });
    if (finMetrics.debtToEquity && finMetrics.debtToEquity.value !== undefined) traceMetrics.push({ name: "Debt to Equity", value: finMetrics.debtToEquity.value.toFixed(2), metadata: finMetrics.debtToEquity.provenance });
  }
  if (evidence?.marketData?.currentPrice && evidence.marketData.currentPrice.value !== undefined) traceMetrics.push({ name: "Current Price", value: "$" + evidence.marketData.currentPrice.value.toFixed(2), metadata: evidence.marketData.currentPrice.provenance });
  if (evidence?.marketData?.marketCap && evidence.marketData.marketCap.value !== undefined) traceMetrics.push({ name: "Market Cap", value: "$" + (evidence.marketData.marketCap.value / 1e9).toFixed(2) + "B", metadata: evidence.marketData.marketCap.provenance });
  return (
    <div className="min-h-screen bg-[var(--color-maven-bg)] text-white">
      {/* Top Nav */}
      <div className="sticky top-0 z-50 bg-[var(--color-maven-bg)]/80 backdrop-blur-lg border-b border-white/5 px-8 py-4 flex justify-between items-center">
        <Link href="/research" className="text-[var(--color-maven-gray-400)] hover:text-white transition-colors text-sm font-medium flex items-center gap-2">
          ← Back to Research
        </Link>
        <button 
          onClick={() => setDevMode(!devMode)}
          className={`flex items-center gap-2 px-3 py-1.5 rounded-md text-xs font-medium transition-colors border ${devMode ? 'bg-white/10 border-white/20 text-white' : 'border-transparent text-[var(--color-maven-gray-500)] hover:bg-white/5'}`}
        >
          <Code size={14} /> Developer Mode
        </button>
      </div>

      <div className="max-w-5xl mx-auto p-8 space-y-12">
        
        {/* Header */}
        <div className="flex flex-col md:flex-row justify-between items-start gap-8">
          <div>
            <h1 className="text-4xl md:text-5xl font-bold tracking-tight mb-3">
              {companyOverview.companyName || companyOverview.ticker} 
              {companyOverview.companyName && <span className="text-[var(--color-maven-gray-500)] font-normal ml-3">({companyOverview.ticker})</span>}
            </h1>
            <div className="flex flex-wrap items-center gap-4 text-sm text-[var(--color-maven-gray-400)]">
              <span>Report compiled on {new Date(report.meta.compiledAt).toLocaleDateString()}</span>
              <span>•</span>
              <span className="flex items-center gap-1"><BookOpen size={14} /> Professional Equity Research</span>
            </div>
          </div>
          <div className={`px-8 py-5 rounded-2xl border ${stanceColor} text-center min-w-[200px] shadow-2xl`}>
            <div className="text-xs uppercase tracking-widest opacity-80 mb-2 font-semibold">Research Recommendation</div>
            <div className="text-3xl font-bold">{recommendation.stance.replace('_', ' ')}</div>
            <div className="mt-2 text-sm opacity-90">{recommendation.investmentOutlook}</div>
          </div>
        </div>
         {/* Investment Decision */}
<section className="space-y-8">

  <div className="space-y-2">
    <p className="text-xs uppercase tracking-[0.2em] text-[var(--color-maven-gray-500)]">
      Should you invest today?
    </p>

    <h2
      className={`text-5xl font-bold ${
        investDecision === "INVEST"
          ? "text-emerald-400"
          : "text-yellow-400"
      }`}
    >
      {investDecision}
    </h2>

    <p className="text-sm text-[var(--color-maven-gray-500)]">
      Based on Maven's complete investment research pipeline.
    </p>
  </div>

  <div className="max-w-4xl">
    <p className="text-xs uppercase tracking-[0.2em] text-[var(--color-maven-gray-500)] mb-3">
      Investment Summary
    </p>

    <p className="text-lg leading-8 text-[var(--color-maven-gray-300)]">
      {recommendation.committeeReasons?.[0] ??
        "No investment summary available."}
    </p>
  </div>

  <div className="grid grid-cols-1 lg:grid-cols-2 gap-10">

    <div>

      <p className="text-xs uppercase tracking-[0.2em] text-[var(--color-maven-gray-500)] mb-4">
        Top Reasons
      </p>

     <div className="space-y-3">
  {topReasons.length > 0 ? (
    topReasons.map((reason: string, index: number) => (
      <div key={index} className="flex items-start gap-3">
        <span className="text-emerald-400 mt-1">✓</span>
        <p className="text-[15px] text-[var(--color-maven-gray-300)] leading-relaxed">
          {reason}
        </p>
      </div>
    ))
  ) : (
    <p className="text-sm text-[var(--color-maven-gray-500)] italic">
      No significant strengths were identified from the available evidence.
    </p>
  )}
</div>

    </div>

    <div>

      <p className="text-xs uppercase tracking-[0.2em] text-[var(--color-maven-gray-500)] mb-4">
        Biggest Concern
      </p>

      <div className="flex items-start gap-3">
        <span className="text-yellow-400 mt-1">⚠</span>

        <p className="text-[15px] text-[var(--color-maven-gray-300)] leading-relaxed">
          {biggestConcern}
        </p>

      </div>

    </div>

  </div>

</section>
        {/* Quick Stats Row */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-[#110e0e] border border-white/5 rounded-2xl p-6">
            <Target className="text-[var(--color-maven-secondary)] mb-3" size={24} />
            <div className="text-xs uppercase tracking-wider text-[var(--color-maven-gray-500)] mb-1">Conviction</div>
            <div className="text-lg font-medium">{recommendation.conviction}</div>
          </div>
          <div className="bg-[#110e0e] border border-white/5 rounded-2xl p-6">
            <Clock className="text-[var(--color-maven-secondary)] mb-3" size={24} />
            <div className="text-xs uppercase tracking-wider text-[var(--color-maven-gray-500)] mb-1">Horizon</div>
            <div className="text-lg font-medium">{recommendation.horizon}</div>
          </div>
        </div>

        {/* Bull Case & Bear Case */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {recommendation.keyPositives && recommendation.keyPositives.length > 0 && (
            <div className="space-y-6">
              <h2 className="text-2xl font-semibold flex items-center gap-3">
                <CheckCircle2 className="text-emerald-500" /> Reasons to Invest
              </h2>
              <ul className="space-y-4">
                {recommendation.keyPositives.map((pos: string, i: number) => (
                  <li key={i} className="bg-emerald-500/5 border border-emerald-500/10 rounded-xl p-4 text-[15px] leading-relaxed text-[var(--color-maven-gray-300)] flex gap-3 items-start">
                    <span className="text-emerald-500 font-bold mt-0.5">+</span> {pos}
                  </li>
                ))}
              </ul>
            </div>
          )}
          
          {recommendation.keyRisks && recommendation.keyRisks.length > 0 && (
            <div className="space-y-6">
              <h2 className="text-2xl font-semibold flex items-center gap-3">
                <AlertTriangle className="text-[var(--color-maven-primary)]" /> Reasons to Pass
              </h2>
              <ul className="space-y-4">
                {recommendation.keyRisks.map((risk: string, i: number) => (
                  <li key={i} className="bg-[var(--color-maven-primary)]/5 border border-[var(--color-maven-primary)]/10 rounded-xl p-4 text-[15px] leading-relaxed text-[var(--color-maven-gray-300)] flex gap-3 items-start">
                    <span className="text-[var(--color-maven-primary)] font-bold mt-0.5">-</span> {risk}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* Investment Committee Transparency */}
        <div className="bg-[#110e0e] border border-white/5 rounded-[24px] p-8 md:p-10">
          <h2 className="text-2xl font-semibold mb-8 flex items-center gap-3">
            <Users className="text-[var(--color-maven-secondary)]" /> How Maven Reached This Decision
          </h2>
          <div className="grid grid-cols-1 gap-4 mb-8">
            {committee?.opinions && committee.opinions.length > 0 && committee.opinions.map((opinion: any, i: number) => {
              const opColor = opinion.recommendation === "SUPPORT" ? "text-emerald-400" : opinion.recommendation === "REJECT" ? "text-[var(--color-maven-primary)]" : "text-[var(--color-maven-gray-400)]";
              const pillarId = opinion.reviewerId || opinion.sourcePillarId || "Unknown";
              const displayName = typeof pillarId === 'string' ? pillarId.replace("intelligence-", "") : "Unknown";
              
              const primaryReason = opinion.supportingStatements?.[0] || opinion.concerns?.[0] || "Committee analysis completed.";
              
              return (
                <div key={i} className="bg-black/20 rounded-xl p-5 border border-white/5 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                  <div className="flex-1">
                    <div className="text-sm font-bold uppercase tracking-wider text-white mb-2">{displayName.replace(/_/g, " ")}</div>
                    <div className="text-sm text-[var(--color-maven-gray-400)]">
                      <span className="text-[var(--color-maven-gray-500)] mr-2">Reason:</span>
                      {primaryReason}
                    </div>
                  </div>
                  <div className={`text-xl font-bold ${opColor} px-4 py-2 rounded-lg bg-white/5 border border-white/10 shrink-0`}>
                    {opinion.recommendation === "SUPPORT" ? "BUY" : opinion.recommendation === "REJECT" ? "SELL" : "HOLD"}
                  </div>
                </div>
              );
            })}
          </div>
          
          {recommendation.committeeReasons && recommendation.committeeReasons.length > 0 && (
            <>
              <h3 className="text-sm font-semibold uppercase tracking-wider text-[var(--color-maven-gray-400)] mb-4">Final Reasoning</h3>
              <ul className="space-y-3 mb-8">
                {recommendation.committeeReasons.map((reason: string, i: number) => (
                  <li key={i} className="text-[15px] leading-relaxed text-[var(--color-maven-gray-300)] flex gap-3 items-start">
                    <span className="text-[var(--color-maven-gray-500)]">•</span> {reason}
                  </li>
                ))}
              </ul>
            </>
          )}
        </div>

        {/* Critique & Key Assumptions */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {critique?.actionableVulnerabilities?.invalidatingAssumptions?.length > 0 && (
            <div className="bg-[#110e0e] border border-white/5 rounded-2xl p-8">
              <h2 className="text-xl font-semibold mb-6 flex items-center gap-3">
                <Shield className="text-[var(--color-maven-gray-400)]" /> Key Assumptions
              </h2>
              <ul className="space-y-4">
                {critique.actionableVulnerabilities.invalidatingAssumptions.map((vuln: any, i: number) => (
                  <li key={i} className="text-sm text-[var(--color-maven-gray-400)] leading-relaxed border-l-2 border-[var(--color-maven-secondary)] pl-4">
                    {vuln.description}
                  </li>
                ))}
              </ul>
            </div>
          )}
          
          {recommendation.catalysts?.length > 0 && (
            <div className="bg-[#110e0e] border border-white/5 rounded-2xl p-8">
              <h2 className="text-xl font-semibold mb-6 flex items-center gap-3">
                <TrendingUp className="text-[var(--color-maven-gray-400)]" /> What could change this?
              </h2>
              <ul className="space-y-4">
                {recommendation.catalysts.map((cat: any, i: number) => (
                  <li key={i} className="text-sm text-[var(--color-maven-gray-400)] leading-relaxed border-l-2 border-[var(--color-maven-gray-600)] pl-4">
                    {cat.description}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* Evidence Trace */}
        {traceMetrics.length > 0 && (
          <div className="bg-[#110e0e] border border-white/5 rounded-[24px] p-8 md:p-10">
            <h2 className="text-2xl font-semibold mb-2 flex items-center gap-3">
              <BarChart3 className="text-[var(--color-maven-secondary)]" /> Evidence Used
            </h2>
            <p className="text-[var(--color-maven-gray-500)] mb-8 text-sm">These are the most important data points used to reach the investment decision.</p>
            
            <div className="space-y-6">
              {traceMetrics.map((metric: any, i: number) => (
                <div key={i} className="bg-black/20 rounded-xl p-5 border border-white/5 flex flex-col md:flex-row gap-6 md:items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-3">
                      <div className="text-xs px-2 py-1 bg-white/5 rounded border border-white/10 text-[var(--color-maven-gray-400)]">Source Data</div>
                      <div className="text-[var(--color-maven-gray-500)] text-xs">→</div>
                      <div className="text-xs px-2 py-1 bg-white/5 rounded border border-white/10 text-[var(--color-maven-gray-400)]">Analyzer</div>
                      <div className="text-[var(--color-maven-gray-500)] text-xs">→</div>
                      <div className="text-xs px-2 py-1 bg-emerald-500/10 rounded border border-emerald-500/20 text-emerald-400 font-bold">Conclusion</div>
                    </div>
                    <div className="font-medium text-white mb-1">{metric.name}</div>
                    <div className="text-2xl font-semibold text-[var(--color-maven-secondary)]">
                      {metric.value != null ? metric.value : 'N/A'}
                    </div>
                  </div>
                  <div className="md:text-right space-y-1 bg-[#110e0e] p-4 rounded-lg border border-white/5">
                    <div className="text-xs text-[var(--color-maven-gray-400)]"><span className="text-[var(--color-maven-gray-500)]">Source:</span> {metric.metadata?.provider || 'Yahoo Finance'}</div>
                    <div className="text-xs text-[var(--color-maven-gray-400)]"><span className="text-[var(--color-maven-gray-500)]">Retrieved:</span> {new Date(metric.metadata?.timestamp || report.meta.compiledAt).toLocaleDateString()}</div>
                    <div className="text-xs text-[var(--color-maven-gray-400)]"><span className="text-[var(--color-maven-gray-500)]">Confidence:</span> {(metric.metadata?.confidence * 100 || 100).toFixed(0)}%</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Developer Mode Raw Data */}
        {devMode && (
          <motion.div 
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            className="bg-black/80 border border-white/20 rounded-2xl p-8 overflow-hidden"
          >
            <h3 className="text-sm font-semibold mb-4 uppercase text-[var(--color-maven-primary)] tracking-widest flex items-center gap-2">
              <Code size={16} /> Developer Pipeline Artifacts
            </h3>
            <pre className="text-xs text-[var(--color-maven-gray-400)] overflow-x-auto bg-[#0a0a0a] p-6 rounded-lg font-mono leading-relaxed border border-white/5">
              {JSON.stringify(report, null, 2)}
            </pre>
          </motion.div>
        )}

      </div>
    </div>
  );
}
