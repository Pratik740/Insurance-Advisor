import { BlurFade } from '../magicui/blur-fade'
import { NumberTicker } from '../magicui/number-ticker'
import { Star } from 'lucide-react'

export default function QuotesSection({ savedQuotes = [] }) {
  if (savedQuotes.length === 0) {
    return (
      <div className="h-full flex flex-col items-center justify-center gap-3 text-center px-8">
        <div className="w-12 h-12 rounded-xl bg-[#0f0f0f] border border-[#1a1a1a] flex items-center justify-center mb-2">
          <Star className="w-5 h-5 text-[#222]" />
        </div>
        <p className="text-[13px] text-[#555]">No saved quotes yet</p>
        <p className="text-[11px] text-[#333] max-w-[240px]">Click "Save Quote" in the top bar while chatting to bookmark plans here.</p>
      </div>
    )
  }

  return (
    <div className="h-full overflow-y-auto px-5 py-5
      [&::-webkit-scrollbar]:w-[3px]
      [&::-webkit-scrollbar-track]:bg-transparent
      [&::-webkit-scrollbar-thumb]:bg-[#1e1e1e]"
    >
      <div className="max-w-2xl mx-auto">
        <BlurFade delay={0.05}>
          <h2 className="text-[15px] font-semibold text-[#e4e4e7] mb-1">Saved Quotes</h2>
          <p className="text-[12px] text-[#444] mb-5">{savedQuotes.length} saved</p>
        </BlurFade>

        <div className="flex flex-col gap-3">
          {savedQuotes.map((quote, i) => (
            <BlurFade key={quote.id} delay={0.1 + i * 0.05}>
              <div className="bg-[#0f0f0f] border border-[#1a1a1a] rounded-xl p-4 hover:border-[#222] transition-colors">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <h3 className="text-[13px] font-medium text-[#e4e4e7]">{quote.planName}</h3>
                    <p className="text-[11px] text-[#444] mt-0.5">{quote.company || 'From Chat'}</p>
                  </div>
                  <div className="text-right shrink-0">
                    <div className="flex items-baseline gap-1">
                      <span className="text-[10px] text-[#444]">₹</span>
                      {quote.premiumMonthly > 0
                        ? <NumberTicker value={quote.premiumMonthly} className="text-[18px] font-bold text-white tabular-nums" />
                        : <span className="text-[18px] font-bold text-[#555]">—</span>
                      }
                      <span className="text-[10px] text-[#444]">/mo</span>
                    </div>
                  </div>
                </div>

                <div className="flex gap-2 mt-3 flex-wrap">
                  {quote.cover && (
                    <span className="text-[10px] text-[#555] bg-[#111] border border-[#1a1a1a] px-2 py-0.5 rounded-full">
                      Cover: {quote.cover}
                    </span>
                  )}
                  {quote.csr && (
                    <span className="text-[10px] text-[#555] bg-[#111] border border-[#1a1a1a] px-2 py-0.5 rounded-full">
                      CSR: {quote.csr}
                    </span>
                  )}
                  <span className="text-[10px] text-[#333] bg-[#0a0a0a] border border-[#141414] px-2 py-0.5 rounded-full">
                    {new Date(quote.savedAt).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' })}
                  </span>
                </div>

                {quote.snippet && (
                  <p className="text-[11px] text-[#333] mt-2.5 line-clamp-2 border-t border-[#141414] pt-2.5">
                    {quote.snippet}
                  </p>
                )}
              </div>
            </BlurFade>
          ))}
        </div>
      </div>
    </div>
  )
}
