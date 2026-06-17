const SESSION_KEY = 'mikey_session_id'

export function getSessionId() {
  let id = localStorage.getItem(SESSION_KEY)
  if (!id) {
    id = crypto.randomUUID()
    localStorage.setItem(SESSION_KEY, id)
  }
  return id
}

export function resetSessionId() {
  const id = crypto.randomUUID()
  localStorage.setItem(SESSION_KEY, id)
  return id
}
