import { useState } from 'react'
import { BlurFade } from '../magicui/blur-fade'
import { Clock, MessageSquare, Search } from 'lucide-react'

export default function HistorySection({ history = [], onResumeThread }) {
  const [query, setQuery] = useState('')

  const filtered = history.filter(h =>
    h.title.toLowerCase().includes(query.toLowerCase())
  )

  return (
    <div className="h-full flex flex-col overflow-hidden">
      {/* Search bar */}
      <div className="px-5 pt-5 pb-3 shrink-0">
        <div className="relative max-w-xl">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-[#333]" />
          <input
            className="w-full bg-[#0f0f0f] border border-[#1a1a1a] rounded-lg pl-9 pr-3 py-2 text-[13px] text-[#e4e4e7] placeholder-[#333] focus:outline-none focus:border-[#222] transition-colors"
            placeholder="Search conversations..."
            value={query}
            onChange={e => setQuery(e.target.value)}
          />
        </div>
      </div>

      {/* List */}
      <div className="flex-1 overflow-y-auto px-5 pb-5
        [&::-webkit-scrollbar]:w-[3px]
        [&::-webkit-scrollbar-track]:bg-transparent
        [&::-webkit-scrollbar-thumb]:bg-[#1e1e1e]"
      >
        {filtered.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-48 gap-2">
            <Clock className="w-8 h-8 text-[#222]" />
            <p className="text-[12px] text-[#333]">
              {query ? 'No matching conversations' : 'No conversation history yet'}
            </p>
          </div>
        ) : (
          <div className="flex flex-col gap-2 max-w-xl">
            {filtered.map((entry, i) => (
              <BlurFade key={entry.id} delay={i * 0.04}>
                <button
                  onClick={() => onResumeThread?.(entry)}
                  className="w-full flex items-start gap-3 p-3 bg-[#0f0f0f] border border-[#1a1a1a] rounded-lg hover:bg-[#111] hover:border-[#222] transition-all text-left group"
                >
                  <MessageSquare className="w-4 h-4 text-[#333] shrink-0 mt-0.5 group-hover:text-[#555] transition-colors" />
                  <div className="min-w-0 flex-1">
                    <p className="text-[13px] text-[#888] truncate group-hover:text-[#aaa] transition-colors">
                      {entry.title}
                    </p>
                    <p className="text-[10px] text-[#333] mt-0.5">
                      {new Date(entry.createdAt).toLocaleDateString('en-IN', {
                        day: 'numeric', month: 'short', year: 'numeric'
                      })}
                    </p>
                  </div>
                </button>
              </BlurFade>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
