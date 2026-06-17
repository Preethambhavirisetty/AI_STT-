function formatTime(ts) {
  return new Date(ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

export default function MessageCard({ role, content, timestamp }) {
  const isUser = role === 'user'
  return (
    <div className={`msg ${isUser ? 'msg-user' : 'msg-bot'}`}>
      <div className={`msg-av ${isUser ? 'av-user' : 'av-bot'}`}>
        {isUser ? 'P' : 'M'}
      </div>
      <div className="msg-body">
        <div className="msg-meta">
          <span className="msg-name">{isUser ? 'Preetham' : 'Mikey'}</span>
          {timestamp && <span className="msg-time">{formatTime(timestamp)}</span>}
        </div>
        <p className="msg-text">{content}</p>
      </div>
    </div>
  )
}
