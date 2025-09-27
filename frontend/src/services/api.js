import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // Increased to 30 seconds
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log(`Making ${config.method?.toUpperCase()} request to ${config.url}`)
    return config
  },
  (error) => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    if (error.code === 'ECONNREFUSED') {
      console.error('Backend server is not running. Please start it with: python manage.py runserver')
      error.message = 'Backend server is not running. Please start it first.'
    } else if (error.code === 'ECONNABORTED') {
      console.error('Request timeout. The analysis is taking longer than expected.')
      error.message = 'Analysis timeout. Please try again or check if the PR exists.'
    } else if (error.response) {
      console.error('API Error:', error.response.data || error.message)
    } else {
      console.error('Network Error:', error.message)
    }
    return Promise.reject(error)
  }
)

// GitHub API methods
export const githubAPI = {
  getStatus: () => api.get('/github/status/'),
  connectRepository: (data) => api.post('/github/connect/', data),
  syncPullRequests: (data) => api.post('/github/sync/', data),
  analyzePR: (data) => api.post('/github/analyze/', data, { timeout: 60000 }), // 60 seconds for analysis
  searchRepositories: (params) => api.get('/github/search/', { params }),
  repoPRs: (params) => api.get('/github/repo-prs/', { params })
}

export default api