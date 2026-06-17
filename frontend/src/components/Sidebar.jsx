import { useState } from 'react'
import { groupByDate } from '../utils/history'

export default function Sidebar({ sessions, activeId, onSelect, onNewChat, onDelete }) {
  const [search, setSearch] = useState('')

  const filtered = search.trim()
    ? sessions.filter((s) => s.title.toLowerCase().includes(search.toLowerCase()))
    : sessions
  const groups = groupByDate(filtered)

  return (
    <aside className="sidebar">
      {/* Brand */}
      <div className="sidebar-brand">
        <div className="brand-mark">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
            <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </div>
        <span className="brand-text">Mikey</span>
      </div>

      {/* Search */}
      <div className="sidebar-search">
        <svg className="search-icon" width="14" height="14" viewBox="0 0 24 24" fill="none">
          <circle cx="11" cy="11" r="8" stroke="currentColor" strokeWidth="2"/>
          <path d="M21 21l-4.35-4.35" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
        </svg>
        <input
          type="text"
          placeholder="Search chats..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="search-input"
        />
      </div>

      {/* Nav */}
      <nav className="sidebar-nav">
        <button
          className={`nav-item ${activeId === null ? 'nav-active' : ''}`}
          onClick={onNewChat}
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
            <path d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          Home
        </button>
        <button className="nav-item">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
            <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2"/>
            <polyline points="12 6 12 12 16 14" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
          </svg>
          History
        </button>
      </nav>

      {/* History list */}
      <div className="history-scroll">
        {groups.length === 0 && !search && (
          <p className="history-empty">No conversations yet</p>
        )}
        {groups.map(({ label, items }) => (
          <div key={label} className="history-group">
            <p className="history-label">{label}</p>
            {items.map((s) => (
              <div
                key={s.id}
                className={`history-item ${s.id === activeId ? 'history-active' : ''}`}
                onClick={() => onSelect(s.id)}
              >
                <span className="history-title">{s.title}</span>
                <button
                  className="history-delete"
                  onClick={(e) => { e.stopPropagation(); onDelete(s.id) }}
                  title="Delete"
                >
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none">
                    <path d="M18 6L6 18M6 6l12 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                  </svg>
                </button>
              </div>
            ))}
          </div>
        ))}
      </div>

      {/* User profile */}
      <div className="sidebar-profile">
        <div className="profile-avatar">P</div>
        <div className="profile-info">
          <p className="profile-name">Preetham</p>
          <p className="profile-email">preethambhavirisetty66@gmail.com</p>
        </div>
      </div>
    </aside>
  )
}
