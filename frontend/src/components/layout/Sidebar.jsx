import { MessageSquare, User, LayoutGrid, Clock, BookOpen, Star } from 'lucide-react'
import { BorderBeam } from '../magicui/border-beam'
import { AnimatedShinyText } from '../magicui/animated-shiny-text'
import { cn } from '@/lib/utils'

const NAV_ITEMS = [
  {
    section: 'Workspace',
    items: [
      { id: 'chat',       label: 'AI Chat',          icon: MessageSquare, badge: 'Live' },
      { id: 'profile',    label: 'My Profile',        icon: User },
      { id: 'comparison', label: 'Plan Comparison',   icon: LayoutGrid, badgeKey: 'savedQuotes' },
      { id: 'history',    label: 'History',           icon: Clock,       badgeKey: 'history' },
    ],
  },
  {
    section: 'Resources',
    items: [
      { id: 'library',    label: 'Policy Library',    icon: BookOpen },
      { id: 'quotes',     label: 'Saved Quotes',      icon: Star, badgeKey: 'savedQuotes' },
    ],
  },
]

export default function Sidebar({ activeSection, onNavigate, savedQuotesCount = 0, historyCount = 0 }) {
  const badgeValues = { savedQuotes: savedQuotesCount, history: historyCount }

  return (
    <aside className="w-[220px] shrink-0 bg-[#080808] border-r border-[#141414] flex flex-col h-full">
      {/* Logo */}
      <div className="px-4 py-5 border-b border-[#141414]">
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 bg-white rounded-lg flex items-center justify-center shrink-0">
            <svg width="14" height="14" viewBox="0 0 16 16" fill="none">
              <path d="M8 2L14 5V11L8 14L2 11V5L8 2Z" stroke="black" strokeWidth="1.5"/>
              <circle cx="8" cy="8" r="2" fill="black"/>
            </svg>
          </div>
          <div>
            <AnimatedShinyText className="text-[13px] font-semibold text-white tracking-tight">
              CoverAI
            </AnimatedShinyText>
            <p className="text-[10px] text-[#444] leading-none mt-0.5">Insurance Advisor</p>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-2 py-3 flex flex-col gap-0.5">
        {NAV_ITEMS.map(({ section, items }) => (
          <div key={section} className="mb-2">
            <p className="text-[9px] uppercase tracking-[1.2px] text-[#333] font-medium px-2 py-1.5">
              {section}
            </p>
            {items.map(({ id, label, icon: Icon, badge, badgeKey }) => {
              const isActive = activeSection === id
              const badgeCount = badgeKey ? badgeValues[badgeKey] : null
              return (
                <button
                  key={id}
                  onClick={() => onNavigate(id)}
                  className={cn(
                    'relative w-full flex items-center gap-2.5 px-2.5 py-2 rounded-lg text-left transition-all duration-150 group overflow-hidden',
                    isActive
                      ? 'bg-[#111] border border-[#222]'
                      : 'border border-transparent hover:bg-[#0f0f0f] hover:border-[#1a1a1a]'
                  )}
                >
                  {/* Active left accent */}
                  {isActive && (
                    <span className="absolute left-0 top-[20%] bottom-[20%] w-[2px] bg-white rounded-r-sm" />
                  )}

                  <Icon
                    className={cn(
                      'w-3.5 h-3.5 shrink-0 transition-opacity',
                      isActive ? 'opacity-100 text-white' : 'opacity-30 text-white group-hover:opacity-60'
                    )}
                  />

                  <span className={cn(
                    'text-[12.5px] flex-1 transition-colors',
                    isActive ? 'text-[#e4e4e7] font-medium' : 'text-[#555] group-hover:text-[#888]'
                  )}>
                    {label}
                  </span>

                  {/* Badge */}
                  {badge && (
                    <span className={cn(
                      'text-[9px] px-1.5 py-0.5 rounded-full font-medium border',
                      isActive ? 'bg-white text-black border-white' : 'bg-[#1a1a1a] text-[#555] border-[#222]'
                    )}>
                      {badge}
                    </span>
                  )}
                  {badgeCount !== null && badgeCount > 0 && (
                    <span className="text-[9px] px-1.5 py-0.5 rounded-full font-medium border bg-[#1a1a1a] text-[#555] border-[#222]">
                      {badgeCount}
                    </span>
                  )}

                  {/* Border beam on active */}
                  {isActive && <BorderBeam size={60} duration={4} colorFrom="#ffffff" colorTo="#888888" />}
                </button>
              )
            })}
          </div>
        ))}
      </nav>

      {/* Footer */}
      <div className="p-2 border-t border-[#111]">
        <div className="flex items-center gap-2 px-2 py-2 rounded-lg hover:bg-[#0f0f0f] cursor-pointer transition-colors">
          <div className="w-6 h-6 rounded-full bg-[#1a1a1a] border border-[#222] flex items-center justify-center text-[10px] text-[#666] font-medium shrink-0">
            U
          </div>
          <div className="min-w-0">
            <p className="text-[12px] text-[#555] truncate">User</p>
            <p className="text-[10px] text-[#333]">Free Plan</p>
          </div>
        </div>
      </div>
    </aside>
  )
}
