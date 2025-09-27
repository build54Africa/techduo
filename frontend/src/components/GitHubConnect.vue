<template>
  <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-xl font-semibold text-gray-900">Connect GitHub Repository</h2>
      <div class="flex items-center space-x-2">
        <div
          class="w-2 h-2 rounded-full"
          :class="githubStatus?.available ? 'bg-green-500' : 'bg-red-500'"
        ></div>
        <span class="text-sm text-gray-600">
          {{ githubStatus?.available ? 'Connected' : 'Not Connected' }}
        </span>
      </div>
    </div>

    <div v-if="!githubStatus?.available" class="mb-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
      <div class="flex items-start">
        <svg class="w-5 h-5 text-yellow-600 mt-0.5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667
                   1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732
                   0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"/>
        </svg>
        <div>
          <h3 class="text-sm font-medium text-yellow-800">GitHub Token Required</h3>
          <p class="text-sm text-yellow-700 mt-1">
            Please configure a GitHub token in the backend to connect to repositories.
          </p>
        </div>
      </div>
    </div>

    <form @submit.prevent="connectRepo" class="space-y-4">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Repository Owner</label>
          <input
            v-model="form.owner"
            type="text"
            placeholder="e.g., microsoft"
            class="w-full px-3 py-2 border border-gray-300 rounded-md
                   focus:outline-none focus:ring-2 focus:ring-blue-500"
            :disabled="!githubStatus?.available"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Repository Name</label>
          <input
            v-model="form.repoName"
            type="text"
            placeholder="e.g., vscode"
            class="w-full px-3 py-2 border border-gray-300 rounded-md
                   focus:outline-none focus:ring-2 focus:ring-blue-500"
            :disabled="!githubStatus?.available"
          />
        </div>
      </div>

      <div class="flex justify-end space-x-3">
        <button
          type="button"
          @click="searchRepos"
          :disabled="!form.owner || loading"
          class="px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 disabled:opacity-50"
        >
          Search
        </button>
        <button
          type="submit"
          :disabled="!form.owner || !form.repoName || loading || !githubStatus?.available"
          class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 flex items-center space-x-2"
        >
          <svg v-if="loading" class="w-4 h-4 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582
                     9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003
                     0 01-15.357-2m15.357 2H15"/>
          </svg>
          <span>{{ loading ? 'Connecting...' : 'Connect Repository' }}</span>
        </button>
      </div>
    </form>

    <!-- Search Results -->
    <div v-if="searchResults.length > 0" class="mt-6">
      <h3 class="text-lg font-medium text-gray-900 mb-3">Search Results</h3>
      <div class="space-y-2 max-h-64 overflow-y-auto">
        <div
          v-for="repo in searchResults"
          :key="repo.full_name"
          class="flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer"
          @click="selectRepository(repo)"
        >
          <div class="flex-1">
            <h4 class="font-medium text-gray-900">{{ repo.full_name }}</h4>
            <p class="text-sm text-gray-600">{{ repo.description || 'No description' }}</p>
            <div class="flex items-center space-x-4 mt-1 text-xs text-gray-500">
              <span>⭐ {{ repo.stars }}</span>
              <span>🍴 {{ repo.forks }}</span>
              <span>🐛 {{ repo.open_issues }}</span>
              <span v-if="repo.language">{{ repo.language }}</span>
            </div>
          </div>
          <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
          </svg>
        </div>
      </div>
    </div>

    <!-- Connected Repositories -->
    <div v-if="repositories.length > 0" class="mt-6">
      <h3 class="text-lg font-medium text-gray-900 mb-3">Connected Repositories</h3>
      <div class="space-y-2">
        <div
          v-for="repo in repositories"
          :key="repo.id"
          class="flex items-center justify-between p-3 bg-green-50 border border-green-200 rounded-lg"
        >
          <div class="flex-1">
            <h4 class="font-medium text-green-900">{{ repo.owner }}/{{ repo.name }}</h4>
            <p class="text-sm text-green-700">{{ repo.github_url }}</p>
          </div>
          <div class="flex items-center space-x-2">
            <button
              @click="syncRepository(repo)"
              :disabled="loading"
              class="px-3 py-1 text-sm bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
            >
              Sync PRs
            </button>
            <button
              @click="removeRepository(repo)"
              class="px-3 py-1 text-sm text-red-600 hover:text-red-800"
            >
              Remove
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Repository PRs -->
    <div v-if="repositories.length > 0" class="mt-6">
      <h3 class="text-lg font-medium text-gray-900 mb-3">Repository PRs</h3>
      <div v-for="repo in repositories" :key="repo.id" class="mb-6">
        <div class="flex items-center justify-between mb-3 p-3 bg-gray-50 rounded-lg">
          <div class="font-semibold text-gray-900">{{ repo.owner }}/{{ repo.name }}</div>
          <button
            @click="loadRepoPRs(repo)"
            :disabled="loading"
            class="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {{ loading ? 'Loading...' : 'Load PRs' }}
          </button>
        </div>

        <div v-if="repo.prs?.length" class="space-y-2 max-h-64 overflow-y-auto">
          <div
            v-for="pr in repo.prs"
            :key="pr.number"
            class="p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer"
            @click="selectPRForAnalysis(repo, pr)"
          >
            <div class="flex items-center justify-between">
              <div class="flex-1">
                <div class="font-medium text-gray-900">
                  #{{ pr.number }} — {{ pr.title }}
                </div>
                <div class="text-sm text-gray-600 mt-1">by {{ pr.author }}</div>
              </div>
              <div class="flex items-center space-x-2">
                <span class="px-2 py-1 rounded text-xs font-medium" :class="getStatusBadgeClass(pr.status)">
                  {{ pr.status }}
                </span>
                <span v-if="pr.risk_score"
                      class="text-sm font-medium"
                      :class="getRiskScoreClass(pr.risk_score)">
                  {{ Math.round(pr.risk_score * 100) }}%
                </span>
              </div>
            </div>
          </div>
        </div>
        <div v-else-if="repo.prs !== undefined" class="text-sm text-gray-500 p-3">
          No PRs found
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { usePRStore } from '../stores/prStore'

