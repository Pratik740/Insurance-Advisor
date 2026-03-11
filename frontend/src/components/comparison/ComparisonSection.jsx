import { MagicCard } from '../magicui/magic-card'
import { NumberTicker } from '../magicui/number-ticker'
import { BlurFade } from '../magicui/blur-fade'
import { BorderBeam } from '../magicui/border-beam'

export default function ComparisonSection({ savedQuotes = [] }) {
  if (savedQuotes.length === 0) {
    return (
      <div className="h-full flex flex-col items-center justify-center gap-3 text-center px-8">
        <div className="w-12 h-12 rounded-xl bg-[#0f0f0f] border border-[#1a1a1a] flex items-center justify-center mb-2">
          <svg width="20" height="20" viewBox="0 0 16 16" fill="none">
            <rect x="1" y="1" width="6" height="6" stroke="#333" strokeWidth="1.2" rx="1"/>
            <rect x="9" y="1" width="6" height="6" stroke="#333" strokeWidth="1.2" rx="1"/>
            <rect x="1" y="9" width="6" height="6" stroke="#333" strokeWidth="1.2" rx="1"/>
            <rect x="9" y="9" width="6" height="6" stroke="#333" strokeWidth="1.2" rx="1"/>
          </svg>
        </div>
        <p className="text-[13px] text-[#555]">No plans to compare yet</p>
        <p className="text-[11px] text-[#333] max-w-[240px]">Chat with the AI advisor and click "Save Quote" to add plans here for side-by-side comparison.</p>
      </div>
    )
  }

  return (
    <div className="h-full overflow-y-auto px-6 py-6
      [&::-webkit-scrollbar]:w-[3px]
      [&::-webkit-scrollbar-track]:bg-transparent
      [&::-webkit-scrollbar-thumb]:bg-[#1e1e1e]"
    >
      <div className="max-w-4xl mx-auto">
        <BlurFade delay={0.05}>
          <h2 className="text-[15px] font-semibold text-[#e4e4e7] mb-1">Plan Comparison</h2>
          <p className="text-[12px] text-[#444] mb-6">{savedQuotes.length} saved plan{savedQuotes.length !== 1 ? 's' : ''}</p>
        </BlurFade>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {savedQuotes.map((quote, i) => (
            <BlurFade key={quote.id} delay={0.1 + i * 0.05}>
              <MagicCard
                className={`relative rounded-xl border overflow-hidden ${i === 0 ? 'border-white/20' : 'border-[#1a1a1a]'}`}
                gradientColor="#141414"
                gradientSize={150}
              >
                {i === 0 && <BorderBeam size={80} duration={4} colorFrom="#ffffff" colorTo="#444" />}
                <div className="p-4 bg-[#0f0f0f]">
                  {i === 0 && (
                    <span className="text-[9px] font-medium text-black bg-white px-2 py-0.5 rounded-full mb-2 inline-block">Best Match</span>
                  )}
                  <h3 className="text-[13px] font-semibold text-[#e4e4e7] mb-0.5">{quote.planName}</h3>
                  <p className="text-[11px] text-[#555] mb-3">{quote.company || 'From Chat'}</p>

                  <div className="flex items-baseline gap-1 mb-3">
                    <span className="text-[11px] text-[#555]">₹</span>
                    {quote.premiumMonthly > 0
                      ? <NumberTicker value={quote.premiumMonthly} className="text-[22px] font-bold text-white tabular-nums" />
                      : <span className="text-[22px] font-bold text-white">—</span>
                    }
                    <span className="text-[11px] text-[#555]">/mo</span>
                  </div>

                  <div className="grid grid-cols-2 gap-2 text-[11px]">
                    <div className="bg-[#0a0a0a] rounded-lg p-2 border border-[#141414]">
                      <p className="text-[#444] mb-0.5">Cover</p>
                      <p className="text-[#888] font-medium">{quote.cover || '—'}</p>
                    </div>
                    <div className="bg-[#0a0a0a] rounded-lg p-2 border border-[#141414]">
                      <p className="text-[#444] mb-0.5">CSR</p>
                      <p className="text-[#888] font-medium">{quote.csr || '—'}</p>
                    </div>
                  </div>

                  {quote.snippet && (
                    <p className="text-[11px] text-[#333] mt-3 line-clamp-2">{quote.snippet}</p>
                  )}
                </div>
              </MagicCard>
            </BlurFade>
          ))}
        </div>
      </div>
    </div>
  )
}
