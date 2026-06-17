const BASE = '/api/v1/chat'

export async function sendMessage(sessionId, message) {
  const res = await fetch(`${BASE}/message`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, message }),
  })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function* streamMessage(sessionId, message) {
  const res = await fetch(`${BASE}/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, message }),
  })
  if (!res.ok) throw new Error(await res.text())

  const reader = res.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split('\n')
    buffer = lines.pop() ?? ''
    for (const line of lines) {
      if (!line.startsWith('data: ')) continue
      const raw = line.slice(6)
      if (raw === '[DONE]') return
      try {
        const { token, error } = JSON.parse(raw)
        if (error) throw new Error(error)
        if (token) yield token
      } catch {}
    }
  }
}

export async function fetchHistory(sessionId) {
  const res = await fetch(`${BASE}/history/${sessionId}`)
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function clearHistory(sessionId) {
  await fetch(`${BASE}/history/${sessionId}`, { method: 'DELETE' })
}
