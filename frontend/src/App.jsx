import { useState, useRef, useEffect } from 'react'
import { Bot, Umbrella, Plus } from 'lucide-react'
import ChatBox from './components/ChatBox'
import InputArea from './components/InputArea'

function App() {
  const [messages, setMessages] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [loadingStatus, setLoadingStatus] = useState("Initializing...")
  const [threadId, setThreadId] = useState(() => crypto.randomUUID())
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
     // Initial greeting
     setMessages([{
         id: 'init',
         role: 'assistant',
         content: "Hello! I am your AI Insurance Advisor. I can help you find the best Life, Health, or Travel insurance policies. How can I help you today?"
     }])
  }, [])

  const handleSendMessage = async (text) => {
    if (!text.trim()) return

    const userMessage = { id: crypto.randomUUID(), role: 'user', content: text }
    setMessages(prev => [...prev, userMessage])
    setIsLoading(true)

    try {
      setLoadingStatus("Connecting to advisor...")
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text, thread_id: threadId })
      })

      if (!response.ok) {
        throw new Error('API request failed')
      }

      // Read SSE Stream
      const reader = response.body.getReader()
      const decoder = new TextDecoder("utf-8")
      let done = false
      let currentEvent = null
      let buffer = ""

      while (!done) {
          const { value, done: readerDone } = await reader.read()
          done = readerDone
          
          if (value) {
              buffer += decoder.decode(value, { stream: true })
              
              // Process complete SSE events delimited by double newlines
              let boundary = buffer.indexOf('\n\n')
              while (boundary !== -1) {
                  const eventChunk = buffer.substring(0, boundary)
                  buffer = buffer.substring(boundary + 2)
                  
                  const lines = eventChunk.split('\n')
                  for (const line of lines) {
                      if (line.startsWith('event: ')) {
                          currentEvent = line.substring(7).trim()
                      } else if (line.startsWith('data: ')) {
                          const dataStr = line.substring(6).trim()
                          if (!dataStr) continue
                          
                          try {
                              const data = JSON.parse(dataStr)
                              
                              if (currentEvent === 'status') {
                                  // Friendly node mappings mappings
                                  const statusMap = {
                                      "agent": "Analyzing query...",
                                      "policy_expert": "Consulting policy documents...",
                                      "recommendation": "Evaluating optimal plans...",
                                      "quick_premium": "Calculating potential premiums...",
                                      "merger_node": "Synthesizing final response..."
                                  }
                                  setLoadingStatus(statusMap[data.node] || `Executing: ${data.node}...`)
                              } 
                              else if (currentEvent === 'message') {
                                  const aiMessage = { 
                                      id: crypto.randomUUID(), 
                                      role: 'assistant', 
                                      content: data.response || "Sorry, I received an empty response."
                                  }
                                  setMessages(prev => [...prev, aiMessage])
                              }
                              else if (currentEvent === 'error') {
                                  throw new Error(`__API_ERROR__${data.error}`)
                              }
                          } catch (e) {
                              if (e.message && e.message.startsWith('__API_ERROR__')) {
                                  throw e // Bubble up intended system errors instantly 
                              }
                              console.error("Failed to parse SSE data string:", dataStr, e)
                          }
                      }
                  }
                  
                  // Re-evaluate next boundary
                  boundary = buffer.indexOf('\n\n')
              }
          }
      }
      
    } catch (error) {
      console.error(error)
      
      let displayMessage = "Sorry, I encountered an error connecting to the server. Please ensure the backend is running."
      
      if (error.message && error.message.startsWith('__API_ERROR__')) {
          displayMessage = `**Backend Error Stopped Execution:**\n\n\`\`\`json\n${error.message.replace('__API_ERROR__', '')}\n\`\`\``
      }
      
      setMessages(prev => [...prev, { 
          id: crypto.randomUUID(), 
          role: 'assistant', 
          content: displayMessage
      }])
    } finally {
      setIsLoading(false)
    }
  }

  const handleNewChat = () => {
    setThreadId(crypto.randomUUID())
    setMessages([{
         id: 'init',
         role: 'assistant',
         content: "Hello! I am your AI Insurance Advisor. I can help you find the best Life, Health, or Travel insurance policies. How can I help you today?"
     }])
  }

  return (
    <div className="flex h-screen w-full bg-dark-bg text-zinc-100 flex-col md:flex-row">
      {/* Sidebar - Desktop Only (Placeholder for history) */}
      <div className="hidden md:flex flex-col w-64 border-r border-dark-border bg-dark-surface p-4">
        <div className="flex items-center gap-2 mb-8 px-2 mt-2">
            <Umbrella className="w-6 h-6 text-primary-500" />
            <span className="font-semibold text-lg tracking-tight">Insurance Advisor</span>
        </div>
        <div className="text-xs font-semibold text-zinc-500 uppercase tracking-wider mb-3 px-2">Today</div>
        <button className="flex items-center gap-2 px-3 py-2 rounded-lg bg-zinc-800/50 text-sm font-medium border border-white/5 w-full text-left transition-colors hover:bg-zinc-800">
            <Bot className="w-4 h-4 text-zinc-400" />
            <span className="truncate">Current Session</span>
        </button>
        
        <button 
            onClick={handleNewChat}
            className="flex items-center justify-center gap-2 px-3 py-2 mt-4 rounded-lg bg-primary-600 text-white text-sm font-medium transition-colors hover:bg-primary-500 w-full"
        >
            <Plus className="w-4 h-4" />
            <span>New Chat</span>
        </button>
        <div className="mt-auto px-2 text-xs text-zinc-500 break-all">
            Thread: <br/>
            <span className="text-[10px] text-zinc-600 font-mono">{threadId}</span>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex flex-col flex-1 h-full relative">
        {/* Mobile Header */}
        <header className="md:hidden flex items-center justify-between h-14 border-b border-dark-border bg-dark-surface/90 backdrop-blur px-4 shrink-0 absolute top-0 w-full z-10">
            <div className="flex items-center">
              <Umbrella className="w-6 h-6 text-primary-500 mr-2" />
              <span className="font-semibold text-lg">Advisor</span>
            </div>
            <button onClick={handleNewChat} className="p-1.5 rounded-md hover:bg-zinc-800 text-zinc-300 transition-colors">
               <Plus className="w-5 h-5" />
            </button>
        </header>
        
        <main className="flex-1 overflow-y-auto custom-scrollbar md:pt-0 pt-14 pb-32">
           <ChatBox messages={messages} isLoading={isLoading} loadingStatus={loadingStatus} onSendClick={handleSendMessage} />
           <div ref={messagesEndRef} />
        </main>
        
        <div className="absolute bottom-0 w-full bg-gradient-to-t from-dark-bg via-dark-bg/95 to-transparent pt-8 pb-6 px-4">
           <div className="max-w-3xl mx-auto">
             <InputArea onSend={handleSendMessage} disabled={isLoading} />
             <div className="text-center mt-3 text-xs text-zinc-500 font-medium">
                Agentic systems can make mistakes. Verify important policy details.
             </div>
           </div>
        </div>
      </div>
    </div>
  )
}

export default App
