# Insurance Advisor Dashboard Redesign Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Redesign the Insurance Advisor frontend into a full 6-section Obsidian Minimal dashboard with shadcn/ui + MagicUI effects and fix the policy markdown table rendering bug.

**Architecture:** State-based SPA (no React Router) — a single `activeSection` state in `App.jsx` drives section switching. New layout shell (`AppShell` → `Sidebar` + `TopBar`) wraps all 6 sections. All existing SSE streaming logic is preserved intact.

**Tech Stack:** React 18, Vite 5, Tailwind v4, shadcn/ui, MagicUI, framer-motion, remark-gfm, lucide-react

**Spec:** `docs/superpowers/specs/2026-03-11-insurance-advisor-dashboard-redesign.md`

---

## Chunk 1: Foundation — Dependencies, Theme, Tooling

### Task 1: Install all npm dependencies

**Files:**
- Modify: `frontend/package.json`

- [ ] **Step 1: Install runtime dependencies**

```bash
cd frontend
npm install remark-gfm react-markdown framer-motion clsx tailwind-merge class-variance-authority lucide-react
```

Note: `react-markdown` is already in `devDependencies` — this command moves it to proper `dependencies` (runtime). `lucide-react` is also promoted from devDependencies to dependencies.

Expected: All packages install without peer dependency errors.

- [ ] **Step 2: Verify Vite handles .tsx files (MagicUI uses TypeScript)**

Create a minimal `tsconfig.json` in `frontend/` so Vite + esbuild can process MagicUI's `.tsx` component files:

```json
// frontend/tsconfig.json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": false,
    "allowJs": true
  },
  "include": ["src"]
}
```

- [ ] **Step 3: Run dev server to verify nothing broke**

```bash
cd frontend && npm run dev
```

Expected: App runs at `http://localhost:5173` with no console errors.

- [ ] **Step 4: Commit**

```bash
cd frontend
git add package.json package-lock.json tsconfig.json
git commit -m "feat: add dashboard redesign dependencies (remark-gfm, framer-motion, clsx, shadcn utils)"
```

---

### Task 2: Initialize shadcn/ui

**Files:**
- Create: `frontend/src/lib/utils.js`
- Create: `frontend/components.json`
- Modify: `frontend/src/index.css` (shadcn appends CSS variable block)

- [ ] **Step 1: Run shadcn init from the frontend directory**

⚠️ **Tailwind v4 + shadcn compatibility note:** This project uses `@tailwindcss/vite` (Tailwind v4), NOT the PostCSS plugin. `shadcn@latest` as of early 2026 has Tailwind v4 support but may still attempt to generate a `tailwind.config.js`. If it does, **delete that file** — it conflicts with the Vite plugin approach. All Tailwind config belongs in `index.css` via `@theme`. If shadcn init fails or reports an incompatible Tailwind version, run with `--no-tailwind` flag and manually copy the CSS variable block from shadcn docs into `index.css` after the `@theme` block.

```bash
cd frontend
npx shadcn@latest init --style default --base-color zinc --css-variables true
```

