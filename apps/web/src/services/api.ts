import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/v1'

export const api = axios.create({
  baseURL: API_URL,
  headers: { 'Content-Type': 'application/json' },
})

// Attach JWT token from localStorage on every request
api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
  }
  return config
})

// Auto-refresh on 401
api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true
      try {
        const refreshToken = localStorage.getItem('refresh_token')
        if (refreshToken) {
          const res = await axios.post(`${API_URL}/auth/refresh`, { refresh_token: refreshToken })
          localStorage.setItem('access_token', res.data.access_token)
          original.headers.Authorization = `Bearer ${res.data.access_token}`
          return api(original)
        }
      } catch {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

// ─── Service Functions ────────────────────────────────────

export const symptomsService = {
  analyze: (symptomText: string, city?: string, language?: string) =>
    api.post('/analyze-symptoms', { symptom_text: symptomText, city, language }),
}

export const placesService = {
  nearby: (params: Record<string, unknown>) =>
    api.get('/places/nearby', { params }),

  detail: (placeId: string) =>
    api.get(`/places/${placeId}`),

  route: (placeId: string, fromLat?: number, fromLng?: number) =>
    api.get('/places/route', { params: { to_place_id: placeId, from_lat: fromLat, from_lng: fromLng } }),
}

export const feesService = {
  get: (specialistType: string, city?: string) =>
    api.get('/fees', { params: { specialist_type: specialistType, city } }),
}

export const savedService = {
  list: () => api.get('/saved'),
  save: (data: Record<string, unknown>) => api.post('/saved', data),
  remove: (id: string) => api.delete(`/saved/${id}`),
}

export const historyService = {
  list: (limit = 10) => api.get('/history', { params: { limit } }),
  deleteItem: (id: string) => api.delete(`/history/${id}`),
  clearAll: () => api.delete('/history'),
}

export const feedbackService = {
  submit: (data: Record<string, unknown>) => api.post('/feedback', data),
}

export const authService = {
  signup: (email: string, password: string, displayName?: string) =>
    api.post('/auth/signup', { email, password, display_name: displayName }),
  login: (email: string, password: string) =>
    api.post('/auth/login', { email, password }),
  logout: (refreshToken: string) =>
    api.post('/auth/logout', { refresh_token: refreshToken }),
}

export const usersService = {
  getProfile: () => api.get('/users/me'),
  updateProfile: (data: Record<string, unknown>) => api.put('/users/me', data),
}
