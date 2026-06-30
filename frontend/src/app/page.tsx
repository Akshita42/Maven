import Link from "next/link";
import { CurrencyCore } from "@/components/ui/CurrencyCore";
import { Activity, BrainCircuit, LineChart, ShieldCheck, Scale, GraduationCap, ArrowRight } from "lucide-react";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-[var(--color-maven-bg)] text-white selection:bg-[var(--color-maven-primary)] selection:text-white">
      {/* Navigation */}
      <nav className="fixed top-0 w-full z-50 bg-[var(--color-maven-bg)]/80 backdrop-blur-md border-b border-white/5">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-xl font-bold tracking-tight text-white">Maven</span>
          </div>
          <div className="hidden md:flex items-center gap-8 text-sm font-medium text-[var(--color-maven-gray-400)]">
            <a href="#features" className="hover:text-white transition-colors">Features</a>
            <a href="#how-it-works" className="hover:text-white transition-colors">How it Works</a>
            <a href="#pricing" className="hover:text-white transition-colors">Pricing</a>
            <a href="https://github.com/maven/maven" target="_blank" className="hover:text-white transition-colors">GitHub</a>
          </div>
          <Link 
            href="/research"
            className="px-4 py-2 bg-[var(--color-maven-primary)] hover:bg-[#b02f3c] text-white text-sm font-medium rounded-full transition-all shadow-[0_0_15px_rgba(209,58,74,0.3)] hover:shadow-[0_0_25px_rgba(209,58,74,0.5)]"
          >
            Start Research
          </Link>
        </div>
      </nav>

      <main>
        {/* Hero Section */}
        <section className="pt-40 pb-20 px-6 max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-16">
          <div className="max-w-2xl flex-1">
            <h1 className="text-5xl md:text-7xl font-semibold tracking-tight leading-tight mb-6 text-transparent bg-clip-text bg-gradient-to-br from-white via-white to-gray-500">
              Research Better.<br />Invest Smarter.
            </h1>
            <p className="text-lg md:text-xl text-[var(--color-maven-gray-400)] mb-10 leading-relaxed max-w-xl font-light">
              Maven combines live financial data, multi-agent reasoning, deterministic investment analysis, and explainable AI to help investors make informed decisions.
            </p>
            <div className="flex flex-col sm:flex-row items-center gap-4">
              <Link 
                href="/research"
                className="w-full sm:w-auto px-8 py-3 bg-[var(--color-maven-primary)] text-white rounded-full font-medium flex items-center justify-center gap-2 hover:bg-[#b02f3c] transition-all shadow-[0_0_20px_rgba(209,58,74,0.3)] hover:shadow-[0_0_30px_rgba(209,58,74,0.5)]"
              >
                Start Research <ArrowRight size={18} />
              </Link>

            </div>
          </div>
          
          <div className="flex-1 flex justify-center md:justify-end">
            <div className="scale-125 md:scale-150 relative">
               <CurrencyCore size="lg" />
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section id="features" className="py-24 px-6 bg-[#110e0e] border-y border-white/5">
          <div className="max-w-6xl mx-auto">
            <h2 className="text-3xl md:text-4xl font-medium tracking-tight mb-16 text-center">Why Maven</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[
                { icon: Activity, title: "Live Financial Data", desc: "Connects directly to real-time market APIs for fundamentals, pricing, and news." },
                { icon: BrainCircuit, title: "Multi-Agent Intelligence", desc: "A swarm of specialized AI agents evaluate business quality, growth, and management." },
                { icon: LineChart, title: "Deterministic Analysis", desc: "Grounds AI reasoning with hard mathematical scoring models and financial heuristics." },
                { icon: ShieldCheck, title: "Explainable AI", desc: "Every recommendation is backed by a verifiable chain of thought and cited evidence." },
                { icon: Scale, title: "Challenge Recommendation", desc: "Ask the AI committee to debate itself and surface hidden counter-arguments." },
                { icon: GraduationCap, title: "Adaptive Explanations", desc: "Tailored insights designed to help you quickly understand complex corporate mechanisms." },
              ].map((feature, i) => (
                <div 
                  key={i} 
                  className="p-8 rounded-[24px] bg-[var(--color-maven-bg)] border border-white/5 hover:border-[var(--color-maven-primary)]/50 hover:shadow-[0_8px_30px_rgba(0,0,0,0.5)] hover:-translate-y-1 transition-all duration-300 group"
                >
                  <feature.icon className="text-[var(--color-maven-secondary)] mb-6 group-hover:text-[var(--color-maven-primary)] transition-colors" size={28} />
                  <h3 className="text-xl font-medium mb-3 text-white">{feature.title}</h3>
                  <p className="text-[var(--color-maven-gray-400)] leading-relaxed font-light text-sm">{feature.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* How it Works Section */}
        <section id="how-it-works" className="py-32 px-6 max-w-6xl mx-auto">
          <h2 className="text-3xl md:text-4xl font-medium tracking-tight mb-20 text-center">How Maven Works</h2>
          
          <div className="relative">
            <div className="absolute top-1/2 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-white/10 to-transparent -translate-y-1/2 hidden lg:block" />
            
            <div className="flex flex-col lg:flex-row justify-between items-center gap-8 lg:gap-4 relative z-10">
              {[
                "Research", "Evidence", "Intelligence", 
                "Committee", "Critique", "Recommendation", "Report"
              ].map((step, i) => (
                <div key={i} className="flex flex-col items-center gap-4">
                  <div className="w-12 h-12 rounded-full bg-[#110e0e] border border-white/10 flex items-center justify-center text-sm font-medium text-[var(--color-maven-gray-400)] shadow-[0_0_15px_rgba(0,0,0,0.5)]">
                    {i + 1}
                  </div>
                  <span className="text-sm font-medium text-white tracking-wide">{step}</span>
                  {i < 6 && <ArrowRight size={16} className="text-white/20 lg:hidden mt-2" />}
                </div>
              ))}
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="py-12 border-t border-white/5 text-center text-sm text-[var(--color-maven-gray-500)]">
        <p>© 2026 Maven Investment Copilot. All rights reserved.</p>
      </footer>
    </div>
  );
}
