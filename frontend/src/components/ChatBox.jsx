import { useState, useEffect } from 'react'
import MessageBubble from './MessageBubble'
import { ShieldAlert } from 'lucide-react'

const LoadingIndicator = () => {
    const statuses = [
        "Analyzing profile...",
        "Querying policy databases...",
        "Evaluating coverage limits...",
        "Formulating recommendations...",
    ]
    const [statusIndex, setStatusIndex] = useState(0)

    useEffect(() => {
        const interval = setInterval(() => {
            setStatusIndex(prev => Math.min(prev + 1, statuses.length - 1))
        }, 2200)
        return () => clearInterval(interval)
    }, [])

    return (
        <div className="flex w-full justify-start mt-2">
           <div className="flex gap-4 w-full md:max-w-[85%] flex-row shadow-sm">
             <div className="w-8 h-8 rounded-full border border-zinc-700 bg-[#0f172a] flex shrink-0 items-center justify-center mt-1 animate-pulse">
               <ShieldAlert className="w-5 h-5 text-zinc-600" />
             </div>
             <div className="bg-dark-surface border border-dark-border rounded-2xl rounded-tl-sm px-5 py-4 flex items-center gap-4">
               <div className="flex space-x-1.5 align-middle mt-0.5">
                 <div className="w-2 h-2 bg-primary-500/80 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                 <div className="w-2 h-2 bg-primary-500/80 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                 <div className="w-2 h-2 bg-primary-500/80 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
               </div>
               <span className="text-sm font-medium text-zinc-400 animate-pulse">{statuses[statusIndex]}</span>
             </div>
           </div>
        </div>
    )
}

export default function ChatBox({ messages, isLoading, onSendClick }) {
  return (
    <div className="flex flex-col max-w-3xl mx-auto w-full px-4 py-8 gap-6">
      {messages.map((msg) => (
        <MessageBubble key={msg.id} role={msg.role} content={msg.content} onSendClick={onSendClick} />
      ))}
      
      {isLoading && <LoadingIndicator />}
    </div>
  )
}
