<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h1 class="text-3xl font-bold text-gray-900">GitHub Analysis</h1>
      <div class="flex space-x-3">
        <button 
          @click="refreshGitHubStatus"
          class="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors"
        >
          Check GitHub Status
        </button>
      </div>
    </div>

    <!-- GitHub Connect Component -->
    <GitHubConnect />

    <!-- GitHub PR Analysis Component -->
    <GitHubPRAnalysis />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { usePRStore } from '../stores/prStore'
import GitHubConnect from '../components/GitHubConnect.vue'
import GitHubPRAnalysis from '../components/GitHubPRAnalysis.vue'

const prStore = usePRStore()

const refreshGitHubStatus = async () => {
  try {
    await prStore.checkGitHubStatus()
  } catch (error) {
    console.error('Failed to check GitHub status:', error)
  }
}

onMounted(async () => {
  await refreshGitHubStatus()
})
</script>
