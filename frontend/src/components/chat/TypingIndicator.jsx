import { MorphingText } from '../magicui/morphing-text'

const THINKING_STRINGS = [
  "Analyzing query...",
  "Consulting policy documents...",
  "Evaluating optimal plans...",
  "Calculating premiums...",
  "Synthesizing response...",
]

export default function TypingIndicator({ status }) {
  const strings = status && THINKING_STRINGS.includes(status)
    ? [status]
    : THINKING_STRINGS

  return (
    <div className="flex items-center gap-3 px-4 py-3 bg-[#0f0f0f] border border-[#1a1a1a] rounded-xl rounded-tl-sm w-fit max-w-[280px]">
      {/* Animated dots */}
      <div className="flex gap-1 items-center shrink-0">
        {[0, 1, 2].map(i => (
          <span
            key={i}
            className="w-1.5 h-1.5 rounded-full bg-[#444]"
            style={{
              animation: `typing-bounce 1.2s ease infinite`,
              animationDelay: `${i * 0.2}s`,
            }}
          />
        ))}
      </div>
      {/* Morphing status text */}
      <MorphingText
        texts={strings}
        className="text-[11px] text-[#444] font-normal"
      />
    </div>
  )
}
