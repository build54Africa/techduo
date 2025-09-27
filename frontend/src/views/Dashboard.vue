<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex justify-between items-center">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">MergeSensei Dashboard</h1>
        <p class="text-gray-600 mt-2">AI-powered conflict prediction and resolution</p>
      </div>
      <div class="flex space-x-3">
        <button 
          @click="refreshData"
          class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          <span>Refresh</span>
        </button>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <StatCard
        title="Total PRs"
        :value="stats.totalPRs"
        icon="📊"
        color="blue"
      />
      <StatCard
        title="High Risk"
        :value="stats.highRiskPRs"
        icon="⚠️"
        color="red"
      />
      <StatCard
        title="AI Predictions"
        :value="stats.aiPredictions"
        icon="🤖"
        color="green"
      />
      <StatCard
        title="Resolved Conflicts"
        :value="stats.resolvedConflicts"
        icon="✅"
        color="purple"
      />
    </div>

    <!-- Main Content Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Pull Requests List -->
      <div class="lg:col-span-2">
        <div class="bg-white rounded-lg shadow-sm border border-gray-200">
          <div class="p-6 border-b border-gray-200">
            <h2 class="text-xl font-semibold text-gray-900">Recent Pull Requests</h2>
          </div>
          <div class="p-6">
            <PullRequestList :prs="pullRequests" @analyze="analyzePR" />
          </div>
        </div>
      </div>

      <!-- AI Insights -->
      <div class="space-y-6">
        <div class="bg-white rounded-lg shadow-sm border border-gray-200">
          <div class="p-6 border-b border-gray-200">
            <h2 class="text-xl font-semibold text-gray-900">AI Insights</h2>
          </div>
          <div class="p-6">
            <AIInsights :insights="aiInsights" />
          </div>
        </div>

        <div class="bg-white rounded-lg shadow-sm border border-gray-200">
          <div class="p-6 border-b border-gray-200">
            <h2 class="text-xl font-semibold text-gray-900">Risk Distribution</h2>
          </div>
          <div class="p-6">
            <RiskChart :data="riskData" />
          </div>
        </div>
      </div>
    </div>

    <!-- Analysis Modal -->
    <AnalysisModal 
      v-if="showAnalysisModal"
      :pr="selectedPR"
      @close="closeAnalysisModal"
      @analyze="performAnalysis"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { usePRStore } from '../stores/prStore'
import StatCard from '../components/StatCard.vue'
import PullRequestList from '../components/PullRequestList.vue'
import AIInsights from '../components/AIInsights.vue'
import RiskChart from '../components/RiskChart.vue'
import AnalysisModal from '../components/AnalysisModal.vue'

const prStore = usePRStore()

// Reactive data
const pullRequests = ref([])
const aiInsights = ref([])
const showAnalysisModal = ref(false)
const selectedPR = ref(null)

// Computed stats
const stats = computed(() => ({
  totalPRs: pullRequests.value.length,
  highRiskPRs: pullRequests.value.filter(pr => pr.risk_level === 'high').length,
  aiPredictions: pullRequests.value.filter(pr => pr.ai_generated).length,
  resolvedConflicts: pullRequests.value.filter(pr => pr.status === 'merged').length
}))

const riskData = computed(() => {
  const riskLevels = ['low', 'medium', 'high']
  return riskLevels.map(level => ({
    level,
    count: pullRequests.value.filter(pr => pr.risk_level === level).length
  }))
})

// Methods
const refreshData = async () => {
  await prStore.fetchPullRequests()
  pullRequests.value = prStore.pullRequests
  await loadAIInsights()
}

const analyzePR = (pr) => {
  selectedPR.value = pr
  showAnalysisModal.value = true
}

const closeAnalysisModal = () => {
  showAnalysisModal.value = false
  selectedPR.value = null
}

const performAnalysis = async (prData) => {
  try {
    const result = await prStore.analyzeRisk(prData)
    // Update the PR with analysis results
    const index = pullRequests.value.findIndex(p => p.number === prData.pr_number)
    if (index !== -1) {
      pullRequests.value[index] = { ...pullRequests.value[index], ...result }
    }
    closeAnalysisModal()
  } catch (error) {
    console.error('Analysis failed:', error)
  }
}

const loadAIInsights = async () => {
  // Mock AI insights for now
  aiInsights.value = [
    {
      type: 'warning',
      title: 'High Conflict Risk Detected',
      description: 'PR #21 and #24 are modifying the same files',
      action: 'Review conflicts'
    },
    {
      type: 'info',
      title: 'AI Model Updated',
      description: 'Conflict prediction accuracy improved to 94%',
      action: 'View details'
    }
  ]
}

// Lifecycle
onMounted(async () => {
  await refreshData()
})
</script>
```

