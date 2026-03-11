import { useState, useRef, useEffect } from 'react'
import { Send, Sparkles } from 'lucide-react'

export default function InputArea({ onSend, disabled }) {
  const [text, setText] = useState('')
  const textareaRef = useRef(null)

  const handleSend = () => {
    if (text.trim() && !disabled) {
      onSend(text)
      setText('')
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`
    }
  }, [text])

  return (
    <div className="relative flex items-end w-full glass-panel rounded-2xl px-3 py-3 ring-1 ring-inset ring-dark-border focus-within:ring-1 focus-within:ring-primary-500 transition-all shadow-lg">
      <div className="flex shrink-0 items-center justify-center h-10 w-10 mr-1 hidden sm:flex">
         <Sparkles className="w-5 h-5 text-zinc-500" />
      </div>
      <textarea
        ref={textareaRef}
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Ask anything about Life, Health, or Travel insurance..."
        className="flex-1 max-h-48 min-h-[40px] bg-transparent border-0 resize-none py-2 px-2 text-white placeholder-zinc-500 focus:outline-none sm:text-base text-sm custom-scrollbar"
        rows={1}
        disabled={disabled}
      />
      <button
        onClick={handleSend}
        disabled={!text.trim() || disabled}
        className="shrink-0 flex items-center w-10 h-10 justify-center rounded-xl bg-primary-600 text-white hover:bg-primary-500 disabled:opacity-50 disabled:hover:bg-primary-600 transition-colors ml-2 cursor-pointer"
      >
        <Send className="w-4 h-4 ml-[-2px]" />
      </button>
    </div>
  )
}
