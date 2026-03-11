import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { User, ArrowRight } from 'lucide-react'
import { BlurFade } from './magicui/blur-fade'
import { MagicCard } from './magicui/magic-card'

function extractPills(content) {
  const lines = content.split('\n')
  let pillIndex = lines.length
  for (let i = lines.length - 1; i >= 0; i--) {
    const line = lines[i].trim()
    if (!line) continue
    const isQuestion = line.endsWith('?')
    const isBullet = /^(\*|-|\d+\.)/.test(line)
    const isDirectQ = /^(Would you|Do you|Can we|Should we|What if|How about|Or perhaps|Are you)/i.test(line)
    if (isQuestion && (isBullet || isDirectQ || i === lines.length - 1)) {
      pillIndex = i
    } else break
  }
  const firstNonEmpty = lines.findIndex(l => l.trim().length > 0)
  if (pillIndex > firstNonEmpty && pillIndex < lines.length) {
    return {
      displayContent: lines.slice(0, pillIndex).join('\n').trim(),
      pills: lines
        .slice(pillIndex)
        .filter(l => l.trim().length > 0)
        .map(l => l.replace(/^(\*|-|\d+\.)\s*/, '').replace(/^\*\*(.*?)\*\*\s*/, '$1').trim()),
    }
  }
  return { displayContent: content, pills: [] }
}

export default function MessageBubble({ role, content, onSendClick, index = 0 }) {
  const isUser = role === 'user'
  const { displayContent, pills } = isUser
    ? { displayContent: content, pills: [] }
    : extractPills(content)

  return (
    <BlurFade delay={index * 0.05} inView>
      <div className={`flex w-full gap-3 ${isUser ? 'justify-end' : 'justify-start'}`}>
        <div className={`flex gap-3 w-full md:max-w-[88%] ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>

          {/* Avatar */}
          <div className={`w-7 h-7 rounded-full flex shrink-0 items-center justify-center mt-1 ${
            isUser
              ? 'bg-white'
              : 'bg-[#0f0f0f] border border-[#1e1e1e]'
          }`}>
            {isUser
              ? <User className="w-3.5 h-3.5 text-black" />
              : (
                <svg width="12" height="12" viewBox="0 0 16 16" fill="none">
                  <path d="M8 2L14 5V11L8 14L2 11V5L8 2Z" stroke="#555" strokeWidth="1.5"/>
                  <circle cx="8" cy="8" r="2" fill="#555"/>
                </svg>
              )
            }
          </div>

          {/* Bubble */}
          {isUser ? (
            <div className="px-4 py-3 bg-white text-[#0a0a0a] rounded-xl rounded-tr-sm text-[13px] leading-relaxed max-w-[85%] self-end">
              {content}
            </div>
          ) : (
            <MagicCard
              className="flex-1 rounded-xl rounded-tl-sm overflow-hidden border border-[#1a1a1a]"
              gradientColor="#141414"
              gradientSize={180}
              gradientOpacity={0.6}
            >
              <div className="bg-[#0f0f0f] px-4 py-3 flex flex-col gap-3">
                <div className="prose prose-invert prose-zinc max-w-none text-[13px]
                  prose-p:leading-relaxed prose-p:text-[#c4c4c7]
                  prose-strong:text-[#e4e4e7]
                  prose-code:text-[#aaa] prose-code:bg-[#141414] prose-code:px-1 prose-code:py-0.5 prose-code:rounded prose-code:text-[12px]
                  prose-pre:bg-[#0a0a0a] prose-pre:border prose-pre:border-[#1a1a1a]
                  prose-ul:text-[#aaa] prose-ol:text-[#aaa]
                ">
                  <ReactMarkdown
                    remarkPlugins={[remarkGfm]}
                    components={{
                      table: ({ node: _node, ...props }) => (
                        <div className="markdown-table-wrapper">
                          <table className="markdown-table" {...props} />
                        </div>
                      ),
                      thead: ({ node: _node, ...props }) => <thead {...props} />,
                      tbody: ({ node: _node, ...props }) => <tbody {...props} />,
                      tr: ({ node: _node, ...props }) => <tr {...props} />,
                      th: ({ node: _node, ...props }) => <th {...props} />,
                      td: ({ node: _node, ...props }) => <td {...props} />,
                    }}
                  >
                    {displayContent}
                  </ReactMarkdown>
                </div>

                {pills.length > 0 && (
                  <div className="flex flex-col gap-1.5 pt-3 border-t border-[#1a1a1a]">
                    <p className="text-[9px] font-medium text-[#333] uppercase tracking-wider">Suggested follow-ups</p>
                    {pills.map((pill, idx) => (
                      <button
                        key={idx}
                        onClick={() => onSendClick?.(pill)}
                        className="flex items-center gap-2.5 px-3 py-2 bg-[#0a0a0a] hover:bg-[#111] border border-[#1a1a1a] hover:border-[#222] rounded-lg transition-all text-left group"
                      >
                        <ArrowRight className="w-3 h-3 text-[#444] shrink-0 group-hover:translate-x-0.5 group-hover:text-[#888] transition-all" />
                        <span className="text-[12px] text-[#555] group-hover:text-[#888]">{pill}</span>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </MagicCard>
          )}
        </div>
      </div>
    </BlurFade>
  )
}
