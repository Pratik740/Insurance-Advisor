import { useEffect, useRef } from 'react'
import MessageBubble from '../MessageBubble'
import TypingIndicator from './TypingIndicator'
import { DotPattern } from '../magicui/dot-pattern'

export default function MessageList({ messages, isLoading, loadingStatus, onSendClick }) {
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isLoading])

  return (
    <div className="relative flex-1 overflow-y-auto px-5 py-6 flex flex-col gap-4
      [&::-webkit-scrollbar]:w-[3px]
      [&::-webkit-scrollbar-track]:bg-transparent
      [&::-webkit-scrollbar-thumb]:bg-[#1e1e1e]
      [&::-webkit-scrollbar-thumb]:rounded-full"
    >
      {/* Dot pattern background */}
      <DotPattern
        className="absolute inset-0 [mask-image:radial-gradient(ellipse_at_center,white_30%,transparent_80%)] opacity-40"
        cr={1}
        cx={14}
        cy={14}
      />

      {/* Messages */}
      <div className="relative z-10 flex flex-col gap-4 max-w-3xl mx-auto w-full">
        {messages.map((msg, i) => (
          <MessageBubble
            key={msg.id}
            role={msg.role}
            content={msg.content}
            onSendClick={onSendClick}
            index={i}
          />
        ))}
        {isLoading && (
          <div className="flex gap-3 items-start">
            <div className="w-7 h-7 rounded-full bg-[#0f0f0f] border border-[#1e1e1e] flex items-center justify-center shrink-0 mt-1">
              <svg width="12" height="12" viewBox="0 0 16 16" fill="none">
                <path d="M8 2L14 5V11L8 14L2 11V5L8 2Z" stroke="#555" strokeWidth="1.5"/>
                <circle cx="8" cy="8" r="2" fill="#555"/>
              </svg>
            </div>
            <TypingIndicator status={loadingStatus} />
          </div>
        )}
      </div>
      <div ref={bottomRef} />
    </div>
  )
}
