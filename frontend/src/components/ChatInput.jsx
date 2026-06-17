import { useRef, useState } from 'react'

export default function ChatInput({ onSend, disabled }) {
  const [text, setText] = useState('')
  const ref = useRef(null)

  function resize() {
    const el = ref.current
    if (!el) return
    el.style.height = 'auto'
    el.style.height = Math.min(el.scrollHeight, 200) + 'px'
  }

  function handleChange(e) {
    setText(e.target.value)
    resize()
  }

  function handleSend() {
    const t = text.trim()
    if (!t || disabled) return
    onSend(t)
    setText('')
    if (ref.current) ref.current.style.height = 'auto'
  }

  function handleKey(e) {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend() }
  }

  const canSend = text.trim().length > 0 && !disabled

  return (
    <div className="input-wrap">
      <div className="input-card">
        <textarea
          ref={ref}
          className="input-field"
          placeholder="Ask me anything, I'm all ears..."
          value={text}
          onChange={handleChange}
          onKeyDown={handleKey}
          disabled={disabled}
          rows={1}
        />
        <div className="input-toolbar">
          <button className="tool-btn" disabled title="Attach file">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
              <path d="M21.44 11.05l-9.19 9.19a6 6 0 01-8.49-8.49l9.19-9.19a4 4 0 015.66 5.66l-9.2 9.19a2 2 0 01-2.83-2.83l8.49-8.48" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
            </svg>
          </button>
          <div className="toolbar-spacer" />
          <button
            className={`send-btn ${canSend ? 'send-ready' : ''}`}
            onClick={handleSend}
            disabled={!canSend}
            title="Send (Enter)"
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
              <path d="M22 2L11 13M22 2L15 22l-4-9-9-4 20-7z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </button>
        </div>
      </div>
      <p className="input-note">Mikey can make mistakes. Think before you trust me blindly.</p>
    </div>
  )
}
