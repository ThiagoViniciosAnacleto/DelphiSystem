export const getBaseURL = () => {
  const envUrl = (typeof import.meta !== 'undefined' && import.meta.env && import.meta.env.VITE_API_URL)
    ? String(import.meta.env.VITE_API_URL).trim()
    : ''
  if (!envUrl) return 'http://localhost:8000'
  return envUrl.replace(/\/+$/, '')
}

export const getAuthHeaders = (extraHeaders = {}) => {
  const token = typeof localStorage !== 'undefined' ? localStorage.getItem('token') : null
  const headers = { ...extraHeaders }
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }
  return headers
}

const handleResponse = async (response) => {
  if (!response.ok) {
    let errorDetail = `Erro HTTP ${response.status}`
    try {
      const data = await response.json()
      errorDetail = data.detail || data.mensagem || data.message || errorDetail
    } catch {
      // Body não é JSON
    }
    const err = new Error(errorDetail)
    err.status = response.status
    throw err
  }
  if (response.status === 204) {
    return null
  }
  return await response.json()
}

export const apiClient = {
  getBaseURL,
  getAuthHeaders,

  async get(endpoint, params = {}) {
    const base = getBaseURL()
    const path = endpoint.startsWith('/') ? endpoint : `/${endpoint}`
    const url = new URL(`${base}${path}`)
    Object.entries(params).forEach(([key, val]) => {
      if (val !== undefined && val !== null && val !== '') {
        url.searchParams.append(key, val)
      }
    })
    const response = await fetch(url.toString(), {
      method: 'GET',
      headers: getAuthHeaders({ 'Content-Type': 'application/json' })
    })
    return handleResponse(response)
  },

  async post(endpoint, body = {}) {
    const base = getBaseURL()
    const path = endpoint.startsWith('/') ? endpoint : `/${endpoint}`
    const response = await fetch(`${base}${path}`, {
      method: 'POST',
      headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify(body)
    })
    return handleResponse(response)
  },

  async postPublic(endpoint, body = {}) {
    const base = getBaseURL()
    const path = endpoint.startsWith('/') ? endpoint : `/${endpoint}`
    const response = await fetch(`${base}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    })
    return handleResponse(response)
  },

  async postForm(endpoint, formDataObject = {}) {
    const base = getBaseURL()
    const path = endpoint.startsWith('/') ? endpoint : `/${endpoint}`
    const params = new URLSearchParams()
    Object.entries(formDataObject).forEach(([key, val]) => {
      if (val !== undefined && val !== null) {
        params.append(key, String(val))
      }
    })
    const response = await fetch(`${base}${path}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: params.toString()
    })
    return handleResponse(response)
  },


  async put(endpoint, body = {}) {
    const base = getBaseURL()
    const path = endpoint.startsWith('/') ? endpoint : `/${endpoint}`
    const response = await fetch(`${base}${path}`, {
      method: 'PUT',
      headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify(body)
    })
    return handleResponse(response)
  },

  async delete(endpoint) {
    const base = getBaseURL()
    const path = endpoint.startsWith('/') ? endpoint : `/${endpoint}`
    const response = await fetch(`${base}${path}`, {
      method: 'DELETE',
      headers: getAuthHeaders()
    })
    return handleResponse(response)
  },

  async upload(endpoint, formData) {
    const base = getBaseURL()
    const path = endpoint.startsWith('/') ? endpoint : `/${endpoint}`
    const response = await fetch(`${base}${path}`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: formData
    })
    return handleResponse(response)
  },

  async download(endpoint, defaultFilename = 'anexo') {
    const base = getBaseURL()
    const path = endpoint.startsWith('/') ? endpoint : `/${endpoint}`
    const url = endpoint.startsWith('http') ? endpoint : `${base}${path}`
    const response = await fetch(url, {
      method: 'GET',
      headers: getAuthHeaders()
    })

    if (!response.ok) {
      let msg = `Falha ao baixar arquivo (HTTP ${response.status})`
      if (response.status === 401) msg = 'Sessão expirada. Faça login novamente.'
      if (response.status === 403) msg = 'Acesso negado para baixar este anexo.'
      if (response.status === 404) msg = 'Arquivo não encontrado.'
      throw new Error(msg)
    }

    const blob = await response.blob()
    const blobUrl = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = blobUrl
    a.download = defaultFilename
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(blobUrl)
  }
}

export default apiClient
