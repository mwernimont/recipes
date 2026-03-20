// frontend/src/services/api.js

const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api'

async function request(path, options = {}) {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  })

  if (res.status === 204) return null

  const data = await res.json()

  if (!res.ok) {
    throw new Error(data.detail ?? `Request failed: ${res.status}`)
  }

  return data
}

export const recipesApi = {
  list: (params = {}) => {
    const q = new URLSearchParams(params).toString()
    return request(`/recipes/${q ? `?${q}` : ''}`)
  },
  get: (id) => request(`/recipes/${id}`),
  create: (data) => request('/recipes/', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  update: (id, data) => request(`/recipes/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  }),
  delete: (id) => request(`/recipes/${id}`, {
    method: 'DELETE',
  }),
  uploadImage: (id, file) => {
    const form = new FormData()
    form.append('file', file)
    return request(`/recipes/${id}/image`, {
      method: 'POST',
      headers: {},  // let browser set multipart boundary
      body: form,
    })
  },
}

export const scraperApi = {
  scrape: (url) => request('/scraper/', {
    method: 'POST',
    body: JSON.stringify({ url }),
  }),
}

export const tagsApi = {
  list: () => request('/tags/'),
}
