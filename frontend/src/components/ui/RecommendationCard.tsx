import { useState } from "react";
import { CheckCircle2, AlertTriangle, Clock, Target, FileText, Share2, SearchX } from "lucide-react";
import { motion } from "framer-motion";
import { MavenAPI } from "@/lib/api";
import Link from "next/link";

export function RecommendationCard({ report }: { report: any }) {
  const [isChallenging, setIsChallenging] = useState(false);
  const [isExplaining, setIsExplaining] = useState(false);

  if (!report) return null;

  const { executiveSummary, recommendation } = report;
  const stance = executiveSummary.stance;
  const conviction = executiveSummary.conviction;

  // Stance colors
  let stanceColor = "text-[var(--color-maven-gray-400)] border-[var(--color-maven-gray-500)] bg-white/5";
  if (stance === "BUY") stanceColor = "text-emerald-400 border-emerald-500/30 bg-emerald-500/10";
  if (stance === "SELL") stanceColor = "text-[var(--color-maven-primary)] border-[var(--color-maven-primary)]/30 bg-[var(--color-maven-primary)]/10";

  const handleChallenge = async () => {
    setIsChallenging(true);
    try {
      await MavenAPI.challengeRecommendation(report.reportId);
    } catch (err) {
      alert("Challenge endpoint not ready yet.");
    } finally {
      setIsChallenging(false);
    }
  };

  const handleExplain = async () => {
    setIsExplaining(true);
    try {
      await MavenAPI.explainRecommendation(report.reportId, "Intermediate");
    } catch (err) {
      alert("Explain endpoint not ready yet.");
    } finally {
      setIsExplaining(false);
    }
  };

  return (
    <motion.div 
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: "easeOut" }}
      className="w-full max-w-2xl bg-[#110e0e] border border-white/10 rounded-2xl overflow-hidden shadow-xl my-4"
    >
      <div className="p-5 flex flex-col gap-4">
        {/* Header & Main Stats */}
        <div className="flex justify-between items-center">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-lg font-bold text-white">
                {report.companyOverview.companyName || report.companyOverview.ticker}
              </span>
              {report.companyOverview.companyName && (
                <span className="text-sm text-[var(--color-maven-gray-400)]">
                  ({report.companyOverview.ticker})
                </span>
              )}
            </div>
            <div className="flex items-center gap-3 text-xs text-[var(--color-maven-gray-400)] font-medium">
              <span>Confidence: {(recommendation.confidenceScore * 100).toFixed(0)}%</span>
              <span>•</span>
              <span>Outlook: {recommendation.investmentOutlook || recommendation.horizon}</span>
            </div>
          </div>
          
          <div className={`px-4 py-1.5 rounded-lg border ${stanceColor} font-bold tracking-wide`}>
            {stance}
          </div>
        </div>

        {/* Positives and Risk */}
        <div className="space-y-3 bg-black/20 rounded-xl p-4 border border-white/5">
          {recommendation.keyPositives && recommendation.keyPositives.length > 0 && (
            <div>
              <div className="text-xs font-semibold text-emerald-400 uppercase tracking-wider mb-2 flex items-center gap-1.5"><CheckCircle2 size={14}/> Top Positives</div>
              <ul className="space-y-1.5">
                {recommendation.keyPositives.slice(0, 3).map((pos: string, i: number) => (
                  <li key={i} className="text-xs text-[var(--color-maven-gray-300)] flex items-start gap-1.5">
                    <span className="text-emerald-500/50 mt-0.5">•</span> {pos}
                  </li>
                ))}
              </ul>
            </div>
          )}
          
          {recommendation.keyRisks && recommendation.keyRisks.length > 0 && (
            <div className="pt-2 border-t border-white/5">
              <div className="text-xs font-semibold text-[var(--color-maven-primary)] uppercase tracking-wider mb-2 flex items-center gap-1.5"><AlertTriangle size={14}/> Primary Risk</div>
              <p className="text-xs text-[var(--color-maven-gray-300)] flex items-start gap-1.5">
                <span className="text-[var(--color-maven-primary)]/50 mt-0.5">•</span> {recommendation.keyRisks[0]}
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Actions */}
      <div className="px-5 py-3 bg-[#0a0808] border-t border-white/5 flex flex-wrap gap-4 items-center justify-between">
        <div className="flex gap-4">
          <button 
            disabled={true}
            className="text-xs font-medium text-[var(--color-maven-gray-500)] flex items-center gap-1.5 cursor-not-allowed"
          >
            <SearchX size={14} /> Challenge <span className="ml-1 text-[9px] bg-white/10 px-1.5 py-0.5 rounded text-[var(--color-maven-gray-500)]">Soon</span>
          </button>
          <button 
            disabled={true}
            className="text-xs font-medium text-[var(--color-maven-gray-500)] flex items-center gap-1.5 cursor-not-allowed"
          >
            <Share2 size={14} /> Explain <span className="ml-1 text-[9px] bg-white/10 px-1.5 py-0.5 rounded text-[var(--color-maven-gray-500)]">Soon</span>
          </button>
        </div>
        <Link 
          href={`/research/${report.reportId}`}
          className="px-4 py-1.5 bg-white text-black hover:bg-gray-200 text-xs font-semibold rounded-full transition-colors flex items-center gap-1.5"
        >
          <FileText size={14} /> Full Report
        </Link>
      </div>
    </motion.div>
  );
}
