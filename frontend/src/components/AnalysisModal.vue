<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-white rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
      <!-- Header -->
      <div class="p-6 border-b border-gray-200">
        <div class="flex items-center justify-between">
          <h2 class="text-2xl font-bold text-gray-900">
            AI Analysis - PR #{{ pr?.number }}
          </h2>
          <button 
            @click="$emit('close')"
            class="text-gray-400 hover:text-gray-600"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      <!-- Content -->
      <div class="p-6 space-y-6">
        <!-- PR Info -->
        <div class="bg-gray-50 rounded-lg p-4">
          <h3 class="text-lg font-semibold text-gray-900 mb-2">{{ pr?.title }}</h3>
          <div class="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span class="text-gray-600">Author:</span>
              <span class="ml-2 font-medium">{{ pr?.author }}</span>
            </div>
            <div>
              <span class="text-gray-600">Branch:</span>
              <span class="ml-2 font-medium">{{ pr?.head_branch }}</span>
            </div>
          </div>
        </div>

        <!-- Analysis Form -->
        <div class="space-y-4">
          <h3 class="text-lg font-semibold text-gray-900">Analysis Parameters</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Repository Name
              </label>
              <input 
                v-model="analysisData.repo_name"
                type="text"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="mergesensei-demo"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Repository Owner
              </label>
              <input 
                v-model="analysisData.repo_owner"
                type="text"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="techduo"
              />
            </div>
          </div>
        </div>

        <!-- Analysis Results -->
        <div v-if="analysisResult" class="space-y-4">
          <h3 class="text-lg font-semibold text-gray-900">Analysis Results</h3>
          
          <!-- Risk Score -->
          <div class="bg-white border border-gray-200 rounded-lg p-4">
            <div class="flex items-center justify-between mb-2">
              <span class="text-sm font-medium text-gray-700">Risk Score</span>
              <span class="text-2xl font-bold" :class="getRiskScoreClass(analysisResult.risk_score)">
                {{ Math.round(analysisResult.risk_score * 100) }}%
              </span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-2">
              <div 
                class="h-2 rounded-full transition-all duration-300"
                :class="getRiskBarClass(analysisResult.risk_score)"
                :style="{ width: `${analysisResult.risk_score * 100}%` }"
              ></div>
            </div>
          </div>

          <!-- AI Analysis Details -->
          <div v-if="analysisResult.ai_analysis" class="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h4 class="font-semibold text-blue-900 mb-2">AI Analysis Details</h4>
            <div class="space-y-2 text-sm">
              <div>
                <span class="text-blue-700 font-medium">Model:</span>
                <span class="ml-2 text-blue-600">{{ analysisResult.ai_analysis.ai_model }}</span>
              </div>
              <div>
                <span class="text-blue-700 font-medium">Confidence:</span>
                <span class="ml-2 text-blue-600">{{ Math.round(analysisResult.ai_analysis.confidence * 100) }}%</span>
              </div>
              <div v-if="analysisResult.ai_analysis.at_risk_files?.length > 0">
                <span class="text-blue-700 font-medium">At Risk Files:</span>
                <div class="mt-1 flex flex-wrap gap-1">
                  <span 
                    v-for="file in analysisResult.ai_analysis.at_risk_files"
                    :key="file"
                    class="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs"
                  >
                    {{ file }}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- Conflicts -->
          <div v-if="analysisResult.conflicts?.length > 0" class="space-y-3">
            <h4 class="font-semibold text-gray-900">Detected Conflicts</h4>
            <div 
              v-for="conflict in analysisResult.conflicts"
              :key="conflict.conflicting_pr_number"
              class="bg-red-50 border border-red-200 rounded-lg p-3"
            >
              <div class="flex items-center justify-between">
                <span class="font-medium text-red-900">
                  Conflict with PR #{{ conflict.conflicting_pr_number }}
                </span>
                <span class="text-sm text-red-600">
                  {{ conflict.risk_level?.toUpperCase() }} RISK
                </span>
              </div>
              <div v-if="conflict.conflicting_files?.length > 0" class="mt-2">
                <div class="flex flex-wrap gap-1">
                  <span 
                    v-for="file in conflict.conflicting_files"
                    :key="file"
                    class="px-2 py-1 bg-red-100 text-red-800 rounded text-xs"
                  >
                    {{ file }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Actions -->
        <div class="flex justify-end space-x-3 pt-4 border-t border-gray-200">
          <button 
            @click="$emit('close')"
            class="px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors"
          >
            Close
          </button>
          <button 
            @click="runAnalysis"
            :disabled="loading"
            class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 transition-colors flex items-center space-x-2"
          >
            <svg v-if="loading" class="w-4 h-4 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            <span>{{ loading ? 'Analyzing...' : 'Run AI Analysis' }}</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'

const props = defineProps({
  pr: Object
})

const emit = defineEmits(['close', 'analyze'])

const loading = ref(false)
const analysisResult = ref(null)

const analysisData = reactive({
  pr_number: props.pr?.number || '',
  repo_name: 'mergesensei-demo',
  repo_owner: 'techduo'
})

const runAnalysis = async () => {
  loading.value = true
  try {
    await emit('analyze', analysisData)
  } finally {
    loading.value = false
  }
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
</script>