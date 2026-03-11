import { useState, useCallback } from 'react'
import AppShell from './components/layout/AppShell'

const GREETING = "Hello! I'm your AI Insurance Advisor. I can help you find the best Life, Health, or Travel insurance policies tailored to your needs. How can I help you today?"

const STATUS_MAP = {
  agent:           "Analyzing query...",
  policy_expert:   "Consulting policy documents...",
  recommendation:  "Evaluating optimal plans...",
  quick_premium:   "Calculating premiums...",
  merger_node:     "Synthesizing response...",
}

function App() {
  // ── Chat state (preserved from original) ──────────────────────────
  const [messages, setMessages] = useState([
    { id: 'init', role: 'assistant', content: GREETING }
  ])
  const [isLoading, setIsLoading] = useState(false)
  const [loadingStatus, setLoadingStatus] = useState("Initializing...")
  const [threadId, setThreadId] = useState(() => crypto.randomUUID())

  // ── Dashboard state (new) ─────────────────────────────────────────
  const [activeSection, setActiveSection] = useState('chat')
  const [userProfile, setUserProfile] = useState({
    name: '', age: '', annualIncome: '', smoker: false,
    gender: '', occupation: 'salaried', dependents: 0,
  })
  const [savedQuotes, setSavedQuotes] = useState([])
  const [conversationHistory, setConversationHistory] = useState(
    () => JSON.parse(localStorage.getItem('ia_history') || '[]')
  )
  const [isFirstMessage, setIsFirstMessage] = useState(true)

  // ── Handlers ──────────────────────────────────────────────────────
  const handleNewChat = useCallback(() => {
    const newId = crypto.randomUUID()
    setThreadId(newId)
    setMessages([{ id: 'init', role: 'assistant', content: GREETING }])
    setIsFirstMessage(true)
  }, [])

  const onResumeThread = useCallback((threadEntry) => {
    setThreadId(threadEntry.id)
    setMessages([{ id: 'init', role: 'assistant', content: GREETING }])
    setActiveSection('chat')
    setIsFirstMessage(false)
  }, [])

  const onSaveQuote = useCallback(() => {
    const lastAI = [...messages].reverse().find(m => m.role === 'assistant')
    if (!lastAI) return
    const quote = {
      id: crypto.randomUUID(),
      planName: 'Quote from Chat',
      company: '',
      cover: '',
      premiumMonthly: 0,
      csr: '',
      savedAt: new Date().toISOString(),
      threadId,
      snippet: lastAI.content.slice(0, 120),
    }
    setSavedQuotes(prev => [quote, ...prev])
    setActiveSection('quotes')
  }, [messages, threadId])

  const onProfileSave = useCallback((profile) => {
    setUserProfile(profile)
  }, [])

  const handleSendMessage = useCallback(async (text) => {
    if (!text.trim()) return

    // On first message of a new thread, save to history
    if (isFirstMessage) {
      const historyEntry = {
        id: threadId,
        title: text.slice(0, 60),
        createdAt: new Date().toISOString(),
        messageCount: 1,
      }
      const updated = [historyEntry, ...conversationHistory]
      setConversationHistory(updated)
      localStorage.setItem('ia_history', JSON.stringify(updated))
      setIsFirstMessage(false)
    }

    const userMessage = { id: crypto.randomUUID(), role: 'user', content: text }
    setMessages(prev => [...prev, userMessage])
    setIsLoading(true)

    try {
      setLoadingStatus("Connecting to advisor...")
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text, thread_id: threadId }),
      })

      if (!response.ok) throw new Error('API request failed')

      const reader = response.body.getReader()
      const decoder = new TextDecoder('utf-8')
      let done = false
      let currentEvent = null
      let buffer = ''

      while (!done) {
        const { value, done: readerDone } = await reader.read()
        done = readerDone
        if (value) {
          buffer += decoder.decode(value, { stream: true })
          let boundary = buffer.indexOf('\n\n')
          while (boundary !== -1) {
            const chunk = buffer.substring(0, boundary)
            buffer = buffer.substring(boundary + 2)
            for (const line of chunk.split('\n')) {
              if (line.startsWith('event: ')) {
                currentEvent = line.substring(7).trim()
              } else if (line.startsWith('data: ')) {
                const dataStr = line.substring(6).trim()
                if (!dataStr) continue
                try {
                  const data = JSON.parse(dataStr)
                  if (currentEvent === 'status') {
                    setLoadingStatus(STATUS_MAP[data.node] || `Executing: ${data.node}...`)
                  } else if (currentEvent === 'message') {
                    setMessages(prev => [...prev, {
                      id: crypto.randomUUID(),
                      role: 'assistant',
                      content: data.response || 'Sorry, I received an empty response.',
                    }])
                  } else if (currentEvent === 'error') {
                    throw new Error(`__API_ERROR__${data.error}`)
                  }
                } catch (e) {
                  if (e.message?.startsWith('__API_ERROR__')) throw e
                  console.error('Failed to parse SSE data:', dataStr, e)
                }
              }
            }
            boundary = buffer.indexOf('\n\n')
          }
        }
      }
    } catch (error) {
      let msg = 'Sorry, I encountered an error. Please ensure the backend is running.'
      if (error.message?.startsWith('__API_ERROR__')) {
        msg = `**Backend Error:**\n\n\`\`\`json\n${error.message.replace('__API_ERROR__', '')}\n\`\`\``
      }
      setMessages(prev => [...prev, { id: crypto.randomUUID(), role: 'assistant', content: msg }])
    } finally {
      setIsLoading(false)
    }
  }, [threadId, isFirstMessage, conversationHistory])

  const chatProps = {
    messages,
    isLoading,
    loadingStatus,
    threadId,
    onSend: handleSendMessage,
    onNewChat: handleNewChat,
    onSaveQuote,
    onResumeThread,
  }

  return (
    <AppShell
      activeSection={activeSection}
      setActiveSection={setActiveSection}
      chatProps={chatProps}
      appState={{ savedQuotes, conversationHistory, userProfile, onProfileSave }}
    />
  )
}

export default App
