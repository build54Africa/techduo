<template>
  <div class="space-y-6">
    <!-- Repository Selector -->
    <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h2 class="text-xl font-semibold text-gray-900 mb-4">Analyze GitHub Pull Request</h2>
      
      <!-- Error Message -->
      <div v-if="error" class="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
        <div class="flex items-start">
          <svg class="w-5 h-5 text-red-600 mt-0.5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div>
            <h3 class="text-sm font-medium text-red-800">Analysis Failed</h3>
            <p class="text-sm text-red-700 mt-1">{{ error }}</p>
            <button 
              @click="clearError"
              class="mt-2 text-xs text-red-600 hover:text-red-800 underline"
            >
              Dismiss
            </button>
          </div>
        </div>
      </div>
      
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Repository</label>
          <select 
            v-model="selectedRepo"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Select a repository</option>
            <option 
              v-for="repo in repositories"
              :key="repo.id"
              :value="repo"
            >
              {{ repo.owner }}/{{ repo.name }}
            </option>
          </select>
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Pull Request Number</label>
          <input 
            v-model="prNumber"
            type="number"
            placeholder="e.g., 123"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        
        <div class="flex items-end">
          <button 
            @click="analyzePR"
            :disabled="!selectedRepo || !prNumber || loading"
            class="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 transition-colors flex items-center justify-center space-x-2"
          >
            <svg v-if="loading" class="w-4 h-4 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            <span>{{ loading ? 'Analyzing...' : 'Analyze PR' }}</span>
          </button>
        </div>
      </div>
      
      <!-- Loading Progress -->
      <div v-if="loading || progress > 0" class="mt-4">
        <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div class="flex items-center mb-2">
            <svg class="w-5 h-5 text-blue-600 animate-spin mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            <div>
              <h4 class="text-sm font-medium text-blue-900">AI Analysis in Progress</h4>
              <p class="text-sm text-blue-700 mt-1">
                This may take up to 60 seconds for complex PRs. Please wait...
              </p>
            </div>
          </div>
          <!-- Progress Bar -->
          <div class="w-full bg-gray-200 rounded-full h-2">
            <div 
              class="h-2 bg-blue-600 rounded-full transition-all duration-300"
              :style="{ width: `${Math.floor(progress)}%` }"
            ></div>
          </div>
          <p class="text-xs text-gray-600 mt-1">Analyzing PR… {{ Math.floor(progress) }}%</p>
        </div>
      </div>
    </div>

    <!-- Analysis Results -->
    <div v-if="analysisResult" class="space-y-6">
      <!-- PR Information -->
      <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div class="flex items-start justify-between mb-4">
          <div>
            <h3 class="text-xl font-semibold text-gray-900">
              PR #{{ analysisResult.pr_number }}: {{ analysisResult.github_data.title }}
            </h3>
            <p class="text-gray-600 mt-1">
              by {{ analysisResult.github_data.author }} • 
              {{ analysisResult.github_data.base_branch }} ← {{ analysisResult.github_data.head_branch }}
            </p>
          </div>
          <a 
            :href="analysisResult.github_data.html_url"
            target="_blank"
            class="text-blue-600 hover:text-blue-800 flex items-center space-x-1"
          >
            <span>View on GitHub</span>
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
            </svg>
          </a>
        </div>

        <!-- Risk Score -->
        <div class="bg-gray-50 rounded-lg p-4 mb-4">
          <div class="flex items-center justify-between mb-2">
            <span class="text-sm font-medium text-gray-700">AI Risk Assessment</span>
            <span 
              class="text-2xl font-bold"
              :class="getRiskScoreClass(analysisResult.ai_analysis.risk_score)"
            >
              {{ Math.round(analysisResult.ai_analysis.risk_score * 100) }}%
            </span>
          </div>
          <div class="w-full bg-gray-200 rounded-full h-3">
            <div 
              class="h-3 rounded-full transition-all duration-300"
              :class="getRiskBarClass(analysisResult.ai_analysis.risk_score)"
              :style="{ width: `${analysisResult.ai_analysis.risk_score * 100}%` }"
            ></div>
          </div>
          <div class="flex justify-between text-xs text-gray-600 mt-1">
            <span>Low Risk</span>
            <span>High Risk</span>
          </div>
        </div>

        <!-- AI Analysis Details -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h4 class="font-semibold text-blue-900 mb-2">AI Analysis</h4>
            <div class="space-y-2 text-sm">
              <div>
                <span class="text-blue-700 font-medium">Model:</span>
                <span class="ml-2 text-blue-600">{{ analysisResult.ai_analysis.ai_model }}</span>
              </div>
              <div>
                <span class="text-blue-700 font-medium">Confidence:</span>
                <span class="ml-2 text-blue-600">{{ Math.round(analysisResult.ai_analysis.confidence * 100) }}%</span>
              </div>
              <div>
                <span class="text-blue-700 font-medium">Risk Level:</span>
                <span 
                  class="ml-2 px-2 py-1 rounded-full text-xs font-medium"
                  :class="getRiskBadgeClass(analysisResult.ai_analysis.risk_level)"
                >
                  {{ analysisResult.ai_analysis.risk_level?.toUpperCase() }}
                </span>
              </div>
            </div>
          </div>

          <div class="bg-green-50 border border-green-200 rounded-lg p-4">
            <h4 class="font-semibold text-green-900 mb-2">PR Statistics</h4>
            <div class="space-y-2 text-sm">
              <div>
                <span class="text-green-700 font-medium">Files Changed:</span>
                <span class="ml-2 text-green-600">{{ analysisResult.github_data.changed_files }}</span>
              </div>
              <div>
                <span class="text-green-700 font-medium">Additions:</span>
                <span class="ml-2 text-green-600">+{{ analysisResult.github_data.additions }}</span>
              </div>
              <div>
                <span class="text-green-700 font-medium">Deletions:</span>
                <span class="ml-2 text-green-600">-{{ analysisResult.github_data.deletions }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Detailed Conflicts -->
      <div v-if="analysisResult.conflicts_detailed?.length > 0" class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Potential Line Conflicts</h3>
        <div class="space-y-4">
          <div 
            v-for="conflict in analysisResult.conflicts_detailed"
            :key="`${conflict.with_pr}-${conflict.file}`"
            class="bg-red-50 border border-red-200 rounded-lg p-4"
          >
            <div class="flex items-center justify-between mb-2">
              <h4 class="font-medium text-red-900">{{ conflict.file }}</h4>
              <span class="text-sm text-red-600">Conflicts with PR #{{ conflict.with_pr }}</span>
            </div>
            <div class="space-y-2">
              <div 
                v-for="(overlap, idx) in conflict.overlaps"
                :key="idx"
                class="flex items-center space-x-4 text-sm"
              >
                <div class="flex items-center space-x-2">
                  <span class="px-2 py-1 bg-red-100 text-red-800 rounded text-xs">
                    This PR: lines {{ overlap.this_lines }}
                  </span>
                  <span class="text-gray-400">↔</span>
                  <span class="px-2 py-1 bg-orange-100 text-orange-800 rounded text-xs">
                    PR #{{ conflict.with_pr }}: lines {{ overlap.other_lines }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Recommendations -->
      <div v-if="analysisResult.recommendations?.length > 0" class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">AI Recommendations</h3>
        <div class="space-y-3">
          <div 
            v-for="(rec, index) in analysisResult.recommendations"
            :key="index"
            class="flex items-start space-x-3 p-3 rounded-lg"
            :class="getRecommendationClass(rec.priority)"
          >
            <div class="flex-shrink-0">
              <div 
                class="w-6 h-6 rounded-full flex items-center justify-center text-sm"
                :class="getRecommendationIconClass(rec.priority)"
              >
                {{ getRecommendationIcon(rec.priority) }}
              </div>
            </div>
            <div class="flex-1">
              <h4 class="font-medium text-gray-900">{{ rec.title }}</h4>
              <p class="text-sm text-gray-600 mt-1">{{ rec.description }}</p>
              <div class="flex items-center space-x-2 mt-2">
                <span 
                  class="px-2 py-1 rounded text-xs font-medium"
                  :class="getPriorityBadgeClass(rec.priority)"
                >
                  {{ rec.priority?.toUpperCase() }} PRIORITY
                </span>
                <span class="text-xs text-gray-500">{{ rec.type?.replace('_', ' ').toUpperCase() }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { usePRStore } from '../stores/prStore'

const prStore = usePRStore()

const selectedRepo = ref(null)
const prNumber = ref('')
const analysisResult = ref(null)
const error = ref(null)
const progress = ref(0)

const repositories = computed(() => prStore.repositories)
const loading = computed(() => prStore.loading)

let progressTimer = null

const startProgress = () => {
  progress.value = 5
  progressTimer = setInterval(() => {
    if (progress.value < 90) {
      progress.value += Math.max(1, (90 - progress.value) * 0.05)
    }
  }, 200)
}

const finishProgress = () => {
  if (progressTimer) {
    clearInterval(progressTimer)
    progressTimer = null
  }
  progress.value = 100
  setTimeout(() => {
    progress.value = 0
  }, 500)
}

const analyzePR = async () => {
  error.value = null
  analysisResult.value = null
  loading.value = true
  startProgress()
  
  try {
    const result = await prStore.analyzeGitHubPR(
      selectedRepo.value.owner,
      selectedRepo.value.name,
      parseInt(prNumber.value)
    )
    analysisResult.value = result
  } catch (err) {
    console.error('Failed to analyze PR:', err)
    error.value = err.message || 'Failed to analyze PR. Please try again.'
  } finally {
    loading.value = false
    finishProgress()
  }
}

const clearError = () => {
  error.value = null
}

const getRiskScoreClass = (score) => {
  if (score > 0.7) return 'text-red-600'
  if (score > 0.4) return 'text-yellow-600'
  return 'text-green-600'
}

const getRiskBarClass = (score) => {
  if (score > 0.7) return 'bg-red-500'
  if (score > 0.4) return 'bg-yellow-500'
  return 'bg-green-500'
}

const getRiskBadgeClass = (level) => {
  const classes = {
    low: 'bg-green-100 text-green-800',
    medium: 'bg-yellow-100 text-yellow-800',
    high: 'bg-red-100 text-red-800'
  }
  return classes[level] || 'bg-gray-100 text-gray-800'
}

const getRecommendationClass = (priority) => {
  const classes = {
    high: 'bg-red-50 border border-red-200',
    medium: 'bg-yellow-50 border border-yellow-200',
    low: 'bg-green-50 border border-green-200'
  }
  return classes[priority] || 'bg-gray-50 border border-gray-200'
}

const getRecommendationIconClass = (priority) => {
  const classes = {
    high: 'bg-red-100 text-red-600',
    medium: 'bg-yellow-100 text-yellow-600',
    low: 'bg-green-100 text-green-600'
  }
  return classes[priority] || 'bg-gray-100 text-gray-600'
}

const getRecommendationIcon = (priority) => {
  const icons = {
    high: '⚠️',
    medium: 'ℹ️',
    low: '✅'
  }
  return icons[priority] || 'ℹ️'
}

const getPriorityBadgeClass = (priority) => {
  const classes = {
    high: 'bg-red-100 text-red-800',
    medium: 'bg-yellow-100 text-yellow-800',
    low: 'bg-green-100 text-green-800'
  }
  return classes[priority] || 'bg-gray-100 text-gray-800'
}

const loadRepoPRs = async (repo) => {
  try {
    const prs = await prStore.repoPRs(repo.owner, repo.name)
    repo.prs = prs
  } catch (error) {
    console.error('Failed to load repo PRs:', error)
  }
}

const selectPRForAnalysis = (repo, pr) => {
  // Emit event to parent component to switch to analysis tab
  // or you can directly set the selected repo and PR number
  selectedRepo.value = repo
  prNumber.value = pr.number
}

const getStatusBadgeClass = (status) => {
  const classes = {
    open: 'bg-blue-100 text-blue-800',
    closed: 'bg-gray-100 text-gray-800',
    merged: 'bg-green-100 text-green-800'
  }
  return classes[status] || 'bg-gray-100 text-gray-800'
}
</script>