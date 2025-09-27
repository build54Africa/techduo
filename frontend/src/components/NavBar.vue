<template>
  <nav class="bg-white shadow-lg border-b border-gray-200">
    <div class="container mx-auto px-4">
      <div class="flex justify-between items-center h-16">
        <!-- Logo -->
        <div class="flex items-center space-x-2">
          <div class="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
            <span class="text-white font-bold text-sm">MS</span>
          </div>
          <span class="text-xl font-bold text-gray-800">MergeSensei</span>
        </div>

        <!-- Navigation Links -->
        <div class="flex space-x-6">
          <router-link 
            to="/" 
            class="text-gray-600 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium transition-colors"
            :class="{ 'text-blue-600 bg-blue-50': $route.path === '/' }"
          >
            Dashboard
          </router-link>
          <router-link 
            to="/prs" 
            class="text-gray-600 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium transition-colors"
            :class="{ 'text-blue-600 bg-blue-50': $route.path === '/prs' }"
          >
            Pull Requests
          </router-link>
          <router-link 
            to="/ai" 
            class="text-gray-600 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium transition-colors"
            :class="{ 'text-blue-600 bg-blue-50': $route.path === '/ai' }"
          >
            AI Analysis
          </router-link>
        </div>

        <!-- Status Indicator -->
        <div class="flex items-center space-x-2">
          <div class="w-2 h-2 bg-green-500 rounded-full"></div>
          <span class="text-sm text-gray-600">AI Active</span>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
// Component logic
</script>