const prStore = usePRStore()

const form = reactive({
  owner: '',
  repoName: ''
})

const searchResults = ref([])
const repositories = ref([])

const loading = computed(() => prStore.loading)
const githubStatus = computed(() => prStore.githubStatus)

const connectRepo = async () => {
  try {
    await prStore.connectRepository(form.owner, form.repoName)
    repositories.value = prStore.repositories
    form.owner = ''
    form.repoName = ''
    searchResults.value = []
  } catch (error) {
    console.error('Failed to connect repository:', error)
  }
}

const searchRepos = async () => {
  try {
    const result = await prStore.searchRepositories(form.owner)
    searchResults.value = result.repositories
  } catch (error) {
    console.error('Failed to search repositories:', error)
  }
}

const selectRepository = (repo) => {
  form.owner = repo.owner
  form.repoName = repo.name
  searchResults.value = []
}

const syncRepository = async (repo) => {
  try {
    await prStore.syncPullRequests(repo.owner, repo.name)
  } catch (error) {
    console.error('Failed to sync repository:', error)
  }
}

const removeRepository = (repo) => {
  const index = repositories.value.findIndex(r => r.id === repo.id)
  if (index > -1) repositories.value.splice(index, 1)
}

/**
 * ✅ FIX: Call syncPullRequests instead of loadPullRequests
 */
const loadRepoPRs = async (repo) => {
  try {
    await prStore.syncPullRequests(repo.owner, repo.name)
    const index = repositories.value.findIndex(r => r.id === repo.id)
    if (index > -1) {
      repositories.value[index].prs =
        prStore.repositories.find(r => r.id === repo.id)?.prs || []
    }
  } catch (error) {
    console.error('Failed to load PRs for repository:', error)
  }
}

const selectPRForAnalysis = (repo, pr) => {
  console.log('Selected PR', pr.number, 'in', repo.name)
}

onMounted(async () => {
  await prStore.checkGitHubStatus()
  repositories.value = prStore.repositories
})
</script>
