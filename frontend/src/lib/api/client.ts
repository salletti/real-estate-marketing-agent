export class ApiError extends Error {
  status: number
  detail: unknown

  constructor(status: number, detail: unknown, message: string) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.detail = detail
  }
}

export async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`/api${path}`, {
    headers: { 'Content-Type': 'application/json', ...init?.headers },
    ...init,
  })

  if (!res.ok) {
    let detail: unknown = null
    try {
      detail = await res.json()
    } catch {
      // non-JSON error body
    }
    throw new ApiError(res.status, detail, `HTTP ${res.status} on ${path}`)
  }

  return res.json() as Promise<T>
}
