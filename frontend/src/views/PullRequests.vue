<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h1 class="text-3xl font-bold text-gray-900">Pull Requests</h1>
      <button class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
        New Analysis
      </button>
    </div>
    
    <div class="bg-white rounded-lg shadow-sm border border-gray-200">
      <div class="p-6">
        <PullRequestList :prs="pullRequests" @analyze="analyzePR" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { usePRStore } from '../stores/prStore'
import PullRequestList from '../components/PullRequestList.vue'

const prStore = usePRStore()
const pullRequests = ref([])

const analyzePR = (pr) => {
  console.log('Analyzing PR:', pr)
}

onMounted(async () => {
  await prStore.fetchPullRequests()
  pullRequests.value = prStore.pullRequests
})
</script>
