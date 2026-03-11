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
