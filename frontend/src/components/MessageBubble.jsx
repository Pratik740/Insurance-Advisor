import ReactMarkdown from 'react-markdown'
import { User, ShieldAlert, ArrowRight } from 'lucide-react'

export default function MessageBubble({ role, content, onSendClick }) {
  const isUser = role === 'user'

  // Extract trailing questions meant for the user into interactive pills
  let contentPills = []
  let displayContent = content

  if (!isUser && content) {
      const lines = content.split('\n')
      let pillIndex = lines.length
      
      for (let i = lines.length - 1; i >= 0; i--) {
          const line = lines[i].trim()
          if (!line) continue
          
          const isQuestion = line.endsWith('?')
          const isBullet = /^(\*|-|\d+\.)/.test(line)
          const isDirectQuestion = /^(Would you|Do you|Can we|Should we|What if|How about|Or perhaps|Are you)/i.test(line)
          
          if (isQuestion && (isBullet || isDirectQuestion || i === lines.length - 1)) {
              pillIndex = i
          } else {
              break
          }
      }
      
      const firstNonEmpty = lines.findIndex(l => l.trim().length > 0)
      if (pillIndex > firstNonEmpty && pillIndex < lines.length) {
          displayContent = lines.slice(0, pillIndex).join('\n').trim()
          contentPills = lines.slice(pillIndex)
              .filter(l => l.trim().length > 0)
              .map(l => l.replace(/^(\*|-|\d+\.)\s*/, '').replace(/^\*\*(.*?)\*\*\s*/, '$1').trim())
      }
  }
  
  return (
    <div className={`flex w-full ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`flex gap-4 w-full md:max-w-[85%] ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
        
        {/* Avatar */}
        <div className={`w-8 h-8 rounded-full flex shrink-0 items-center justify-center mt-1 ${isUser ? 'bg-primary-600' : 'bg-[#0f172a] border border-zinc-700'}`}>
           {isUser ? <User className="w-5 h-5 text-white" /> : <ShieldAlert className="w-5 h-5 text-primary-400" />}
        </div>
        
        {/* Bubble */}
        <div className={`px-5 py-4 flex flex-col gap-2 shadow-sm ${
            isUser ? 
            'bg-primary-600 text-white rounded-2xl rounded-tr-sm self-end max-w-[85%]' : 
            'bg-dark-surface border border-dark-border text-zinc-200 rounded-2xl rounded-tl-sm w-full outline outline-1 outline-white/5'
        }`}>
            {isUser ? (
                <div className="whitespace-pre-wrap leading-relaxed text-sm md:text-base">{content}</div>
            ) : (
                <div className="flex flex-col gap-4">
                  <div className="prose prose-invert prose-zinc max-w-none prose-p:leading-relaxed prose-pre:bg-zinc-900 prose-pre:border prose-pre:border-zinc-800 prose-td:border prose-td:border-zinc-700 prose-th:border prose-th:border-zinc-600 prose-th:bg-zinc-800 text-sm md:text-base prose-p:my-2 prose-ul:my-2 prose-ol:my-2 prose-table:markdown-table-wrapper prose-table:markdown-table">
                      <ReactMarkdown>{displayContent}</ReactMarkdown>
                  </div>
                  
                  {contentPills.length > 0 && (
                      <div className="flex flex-col gap-2 mt-2 pt-4 border-t border-zinc-800">
                          <p className="text-xs font-semibold text-zinc-400 uppercase tracking-wider mb-1">Suggested Follow-ups</p>
                          {contentPills.map((pill, idx) => (
                              <button 
                                  key={idx}
                                  onClick={() => onSendClick && onSendClick(pill)}
                                  className="flex items-start text-left gap-3 px-4 py-3 bg-zinc-800/40 hover:bg-zinc-800/80 border border-zinc-700/50 hover:border-primary-500/50 rounded-xl transition-all duration-200 group"
                              >
                                  <ArrowRight className="w-4 h-4 mt-0.5 text-primary-500 shrink-0 group-hover:translate-x-1 transition-transform" />
                                  <span className="text-sm font-medium text-zinc-300 group-hover:text-zinc-100">{pill}</span>
                              </button>
                          ))}
                      </div>
                  )}
                </div>
            )}
        </div>
      </div>
    </div>
  )
}
