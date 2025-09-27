<template>
  <div class="space-y-4">
    <div v-if="insights.length === 0" class="text-center py-4 text-gray-500">
      No AI insights available
    </div>
    
    <div v-else class="space-y-3">
      <div 
        v-for="insight in insights" 
        :key="insight.title"
        class="flex items-start space-x-3 p-3 rounded-lg"
        :class="getInsightClass(insight.type)"
      >
        <div class="flex-shrink-0">
          <div 
            class="w-6 h-6 rounded-full flex items-center justify-center text-sm"
            :class="getIconClass(insight.type)"
          >
            {{ getIcon(insight.type) }}
          </div>
        </div>
        <div class="flex-1 min-w-0">
          <h4 class="text-sm font-medium text-gray-900">{{ insight.title }}</h4>
          <p class="text-sm text-gray-600 mt-1">{{ insight.description }}</p>
          <button 
            v-if="insight.action"
            class="text-xs text-blue-600 hover:text-blue-800 mt-1"
          >
            {{ insight.action }} →
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  insights: {
    type: Array,
    default: () => []
  }
})

const getInsightClass = (type) => {
  const classes = {
    warning: 'bg-yellow-50 border border-yellow-200',
    info: 'bg-blue-50 border border-blue-200',
    success: 'bg-green-50 border border-green-200',
    error: 'bg-red-50 border border-red-200'
  }
  return classes[type] || 'bg-gray-50 border border-gray-200'
}

const getIconClass = (type) => {
  const classes = {
    warning: 'bg-yellow-100 text-yellow-600',
    info: 'bg-blue-100 text-blue-600',
    success: 'bg-green-100 text-green-600',
    error: 'bg-red-100 text-red-600'
  }
  return classes[type] || 'bg-gray-100 text-gray-600'
}

const getIcon = (type) => {
  const icons = {
    warning: '⚠️',
    info: 'ℹ️',
    success: '✅',
    error: '❌'
  }
  return icons[type] || 'ℹ️'
}
</script>