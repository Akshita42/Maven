'use client';

import { useEffect, useState, use } from 'react';
import { CheckCircle2, AlertTriangle, Target, Clock, Code, BookOpen, Shield, TrendingUp, BarChart3, Users, LineChart, FileText, Database } from 'lucide-react';
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

  const investDecision = recommendation.stance.includes("BUY") ? "INVEST" : "PASS";
  const traceMetrics: any[] = [];

  const marketDataMetrics: any[] = [];
  const financialMetrics: any[] = [];
  const profileMetrics: any[] = [];
  
  if (evidence?.marketData) {
    const md = evidence.marketData;
    if (md.currentPrice?.value !== undefined) marketDataMetrics.push({ name: "Current Price", value: "$" + md.currentPrice.value.toFixed(2), source: md.currentPrice.provenance?.provider });
    if (md.marketCap?.value !== undefined) marketDataMetrics.push({ name: "Market Cap", value: "$" + (md.marketCap.value / 1e9).toFixed(2) + "B", source: md.marketCap.provenance?.provider });
    if (md.beta?.value !== undefined) marketDataMetrics.push({ name: "Beta", value: md.beta.value.toFixed(2), source: md.beta.provenance?.provider });
    if (md.fiftyTwoWeekHigh?.value !== undefined) marketDataMetrics.push({ name: "52 Week High", value: "$" + md.fiftyTwoWeekHigh.value.toFixed(2), source: md.fiftyTwoWeekHigh.provenance?.provider });
    if (md.fiftyTwoWeekLow?.value !== undefined) marketDataMetrics.push({ name: "52 Week Low", value: "$" + md.fiftyTwoWeekLow.value.toFixed(2), source: md.fiftyTwoWeekLow.provenance?.provider });
    if (md.volume?.value !== undefined) marketDataMetrics.push({ name: "Volume", value: (md.volume.value / 1e6).toFixed(2) + "M", source: md.volume.provenance?.provider });
  }

  if (evidence?.financials?.value?.annualDerivedMetrics?.[0]?.metrics) {
    const fin = evidence.financials.value.annualDerivedMetrics[0].metrics;
    if (fin.revenueGrowthYoY?.value !== undefined) financialMetrics.push({ name: "Revenue Growth (YoY)", value: (fin.revenueGrowthYoY.value * 100).toFixed(2) + "%", source: fin.revenueGrowthYoY.provenance?.provider });
    if (fin.operatingMargin?.value !== undefined) financialMetrics.push({ name: "Operating Margin", value: (fin.operatingMargin.value * 100).toFixed(2) + "%", source: fin.operatingMargin.provenance?.provider });
    if (fin.netMargin?.value !== undefined) financialMetrics.push({ name: "Net Margin", value: (fin.netMargin.value * 100).toFixed(2) + "%", source: fin.netMargin.provenance?.provider });
    if (fin.returnOnEquity?.value !== undefined) financialMetrics.push({ name: "Return on Equity", value: (fin.returnOnEquity.value * 100).toFixed(2) + "%", source: fin.returnOnEquity.provenance?.provider });
    if (fin.debtToEquity?.value !== undefined) financialMetrics.push({ name: "Debt to Equity", value: fin.debtToEquity.value.toFixed(2), source: fin.debtToEquity.provenance?.provider });
    if (fin.currentRatio?.value !== undefined) financialMetrics.push({ name: "Current Ratio", value: fin.currentRatio.value.toFixed(2), source: fin.currentRatio.provenance?.provider });
    if (fin.freeCashFlowMargin?.value !== undefined) financialMetrics.push({ name: "FCF Margin", value: (fin.freeCashFlowMargin.value * 100).toFixed(2) + "%", source: fin.freeCashFlowMargin.provenance?.provider });
  }

  if (evidence?.companyProfile) {
    const cp = evidence.companyProfile;
    if (cp.sector?.value !== undefined) profileMetrics.push({ name: "Sector", value: cp.sector.value, source: cp.sector.provenance?.provider || "Yahoo Finance" });
    if (cp.industry?.value !== undefined) profileMetrics.push({ name: "Industry", value: cp.industry.value, source: cp.industry.provenance?.provider || "Yahoo Finance" });
    if (cp.fullTimeEmployees?.value !== undefined) profileMetrics.push({ name: "Employees", value: cp.fullTimeEmployees.value.toLocaleString(), source: cp.fullTimeEmployees.provenance?.provider || "Yahoo Finance" });
  }
  
  const allEvidence = [
    { title: "Market Data", data: marketDataMetrics },
    { title: "Financial Metrics", data: financialMetrics },
    { title: "Company Profile", data: profileMetrics },
  ].filter(section => section.data.length > 0);
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

      <div className="w-full max-w-[1600px] mx-auto px-8 lg:px-12 xl:px-16 py-8 space-y-20 lg:space-y-28 pb-32">
        
        {/* 1. REPORT COVER (Header) */}
        <div className="flex flex-col xl:flex-row items-start xl:items-center justify-between gap-10 xl:gap-16 py-8 border-b border-white/10 w-full">
          {/* Left Side */}
          <div className="space-y-6 flex-shrink-0">
            <h1 className="text-5xl md:text-6xl lg:text-7xl font-extrabold tracking-tight">
              {companyOverview.companyName || companyOverview.ticker}
            </h1>
            <div className="flex flex-wrap items-center gap-4 text-sm text-[var(--color-maven-gray-400)] uppercase tracking-widest font-semibold">
              <span className="text-white bg-white/10 px-3 py-1.5 rounded-md">{companyOverview.ticker}</span>
              {companyOverview.sector && (
                <>
                  <span>•</span>
                  <span>{companyOverview.sector} {companyOverview.industry && `/ ${companyOverview.industry}`}</span>
                </>
              )}
              <span>•</span>
              <span>{new Date(report.meta.compiledAt).toLocaleDateString()}</span>
            </div>
          </div>

          {/* Right Side Cards */}
          <div className="flex flex-wrap gap-4 xl:justify-end xl:mt-0">
            <div className={`px-8 py-5 rounded-2xl border ${stanceColor} shadow-xl flex flex-col justify-center min-w-[200px]`}>
              <div className="text-xs uppercase tracking-[0.2em] opacity-80 mb-2 font-bold">Final Decision</div>
              <div className="text-4xl font-black tracking-tight">{investDecision}</div>
            </div>
            
            <div className="bg-white/5 border border-white/10 rounded-2xl p-6 shadow-xl flex flex-col justify-center text-center min-w-[140px]">
              <div className="text-xs uppercase tracking-wider text-[var(--color-maven-gray-500)] mb-2 font-semibold">Confidence</div>
              <div className="text-3xl font-bold text-[var(--color-maven-secondary)]">{(recommendation.confidenceScore * 100).toFixed(0)}%</div>
            </div>
          </div>
        </div>

        {/* 2. EXECUTIVE SUMMARY */}
        <section className="flex flex-col lg:flex-row gap-12 w-full">
          {/* Left Column (65%) */}
          <div className="lg:w-[65%] space-y-6">
            <h2 className="text-sm uppercase tracking-[0.2em] text-[var(--color-maven-gray-500)] font-bold">
              Executive Summary
            </h2>
            <div className="text-base md:text-lg leading-[1.7] text-gray-300 max-w-[85ch] space-y-6">
              {recommendation.committeeReasons?.flatMap((reason: string) => reason.split(/\n+/)).map((para: string, i: number) => (
                <p key={i}>{para.trim()}</p>
              )) ?? (
                <p>{executiveSummary ?? "No investment summary available."}</p>
              )}
            </div>
          </div>

          {/* Right Column (35%) */}
          <div className="lg:w-[35%] flex flex-col gap-4">
            <div className="bg-white/5 border border-white/10 rounded-2xl p-6 shadow-xl">
              <div className="flex items-center gap-3 mb-2">
                <Clock className="text-[var(--color-maven-secondary)]" size={24} />
                <div className="text-xs uppercase tracking-wider text-[var(--color-maven-gray-500)] font-semibold">Investment Horizon</div>
              </div>
              <div className="text-2xl font-bold mt-2">{recommendation.horizon}</div>
            </div>
            
            <div className="bg-white/5 border border-white/10 rounded-2xl p-6 shadow-xl">
              <div className="flex items-center gap-3 mb-2">
                <Target className="text-[var(--color-maven-secondary)]" size={24} />
                <div className="text-xs uppercase tracking-wider text-[var(--color-maven-gray-500)] font-semibold">Conviction</div>
              </div>
              <div className="text-2xl font-bold mt-2">{recommendation.conviction}</div>
            </div>
          </div>
        </section>

        <hr className="border-white/10" />

        {/* 3. DETAILED INVESTMENT CASE */}
        <section className="space-y-8 w-full">
          <h2 className="text-3xl font-bold tracking-tight">Detailed Investment Case</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
            {/* Bull Case */}
            <div className="space-y-6">
              <h3 className="text-xl font-semibold flex items-center gap-3 text-emerald-400">
                <CheckCircle2 /> Bull Case
              </h3>
              <div className="space-y-3">
                {recommendation.keyPositives && recommendation.keyPositives.length > 0 ? (
                  recommendation.keyPositives.map((pos: string, i: number) => (
                    <div key={i} className="bg-emerald-500/5 border border-emerald-500/10 rounded-xl p-4 text-[15px] leading-snug text-[var(--color-maven-gray-300)] flex gap-4 items-start">
                      <span className="text-emerald-500 font-bold mt-0.5">+</span> 
                      <p>{pos}</p>
                    </div>
                  ))
                ) : (
                  <p className="text-[var(--color-maven-gray-500)] italic text-sm">No significant strengths identified.</p>
                )}
              </div>
            </div>
            
            {/* Bear Case */}
            <div className="space-y-6">
              <h3 className="text-xl font-semibold flex items-center gap-3 text-yellow-400">
                <AlertTriangle /> Bear Case
              </h3>
              <div className="space-y-3">
                {recommendation.keyRisks && recommendation.keyRisks.length > 0 ? (
                  recommendation.keyRisks.map((risk: string, i: number) => (
                    <div key={i} className="bg-[var(--color-maven-primary)]/5 border border-[var(--color-maven-primary)]/10 rounded-xl p-4 text-[15px] leading-snug text-[var(--color-maven-gray-300)] flex gap-4 items-start">
                      <span className="text-[var(--color-maven-primary)] font-bold mt-0.5">-</span> 
                      <p>{risk}</p>
                    </div>
                  ))
                ) : (
                  <p className="text-[var(--color-maven-gray-500)] italic text-sm">No significant risks identified.</p>
                )}
              </div>
            </div>
          </div>
        </section>

        <hr className="border-white/10" />

        {/* 4. COMMITTEE SUMMARY & CATALYSTS */}
        <section className="grid grid-cols-1 lg:grid-cols-2 gap-10 w-full">
          {/* Committee Summary */}
          <div className="space-y-8">
            <h2 className="text-3xl font-bold tracking-tight">Committee Summary</h2>
            
            {recommendation.committeeReasons && recommendation.committeeReasons.length > 0 && (
              <div className="text-[17px] leading-relaxed text-[var(--color-maven-gray-300)] space-y-4 max-w-[85ch]">
                {recommendation.committeeReasons.map((reason: string, i: number) => (
                  <p key={i}>{reason}</p>
                ))}
              </div>
            )}

            <div className="bg-[#110e0e] border border-white/5 rounded-3xl overflow-hidden shadow-xl h-fit flex flex-col">
              <div className="overflow-x-auto flex-1">
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="bg-white/5 border-b border-white/10 text-[10px] uppercase tracking-widest text-[var(--color-maven-gray-500)]">
                      <th className="p-4 font-bold">Committee Member</th>
                      <th className="p-4 font-bold">Analysis Summary</th>
                      <th className="p-4 font-bold text-center">Vote</th>
                      <th className="p-4 font-bold text-center">Confidence</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/5">
                    {committee?.opinions && committee.opinions.length > 0 ? committee.opinions.map((opinion: any, i: number) => {
                      const opColor = opinion.recommendation === "SUPPORT" ? "text-emerald-400 bg-emerald-500/10" : opinion.recommendation === "REJECT" ? "text-[var(--color-maven-primary)] bg-[var(--color-maven-primary)]/10" : "text-[var(--color-maven-gray-400)] bg-white/5";
                      const pillarId = opinion.reviewerId || opinion.sourcePillarId || "Unknown";
                      const displayName = typeof pillarId === 'string' ? pillarId.replace("intelligence-", "").replace(/_/g, " ") : "Unknown";
                      const primaryReason = opinion.supportingStatements?.[0] || opinion.concerns?.[0] || "Committee analysis completed.";
                      const conf = opinion.confidenceScore ?? opinion.confidence;
                      const confDisplay = conf !== undefined ? (conf * 100).toFixed(0) + '%' : '--';
                      
                      return (
                        <tr key={i} className="hover:bg-white/[0.02] transition-colors">
                          <td className="p-4 text-xs font-bold uppercase tracking-widest text-white whitespace-nowrap">{displayName}</td>
                          <td className="p-4 text-[13px] text-[var(--color-maven-gray-300)] leading-snug min-w-[200px]">{primaryReason}</td>
                          <td className="p-4 text-center">
                            <span className={`text-xs font-bold px-3 py-1.5 rounded-lg ${opColor}`}>
                              {opinion.recommendation === "SUPPORT" ? "BUY" : opinion.recommendation === "REJECT" ? "SELL" : "HOLD"}
                            </span>
                          </td>
                          <td className="p-4 text-center text-sm font-semibold text-[var(--color-maven-secondary)]">{confDisplay}</td>
                        </tr>
                      );
                    }) : (
                      <tr>
                        <td colSpan={4} className="p-4 text-center text-sm text-[var(--color-maven-gray-500)] italic">No committee data available.</td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
              
            </div>
          </div>

          {/* What Could Change This */}
          <div className="space-y-8">
            <h2 className="text-3xl font-bold tracking-tight">What could change this?</h2>
            <div className="bg-[#110e0e] border border-white/5 rounded-3xl p-8 shadow-xl h-fit flex flex-col gap-8">
              {recommendation.catalysts?.length > 0 ? (
                <ul className="space-y-5 flex-1">
                  {recommendation.catalysts.map((cat: any, i: number) => (
                    <li key={i} className="text-[15px] text-[var(--color-maven-gray-400)] leading-snug border-l-2 border-[var(--color-maven-secondary)] pl-5">
                      {cat.description}
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-[var(--color-maven-gray-500)] italic text-sm flex-1">No specific catalysts identified.</p>
              )}
              
              {critique?.actionableVulnerabilities?.invalidatingAssumptions?.length > 0 && (
                <div className="pt-6 border-t border-white/10">
                  <h3 className="text-sm font-bold uppercase tracking-widest text-white mb-4 flex items-center gap-2">
                    <Shield size={16} className="text-[var(--color-maven-gray-400)]" /> Key Assumptions
                  </h3>
                  <ul className="space-y-3">
                    {critique.actionableVulnerabilities.invalidatingAssumptions.map((vuln: any, i: number) => (
                      <li key={i} className="text-sm text-[var(--color-maven-gray-400)] leading-relaxed">
                        • {vuln.description}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        </section>

        {traceMetrics.length > 0 && <hr className="border-white/10" />}

        {/* 5. EVIDENCE AUDIT TRACKER */}
        {allEvidence.length > 0 && (
          <section className="space-y-8 w-full border-t border-white/10 pt-16">
            <div className="flex flex-col gap-2">
              <h2 className="text-3xl font-bold tracking-tight">Evidence Audit & Data Room</h2>
              <p className="text-[var(--color-maven-gray-400)] text-[15px] max-w-[80ch]">
                Maven’s AI Committee relies strictly on deterministic data. The exact metrics and sources used to generate this report are fully logged below for transparency and verification.
              </p>
            </div>
            
            <div className="space-y-12">
              {allEvidence.map((section, idx) => (
                <div key={idx} className="space-y-6">
                  <h3 className="text-sm font-bold uppercase tracking-[0.2em] text-[var(--color-maven-secondary)] flex items-center gap-2">
                    <Database size={16} /> {section.title}
                  </h3>
                  <div className="bg-[#110e0e] border border-white/5 rounded-3xl overflow-hidden shadow-xl">
                    <table className="w-full text-left border-collapse">
                      <thead>
                        <tr className="bg-white/5 border-b border-white/10 text-[10px] uppercase tracking-widest text-[var(--color-maven-gray-500)]">
                          <th className="p-4 pl-6 font-bold w-1/3">Metric Name</th>
                          <th className="p-4 font-bold w-1/3">Value</th>
                          <th className="p-4 pr-6 font-bold w-1/3 text-right">Data Source</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-white/5">
                        {section.data.map((metric, i) => (
                          <tr key={i} className="hover:bg-white/[0.02] transition-colors">
                            <td className="p-4 pl-6 text-[13px] font-semibold text-[var(--color-maven-gray-300)] whitespace-nowrap">{metric.name}</td>
                            <td className="p-4 text-[14px] font-bold text-white">{metric.value != null ? metric.value : 'N/A'}</td>
                            <td className="p-4 pr-6 text-right">
                              <span className="text-[10px] uppercase tracking-widest px-3 py-1.5 rounded-md bg-white/5 text-[var(--color-maven-gray-400)] border border-white/10">
                                {metric.source || 'Verified Source'}
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              ))}
            </div>
          </section>
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
