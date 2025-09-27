<template>
  <div class="space-y-4">
    <div v-if="prs.length === 0" class="text-center py-8 text-gray-500">
      No pull requests found
    </div>
    
    <div v-else class="space-y-3">
      <div 
        v-for="pr in prs" 
        :key="pr.number"
        class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
        @click="$emit('analyze', pr)"
      >
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-3">
            <div class="flex-shrink-0">
              <span class="text-sm font-medium text-gray-900">#{{ pr.number }}</span>
            </div>
            <div class="min-w-0 flex-1">
              <h3 class="text-sm font-medium text-gray-900 truncate">{{ pr.title }}</h3>
              <p class="text-sm text-gray-500">by {{ pr.author }}</p>
            </div>
          </div>
          
          <div class="flex items-center space-x-3">
            <!-- Risk Level Badge -->
            <span 
              class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
              :class="getRiskBadgeClass(pr.risk_level)"
            >
              {{ pr.risk_level?.toUpperCase() || 'UNKNOWN' }}
            </span>
            
            <!-- Risk Score -->
            <div class="text-right">
              <div class="text-sm font-medium text-gray-900">
                {{ Math.round((pr.risk_score || 0) * 100) }}%
              </div>
              <div class="text-xs text-gray-500">risk</div>
            </div>
            
            <!-- Status -->
            <span 
              class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium"
              :class="getStatusBadgeClass(pr.status)"
            >
              {{ pr.status }}
            </span>
          </div>
        </div>
        
        <!-- Conflict Files -->
        <div v-if="pr.conflict_files && pr.conflict_files.length > 0" class="mt-3">
          <div class="flex flex-wrap gap-1">
            <span 
              v-for="file in pr.conflict_files.slice(0, 3)" 
              :key="file"
              class="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-red-100 text-red-800"
            >
              {{ file }}
            </span>
            <span 
              v-if="pr.conflict_files.length > 3"
              class="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-gray-100 text-gray-600"
            >
              +{{ pr.conflict_files.length - 3 }} more
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  prs: {
    type: Array,
    default: () => []
  }
})

defineEmits(['analyze'])

const getRiskBadgeClass = (riskLevel) => {
  const classes = {
    low: 'bg-green-100 text-green-800',
    medium: 'bg-yellow-100 text-yellow-800',
    high: 'bg-red-100 text-red-800'
  }
  return classes[riskLevel] || 'bg-gray-100 text-gray-800'
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