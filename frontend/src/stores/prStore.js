import { defineStore } from 'pinia'
import { ref } from 'vue'
import api, { githubAPI } from '../services/api'

export const usePRStore = defineStore('pr', () => {
  const pullRequests = ref([])
  const repositories = ref([])
  const loading = ref(false)
  const error = ref(null)
  const githubStatus = ref(null)

  // GitHub methods
  const checkGitHubStatus = async () => {
    try {
      const response = await githubAPI.getStatus()
      githubStatus.value = response.data
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    }
  }

  const connectRepository = async (owner, repoName) => {
    loading.value = true
    error.value = null
    try {
      const response = await githubAPI.connectRepository({
        owner,
        repo_name: repoName
      })
      
      // Add to repositories list
      const repo = response.data.repository
      const existingIndex = repositories.value.findIndex(r => r.id === repo.id)
      if (existingIndex >= 0) {
        repositories.value[existingIndex] = repo
      } else {
        repositories.value.push(repo)
      }
      
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const syncPullRequests = async (owner, repoName, state = 'open') => {
    loading.value = true
    error.value = null
    try {
      const response = await githubAPI.syncPullRequests({
        owner,
        repo_name: repoName,
        state
      })
      
      // Update pull requests list
      await fetchPullRequests()
      
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const analyzeGitHubPR = async (owner, repoName, prNumber) => {
    try {
      const response = await githubAPI.analyzePR({
        owner,
        repo_name: repoName,
        pr_number: prNumber
      })
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    }
  }

  const searchRepositories = async (query, language = null) => {
    try {
      const response = await githubAPI.searchRepositories({
        q: query,
        language
      })
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    }
  }

  // Existing methods
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
    repositories,
    loading,
    error,
    githubStatus,
    checkGitHubStatus,
    connectRepository,
    syncPullRequests,
    analyzeGitHubPR,
    searchRepositories,
    fetchPullRequests,
    analyzeRisk,
    getRecommendations,
    predictConflicts,
    trainMLModel
  }
})