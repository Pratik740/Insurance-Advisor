# Insurance Advisor — Dashboard Redesign & Policy Formatting Fix

**Date:** 2026-03-11
**Status:** Approved by user

---

## Context

The current frontend is a minimal single-page chat UI built with React 18 + Vite 5 + Tailwind v4. It has a placeholder sidebar with no real navigation and no section-switching. The `react-markdown` component is used without the `remark-gfm` plugin, causing markdown tables from the AI to render as raw `|---|` pipe text. The user wants the site elevated to a professional-grade full dashboard with Obsidian Minimal aesthetics, sleek animations, and interactive elements using shadcn/ui + MagicUI.

---

## Goals

1. Redesign the frontend into a full multi-section dashboard (6 sections, state-based SPA navigation — no React Router)
2. Apply **Obsidian Minimal** aesthetic: near-black bg, pure white accents, razor-sharp borders, no color gradients
3. Integrate **shadcn/ui** as the component foundation and **MagicUI** for motion/effects
4. Fix markdown table and spacing rendering — root cause: missing `remark-gfm` plugin in `MessageBubble.jsx`
5. Add sleek blur-fade, magic-card, border-beam, shimmer, and number-ticker effects throughout

---

## Design Aesthetic: Obsidian Minimal

- Background: `#080808` / `#0a0a0a`
- Surfaces: `#0f0f0f` / `#111111`
- Borders: `#1a1a1a` / `#1e1e1e` / `#222222`
- Text primary: `#e4e4e7` · secondary: `#888888` · muted: `#444444`
- Accent: `#ffffff` (pure white only — no blue/purple/green accents)
- Font: Inter (already configured)

---

## Navigation: State-based SPA

No React Router. A single `activeSection` state in `App.jsx` controls which section renders. This preserves the existing SSE streaming logic intact and avoids routing overhead.

---

## New File Structure

```
frontend/src/
├── App.jsx                          (updated: activeSection + full state shape)
├── main.jsx                         (unchanged)
├── index.css                        (updated: Obsidian theme + keep/update markdown-table styles)
├── lib/
│   └── utils.js                     (shadcn cn() utility — created by shadcn init)
├── components/
│   ├── ui/                          (created by shadcn init — do not hand-edit)
│   ├── layout/
│   │   ├── AppShell.jsx             (sidebar + main wrapper, routes activeSection)
│   │   ├── Sidebar.jsx              (nav items + active state + border-beam)
│   │   └── TopBar.jsx               (section title + contextual actions)
│   ├── chat/
│   │   ├── ChatSection.jsx          (replaces App's inline chat layout)
│   │   ├── MessageList.jsx          (replaces ChatBox.jsx — message list + scroll)
│   │   ├── MessageBubble.jsx        (updated: remark-gfm + blur-fade + magic-card)
│   │   ├── InputArea.jsx            (updated: shimmer-button + border-beam on focus)
│   │   └── TypingIndicator.jsx      (morphing-text status)
│   ├── profile/
│   │   └── ProfileSection.jsx       (shadcn form inputs, confetti on save)
│   ├── comparison/
│   │   └── ComparisonSection.jsx    (magic-card plan cards + shadcn Table + number-ticker)
│   ├── history/
│   │   └── HistorySection.jsx       (thread list from localStorage, resume thread)
│   ├── library/
│   │   └── LibrarySection.jsx       (shadcn Accordion cards from term_life_companies.json)
│   └── quotes/
│       └── QuotesSection.jsx        (savedQuotes state, number-ticker premiums)
```

**Files to delete:** `src/components/ChatBox.jsx` (content migrated into `ChatSection.jsx` + `MessageList.jsx`)

---

## AppShell Component Spec

`AppShell.jsx` is the root layout wrapper. It receives `activeSection` and `setActiveSection` from `App.jsx` and renders the appropriate section in the main area.

```jsx
// Props
{ activeSection, setActiveSection, chatProps }

// Layout: fixed sidebar (220px) + flex-1 main
// chatProps is the full chat state bundle passed through to ChatSection only

function AppShell({ activeSection, setActiveSection, chatProps }) {
  const sectionMap = {
    chat:       <ChatSection {...chatProps} />,
    profile:    <ProfileSection />,
    comparison: <ComparisonSection />,
    history:    <HistorySection onResumeThread={chatProps.onResumeThread} />,
    library:    <LibrarySection />,
    quotes:     <QuotesSection />,
  }
  return (
    <div className="flex h-screen w-full bg-bg overflow-hidden">
      <Sidebar activeSection={activeSection} onNavigate={setActiveSection} />
      <div className="flex flex-col flex-1 min-w-0">
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

## Full State Shape in App.jsx

```js
// Preserved from current implementation
const [messages, setMessages] = useState([{ id: 'init', role: 'assistant', content: GREETING }])
const [isLoading, setIsLoading] = useState(false)
const [loadingStatus, setLoadingStatus] = useState("Initializing...")
const [threadId, setThreadId] = useState(() => crypto.randomUUID())

