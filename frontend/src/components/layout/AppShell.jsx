import Sidebar from './Sidebar'
import TopBar from './TopBar'
import ChatSection from '../chat/ChatSection'
import ProfileSection from '../profile/ProfileSection'
import ComparisonSection from '../comparison/ComparisonSection'
import HistorySection from '../history/HistorySection'
import LibrarySection from '../library/LibrarySection'
import QuotesSection from '../quotes/QuotesSection'

export default function AppShell({ activeSection, setActiveSection, chatProps, appState }) {
  const { savedQuotes = [], conversationHistory = [], userProfile, onProfileSave } = appState || {}

  const sectionMap = {
    chat:       <ChatSection {...chatProps} />,
    profile:    <ProfileSection userProfile={userProfile} onProfileSave={onProfileSave} />,
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
