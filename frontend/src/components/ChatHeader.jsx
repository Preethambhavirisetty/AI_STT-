export default function ChatHeader({ onNewChat }) {
  return (
    <header className="chat-header">
      <div className="header-left">
        <div className="model-badge">
          <div className="model-dot" />
          Mikey
        </div>
      </div>
      <div className="header-right">
        <button className="new-chat-btn" onClick={onNewChat}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
            <path d="M12 5v14M5 12h14" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"/>
          </svg>
          New Chat
        </button>
        <div className="header-avatar">P</div>
      </div>
    </header>
  )
}