When prompted:
- Which style? → `Default`
- Which color? → `Zinc`
- Use CSS variables? → `yes`
- Where is your CSS file? → `src/index.css`
- Where to put components? → `src/components/ui`
- Where to put utils? → `src/lib/utils` (auto-generated — do not create manually)
- Use RSC? → `no`
- Use TypeScript? → `no` (we're using JSX)

Note: shadcn will append `:root { --background: ... }` CSS variables to `index.css`. These coexist with our Tailwind `@theme` block. If `tailwind.config.js` is generated, delete it.

- [ ] **Step 2: Add all required shadcn components**

```bash
cd frontend
npx shadcn@latest add button input label select card table accordion scroll-area separator badge tooltip sheet
```

Expected: Files appear in `src/components/ui/`.

- [ ] **Step 3: Install MagicUI components**

```bash
cd frontend
npx magicui@latest add border-beam
npx magicui@latest add magic-card
npx magicui@latest add number-ticker
npx magicui@latest add blur-fade
npx magicui@latest add shimmer-button
npx magicui@latest add dot-pattern
npx magicui@latest add morphing-text
npx magicui@latest add confetti
npx magicui@latest add animated-shiny-text
```

Expected: Files appear in `src/components/magicui/`.

⚠️ **MagicUI prop verification:** After install, open each installed `.tsx` file and check the exported component's props interface before using it. Key components to verify:
- `AnimatedShinyText` — check if it accepts `className` directly or requires a wrapper
- `ShimmerButton` — verify `shimmerColor`, `background`, `borderRadius` prop names
- `MorphingText` — verify prop name for the array of strings (`texts` vs `words`)
- `DotPattern` — verify prop names for dot spacing (`cx`, `cy`, `cr` vs `width`, `height`, `radius`)

If any prop name differs from what's shown in the plan, adjust the component usage to match the installed file's actual interface.

- [ ] **Step 4: Run dev server — verify no import errors**

```bash
cd frontend && npm run dev
```

Expected: Existing app still loads. Console may show Tailwind CSS variable warnings — these are harmless.

- [ ] **Step 5: Commit**

```bash
cd frontend
git add src/components/ui src/components/magicui src/lib components.json
git commit -m "feat: add shadcn/ui and magicui component libraries"
```

---

### Task 3: Update Tailwind theme + fix App.css

**Files:**
- Modify: `frontend/src/index.css`
- Modify: `frontend/src/App.css`

- [ ] **Step 1: Replace the `@theme` block in `frontend/src/index.css`**

Find the existing `@theme { ... }` block (lines 3–20) and replace it entirely:

```css
@theme {
  --font-sans: "Inter", ui-sans-serif, system-ui, sans-serif;

  /* Obsidian Minimal palette */
  --color-bg:           #080808;
  --color-surface:      #0f0f0f;
  --color-surface-2:    #111111;
  --color-border:       #1a1a1a;
  --color-border-2:     #222222;
  --color-text:         #e4e4e7;
  --color-text-2:       #888888;
  --color-text-muted:   #444444;
  --color-accent:       #ffffff;

  /* Backwards compat — all primary-* map to white/near-white */
  --color-primary-50:   #f4f4f5;
  --color-primary-100:  #e4e4e7;
  --color-primary-200:  #d4d4d8;
  --color-primary-300:  #a1a1aa;
  --color-primary-400:  #71717a;
  --color-primary-500:  #ffffff;
  --color-primary-600:  #e4e4e7;
  --color-primary-700:  #d4d4d8;
  --color-primary-800:  #a1a1aa;
  --color-primary-900:  #71717a;

  /* Legacy aliases */
  --color-dark-bg:      #080808;
  --color-dark-surface: #0f0f0f;
  --color-dark-border:  #1a1a1a;
}
```

- [ ] **Step 2: Update the `body` rule in `index.css`**

```css
body {
  @apply bg-bg text-text font-sans antialiased h-screen w-screen overflow-hidden;
}
```

- [ ] **Step 3: Replace the `.markdown-table` block in `index.css` (lines 54–78)**

```css
/* Rich Markdown Table Styling — Obsidian theme */
.markdown-table-wrapper {
  @apply overflow-hidden rounded-lg border border-[#1e1e1e] my-3 bg-[#0a0a0a];
}
.markdown-table { @apply w-full text-left text-xs border-collapse; }
.markdown-table th {
  @apply bg-[#141414] px-3 py-2 font-medium text-[#888] uppercase tracking-wider
         text-[10px] border-b border-[#1e1e1e];
}
.markdown-table td { @apply px-3 py-2 border-b border-[#161616] text-[#aaa]; }
.markdown-table tbody tr:hover td { @apply bg-[#0f0f0f]; }
.markdown-table tbody tr:last-child td { @apply border-0; }

/* Paragraph and list spacing in AI responses */
.prose p { @apply my-1.5; }
.prose ul, .prose ol { @apply my-1.5; }
.prose li { @apply my-0.5; }
```

- [ ] **Step 4: Remove stale CSS utilities that reference old color tokens**

In `index.css`, delete the following blocks entirely (they reference `dark-surface`, `zinc-700`, `zinc-600` which no longer exist in the new theme):

- The `.glass-panel` block (all 3 lines)
- The `.custom-scrollbar` block (all 4 rules)

These are replaced by inline Tailwind classes with the new hex values throughout the new components.

- [ ] **Step 5: Clear `frontend/src/App.css`**

Replace entire file content with:
```css
/* cleared — Vite scaffold styles removed to allow full-bleed dashboard layout */
```

- [ ] **Step 5: Verify dev server renders with new dark theme**

```bash
cd frontend && npm run dev
```

Expected: App loads with `#080808` background. Existing chat still functions.

- [ ] **Step 6: Commit**

```bash
cd frontend
git add src/index.css src/App.css
git commit -m "feat: apply Obsidian Minimal theme to Tailwind + fix markdown-table Obsidian colors"
```

---

## Chunk 2: Layout Shell — AppShell, Sidebar, TopBar, App.jsx

### Task 4: Create Sidebar component

**Files:**
- Create: `frontend/src/components/layout/Sidebar.jsx`

- [ ] **Step 1: Create `frontend/src/components/layout/Sidebar.jsx`**

```jsx
import { MessageSquare, User, LayoutGrid, Clock, BookOpen, Star } from 'lucide-react'
import { BorderBeam } from '../magicui/border-beam'
import { AnimatedShinyText } from '../magicui/animated-shiny-text'
import { cn } from '../../lib/utils'

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
```

- [ ] **Step 2: Verify file was created with no syntax errors**

```bash
cd frontend && npm run build 2>&1 | head -20
```

Expected: No errors for `Sidebar.jsx`. (Build may fail on missing imports — that's okay at this stage.)

---

### Task 5: Create TopBar component

**Files:**
- Create: `frontend/src/components/layout/TopBar.jsx`

- [ ] **Step 1: Create `frontend/src/components/layout/TopBar.jsx`**

```jsx
import { Plus, Star } from 'lucide-react'
import { ShimmerButton } from '../magicui/shimmer-button'
import { cn } from '../../lib/utils'

const SECTION_LABELS = {
  chat:       { title: 'AI Chat',          sub: 'Multi-agent insurance advisor' },
  profile:    { title: 'My Profile',       sub: 'Your insurance profile' },
  comparison: { title: 'Plan Comparison',  sub: 'Compare recommended plans' },
  history:    { title: 'History',          sub: 'Past conversations' },
  library:    { title: 'Policy Library',   sub: 'All available plans' },
  quotes:     { title: 'Saved Quotes',     sub: 'Bookmarked plans' },
}

export default function TopBar({ activeSection, chatProps }) {
  const { title, sub } = SECTION_LABELS[activeSection] || SECTION_LABELS.chat
  const { onNewChat, onSaveQuote, threadId } = chatProps || {}

  return (
    <header className="h-[52px] shrink-0 border-b border-[#111] flex items-center px-5 gap-3 bg-[#080808]/80 backdrop-blur-sm">
      {/* Live status dot (chat only) */}
      {activeSection === 'chat' && (
        <span className="relative flex h-2 w-2 shrink-0">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-40" />
          <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500" />
        </span>
      )}

      {/* Title */}
      <div className="min-w-0">
        <h1 className="text-[13px] font-medium text-[#e4e4e7] leading-none">{title}</h1>
        <p className="text-[11px] text-[#333] mt-0.5 truncate">{sub}</p>
      </div>

      {/* Actions */}
      <div className="ml-auto flex items-center gap-2">
        {activeSection === 'chat' && (
          <>
            <button
              onClick={onNewChat}
              className="h-7 px-2.5 rounded-md border border-[#1e1e1e] bg-transparent text-[#555] text-[11px] flex items-center gap-1.5 hover:bg-[#111] hover:text-[#888] hover:border-[#222] transition-all"
            >
              <Plus className="w-3 h-3" />
              New Chat
            </button>
            <ShimmerButton
              onClick={onSaveQuote}
              shimmerColor="#888"
              background="#0f0f0f"
              borderRadius="6px"
              className="h-7 px-2.5 text-[11px] font-medium text-white border border-[#222]"
            >
              <Star className="w-3 h-3 mr-1" />
              Save Quote
            </ShimmerButton>
          </>
        )}
      </div>
    </header>
  )
}
```

---

### Task 6: Create AppShell component

**Files:**
- Create: `frontend/src/components/layout/AppShell.jsx`

- [ ] **Step 1: Create `frontend/src/components/layout/AppShell.jsx`**

```jsx
import Sidebar from './Sidebar'
import TopBar from './TopBar'
import ChatSection from '../chat/ChatSection'
import ProfileSection from '../profile/ProfileSection'
import ComparisonSection from '../comparison/ComparisonSection'
import HistorySection from '../history/HistorySection'
import LibrarySection from '../library/LibrarySection'
import QuotesSection from '../quotes/QuotesSection'

export default function AppShell({ activeSection, setActiveSection, chatProps, appState }) {
  const { savedQuotes = [], conversationHistory = [] } = appState || {}

  const sectionMap = {
    chat:       <ChatSection {...chatProps} />,
    profile:    <ProfileSection />,
    comparison: <ComparisonSection savedQuotes={savedQuotes} />,
    history:    <HistorySection
                  history={conversationHistory}
                  onResumeThread={chatProps.onResumeThread}
                />,
    library:    <LibrarySection />,
    quotes:     <QuotesSection savedQuotes={savedQuotes} />,
  }

  return (
    <div className="flex h-screen w-full bg-bg overflow-hidden">
      <Sidebar
        activeSection={activeSection}
        onNavigate={setActiveSection}
        savedQuotesCount={savedQuotes.length}
        historyCount={conversationHistory.length}
      />
      <div className="flex flex-col flex-1 min-w-0 overflow-hidden">
        <TopBar activeSection={activeSection} chatProps={chatProps} />
        <main className="flex-1 overflow-hidden">
          {sectionMap[activeSection]}
        </main>
      </div>
    </div>
  )
}
```

---

### Task 7: Rewrite App.jsx

**Files:**
- Modify: `frontend/src/App.jsx`

- [ ] **Step 1: Replace `frontend/src/App.jsx` entirely**

```jsx
import { useState, useRef, useEffect, useCallback } from 'react'
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
    // Extract last AI message for quote data — user can extend this
    const lastAI = [...messages].reverse().find(m => m.role === 'assistant')
    if (!lastAI) return
    const quote = {
      id: crypto.randomUUID(),
      planName: 'Quote from Chat',
      company: '',
      cover: '',
      premiumMonthly: 0,  // MVP: no auto-extraction; number-ticker shows 0. Future: parse from AI message.
      csr: '',
      savedAt: new Date().toISOString(),
      threadId,
      snippet: lastAI.content.slice(0, 120),
    }
    setSavedQuotes(prev => [quote, ...prev])
    setActiveSection('quotes')
  }, [messages, threadId])

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
      appState={{ savedQuotes, conversationHistory, userProfile }}
    />
  )
}

export default App
```

- [ ] **Step 2: Run dev server and verify the app still loads**

```bash
cd frontend && npm run dev
```

Expected: App loads. You'll see import errors for missing section components — that's expected. Fix: create placeholder files next.

---

### Task 8: Create placeholder section stubs (so AppShell can import without errors)

**Files:**
- Create: `frontend/src/components/chat/ChatSection.jsx` (stub)
- Create: `frontend/src/components/profile/ProfileSection.jsx` (stub)
- Create: `frontend/src/components/comparison/ComparisonSection.jsx` (stub)
- Create: `frontend/src/components/history/HistorySection.jsx` (stub)
- Create: `frontend/src/components/library/LibrarySection.jsx` (stub)
- Create: `frontend/src/components/quotes/QuotesSection.jsx` (stub)

- [ ] **Step 1: Create stub for each section**

`frontend/src/components/chat/ChatSection.jsx`:
```jsx
export default function ChatSection() {
  return <div className="h-full flex items-center justify-center text-[#444] text-sm">Chat — coming soon</div>
}
```

`frontend/src/components/profile/ProfileSection.jsx`:
```jsx
export default function ProfileSection() {
  return <div className="h-full flex items-center justify-center text-[#444] text-sm">Profile — coming soon</div>
}
```

`frontend/src/components/comparison/ComparisonSection.jsx`:
```jsx
export default function ComparisonSection() {
  return <div className="h-full flex items-center justify-center text-[#444] text-sm">Comparison — coming soon</div>
}
```

`frontend/src/components/history/HistorySection.jsx`:
```jsx
export default function HistorySection() {
  return <div className="h-full flex items-center justify-center text-[#444] text-sm">History — coming soon</div>
}
```

`frontend/src/components/library/LibrarySection.jsx`:
```jsx
export default function LibrarySection() {
  return <div className="h-full flex items-center justify-center text-[#444] text-sm">Library — coming soon</div>
}
```

`frontend/src/components/quotes/QuotesSection.jsx`:
```jsx
export default function QuotesSection() {
  return <div className="h-full flex items-center justify-center text-[#444] text-sm">Quotes — coming soon</div>
}
```

- [ ] **Step 2: Run dev server — all 6 nav items should be clickable**

```bash
cd frontend && npm run dev
```

Expected: Sidebar renders, clicking each item switches the main area content. App is functional as a skeleton.

- [ ] **Step 3: Commit layout shell**

```bash
cd frontend
git add src/
git commit -m "feat: add AppShell + Sidebar + TopBar layout with state-based section routing"
```

---

## Chunk 3: Policy Fix + Chat Section

### Task 9: Fix markdown table rendering (remark-gfm)

**Files:**
- Modify: `frontend/src/components/MessageBubble.jsx`

- [ ] **Step 1: Add `remark-gfm` import and plugin to `MessageBubble.jsx`**

At the top of the file, after the existing imports, add:
```jsx
import remarkGfm from 'remark-gfm'
```

Find the `<ReactMarkdown>` element (currently at line 59):
```jsx
<ReactMarkdown>{displayContent}</ReactMarkdown>
```
Replace with:
```jsx
<ReactMarkdown remarkPlugins={[remarkGfm]}>{displayContent}</ReactMarkdown>
```

- [ ] **Step 2: Verify fix in browser**

With backend running, send: `"I'm 32, earn ₹18L/year. What term life insurance should I get?"`

Expected: AI response with policy comparison renders as a **formatted table** (aligned columns, styled rows) instead of raw `| Company | Plan | Premium |` pipe text.

---

### Task 10: Create TypingIndicator

**Files:**
- Create: `frontend/src/components/chat/TypingIndicator.jsx`

- [ ] **Step 1: Create `frontend/src/components/chat/TypingIndicator.jsx`**

```jsx
import { MorphingText } from '../magicui/morphing-text'

const THINKING_STRINGS = [
  "Analyzing query...",
  "Consulting policy documents...",
  "Evaluating optimal plans...",
  "Calculating premiums...",
  "Synthesizing response...",
]

export default function TypingIndicator({ status }) {
  // Use the active status string if it matches a known one, otherwise use morphing list
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
```

Add the `typing-bounce` keyframe to `index.css`:
```css
@keyframes typing-bounce {
  0%, 80%, 100% { transform: scale(0.6); opacity: 0.3; }
  40% { transform: scale(1); opacity: 1; }
}
```

---

### Task 11: Rebuild MessageBubble with effects

**Files:**
- Modify: `frontend/src/components/MessageBubble.jsx` (replace entirely — keep pill extraction logic)

- [ ] **Step 1: Replace `frontend/src/components/MessageBubble.jsx`**

```jsx
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { User, ArrowRight } from 'lucide-react'
import { BlurFade } from '../magicui/blur-fade'
import { MagicCard } from '../magicui/magic-card'

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
                      // Inject .markdown-table-wrapper and .markdown-table CSS classes
                      // so the existing index.css styles are applied to GFM tables
                      table: ({ node, ...props }) => (
                        <div className="markdown-table-wrapper">
                          <table className="markdown-table" {...props} />
                        </div>
                      ),
                      thead: ({ node, ...props }) => <thead {...props} />,
                      tbody: ({ node, ...props }) => <tbody {...props} />,
                      tr: ({ node, ...props }) => <tr {...props} />,
                      th: ({ node, ...props }) => <th {...props} />,
                      td: ({ node, ...props }) => <td {...props} />,
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
```

---

### Task 12: Update InputArea with ShimmerButton + BorderBeam

**Files:**
- Modify: `frontend/src/components/InputArea.jsx` (replace entirely)

- [ ] **Step 1: Replace `frontend/src/components/InputArea.jsx`**

```jsx
import { useState, useRef, useEffect } from 'react'
import { Send } from 'lucide-react'
import { BorderBeam } from '../magicui/border-beam'
import { ShimmerButton } from '../magicui/shimmer-button'

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
      {/* ShimmerButton for send — shimmer sweeps across the button surface */}
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
```

---

### Task 13: Create MessageList

**Files:**
- Create: `frontend/src/components/chat/MessageList.jsx`

- [ ] **Step 1: Create `frontend/src/components/chat/MessageList.jsx`**

```jsx
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
```

---

### Task 14: Build full ChatSection (replaces ChatBox)

**Files:**
- Modify: `frontend/src/components/chat/ChatSection.jsx` (replace stub)
- Delete: `frontend/src/components/ChatBox.jsx`

- [ ] **Step 1: Replace `frontend/src/components/chat/ChatSection.jsx`**

```jsx
import MessageList from './MessageList'
import InputArea from '../InputArea'

export default function ChatSection({ messages, isLoading, loadingStatus, onSend }) {
  return (
    <div className="flex flex-col h-full bg-bg overflow-hidden">
      <MessageList
        messages={messages}
        isLoading={isLoading}
        loadingStatus={loadingStatus}
        onSendClick={onSend}
      />
      <div className="shrink-0 px-5 pb-5 pt-3 border-t border-[#111] bg-[#080808]">
        <div className="max-w-3xl mx-auto">
          <InputArea onSend={onSend} disabled={isLoading} />
          <p className="text-center mt-2 text-[10px] text-[#2a2a2a]">
            AI responses may be inaccurate. Verify important policy details independently.
          </p>
        </div>
      </div>
    </div>
  )
}
```

- [ ] **Step 2: Delete `frontend/src/components/ChatBox.jsx`**

```bash
rm frontend/src/components/ChatBox.jsx
```

- [ ] **Step 3: Remove ChatBox import from App.jsx (if still present)**

Check `App.jsx` for any remaining `import ChatBox` lines and delete them. (The rewrite in Task 7 should have removed it already.)

- [ ] **Step 4: Run dev server — verify full chat flow works**

```bash
cd frontend && npm run dev
```

Expected:
- Sidebar renders with 6 nav items
- Chat section shows dot-pattern background, message bubbles with blur-fade animation
- Sending a message streams back AI response
- AI response tables render as formatted tables (remark-gfm fix active)
- TypingIndicator shows morphing text while streaming

- [ ] **Step 5: Commit**

```bash
cd frontend
git add src/
git rm src/components/ChatBox.jsx
git commit -m "feat: rebuild chat section with remark-gfm table fix, blur-fade messages, magic-card bubbles, morphing typing indicator"
```

---

## Chunk 4: Profile + Comparison + History Sections

### Task 15: Build ProfileSection

**Files:**
- Modify: `frontend/src/components/profile/ProfileSection.jsx` (replace stub)

- [ ] **Step 1: Install canvas-confetti**

```bash
cd frontend && npm install canvas-confetti
```

Note: The MagicUI `confetti` component wraps `canvas-confetti` internally, but we import `canvas-confetti` directly for the imperative API (`confetti({ particleCount: ... })`). Installing it explicitly ensures it's in `package.json`.

- [ ] **Step 2: Replace `frontend/src/components/profile/ProfileSection.jsx`**

```jsx
import { useState } from 'react'
import { BlurFade } from '../magicui/blur-fade'
import confetti from 'canvas-confetti'

const OCCUPATIONS = ['salaried', 'self-employed', 'business-owner', 'retired', 'student']
const GENDERS = ['male', 'female', 'prefer-not-to-say']

export default function ProfileSection({ userProfile = {}, onProfileSave }) {
  const [form, setForm] = useState({
    name: '', age: '', annualIncome: '', smoker: false,
    gender: '', occupation: 'salaried', dependents: 0,
    ...userProfile,
  })
  const [saved, setSaved] = useState(false)

  const update = (key, value) => setForm(prev => ({ ...prev, [key]: value }))

  const handleSave = () => {
    onProfileSave?.(form)
    setSaved(true)
    confetti({ particleCount: 80, spread: 60, origin: { y: 0.6 }, colors: ['#fff', '#888', '#444'] })
    setTimeout(() => setSaved(false), 3000)
  }

  const inputClass = "w-full bg-[#0f0f0f] border border-[#1e1e1e] rounded-lg px-3 py-2 text-[13px] text-[#e4e4e7] placeholder-[#333] focus:outline-none focus:border-[#333] transition-colors"
  const labelClass = "block text-[11px] font-medium text-[#555] uppercase tracking-wider mb-1.5"

  return (
    <div className="h-full overflow-y-auto px-6 py-6
      [&::-webkit-scrollbar]:w-[3px]
      [&::-webkit-scrollbar-track]:bg-transparent
      [&::-webkit-scrollbar-thumb]:bg-[#1e1e1e]"
    >
      <div className="max-w-xl mx-auto">
        <BlurFade delay={0.05}>
          <h2 className="text-[15px] font-semibold text-[#e4e4e7] mb-1">Your Insurance Profile</h2>
          <p className="text-[12px] text-[#444] mb-6">This profile helps the AI advisor tailor recommendations to your specific situation.</p>
        </BlurFade>

        <div className="flex flex-col gap-5">
          {/* Name */}
          <BlurFade delay={0.1}>
            <label className={labelClass}>Full Name</label>
            <input className={inputClass} value={form.name} onChange={e => update('name', e.target.value)} placeholder="Your name" />
          </BlurFade>

          {/* Age + Income */}
          <BlurFade delay={0.15}>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className={labelClass}>Age</label>
                <input type="number" className={inputClass} value={form.age} onChange={e => update('age', e.target.value)} placeholder="e.g. 32" min={18} max={70} />
              </div>
              <div>
                <label className={labelClass}>Annual Income (₹)</label>
                <input type="number" className={inputClass} value={form.annualIncome} onChange={e => update('annualIncome', e.target.value)} placeholder="e.g. 1800000" />
              </div>
            </div>
          </BlurFade>

          {/* Gender + Occupation */}
          <BlurFade delay={0.2}>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className={labelClass}>Gender</label>
                <select className={inputClass} value={form.gender} onChange={e => update('gender', e.target.value)}>
                  <option value="">Select</option>
                  {GENDERS.map(g => <option key={g} value={g}>{g.replace('-', ' ')}</option>)}
                </select>
              </div>
              <div>
                <label className={labelClass}>Occupation</label>
                <select className={inputClass} value={form.occupation} onChange={e => update('occupation', e.target.value)}>
                  {OCCUPATIONS.map(o => <option key={o} value={o}>{o.replace('-', ' ')}</option>)}
                </select>
              </div>
            </div>
          </BlurFade>

          {/* Dependents */}
          <BlurFade delay={0.25}>
            <label className={labelClass}>Number of Dependents</label>
            <input type="number" className={inputClass} value={form.dependents} onChange={e => update('dependents', parseInt(e.target.value) || 0)} min={0} max={10} />
          </BlurFade>

          {/* Smoker toggle */}
          <BlurFade delay={0.3}>
            <div className="flex items-center justify-between p-4 bg-[#0f0f0f] border border-[#1a1a1a] rounded-lg">
              <div>
                <p className="text-[13px] text-[#e4e4e7] font-medium">Smoker</p>
                <p className="text-[11px] text-[#444] mt-0.5">Smokers pay ~30% higher premiums</p>
              </div>
              <button
                onClick={() => update('smoker', !form.smoker)}
                className={`relative w-10 h-5 rounded-full transition-colors ${form.smoker ? 'bg-white' : 'bg-[#222]'}`}
              >
                <span className={`absolute top-0.5 left-0.5 w-4 h-4 rounded-full bg-[#0f0f0f] transition-transform ${form.smoker ? 'translate-x-5' : ''}`} />
              </button>
            </div>
          </BlurFade>

          {/* Save button */}
          <BlurFade delay={0.35}>
            <button
              onClick={handleSave}
              className="w-full py-2.5 bg-white text-black text-[13px] font-medium rounded-lg hover:bg-[#e4e4e7] transition-colors active:scale-[0.99]"
            >
              {saved ? '✓ Profile Saved!' : 'Save Profile'}
            </button>
          </BlurFade>
        </div>
      </div>
    </div>
  )
}
```

- [ ] **Step 2: Wire ProfileSection into AppShell — pass `userProfile` + `onProfileSave`**

In `AppShell.jsx`, update the profile section entry:
```jsx
profile: <ProfileSection
  userProfile={appState?.userProfile}
  onProfileSave={appState?.onProfileSave}
/>,
```

In `App.jsx`, add `onProfileSave` handler and pass it in `appState`:
```jsx
const onProfileSave = useCallback((profile) => {
  setUserProfile(profile)
}, [])

// In appState:
appState={{ savedQuotes, conversationHistory, userProfile, onProfileSave }}
```

---

### Task 16: Build ComparisonSection

**Files:**
- Modify: `frontend/src/components/comparison/ComparisonSection.jsx` (replace stub)

- [ ] **Step 1: Replace stub with full implementation**

```jsx
import { MagicCard } from '../magicui/magic-card'
import { NumberTicker } from '../magicui/number-ticker'
import { BlurFade } from '../magicui/blur-fade'
import { BorderBeam } from '../magicui/border-beam'

export default function ComparisonSection({ savedQuotes = [] }) {
  if (savedQuotes.length === 0) {
    return (
      <div className="h-full flex flex-col items-center justify-center gap-3 text-center px-8">
        <div className="w-12 h-12 rounded-xl bg-[#0f0f0f] border border-[#1a1a1a] flex items-center justify-center mb-2">
          <svg width="20" height="20" viewBox="0 0 16 16" fill="none">
            <rect x="1" y="1" width="6" height="6" stroke="#333" strokeWidth="1.2" rx="1"/>
            <rect x="9" y="1" width="6" height="6" stroke="#333" strokeWidth="1.2" rx="1"/>
            <rect x="1" y="9" width="6" height="6" stroke="#333" strokeWidth="1.2" rx="1"/>
            <rect x="9" y="9" width="6" height="6" stroke="#333" strokeWidth="1.2" rx="1"/>
          </svg>
        </div>
        <p className="text-[13px] text-[#555]">No plans to compare yet</p>
        <p className="text-[11px] text-[#333] max-w-[240px]">Chat with the AI advisor and click "Save Quote" to add plans here for side-by-side comparison.</p>
      </div>
    )
  }

  return (
    <div className="h-full overflow-y-auto px-6 py-6
      [&::-webkit-scrollbar]:w-[3px]
      [&::-webkit-scrollbar-track]:bg-transparent
      [&::-webkit-scrollbar-thumb]:bg-[#1e1e1e]"
    >
      <div className="max-w-4xl mx-auto">
        <BlurFade delay={0.05}>
          <h2 className="text-[15px] font-semibold text-[#e4e4e7] mb-1">Plan Comparison</h2>
          <p className="text-[12px] text-[#444] mb-6">{savedQuotes.length} saved plan{savedQuotes.length !== 1 ? 's' : ''}</p>
        </BlurFade>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {savedQuotes.map((quote, i) => (
            <BlurFade key={quote.id} delay={0.1 + i * 0.05}>
              <MagicCard
                className={`relative rounded-xl border overflow-hidden ${i === 0 ? 'border-white/20' : 'border-[#1a1a1a]'}`}
                gradientColor="#141414"
                gradientSize={150}
              >
                {i === 0 && <BorderBeam size={80} duration={4} colorFrom="#ffffff" colorTo="#444" />}
                <div className="p-4 bg-[#0f0f0f]">
                  {i === 0 && (
                    <span className="text-[9px] font-medium text-black bg-white px-2 py-0.5 rounded-full mb-2 inline-block">Best Match</span>
                  )}
                  <h3 className="text-[13px] font-semibold text-[#e4e4e7] mb-0.5">{quote.planName}</h3>
                  <p className="text-[11px] text-[#555] mb-3">{quote.company || 'From Chat'}</p>

                  <div className="flex items-baseline gap-1 mb-3">
                    <span className="text-[11px] text-[#555]">₹</span>
                    {quote.premiumMonthly > 0
                      ? <NumberTicker value={quote.premiumMonthly} className="text-[22px] font-bold text-white tabular-nums" />
                      : <span className="text-[22px] font-bold text-white">—</span>
                    }
                    <span className="text-[11px] text-[#555]">/mo</span>
                  </div>

                  <div className="grid grid-cols-2 gap-2 text-[11px]">
                    <div className="bg-[#0a0a0a] rounded-lg p-2 border border-[#141414]">
                      <p className="text-[#444] mb-0.5">Cover</p>
                      <p className="text-[#888] font-medium">{quote.cover || '—'}</p>
                    </div>
                    <div className="bg-[#0a0a0a] rounded-lg p-2 border border-[#141414]">
                      <p className="text-[#444] mb-0.5">CSR</p>
                      <p className="text-[#888] font-medium">{quote.csr || '—'}</p>
                    </div>
                  </div>

                  {quote.snippet && (
                    <p className="text-[11px] text-[#333] mt-3 line-clamp-2">{quote.snippet}</p>
                  )}
                </div>
              </MagicCard>
            </BlurFade>
          ))}
        </div>
      </div>
    </div>
  )
}
```

---

### Task 17: Build HistorySection

**Files:**
- Modify: `frontend/src/components/history/HistorySection.jsx` (replace stub)

- [ ] **Step 1: Replace stub with full implementation**

```jsx
import { useState } from 'react'
import { BlurFade } from '../magicui/blur-fade'
import { Clock, MessageSquare, Search } from 'lucide-react'

export default function HistorySection({ history = [], onResumeThread }) {
  const [query, setQuery] = useState('')

  const filtered = history.filter(h =>
    h.title.toLowerCase().includes(query.toLowerCase())
  )

  return (
    <div className="h-full flex flex-col overflow-hidden">
      {/* Search bar */}
      <div className="px-5 pt-5 pb-3 shrink-0">
        <div className="relative max-w-xl">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-[#333]" />
          <input
            className="w-full bg-[#0f0f0f] border border-[#1a1a1a] rounded-lg pl-9 pr-3 py-2 text-[13px] text-[#e4e4e7] placeholder-[#333] focus:outline-none focus:border-[#222] transition-colors"
            placeholder="Search conversations..."
            value={query}
            onChange={e => setQuery(e.target.value)}
          />
        </div>
      </div>

      {/* List */}
      <div className="flex-1 overflow-y-auto px-5 pb-5
        [&::-webkit-scrollbar]:w-[3px]
        [&::-webkit-scrollbar-track]:bg-transparent
        [&::-webkit-scrollbar-thumb]:bg-[#1e1e1e]"
      >
        {filtered.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-48 gap-2">
            <Clock className="w-8 h-8 text-[#222]" />
            <p className="text-[12px] text-[#333]">
              {query ? 'No matching conversations' : 'No conversation history yet'}
            </p>
          </div>
        ) : (
          <div className="flex flex-col gap-2 max-w-xl">
            {filtered.map((entry, i) => (
              <BlurFade key={entry.id} delay={i * 0.04}>
                <button
                  onClick={() => onResumeThread?.(entry)}
                  className="w-full flex items-start gap-3 p-3 bg-[#0f0f0f] border border-[#1a1a1a] rounded-lg hover:bg-[#111] hover:border-[#222] transition-all text-left group"
                >
                  <MessageSquare className="w-4 h-4 text-[#333] shrink-0 mt-0.5 group-hover:text-[#555] transition-colors" />
                  <div className="min-w-0 flex-1">
                    <p className="text-[13px] text-[#888] truncate group-hover:text-[#aaa] transition-colors">
                      {entry.title}
                    </p>
                    <p className="text-[10px] text-[#333] mt-0.5">
                      {new Date(entry.createdAt).toLocaleDateString('en-IN', {
                        day: 'numeric', month: 'short', year: 'numeric'
                      })}
                    </p>
                  </div>
                </button>
              </BlurFade>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
```

- [ ] **Step 2: Run dev server — verify Profile, Comparison, History sections render**

Expected:
- Profile shows form with blur-fade entrances, smoker toggle works, save fires confetti
- Comparison shows empty state (no quotes saved yet)
- History shows empty state initially, populates after first chat message

- [ ] **Step 3: Commit**

```bash
cd frontend
git add src/
git commit -m "feat: add Profile, Comparison, History sections with MagicUI effects"
```

---

## Chunk 5: Library + Quotes + Final Polish

### Task 18: Build LibrarySection

**Files:**
- Modify: `frontend/src/components/library/LibrarySection.jsx` (replace stub)

- [ ] **Step 1: Replace stub with full implementation**

```jsx
import { useState } from 'react'
import { BlurFade } from '../magicui/blur-fade'
import { MagicCard } from '../magicui/magic-card'
import { Search, ChevronDown, ChevronUp } from 'lucide-react'
import companies from '../../../../data/term_life_companies.json'

function PlanCard({ plan, index }) {
  const [open, setOpen] = useState(false)

  return (
    <BlurFade delay={index * 0.04}>
      <MagicCard
        className="rounded-xl border border-[#1a1a1a] overflow-hidden"
        gradientColor="#141414"
        gradientSize={120}
      >
        <div className="bg-[#0f0f0f]">
          <button
            onClick={() => setOpen(o => !o)}
            className="w-full flex items-center gap-3 p-4 text-left"
          >
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-0.5">
                <span className="text-[13px] font-medium text-[#e4e4e7]">{plan.plan_name}</span>
                <span className="text-[9px] font-medium text-[#555] bg-[#141414] border border-[#1e1e1e] px-1.5 py-0.5 rounded-full">
                  CSR {plan.claim_settlement_ratio}%
                </span>
              </div>
              <p className="text-[11px] text-[#444] truncate">{plan.company_name}</p>
            </div>
            <div className="flex items-center gap-3 shrink-0">
              <div className="text-right">
                <p className="text-[10px] text-[#444]">Base rate</p>
                <p className="text-[12px] font-medium text-[#888]">₹{plan.base_rate}/1000</p>
              </div>
              {open ? <ChevronUp className="w-4 h-4 text-[#333]" /> : <ChevronDown className="w-4 h-4 text-[#333]" />}
            </div>
          </button>

          {open && (
            <div className="px-4 pb-4 border-t border-[#141414] pt-3 flex flex-col gap-3">
              {/* Stats */}
              <div className="grid grid-cols-3 gap-2">
                {[
                  { label: 'Max Cover', value: `₹${(plan.max_life_cover / 10000000).toFixed(0)} Cr` },
                  { label: 'Age Range', value: `${plan.min_entry_age}–${plan.max_entry_age}` },
                  { label: 'Cover Till', value: `Age ${plan.max_cover_till_age}` },
                ].map(({ label, value }) => (
                  <div key={label} className="bg-[#0a0a0a] rounded-lg p-2 border border-[#141414]">
                    <p className="text-[9px] text-[#444] uppercase tracking-wider mb-0.5">{label}</p>
                    <p className="text-[12px] text-[#888] font-medium">{value}</p>
                  </div>
                ))}
              </div>

              {/* Features */}
              {plan.features?.length > 0 && (
                <div>
                  <p className="text-[9px] uppercase tracking-wider text-[#333] mb-1.5">Features</p>
                  <ul className="flex flex-col gap-1">
                    {plan.features.map((f, i) => (
                      <li key={i} className="text-[11px] text-[#555] flex items-center gap-2">
                        <span className="w-1 h-1 rounded-full bg-[#333] shrink-0" />
                        {f}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Riders */}
              {plan.optional_riders?.length > 0 && (
                <div>
                  <p className="text-[9px] uppercase tracking-wider text-[#333] mb-1.5">Optional Riders</p>
                  <div className="flex flex-wrap gap-1.5">
                    {plan.optional_riders.map((r, i) => (
                      <span key={i} className="text-[10px] text-[#555] bg-[#111] border border-[#1a1a1a] px-2 py-0.5 rounded-full">
                        {r}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </MagicCard>
    </BlurFade>
  )
}

export default function LibrarySection() {
  const [query, setQuery] = useState('')

  const filtered = companies.filter(p =>
    p.plan_name.toLowerCase().includes(query.toLowerCase()) ||
    p.company_name.toLowerCase().includes(query.toLowerCase())
  )

  return (
    <div className="h-full flex flex-col overflow-hidden">
      <div className="px-5 pt-5 pb-3 shrink-0">
        <div className="relative max-w-xl">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-[#333]" />
          <input
            className="w-full bg-[#0f0f0f] border border-[#1a1a1a] rounded-lg pl-9 pr-3 py-2 text-[13px] text-[#e4e4e7] placeholder-[#333] focus:outline-none focus:border-[#222] transition-colors"
            placeholder="Search plans or insurers..."
            value={query}
            onChange={e => setQuery(e.target.value)}
          />
        </div>
        <p className="text-[11px] text-[#333] mt-2">{filtered.length} plan{filtered.length !== 1 ? 's' : ''} available</p>
      </div>

      <div className="flex-1 overflow-y-auto px-5 pb-5
        [&::-webkit-scrollbar]:w-[3px]
        [&::-webkit-scrollbar-track]:bg-transparent
        [&::-webkit-scrollbar-thumb]:bg-[#1e1e1e]"
      >
        <div className="flex flex-col gap-2 max-w-2xl">
          {filtered.map((plan, i) => (
            <PlanCard key={plan.plan_id} plan={plan} index={i} />
          ))}
        </div>
      </div>
    </div>
  )
}
```

- [ ] **Step 2: Verify Vite can import JSON file from outside `frontend/`**

Vite by default only serves files within the project root (`frontend/`). Since `data/term_life_companies.json` is at `../data/` relative to `frontend/`, we need to tell Vite to allow it.

In `frontend/vite.config.js`, add `server.fs.allow`:

```js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import path from 'path'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    fs: {
      allow: ['.', '..'],  // allow parent directory for data/
    },
  },
  resolve: {
    alias: {
      '@data': path.resolve(__dirname, '../data'),
    },
  },
})
```

Then update the import in `LibrarySection.jsx`:
```jsx
import companies from '@data/term_life_companies.json'
```

---

### Task 19: Build QuotesSection

**Files:**
- Modify: `frontend/src/components/quotes/QuotesSection.jsx` (replace stub)

- [ ] **Step 1: Replace stub with full implementation**

```jsx
import { BlurFade } from '../magicui/blur-fade'
import { NumberTicker } from '../magicui/number-ticker'
import { Star } from 'lucide-react'

export default function QuotesSection({ savedQuotes = [] }) {
  if (savedQuotes.length === 0) {
    return (
      <div className="h-full flex flex-col items-center justify-center gap-3 text-center px-8">
        <div className="w-12 h-12 rounded-xl bg-[#0f0f0f] border border-[#1a1a1a] flex items-center justify-center mb-2">
          <Star className="w-5 h-5 text-[#222]" />
        </div>
        <p className="text-[13px] text-[#555]">No saved quotes yet</p>
        <p className="text-[11px] text-[#333] max-w-[240px]">Click "Save Quote" in the top bar while chatting to bookmark plans here.</p>
      </div>
    )
  }

  return (
    <div className="h-full overflow-y-auto px-5 py-5
      [&::-webkit-scrollbar]:w-[3px]
      [&::-webkit-scrollbar-track]:bg-transparent
      [&::-webkit-scrollbar-thumb]:bg-[#1e1e1e]"
    >
      <div className="max-w-2xl mx-auto">
        <BlurFade delay={0.05}>
          <h2 className="text-[15px] font-semibold text-[#e4e4e7] mb-1">Saved Quotes</h2>
          <p className="text-[12px] text-[#444] mb-5">{savedQuotes.length} saved</p>
        </BlurFade>

        <div className="flex flex-col gap-3">
          {savedQuotes.map((quote, i) => (
            <BlurFade key={quote.id} delay={0.1 + i * 0.05}>
              <div className="bg-[#0f0f0f] border border-[#1a1a1a] rounded-xl p-4 hover:border-[#222] transition-colors">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <h3 className="text-[13px] font-medium text-[#e4e4e7]">{quote.planName}</h3>
                    <p className="text-[11px] text-[#444] mt-0.5">{quote.company || 'From Chat'}</p>
                  </div>
                  <div className="text-right shrink-0">
                    <div className="flex items-baseline gap-1">
                      <span className="text-[10px] text-[#444]">₹</span>
                      {quote.premiumMonthly > 0
                        ? <NumberTicker value={quote.premiumMonthly} className="text-[18px] font-bold text-white tabular-nums" />
                        : <span className="text-[18px] font-bold text-[#555]">—</span>
                      }
                      <span className="text-[10px] text-[#444]">/mo</span>
                    </div>
                  </div>
                </div>

                <div className="flex gap-2 mt-3 flex-wrap">
                  {quote.cover && (
                    <span className="text-[10px] text-[#555] bg-[#111] border border-[#1a1a1a] px-2 py-0.5 rounded-full">
                      Cover: {quote.cover}
                    </span>
                  )}
                  {quote.csr && (
                    <span className="text-[10px] text-[#555] bg-[#111] border border-[#1a1a1a] px-2 py-0.5 rounded-full">
                      CSR: {quote.csr}
                    </span>
                  )}
                  <span className="text-[10px] text-[#333] bg-[#0a0a0a] border border-[#141414] px-2 py-0.5 rounded-full">
                    {new Date(quote.savedAt).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' })}
                  </span>
                </div>

                {quote.snippet && (
                  <p className="text-[11px] text-[#333] mt-2.5 line-clamp-2 border-t border-[#141414] pt-2.5">
                    {quote.snippet}
                  </p>
                )}
              </div>
            </BlurFade>
          ))}
        </div>
      </div>
    </div>
  )
}
```

---

### Task 20: Final integration verification

- [ ] **Step 1: Run full dev server and perform end-to-end verification**

```bash
cd frontend && npm run dev
```

Work through each verification step from the spec:

1. `npm run dev` — no console errors, app renders at `http://localhost:5173`
2. All 6 sidebar items clickable; each renders its section
3. Send "I'm 32, earn ₹18L/year. Recommend term life insurance." — table renders formatted (not raw pipe text)
4. Hover over AI message bubble — mouse spotlight follows cursor
5. New messages appear with blur-fade-in animation
6. Navigate to Plan Comparison — shows empty state with clear CTA. Then go back to Chat, click "Save Quote", navigate to Plan Comparison again — quote card appears and the `number-ticker` premium value animates up from 0 on mount
7. Navigate to My Profile — fill form, click Save → confetti fires
8. Send a chat message — History section gains a new entry
9. Navigate to Policy Library — plans from `term_life_companies.json` render in expandable cards with search
10. Click "Save Quote" in TopBar — navigates to Saved Quotes section showing the saved entry
11. During AI streaming — TypingIndicator shows morphing text

- [ ] **Step 2: Fix any visual issues found during verification**

Common issues to check:
- Tailwind classes using `bg-bg`, `text-text`, `border-border` — these map to the new theme variables. If Tailwind doesn't resolve them, use raw hex values (e.g., `bg-[#080808]`).
- MagicUI `MorphingText` requires `texts` prop as an array — verify TypingIndicator passes correct prop.
- `DotPattern` — check the `cr`, `cx`, `cy` prop names match the installed component's API.
- `BlurFade` — verify it accepts `delay` and `inView` props as expected.

- [ ] **Step 3: Run linter**

```bash
cd frontend && npm run lint
```

Fix any errors (unused imports, missing keys, etc.).

- [ ] **Step 4: Final commit**

```bash
cd frontend
git add src/ data/ vite.config.js
git commit -m "feat: complete Insurance Advisor dashboard redesign — 6-section Obsidian Minimal UI with MagicUI effects"
```

---

## Quick Reference

| Section | File | Key Effects |
|---|---|---|
| Sidebar | `components/layout/Sidebar.jsx` | `AnimatedShinyText` logo, `BorderBeam` on active item |
| TopBar | `components/layout/TopBar.jsx` | `ShimmerButton` Save Quote |
| Chat | `components/chat/ChatSection.jsx` | Full chat with all effects |
| Messages | `components/chat/MessageList.jsx` | `DotPattern` bg |
| Bubble | `components/MessageBubble.jsx` | `BlurFade` entrance, `MagicCard` spotlight |
| Input | `components/InputArea.jsx` | `BorderBeam` on focus |
| Typing | `components/chat/TypingIndicator.jsx` | `MorphingText` |
| Profile | `components/profile/ProfileSection.jsx` | `BlurFade`, `confetti` on save |
| Comparison | `components/comparison/ComparisonSection.jsx` | `MagicCard`, `NumberTicker`, `BorderBeam` |
| History | `components/history/HistorySection.jsx` | `BlurFade` list items |
| Library | `components/library/LibrarySection.jsx` | `MagicCard`, expandable accordion |
| Quotes | `components/quotes/QuotesSection.jsx` | `BlurFade`, `NumberTicker` |
