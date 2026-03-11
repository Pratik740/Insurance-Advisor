import { useState, useRef, useEffect } from 'react'
import { Send } from 'lucide-react'
import { BorderBeam } from './magicui/border-beam'
import { ShimmerButton } from './magicui/shimmer-button'

export default function InputArea({ onSend, disabled }) {
  const [text, setText] = useState('')
  const [focused, setFocused] = useState(false)
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

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`
    }
  }, [text])

  return (
    <div
      className="relative flex items-end w-full bg-[#0f0f0f] border border-[#1e1e1e] rounded-xl px-3 py-2.5 transition-colors overflow-hidden"
      style={{ borderColor: focused ? '#333' : undefined }}
    >
      <textarea
        ref={textareaRef}
        value={text}
        onChange={e => setText(e.target.value)}
        onKeyDown={handleKeyDown}
        onFocus={() => setFocused(true)}
        onBlur={() => setFocused(false)}
        placeholder="Ask anything about Life, Health, or Travel insurance..."
        className="flex-1 max-h-48 min-h-[24px] bg-transparent border-0 resize-none py-1 px-1 text-[#e4e4e7] placeholder-[#2a2a2a] focus:outline-none text-[13px] leading-relaxed"
        rows={1}
        disabled={disabled}
      />
      <ShimmerButton
        onClick={handleSend}
        disabled={!text.trim() || disabled}
        shimmerColor="#888888"
        background="#ffffff"
        borderRadius="8px"
        className="shrink-0 w-8 h-8 ml-2 flex items-center justify-center disabled:opacity-30 disabled:cursor-not-allowed"
      >
        <Send className="w-3.5 h-3.5 text-black" />
      </ShimmerButton>

      {focused && (
        <BorderBeam size={80} duration={3} colorFrom="#ffffff" colorTo="#444444" />
      )}
    </div>
  )
}
