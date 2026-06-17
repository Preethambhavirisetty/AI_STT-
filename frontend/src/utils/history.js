const KEY = 'mikey_sessions'

export function getSessions() {
  try { return JSON.parse(localStorage.getItem(KEY) || '[]') }
  catch { return [] }
}

export function addSession(id, title) {
  const sessions = getSessions()
  if (sessions.find((s) => s.id === id)) return
  sessions.unshift({ id, title: title.slice(0, 60), createdAt: Date.now() })
  localStorage.setItem(KEY, JSON.stringify(sessions))
}

export function updateTitle(id, title) {
  const sessions = getSessions()
  const s = sessions.find((s) => s.id === id)
  if (s) { s.title = title.slice(0, 60); localStorage.setItem(KEY, JSON.stringify(sessions)) }
}

export function removeSession(id) {
  localStorage.setItem(KEY, JSON.stringify(getSessions().filter((s) => s.id !== id)))
}

export function groupByDate(sessions) {
  const now = Date.now()
  const dayStart = (d) => new Date(d).setHours(0, 0, 0, 0)
  const today = dayStart(now)
  const groups = []
  const buckets = { Today: [], Yesterday: [], 'Previous 7 Days': [], Older: [] }
  sessions.forEach((s) => {
    const d = dayStart(s.createdAt)
    if (d >= today) buckets.Today.push(s)
    else if (d >= today - 864e5) buckets.Yesterday.push(s)
    else if (d >= today - 7 * 864e5) buckets['Previous 7 Days'].push(s)
    else buckets.Older.push(s)
  })
  Object.entries(buckets).forEach(([label, items]) => { if (items.length) groups.push({ label, items }) })
  return groups
}

export function getGreeting() {
  const h = new Date().getHours()
  if (h >= 5 && h < 12) return 'Good Morning'
  if (h >= 12 && h < 17) return 'Good Afternoon'
  if (h >= 17 && h < 21) return 'Good Evening'
  return 'Hey'
}
