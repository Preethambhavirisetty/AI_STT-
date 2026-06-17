export default function TypingIndicator({ text }) {
  return (
    <div className="msg msg-bot">
      <div className="msg-av av-bot">M</div>
      <div className="msg-body">
        <div className="msg-meta">
          <span className="msg-name">Mikey</span>
        </div>
        {text ? (
          <p className="msg-text msg-streaming">{text}</p>
        ) : (
          <div className="dots">
            <span /><span /><span />
          </div>
        )}
      </div>
    </div>
  )
}
