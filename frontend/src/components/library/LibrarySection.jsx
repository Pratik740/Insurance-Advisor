import { useState } from 'react'
import { BlurFade } from '../magicui/blur-fade'
import { MagicCard } from '../magicui/magic-card'
import { Search, ChevronDown, ChevronUp } from 'lucide-react'
import companies from '@data/term_life_companies.json'

function PlanCard({ plan, index }) {
  const [open, setOpen] = useState(false)

  return (
    <BlurFade delay={index * 0.04}>
      <MagicCard
        className="rounded-xl border border-[#1a1a1a] overflow-hidden"
        gradientColor="#141414"
        gradientSize={120}
      >
        <div className="bg-[#0f0f0f]">
          <button
            onClick={() => setOpen(o => !o)}
            className="w-full flex items-center gap-3 p-4 text-left"
          >
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-0.5">
                <span className="text-[13px] font-medium text-[#e4e4e7]">{plan.plan_name}</span>
                <span className="text-[9px] font-medium text-[#555] bg-[#141414] border border-[#1e1e1e] px-1.5 py-0.5 rounded-full">
                  CSR {plan.claim_settlement_ratio}%
                </span>
              </div>
              <p className="text-[11px] text-[#444] truncate">{plan.company_name}</p>
            </div>
            <div className="flex items-center gap-3 shrink-0">
              <div className="text-right">
                <p className="text-[10px] text-[#444]">Base rate</p>
                <p className="text-[12px] font-medium text-[#888]">₹{plan.base_rate}/1000</p>
              </div>
              {open ? <ChevronUp className="w-4 h-4 text-[#333]" /> : <ChevronDown className="w-4 h-4 text-[#333]" />}
            </div>
          </button>

          {open && (
            <div className="px-4 pb-4 border-t border-[#141414] pt-3 flex flex-col gap-3">
              {/* Stats */}
              <div className="grid grid-cols-3 gap-2">
                {[
                  { label: 'Max Cover', value: `₹${(plan.max_life_cover / 10000000).toFixed(0)} Cr` },
                  { label: 'Age Range', value: `${plan.min_entry_age}–${plan.max_entry_age}` },
                  { label: 'Cover Till', value: `Age ${plan.max_cover_till_age}` },
                ].map(({ label, value }) => (
                  <div key={label} className="bg-[#0a0a0a] rounded-lg p-2 border border-[#141414]">
                    <p className="text-[9px] text-[#444] uppercase tracking-wider mb-0.5">{label}</p>
                    <p className="text-[12px] text-[#888] font-medium">{value}</p>
                  </div>
                ))}
              </div>

              {/* Features */}
              {plan.features?.length > 0 && (
                <div>
                  <p className="text-[9px] uppercase tracking-wider text-[#333] mb-1.5">Features</p>
                  <ul className="flex flex-col gap-1">
                    {plan.features.map((f, i) => (
                      <li key={i} className="text-[11px] text-[#555] flex items-center gap-2">
                        <span className="w-1 h-1 rounded-full bg-[#333] shrink-0" />
                        {f}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Riders */}
              {plan.optional_riders?.length > 0 && (
                <div>
                  <p className="text-[9px] uppercase tracking-wider text-[#333] mb-1.5">Optional Riders</p>
                  <div className="flex flex-wrap gap-1.5">
                    {plan.optional_riders.map((r, i) => (
                      <span key={i} className="text-[10px] text-[#555] bg-[#111] border border-[#1a1a1a] px-2 py-0.5 rounded-full">
                        {r}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </MagicCard>
    </BlurFade>
  )
}

export default function LibrarySection() {
  const [query, setQuery] = useState('')

  const filtered = companies.filter(p =>
    p.plan_name.toLowerCase().includes(query.toLowerCase()) ||
    p.company_name.toLowerCase().includes(query.toLowerCase())
  )

  return (
    <div className="h-full flex flex-col overflow-hidden">
      <div className="px-5 pt-5 pb-3 shrink-0">
        <div className="relative max-w-xl">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-[#333]" />
          <input
            className="w-full bg-[#0f0f0f] border border-[#1a1a1a] rounded-lg pl-9 pr-3 py-2 text-[13px] text-[#e4e4e7] placeholder-[#333] focus:outline-none focus:border-[#222] transition-colors"
            placeholder="Search plans or insurers..."
            value={query}
            onChange={e => setQuery(e.target.value)}
          />
        </div>
        <p className="text-[11px] text-[#333] mt-2">{filtered.length} plan{filtered.length !== 1 ? 's' : ''} available</p>
      </div>

      <div className="flex-1 overflow-y-auto px-5 pb-5
        [&::-webkit-scrollbar]:w-[3px]
        [&::-webkit-scrollbar-track]:bg-transparent
        [&::-webkit-scrollbar-thumb]:bg-[#1e1e1e]"
      >
        <div className="flex flex-col gap-2 max-w-2xl">
          {filtered.map((plan, i) => (
            <PlanCard key={plan.plan_id} plan={plan} index={i} />
          ))}
        </div>
      </div>
    </div>
  )
}
