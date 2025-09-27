import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../services/api'

export const usePRStore = defineStore('pr', () => {
  const pullRequests = ref([])
  const loading = ref(false)
  const error = ref(null)

  const fetchPullRequests = async () => {
    loading.value = true
    error.value = null
    try {
      const response = await api.get('/prs/')
      pullRequests.value = response.data
    } catch (err) {
      error.value = err.message
      console.error('Failed to fetch PRs:', err)
      
      // If no PRs are available, use mock data for demo
      if (err.code === 'ECONNREFUSED') {
        pullRequests.value = [
          {
            number: 21,
            title: 'Update dashboard UI',
            author: 'alice',
            status: 'open',
            risk_score: 0.8,
            risk_level: 'high',
            conflict_files: ['src/dashboard.html'],
            head_branch: 'feature/dashboard-update'
          },
          {
            number: 24,
            title: 'Add new dashboard features',
            author: 'bob',
            status: 'open',
            risk_score: 0.7,
            risk_level: 'high',
            conflict_files: ['src/dashboard.html'],
            head_branch: 'feature/dashboard-features'
          }
        ]
        console.log('Using mock data - backend not available')
      }
    } finally {
      loading.value = false
    }
  }

  const analyzeRisk = async (prData) => {
    try {
      const response = await api.post('/risk/', prData)
      return response.data
    } catch (err) {
      error.value = err.message
      console.error('Risk analysis failed:', err)
      
      // Mock response for demo
      if (err.code === 'ECONNREFUSED') {
        return {
          pr_number: prData.pr_number,
          risk_score: 0.75,
          risk_level: 'high',
          confidence: 0.85,
          conflicts: [
            {
              conflicting_pr_number: 24,
              conflicting_files: ['src/dashboard.html'],
              risk_level: 'high'
            }
          ],
          ai_analysis: {
            ai_model: 'mock-model',
            confidence: 0.85,
            at_risk_files: ['src/dashboard.html']
          },
          status: 'analyzed',
          message: 'Mock analysis completed (backend not available)'
        }
      }
      throw err
    }
  }

  const getRecommendations = async (prData) => {
    try {
      const response = await api.post('/recommendation/', prData)
      return response.data
    } catch (err) {
      error.value = err.message
      console.error('Recommendations failed:', err)
      
      // Mock response for demo
      if (err.code === 'ECONNREFUSED') {
        return {
          pr_number: prData.pr_number,
          recommendations: [
            {
              type: 'sync_suggestion',
              title: 'Sync with conflicting PRs',
              description: 'Multiple PRs are modifying the same files. Consider syncing branches before merging.',
              priority: 'high',
              action: 'sync_branches'
            }
          ],
          priority: 'high',
          ai_generated: true
        }
      }
      throw err
    }
  }

  const predictConflicts = async (features) => {
    try {
      const response = await api.post('/predict/', { features })
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    }
  }

  const trainMLModel = async () => {
    try {
      const response = await api.post('/train/')
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    }
  }

  return {
    pullRequests,
    loading,
    error,
    fetchPullRequests,
    analyzeRisk,
    getRecommendations,
    predictConflicts,
    trainMLModel
  }
})