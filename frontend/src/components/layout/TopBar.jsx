import { Plus, Star } from 'lucide-react'
import { ShimmerButton } from '../magicui/shimmer-button'

const SECTION_LABELS = {
  chat:       { title: 'AI Chat',          sub: 'Multi-agent insurance advisor' },
  profile:    { title: 'My Profile',       sub: 'Your insurance profile' },
  comparison: { title: 'Plan Comparison',  sub: 'Compare recommended plans' },
  history:    { title: 'History',          sub: 'Past conversations' },
  library:    { title: 'Policy Library',   sub: 'All available plans' },
  quotes:     { title: 'Saved Quotes',     sub: 'Bookmarked plans' },
}

export default function TopBar({ activeSection, chatProps }) {
  const { title, sub } = SECTION_LABELS[activeSection] || SECTION_LABELS.chat
  const { onNewChat, onSaveQuote } = chatProps || {}

  return (
    <header className="h-[52px] shrink-0 border-b border-[#111] flex items-center px-5 gap-3 bg-[#080808]/80 backdrop-blur-sm">
      {/* Live status dot (chat only) */}
      {activeSection === 'chat' && (
        <span className="relative flex h-2 w-2 shrink-0">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-40" />
          <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500" />
        </span>
      )}

      {/* Title */}
      <div className="min-w-0">
        <h1 className="text-[13px] font-medium text-[#e4e4e7] leading-none">{title}</h1>
        <p className="text-[11px] text-[#333] mt-0.5 truncate">{sub}</p>
      </div>

      {/* Actions */}
      <div className="ml-auto flex items-center gap-2">
        {activeSection === 'chat' && (
          <>
            <button
              onClick={onNewChat}
              className="h-7 px-2.5 rounded-md border border-[#1e1e1e] bg-transparent text-[#555] text-[11px] flex items-center gap-1.5 hover:bg-[#111] hover:text-[#888] hover:border-[#222] transition-all"
            >
              <Plus className="w-3 h-3" />
              New Chat
            </button>
            <ShimmerButton
              onClick={onSaveQuote}
              shimmerColor="#888"
              background="#0f0f0f"
              borderRadius="6px"
              className="h-7 px-2.5 text-[11px] font-medium text-white border border-[#222]"
            >
              <Star className="w-3 h-3 mr-1" />
              Save Quote
            </ShimmerButton>
          </>
        )}
      </div>
    </header>
  )
}
