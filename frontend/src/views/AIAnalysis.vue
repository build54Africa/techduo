<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h1 class="text-3xl font-bold text-gray-900">AI Analysis</h1>
      <div class="flex space-x-3">
        <button 
          @click="trainModel"
          :disabled="training"
          class="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 disabled:opacity-50"
        >
          {{ training ? 'Training...' : 'Train Model' }}
        </button>
        <button class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
          Run Prediction
        </button>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 class="text-xl font-semibold text-gray-900 mb-4">AI Status</h2>
        <div class="space-y-3">
          <div class="flex justify-between">
            <span class="text-gray-600">Conflict AI</span>
            <span class="text-green-600 font-medium">Active</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-600">Recommendation AI</span>
            <span class="text-green-600 font-medium">Active</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-600">ML Model</span>
            <span class="text-yellow-600 font-medium">{{ mlModelTrained ? 'Trained' : 'Not Trained' }}</span>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 class="text-xl font-semibold text-gray-900 mb-4">Model Performance</h2>
        <div class="space-y-3">
          <div class="flex justify-between">
            <span class="text-gray-600">Accuracy</span>
            <span class="text-blue-600 font-medium">94.2%</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-600">Predictions Made</span>
            <span class="text-blue-600 font-medium">1,247</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-600">Last Updated</span>
            <span class="text-gray-600">2 hours ago</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { usePRStore } from '../stores/prStore'

const prStore = usePRStore()
const training = ref(false)
const mlModelTrained = ref(false)

const trainModel = async () => {
  training.value = true
  try {
    const result = await prStore.trainMLModel()
    console.log('Training result:', result)
    mlModelTrained.value = true
  } catch (error) {
    console.error('Training failed:', error)
  } finally {
    training.value = false
  }
}
</script>
```

