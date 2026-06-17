import { useEffect, useRef, useState } from 'react'
import { clearHistory, fetchHistory, streamMessage } from '../api/chatApi'
import ChatHeader from '../components/ChatHeader'
import ChatInput from '../components/ChatInput'
import MessageCard from '../components/MessageCard'
import Sidebar from '../components/Sidebar'
import TypingIndicator from '../components/TypingIndicator'
import { addSession, getSessions, getGreeting, removeSession } from '../utils/history'
import { getSessionId, resetSessionId } from '../utils/session'
import '../styles/chat.css'

export default function ChatPage() {
  const [sessions, setSessions] = useState(getSessions)
  const [activeId, setActiveId] = useState(null)           // null = home/greeting
  const [messages, setMessages] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [streamText, setStreamText] = useState('')
  const bottomRef = useRef(null)

  // current working session id (separate from "activeId" which drives the sidebar selection)
  const sessionIdRef = useRef(getSessionId())

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, streamText, isLoading])

  async function loadSession(id) {
    setActiveId(id)
    sessionIdRef.current = id
    try {
      const data = await fetchHistory(id)
      setMessages(data.messages.map((m) => ({ ...m, timestamp: Date.now() })))
    } catch {
      setMessages([])
    }
  }

  async function handleNewChat() {
    const newId = resetSessionId()
    sessionIdRef.current = newId
    setActiveId(null)
    setMessages([])
    setStreamText('')
  }

  async function handleDelete(id) {
    await clearHistory(id).catch(() => {})
    removeSession(id)
    setSessions(getSessions())
    if (activeId === id) { handleNewChat() }
  }

  async function handleSend(text) {
    const sid = sessionIdRef.current

    // Register in history on first message
    if (!sessions.find((s) => s.id === sid)) {
      addSession(sid, text)
      setSessions(getSessions())
      setActiveId(sid)
    }

    setMessages((prev) => [...prev, { role: 'user', content: text, timestamp: Date.now() }])
    setIsLoading(true)
    setStreamText('')

    let full = ''
    try {
      for await (const token of streamMessage(sid, text)) {
        full += token
        setStreamText(full)
      }
      setMessages((prev) => [...prev, { role: 'assistant', content: full, timestamp: Date.now() }])
    } catch {
      setMessages((prev) => [...prev, {
        role: 'assistant',
        content: "Something went wrong on my end. Give it another shot?",
        timestamp: Date.now(),
      }])
    } finally {
      setStreamText('')
      setIsLoading(false)
    }
  }

  const greeting = getGreeting()
  const showGreeting = messages.length === 0 && !isLoading

  return (
    <div className="app">
      <Sidebar
        sessions={sessions}
        activeId={activeId}
        onSelect={loadSession}
        onNewChat={handleNewChat}
        onDelete={handleDelete}
      />

      <div className="main">
        <ChatHeader onNewChat={handleNewChat} />

        <div className="content">
          {showGreeting ? (
            <div className="greeting">
              <div className="orb" />
              <h1 className="greet-line1">{greeting}, Preetham</h1>
              <h2 className="greet-line2">
                How Can I <span className="greet-accent">Help You Today?</span>
              </h2>
            </div>
          ) : (
            <div className="messages">
              {messages.map((m, i) => (
                <MessageCard key={i} role={m.role} content={m.content} timestamp={m.timestamp} />
              ))}
              {isLoading && <TypingIndicator text={streamText} />}
              <div ref={bottomRef} />
            </div>
          )}
        </div>

        <ChatInput onSend={handleSend} disabled={isLoading} />
      </div>
    </div>
  )
}