// New
const [activeSection, setActiveSection] = useState('chat')
const [userProfile, setUserProfile] = useState({
  name: '', age: '', annualIncome: '', smoker: false,
  gender: '', occupation: 'salaried', dependents: 0
})
const [savedQuotes, setSavedQuotes] = useState([])      // see schema below
const [conversationHistory, setConversationHistory] = useState(
  () => JSON.parse(localStorage.getItem('ia_history') || '[]')
)
```

**`savedQuotes` item schema:**
```js
{
  id: string,           // crypto.randomUUID()
  planName: string,     // e.g. "HDFC Click2Protect"
  company: string,
  cover: string,        // e.g. "₹2 Cr"
  premiumMonthly: number, // raw number for number-ticker
  csr: string,          // e.g. "99.5%"
  savedAt: string,      // ISO timestamp
  threadId: string,     // which chat session this came from
}
```

**`conversationHistory` item schema:**
```js
{
  id: string,           // threadId (UUID)
  title: string,        // first user message text (truncated to 60 chars)
  createdAt: string,    // ISO timestamp
  messageCount: number,
}
```

**Persistence:** `conversationHistory` is read from `localStorage` on init and written back whenever a new thread's first message is sent. `savedQuotes` is ephemeral (session-only) — no localStorage needed for MVP.

**`onResumeThread` function stub (include in App.jsx alongside state):**
```js
const onResumeThread = (threadEntry) => {
  setThreadId(threadEntry.id)
  setMessages([{ id: 'init', role: 'assistant', content: GREETING }])
  setActiveSection('chat')
}
```
This is passed into `chatProps` so `AppShell` can forward it to `HistorySection`.

---

## Policy Formatting Fix

### Root Cause
`MessageBubble.jsx` line 59 passes no plugins to `ReactMarkdown`. GFM tables require `remark-gfm`. Without it, `| col |` renders as literal text.

### Fix: Add remark-gfm plugin only
```bash
npm install remark-gfm
```

```jsx
// In MessageBubble.jsx
import remarkGfm from 'remark-gfm'

<ReactMarkdown remarkPlugins={[remarkGfm]}>
  {displayContent}
</ReactMarkdown>
```

### CSS: Update existing `.markdown-table` styles (do NOT add new `.prose table` rules)
The existing `.markdown-table` class in `index.css` (lines 59–78) already handles table styling. Update it to match the new Obsidian theme colors instead of adding new selectors:

```css
/* Replace existing .markdown-table block — keep selector names unchanged */
.markdown-table-wrapper {
  @apply overflow-hidden rounded-lg border border-[#1e1e1e] my-3 bg-[#0a0a0a];
}
.markdown-table { @apply w-full text-left text-xs border-collapse; }
.markdown-table th {
  @apply bg-[#141414] px-3 py-2 font-medium text-[#888] uppercase tracking-wider text-[10px]
         border-b border-[#1e1e1e];
}
.markdown-table td { @apply px-3 py-2 border-b border-[#161616] text-[#aaa]; }
.markdown-table tbody tr:hover td { @apply bg-[#0f0f0f]; }
.markdown-table tbody tr:last-child td { @apply border-0; }
```

### Spacing fix
Add to `index.css` after the table block:
```css
/* Paragraph and list spacing in AI responses */
.prose p { @apply my-1.5; }
.prose ul, .prose ol { @apply my-1.5; }
.prose li { @apply my-0.5; }
```

---

## Tailwind Theme Update (`index.css` `@theme` block)

Replace the existing `@theme` block entirely:
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
  --color-primary-400:  #71717a;   /* used in MessageBubble.jsx avatar icon */
  --color-primary-500:  #ffffff;
  --color-primary-600:  #e4e4e7;
  --color-primary-700:  #d4d4d8;
  --color-primary-800:  #a1a1aa;
  --color-primary-900:  #71717a;

  /* Legacy alias — keep so existing class refs don't break */
  --color-dark-bg:      #080808;
  --color-dark-surface: #0f0f0f;
  --color-dark-border:  #1a1a1a;
}
```

---

## New Dependencies

```bash
# In frontend/
npm install remark-gfm
npm install framer-motion
npm install clsx tailwind-merge class-variance-authority

# shadcn/ui — Tailwind v4 requires explicit CSS variables mode
# Run from frontend/ directory:
npx shadcn@latest init --style default --base-color zinc --css-variables true
# When prompted: use src/lib/utils.js, CSS file: src/index.css

# Add shadcn components:
npx shadcn@latest add button input label select card table accordion scroll-area separator badge tooltip sheet

# MagicUI — correct CLI is `npx magicui@latest add`
npx magicui@latest add border-beam
npx magicui@latest add magic-card
npx magicui@latest add number-ticker
npx magicui@latest add blur-fade
npx magicui@latest add shimmer-button
npx magicui@latest add dot-pattern
npx magicui@latest add morphing-text
npx magicui@latest add confetti
npx magicui@latest add animated-shiny-text

# Move lucide-react from devDependencies to dependencies
npm install lucide-react
```

---

## MagicUI Effects Map

| Component | Location | Effect |
|---|---|---|
| `border-beam` | Active sidebar nav item, input wrapper on focus, top-ranked plan card | Animated light sweeps around border |
| `magic-card` | AI message bubbles, plan comparison cards, library cards | Mouse spotlight follows cursor over card |
| `number-ticker` | Premium amounts in ComparisonSection + QuotesSection | Numbers count up on mount |
| `blur-fade` | Message entrance, section mount transitions, profile form fields | Blur + fade + translate-y fade in |
| `shimmer-button` | Send button in InputArea, Save Quote in TopBar | Shimmer light sweeps across button |
| `dot-pattern` | Chat message area background | Subtle `#1a1a1a` dot grid on `#080808` |
| `morphing-text` | TypingIndicator while SSE is streaming | Morphs between status strings (see below) |
| `confetti` | Profile save success callback | Burst confetti on save |
| `animated-shiny-text` | Sidebar logo "CoverAI" text | Shimmer sweep on logo text |

**MorphingText strings array for TypingIndicator:**
```js
const THINKING_STRINGS = [
  "Analyzing query...",
  "Consulting policy documents...",
  "Evaluating optimal plans...",
  "Calculating premiums...",
  "Synthesizing response...",
]
```
This replaces the `statusMap` lookup — morphing-text cycles through strings on a timer; the active `loadingStatus` text is passed in to override if available.

---

## Section Data Sources

| Section | Data Source |
|---|---|
| AI Chat | SSE stream from `http://localhost:8000/api/chat` |
| My Profile | `userProfile` state in App.jsx (in-memory) |
| Plan Comparison | `savedQuotes` state + chat-derived data |
| History | `conversationHistory` state (persisted to `localStorage`) |
| Policy Library | `data/term_life_companies.json` (import statically in LibrarySection — path from `frontend/src/components/library/LibrarySection.jsx` is `../../../../data/term_life_companies.json`) |
| Saved Quotes | `savedQuotes` state in App.jsx (session-only for MVP) |

---

## Sidebar Navigation Items

```
Workspace
  ✦ AI Chat        [Live badge when connected]
  ◈ My Profile
  ⊞ Plan Comparison [count badge]
  ◷ History         [count badge]

Resources
  ◫ Policy Library
  ◎ Saved Quotes    [count badge]

Footer: user avatar + name + plan tier
```

Active item: white left border accent + `border-beam` + slightly lighter background. Inactive: muted icon + dim text. Hover: slight brightness increase.

---

## Critical Files to Modify

| File | Change |
|---|---|
| `frontend/src/App.jsx` | Add `activeSection`, `userProfile`, `savedQuotes`, `conversationHistory` state; wrap in `<AppShell>`; preserve all SSE logic |
| `frontend/src/index.css` | Replace `@theme` block; update `.markdown-table` styles to Obsidian colors; add prose spacing rules |
| `frontend/src/components/MessageBubble.jsx` | Add `remark-gfm` plugin; wrap bubble in `BlurFade`; apply `MagicCard` |
| `frontend/src/components/InputArea.jsx` | Replace send button with `ShimmerButton`; add `BorderBeam` to input wrapper on focus |
| `frontend/package.json` | New deps added; `lucide-react` moved to `dependencies` |

**Delete:** `frontend/src/components/ChatBox.jsx` — functionality split into `ChatSection.jsx` (container/scroll) and `MessageList.jsx` (message rendering loop).

**Clear:** `frontend/src/App.css` — remove all Vite scaffold defaults (especially `#root { max-width: 1280px; margin: 0 auto; }`) which will constrain the full-bleed dashboard layout. Replace with an empty file or a single `/* cleared */` comment.

---

## Verification

1. `npm run dev` in `frontend/` — no console errors, app renders
2. All 6 sidebar items are clickable; each renders its section with a `blur-fade` transition
3. Send "I'm 32, earn ₹18L/year. Recommend term life insurance." — AI response with markdown table renders as a proper formatted table with styled rows and headers (not raw pipe text)
4. Hover over an AI message bubble — mouse spotlight follows cursor (magic-card effect visible)
5. New messages appear with blur-fade-in animation
6. Plan Comparison section: premium numbers animate up (number-ticker) on section mount
7. Fill out My Profile and click Save → confetti fires
8. History section shows current session thread entry after first message sent
9. Policy Library shows plan cards from `term_life_companies.json` in Accordion layout
10. TopBar "Save Quote" button (when in Chat section) adds an entry to Saved Quotes section
11. TypingIndicator morphs text smoothly between status strings during SSE streaming
